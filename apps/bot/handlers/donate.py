import uuid

from click_up import ClickUp
from django.utils.translation import activate
from django.utils.translation import gettext as _
from payme import Payme
from telebot import TeleBot
from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
    CallbackQuery,
)

from apps.bot.logger import logger
from apps.bot.utils import update_or_create_user
from apps.bot.utils.language import set_language_code
from apps.shop.models.donate import Donate
from apps.shop.models.order import Order
from apps.shop.models.users import BotUsers
from core import settings

# Initialize payment processors
click_up = ClickUp(
    service_id=settings.CLICK_SERVICE_ID, merchant_id=settings.CLICK_MERCHANT_ID
)
payme = Payme(payme_id=settings.PAYME_ID, is_test_mode=settings.PAYME_TEST_MODE)


def send_donation_selection(
    chat_id: int, row_width: int = 2
) -> (str, InlineKeyboardMarkup):
    """
    Build the donation selection message and keyboard.
    """
    donate_prices = Donate.objects.filter(is_active=True)
    keyboard = InlineKeyboardMarkup()
    row = []
    for index, donate in enumerate(donate_prices):
        text = f"{int(float(donate.amount)):,} UZS".replace(",", " ")
        button = InlineKeyboardButton(text=text, callback_data=f"donate_{donate.id}")
        row.append(button)
        if (index + 1) % row_width == 0:
            keyboard.row(*row)
            row = []
    if row:
        keyboard.row(*row)
    # Add a Cancel button at the bottom
    keyboard.add(InlineKeyboardButton(text=_("Cancel"), callback_data="donate_cancel"))
    text = _("Please select a donation amount:")
    return text, keyboard


def get_payment_method_keyboard(order: Order) -> (str, InlineKeyboardMarkup):
    """
    Build the payment method selection message and keyboard for a given order.
    """
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            text=_("Payme"), callback_data=f"select_donate_payme_{order.id}"
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text=_("Click"), callback_data=f"select_donate_click_{order.id}"
        )
    )
    # Back button to go back to donation amount selection
    keyboard.add(
        InlineKeyboardButton(text=_("Back"), callback_data="back_to_amount_selection")
    )
    text = _(
        "Please select a payment method to complete your donation of {amount}:"
    ).format(amount=order.amount)
    return text, keyboard


def get_payment_link_keyboard(
    order: Order, payment_link: str, method: str
) -> (str, InlineKeyboardMarkup):
    """
    Build the final payment link message and keyboard.
    The `method` parameter should be either "payme" or "click".
    """
    keyboard = InlineKeyboardMarkup()
    button_text = _("Payme") if method == "payme" else _("Click")
    # Button to open the actual payment link
    keyboard.add(InlineKeyboardButton(text=button_text, url=payment_link))
    # Back button to return to the payment method selection screen
    keyboard.add(
        InlineKeyboardButton(
            text=_("Back"), callback_data=f"back_to_payment_method_{order.id}"
        )
    )
    text = _("Click the button below to complete your donation of {amount}:").format(
        amount=order.amount
    )
    return text, keyboard


def handle_donate(message: Message, bot: TeleBot) -> None:
    """
    Handle the initial donation command.
    """
    activate(set_language_code(message.from_user.id))
    update_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        is_active=True,
    )
    logger.info(f"User {message.from_user.id} initiated a donation.")

    text, keyboard = send_donation_selection(message.chat.id)
    bot.send_message(message.chat.id, text, reply_markup=keyboard)


