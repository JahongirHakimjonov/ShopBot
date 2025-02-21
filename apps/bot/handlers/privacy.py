from django.utils.translation import activate
from django.utils.translation import gettext as _
from telebot import TeleBot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from apps.bot.logger import logger
from apps.bot.utils import update_or_create_user
from apps.bot.utils.language import set_language_code


def handle_privacy(message: Message, bot: TeleBot):
    activate(set_language_code(message.from_user.id))
    update_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        is_active=True,
    )
    logger.info(f"User {message.from_user.id} selected a handle privacy.")

    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            text=_("Read"),
            url="https://telegra.ph/MilliyTech-Shop-Telegram-Bot-Maxfiylik-Siyosati-02-21",
        )
    )

    text = _(
        "This bot respects your privacy. By using this bot, you agree to our privacy policy. "
        "For more details, please read our full privacy policy by clicking the button below."
    )

    bot.send_message(
        message.chat.id,
        text=text,
        parse_mode="Markdown",
        reply_markup=keyboard,
    )
