import re

from django.utils.translation import activate, gettext as _
from telebot import TeleBot
from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
)

from apps.bot.handlers.clear import handle_clear
from apps.bot.handlers.order import handle_order
from apps.bot.handlers.user import start_handler
from apps.bot.keyboard import get_main_buttons
from apps.bot.logger import logger
from apps.bot.utils import update_or_create_user
from apps.bot.utils.language import set_language_code
from apps.shop.models.cart import Cart, CartItem
from apps.shop.models.users import BotUsers


def handle_cart(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    activate(set_language_code(user_id))

    update_or_create_user(
        telegram_id=user_id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        is_active=True,
    )

    logger.info(f"User {user_id} selected a handle cart.")

    user = BotUsers.objects.filter(telegram_id=user_id).first()
    if not user:
        bot.send_message(message.chat.id, _("User not found."))
        return

    cart = Cart.objects.filter(user=user).first()
    if not cart:
        bot.send_message(message.chat.id, _("Cart is empty."))
        return

    cart_items = CartItem.objects.filter(cart=cart)
    if not cart_items.exists():
        bot.send_message(message.chat.id, _("Cart is empty."))
        return

    pieces_text = _("pieces")
    home_text = _("Home")
    clear_text = _("Clear")
    order_text = _("Order")
    total_text = _("Total")
    your_cart_text = _("Your cart")

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton(text=home_text), KeyboardButton(text=clear_text))

    items_text = []
    for index, item in enumerate(cart_items, start=1):
        keyboard.add(KeyboardButton(text=f"№{index} - {item.product.title}✏️"))
        items_text.append(
            f"№{index} - *{item.product.title}*\n{item.quantity} x {int(float(item.product.price)):,} = *{int(float(item.amount)):,} UZS*".replace(
                ",", " "
            )
        )

    keyboard.add(KeyboardButton(text=order_text))

    text = f"{your_cart_text}:\n\n{'-' * 20}\n\n"
    text += "\n".join(items_text)
    text += (
        f"\n\n{'-' * 20}\n\n{total_text}: *{int(float(cart.amount)):,} UZS*".replace(
            ",", " "
        )
    )

    bot.send_message(
        message.chat.id, text=text, reply_markup=keyboard, parse_mode="Markdown"
    )


def build_cart_item_keyboard(item):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(text=_("Clear"), callback_data=f"clear_{item.id}")
    )
    keyboard.row(
        InlineKeyboardButton(text=_("➖"), callback_data=f"minus_{item.id}"),
        InlineKeyboardButton(
            text=f"{item.quantity}", callback_data=f"quantity_{item.id}"
        ),
        InlineKeyboardButton(text=_("➕"), callback_data=f"plus_{item.id}"),
    )
    keyboard.add(InlineKeyboardButton(text=_("Save"), callback_data=f"save_{item.id}"))
    return keyboard


def update_cart_message(bot, call, item):
    user_id = call.from_user.id
    activate(set_language_code(user_id))
    keyboard = build_cart_item_keyboard(item)
    total_text = _("Total amount")
    pieces_text = _("pieces")
    new_caption = (
        f"{item.product.title}\n\n\t\t{item.product.description}\n\n"
        f"{total_text}: *{int(float(item.amount)):,} UZS*\n\n"
        f"{item.quantity} {pieces_text}"
    ).replace(",", " ")

    current_caption = call.message.caption

    if new_caption != current_caption:
        try:
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption=new_caption,
                reply_markup=keyboard,
                parse_mode="Markdown",
            )
        except Exception as e:
            logger.error(f"Error editing message: {e}")
    else:
        logger.info(
            "New message content is the same as the current content. No update needed."
        )