def handle_donate_selection(call: CallbackQuery, bot: TeleBot) -> None:
    """
    Handle the donation amount selection and the "cancel/back" actions from the donation selection screen.
    """
    activate(set_language_code(call.from_user.id))
    try:
        user = BotUsers.objects.get(telegram_id=call.from_user.id)
    except BotUsers.DoesNotExist:
        bot.answer_callback_query(call.id, _("User not found."))
        return

    # Handle cancel or back actions for donation selection
    if call.data in ("donate_cancel", "back_to_amount_selection"):
        if call.data == "donate_cancel":
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, _("Donation canceled."))
            bot.answer_callback_query(call.id, _("Donation canceled."))
        elif call.data == "back_to_amount_selection":
            text, keyboard = send_donation_selection(call.message.chat.id)
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=text,
                reply_markup=keyboard,
            )
            bot.answer_callback_query(call.id, _("Returning to donation options."))
        return

    # Process donation amount selection (expected format: "donate_<donate_id>")
    if call.data.startswith("donate_") and not (
        call.data.startswith("donate_payme_") or call.data.startswith("donate_click_")
    ):
        try:
            donate_id = int(call.data.split("_")[1])
        except (IndexError, ValueError):
            bot.answer_callback_query(call.id, _("Invalid donation data."))
            return

        try:
            donate = Donate.objects.get(id=donate_id)
        except Donate.DoesNotExist:
            bot.answer_callback_query(call.id, _("Donation option not found."))
            return

        order_identifier = f"donate_{uuid.uuid4()}_{donate.id}"
        order = Order.objects.create(
            order_id=order_identifier,
            amount=donate.amount,
            user=user,
            order_type=Order.OrderType.DONATE,
        )

        text, keyboard = get_payment_method_keyboard(order)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=keyboard,
        )
        bot.answer_callback_query(call.id, _("Donation amount selected."))
        logger.info(
            f"User {call.from_user.id} created order {order.id} for donation amount {donate.amount}."
        )
        return

    bot.answer_callback_query(call.id, _("Unrecognized action."))
    logger.info(f"User {call.from_user.id} sent unrecognized callback: {call.data}")


def handle_send_donate_link(call: CallbackQuery, bot: TeleBot) -> None:
    """
    Handle the payment method selection and display the final payment link.
    Also supports going back to the payment method selection screen.
    """
    activate(set_language_code(call.from_user.id))

    # Handle navigation back to the payment method selection screen
    if call.data.startswith("back_to_payment_method_"):
        try:
            order_id = int(call.data.split("_")[-1])
            order = Order.objects.get(id=order_id)
        except (ValueError, Order.DoesNotExist):
            bot.answer_callback_query(call.id, _("Order not found."))
            return

        text, keyboard = get_payment_method_keyboard(order)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=keyboard,
        )
        bot.answer_callback_query(call.id, _("Returning to payment selection."))
        return

    # Expecting callback formats:
    # "select_donate_payme_{order.id}" or "select_donate_click_{order.id}"
    parts = call.data.split("_")
    if len(parts) < 4:
        bot.answer_callback_query(call.id, _("Invalid payment data."))
        return

    try:
        order_id = int(parts[3])
    except ValueError:
        bot.answer_callback_query(call.id, _("Invalid order identifier."))
        return

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        bot.answer_callback_query(call.id, _("Order not found."))
        return

    # Generate payment link based on the selected payment method
    if call.data.startswith("select_donate_payme_"):
        payme_link = payme.initializer.generate_pay_link(
            id=order.id,
            amount=int(float(order.amount)),
            return_url=str(settings.PAYME_SUCCESS_URL),
        )
        payment_link = payme_link
        method = "payme"
    elif call.data.startswith("select_donate_click_"):
        click_link = click_up.initializer.generate_pay_link(
            id=order.id,
            amount=int(float(order.amount)),
            return_url=str(settings.CLICK_SUCCESS_URL),
        )
        payment_link = click_link
        method = "click"
    else:
        bot.answer_callback_query(call.id, _("Unrecognized payment method."))
        return

    text, keyboard = get_payment_link_keyboard(order, payment_link, method)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=text,
        reply_markup=keyboard,
    )
    bot.answer_callback_query(call.id)
    logger.info(
        f"User {call.from_user.id} selected payment method for order {order.id}."
    )
