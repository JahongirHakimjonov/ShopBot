from django.utils.translation import activate
from telebot import TeleBot
from telebot.types import Message

from apps.bot.logger import logger
from apps.bot.utils import update_or_create_user
from apps.bot.utils.language import set_language_code
from apps.shop.models.help import Help


def handle_help(message: Message, bot: TeleBot):
    activate(set_language_code(message.from_user.id))
    update_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        is_active=True,
    )
    logger.info(f"User {message.from_user.id} selected a help.")

    helps = Help.objects.filter(is_active=True)
    for help in helps:
        text = f"*{help.title}*\n\n{help.description}"
        bot.send_message(
            message.chat.id,
            text,
            parse_mode="Markdown",
        )
