from django.utils.translation import activate, gettext as _
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, Message

from apps.bot.handlers.clear import handle_clear
from apps.bot.handlers.user import any_user
from apps.bot.logger import logger
from apps.bot.utils import update_or_create_user
from apps.bot.utils.language import set_language_code
from apps.shop.models.cart import Cart, CartItem
from apps.shop.models.users import BotUsers


def handle_order(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    activate(set_language_code(user_id))

    update_or_create_user(
        telegram_id=user_id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        is_active=True,
    )

    logger.info(f"User {user_id} selected a product category.")
