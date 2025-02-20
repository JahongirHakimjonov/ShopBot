from django.utils.translation import gettext as _
from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_buttons():
    buttons = [
        [KeyboardButton(_("Products"))],
        [KeyboardButton(_("Cart"))],
        [KeyboardButton(_("Info"))],
        [KeyboardButton(_("Language"))],
        [KeyboardButton(_("Donate"))],
    ]
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(*[button for row in buttons for button in row])
    return markup
