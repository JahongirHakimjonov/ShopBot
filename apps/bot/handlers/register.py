from django.utils.translation import activate, gettext as _
from telebot import TeleBot
from telebot.types import Message, CallbackQuery
import re
from apps.bot.handlers.cart import (
    handle_cart,
    handle_cart_selection,
    plus_handler,
    minus_handler,
    clear_handler,
    save_handler,
)
from apps.bot.handlers.clear import handle_clear
from apps.bot.handlers.donate import (
    handle_donate,
    handle_donate_selection,
    handle_send_donate_link,
)
from apps.bot.handlers.help import handle_help
from apps.bot.handlers.info import handle_info
from apps.bot.handlers.language import handle_language, handle_language_selection
from apps.bot.handlers.order import handle_order, handle_payment
from apps.bot.handlers.products import handle_category
from apps.bot.handlers.user import any_user
from apps.bot.keyboard import get_main_buttons
from apps.bot.logger import logger
from apps.bot.utils import update_or_create_user
from apps.bot.utils.language import set_language_code


def handle_message(message: Message, bot: TeleBot):
    activate(set_language_code(message.from_user.id))
    if message.text == _("Language"):
        handle_language(message, bot)
    elif message.text == _("Cart"):
        handle_cart(message, bot)
    elif message.text == _("Order"):
        handle_order(message, bot)
    elif message.text == _("Clear"):
        handle_clear(message, bot)
    elif message.text == _("Products"):
        handle_category(message, bot)
    elif message.text == _("Info") or message.text == "/info":
        handle_info(message, bot)
    elif message.text == _("Donate"):
        handle_donate(message, bot)
    elif message.text == _("Home"):
        any_user(message, bot)
    elif message.text == "/help":
        handle_help(message, bot)
    elif re.match(r"№\d+ -", message.text):
        handle_cart_selection(message, bot)
    else:
        logger.info(f"User {message.from_user.id} sent a message.")
        bot.send_message(
            message.chat.id, _("Unknown command."), reply_markup=get_main_buttons()
        )
        update_or_create_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            is_active=True,
        )


def handle_callback_query(call: CallbackQuery, bot: TeleBot):
    activate(set_language_code(call.from_user.id))
    logger.info(f"User {call.data} ====================================")
    if call.data == "lang_ru" or call.data == "lang_uz":
        handle_language_selection(call, bot)
        logger.info(f"User {call.from_user.id} selected a language.")
    elif call.data.startswith("donate_") or call.data == "back_to_amount_selection":
        handle_donate_selection(call, bot)
        logger.info(f"User {call.from_user.id} selected a donate.")
    elif (
        call.data.startswith("select_donate_payme_")
        or call.data.startswith("select_donate_click_")
        or call.data.startswith("back_to_payment_method_")
    ):
        handle_send_donate_link(call, bot)
    elif call.data.startswith("plus_"):
        plus_handler(call, bot)
    elif call.data.startswith("minus_"):
        minus_handler(call, bot)
    elif call.data.startswith("clear_"):
        clear_handler(call, bot)
    elif call.data.startswith("save_"):
        save_handler(call, bot)
    elif call.data == "payme" or call.data == "click":
        handle_payment(call, bot)
    else:
        bot.answer_callback_query(call.id, _("Unknown action."))
        logger.info(f"User {call.from_user.id} performed an unknown action.")