def handle_cart_selection(message, bot: TeleBot):
    """
    Handle a user’s selection on the cart menu.
    """
    user_id = message.from_user.id
    activate(set_language_code(user_id))

    # Update or create the user record.
    update_or_create_user(
        telegram_id=user_id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        is_active=True,
    )

    logger.info(f"User {user_id} selected a handle cart selection.")

    user = BotUsers.objects.filter(telegram_id=user_id).first()
    if not user:
        bot.send_message(message.chat.id, _("User not found."))
        return

    cart = Cart.objects.filter(user=user).first()
    if not cart:
        bot.send_message(message.chat.id, _("Cart is empty."))
        return

    cart_items = CartItem.objects.filter(cart=cart)
    if not cart_items.exists():
        bot.send_message(message.chat.id, _("Cart is empty."))
        return

    text = message.text
    if text == _("Home"):
        start_handler(message, bot)
        return
    elif text == _("Clear"):
        handle_clear(message, bot)
        return
    elif text == _("Order"):
        handle_order(message, bot)
        return
    elif re.match(r"№\d+ -", message.text):
        try:
            # Extract the index from text like "№3 - ..." and adjust for 0-based indexing.
            index = int(text.split("№")[1].split(" -")[0]) - 1
            item = cart_items[index]
        except (IndexError, ValueError):
            bot.send_message(
                message.chat.id, _("Invalid selection format or item not found.")
            )
            return

        keyboard = build_cart_item_keyboard(item)
        bot.send_photo(
            message.chat.id,
            photo=item.product.image,
            caption=(
                f"{item.product.title}\n\n\t\t{item.product.description}\n\n"
                f"{_('Total amount')}: *{int(float(item.amount)):,} UZS*\n\n"
                f"{item.quantity} {_('pieces')}"
            ).replace(",", " "),
            reply_markup=keyboard,
            parse_mode="Markdown",
        )
        return
    else:
        bot.send_message(message.chat.id, _("Invalid selection."))
        handle_cart(message, bot)


def get_cart_item(item_id: str, bot: TeleBot, call: CallbackQuery):
    """
    Retrieve a CartItem by its ID. If not found, notify via callback.
    """
    user_id = call.from_user.id
    activate(set_language_code(user_id))
    try:
        return CartItem.objects.get(id=item_id)
    except CartItem.DoesNotExist:
        bot.answer_callback_query(call.id, text=_("Item not found."))
        return None


def plus_handler(call: CallbackQuery, bot: TeleBot):
    """
    Increase the quantity of a cart item.
    """
    user_id = call.from_user.id
    activate(set_language_code(user_id))
    item_id = call.data.split("_")[1]
    item = get_cart_item(item_id, bot, call)
    if not item:
        return

    item.quantity += 1
    item.amount = item.quantity * item.product.price
    item.save()
    update_cart_message(bot, call, item)


def minus_handler(call: CallbackQuery, bot: TeleBot):
    """
    Decrease the quantity of a cart item (ensuring quantity remains at least 1).
    """
    user_id = call.from_user.id
    activate(set_language_code(user_id))
    item_id = call.data.split("_")[1]
    item = get_cart_item(item_id, bot, call)
    if not item:
        return

    if item.quantity > 1:
        item.quantity -= 1
        item.amount = item.quantity * item.product.price
        item.save()
        update_cart_message(bot, call, item)
    else:
        bot.answer_callback_query(call.id, text=_("Quantity cannot be less than 1."))


def clear_handler(call: CallbackQuery, bot: TeleBot):
    """
    Remove an item from the cart.
    """
    user_id = call.from_user.id
    activate(set_language_code(user_id))
    item_id = call.data.split("_")[1]
    item = get_cart_item(item_id, bot, call)
    if not item:
        return

    item.delete()
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(
        call.message.chat.id,
        _("Item removed from cart."),
        reply_markup=get_main_buttons(),
    )


def save_handler(call: CallbackQuery, bot: TeleBot):
    """
    Save changes for a cart item.
    """
    user_id = call.from_user.id
    activate(set_language_code(user_id))
    item_id = call.data.split("_")[1]
    item = get_cart_item(item_id, bot, call)
    if not item:
        return

    # Place any additional save logic here if necessary.
    bot.answer_callback_query(call.id, text=_("Changes saved."))
    update_cart_message(bot, call, item)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(
        call.message.chat.id, _("Changes saved."), reply_markup=get_main_buttons()
    )
