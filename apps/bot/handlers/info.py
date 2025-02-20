from django.utils.translation import activate, gettext as _
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import Message

from apps.bot.logger import logger
from apps.bot.utils import update_or_create_user
from apps.bot.utils.language import set_language_code
from apps.shop.models.info import Info


def handle_info(message: Message, bot: TeleBot):
    activate(set_language_code(message.from_user.id))
    update_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        is_active=True,
    )
    logger.info(f"User {message.from_user.id} selected a info.")

    inline_keyboard = InlineKeyboardMarkup()
    inline_button = InlineKeyboardButton(
        text=_("Search Products"), switch_inline_query_current_chat=""
    )
    inline_keyboard.add(inline_button)

    infos = Info.objects.filter(is_active=True)
    for info in infos:
        caption = f"*{info.title}*\n\n{info.description}"
        bot.send_photo(
            message.chat.id,
            photo=info.image,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=inline_keyboard,
        )
