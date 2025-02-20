from django.utils.translation import activate, gettext as _
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, Message

from apps.bot.keyboard import get_main_buttons
from apps.bot.logger import logger
from apps.bot.utils import update_or_create_user
from apps.bot.utils.language import set_language_code
from apps.shop.models.cart import Cart, CartItem
from apps.shop.models.users import BotUsers


def handle_clear(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    activate(set_language_code(user_id))

    update_or_create_user(
        telegram_id=user_id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        is_active=True,
    )

    logger.info(f"User {user_id} selected a cart clear.")

    user = BotUsers.objects.filter(telegram_id=user_id).first()
    if not user:
        bot.send_message(
            message.chat.id, _("User not found."), reply_markup=get_main_buttons()
        )
        return

    cart = Cart.objects.filter(user=user).first()
    if not cart:
        bot.send_message(
            message.chat.id, _("Cart is empty."), reply_markup=get_main_buttons()
        )
        return

    cart.delete()
    bot.send_message(
        message.chat.id, _("Cart is cleared."), reply_markup=get_main_buttons()
    )
