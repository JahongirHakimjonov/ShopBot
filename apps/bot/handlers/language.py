from django.utils.translation import activate, gettext as _
from telebot import TeleBot, types
from telebot.types import Message, CallbackQuery

from apps.bot.keyboard import get_main_buttons
from apps.bot.logger import logger
from apps.bot.utils import update_or_create_user
from apps.bot.utils.language import set_language_code
from apps.shop.models.users import BotUsers, LanguageChoices


def handle_language(message: Message, bot: TeleBot):
    activate(set_language_code(message.from_user.id))
    update_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        is_active=True,
    )
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    logger.info(f"User {message.from_user.id} selected a language.")

    # Create buttons for Russian and Uzbek languages
    uz_button = types.InlineKeyboardButton(text="O'zbek", callback_data="lang_uz")
    ru_button = types.InlineKeyboardButton(text="Русский", callback_data="lang_ru")

    # Add buttons to the keyboard
    keyboard.add(uz_button, ru_button)

    bot.send_message(
        message.chat.id,
        "Tilni tanlang / Выберите язык",
        reply_markup=keyboard,
    )


def handle_language_selection(call: CallbackQuery, bot: TeleBot):
    activate(set_language_code(call.from_user.id))
    user = BotUsers.objects.get(telegram_id=call.from_user.id)
    logger.info(f"User {user.telegram_id} selected a language.")
    if call.data == "lang_ru":
        user.language_code = LanguageChoices.RU
    elif call.data == "lang_uz":
        user.language_code = LanguageChoices.UZ
    user.save()
    activate(set_language_code(call.from_user.id))
    bot.send_message(
        call.message.chat.id,
        _("Language updated successfully!"),
        reply_markup=get_main_buttons(),
    )
    bot.delete_message(call.message.chat.id, call.message.message_id)
