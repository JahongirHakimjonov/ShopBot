import json
import os
import uuid

import redis
from click_up import ClickUp
from django.utils.translation import activate, gettext as _
from payme import Payme
from telebot import TeleBot
from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)

from apps.bot.keyboard import get_main_buttons
from apps.bot.logger import logger
from apps.bot.utils import update_or_create_user
from apps.bot.utils.language import set_language_code
from apps.shop.models.cart import Cart, CartItem
from apps.shop.models.order import Order, PaymentMethodChoices, OrderItem
from apps.shop.models.users import BotUsers
from core import settings

# Initialize Redis instance
redis_instance = redis.StrictRedis.from_url(
    os.getenv("REDIS_CACHE_URL"), decode_responses=True
)

# Initialize Payment Services
click_service = ClickUp(
    service_id=settings.CLICK_SERVICE_ID, merchant_id=settings.CLICK_MERCHANT_ID
)
payme_service = Payme(payme_id=settings.PAYME_ID, is_test_mode=settings.PAYME_TEST_MODE)


def set_user_data(user_id: int, data: dict) -> None:
    key = f"user_data:{user_id}"
    redis_instance.set(key, json.dumps(data))


def get_user_data(user_id: int) -> dict:
    key = f"user_data:{user_id}"
    data = redis_instance.get(key)
    return json.loads(data) if data else {}


def delete_user_data(user_id: int) -> None:
    key = f"user_data:{user_id}"
    redis_instance.delete(key)


def send_reply(bot: TeleBot, user_id: int, text: str, reply_markup) -> None:
    bot.send_message(chat_id=user_id, text=text, reply_markup=reply_markup)


def handle_order(message: Message, bot: TeleBot) -> None:
    user_id = message.from_user.id
    activate(set_language_code(user_id))
    update_or_create_user(
        telegram_id=user_id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        is_active=True,
    )
    logger.info(f"User {user_id} selected to start an order.")

    # Initialize empty session data in Redis
    set_user_data(user_id, {})

    markup = ReplyKeyboardMarkup(
        row_width=2, resize_keyboard=True, one_time_keyboard=True
    )
    markup.add(
        KeyboardButton(text=_("Send location"), request_location=True),
        KeyboardButton(text=_("Home")),
        KeyboardButton(text=_("Back")),
    )

    send_reply(bot, user_id, _("Please, send your location."), markup)
    bot.register_next_step_handler(message, handle_location, bot=bot)


def handle_location(message: Message, bot: TeleBot) -> None:
    user_id = message.from_user.id
    try:
        latitude = message.location.latitude
        longitude = message.location.longitude
    except AttributeError:
        logger.error(f"User {user_id} did not provide a valid location.")
        bot.send_message(user_id, _("Invalid location data. Please try again."))
        return

    logger.info(f"User {user_id} location: lat={latitude}, lon={longitude}")

    user_data = get_user_data(user_id)
    user_data.update({"latitude": latitude, "longitude": longitude})
    set_user_data(user_id, user_data)

    markup = ReplyKeyboardMarkup(
        row_width=1, resize_keyboard=True, one_time_keyboard=True
    )
    markup.add(KeyboardButton(text=_("Send your phone"), request_contact=True))

    send_reply(bot, user_id, _("Please, send your phone number."), markup)
    bot.register_next_step_handler(message, handle_contact, bot=bot)


def handle_contact(message: Message, bot: TeleBot) -> None:
    user_id = message.from_user.id
    try:
        contact = message.contact.phone_number
    except AttributeError:
        logger.error(f"User {user_id} did not provide valid contact information.")
        bot.send_message(user_id, _("Invalid contact information. Please try again."))
        return

    logger.info(f"User {user_id} phone: {contact}")
    user_data = get_user_data(user_id)
    user_data["contact"] = contact
    set_user_data(user_id, user_data)

    bot.send_message(
        user_id, _("I've saved your phone number."), reply_markup=ReplyKeyboardRemove()
    )

    inline_markup = InlineKeyboardMarkup(row_width=1)
    inline_markup.add(
        InlineKeyboardButton(text="Click", callback_data="click"),
        InlineKeyboardButton(text="Payme", callback_data="payme"),
    )

    send_reply(bot, user_id, _("Please, select a payment method."), inline_markup)


def handle_payment(call: CallbackQuery, bot: TeleBot) -> None:
    user_id = call.from_user.id
    try:
        user = BotUsers.objects.get(telegram_id=user_id)
    except BotUsers.DoesNotExist:
        logger.error(f"User {user_id} not found.")
        bot.answer_callback_query(call.id, text=_("User not found."))
        return

    user_data = get_user_data(user_id)
    if call.data == "click":
        payment_method = PaymentMethodChoices.CLICK
    elif call.data == "payme":
        payment_method = PaymentMethodChoices.PAYME
    else:
        logger.error(f"User {user_id} selected an invalid payment method: {call.data}")
        bot.answer_callback_query(call.id, text=_("Invalid payment method selected."))
        return

    try:
        cart = Cart.objects.get(user=user)
        cart_items = CartItem.objects.filter(cart=cart)
    except Exception as e:
        logger.error(f"Error retrieving cart for user {user_id}: {e}")
        bot.answer_callback_query(call.id, text=_("Error retrieving your cart."))
        return

    order_identifier = f"order_{uuid.uuid4()}"
    order, created = Order.objects.update_or_create(
        order_id=order_identifier,
        user=user,
        order_type=Order.OrderType.PRODUCT,
        defaults={
            "latitude": user_data.get("latitude"),
            "longitude": user_data.get("longitude"),
            "phone": user_data.get("contact"),
            "payment_method": payment_method,
        },
    )

    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            quantity=cart_item.quantity,
            price=cart_item.product.price,
        )
    logger.info(
        f"Order for user {user_id} {'created' if created else 'updated'} with data: {user_data}"
    )

    if call.data == "click":
        response_text = _(
            "You selected the Click payment method. The payment process is starting. Amount: {}"
        ).format(order.amount)
        payment_link = click_service.initializer.generate_pay_link(
            id=order.id,
            amount=int(float(order.amount)),
            return_url=str(settings.CLICK_SUCCESS_URL),
        )
    else:  # payme
        response_text = _(
            "You selected the Payme payment method. The payment process is starting. Amount: {}"
        ).format(order.amount)
        payment_link = payme_service.initializer.generate_pay_link(
            id=order.id,
            amount=int(float(order.amount)),
            return_url=str(settings.PAYME_SUCCESS_URL),
        )

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text=_("Pay"), url=payment_link))

    # Clean up temporary user data
    delete_user_data(user_id)

    bot.answer_callback_query(call.id, text=response_text)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    send_reply(bot, user_id, response_text, keyboard)
    send_reply(bot, user_id, _("Thanks"), get_main_buttons())
