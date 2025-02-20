from django.utils.translation import activate, gettext as _
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import Message

from apps.bot.keyboard import get_main_buttons
from apps.bot.logger import logger
from apps.bot.utils import update_or_create_user
from apps.bot.utils.language import set_language_code
from apps.shop.models.products import Product


def any_user(message: Message, bot: TeleBot):
    try:
        activate(set_language_code(message.from_user.id))
        update_or_create_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            is_active=True,
        )
        logger.info(f"User {message.from_user.id} started the bot.")

        inline_keyboard = InlineKeyboardMarkup()
        inline_button = InlineKeyboardButton(
            text=_("Search Products"), switch_inline_query_current_chat=""
        )
        inline_keyboard.add(inline_button)

        if message.text.startswith("/start "):
            product_id = message.text.split(" ")[1]
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                bot.send_message(message.chat.id, _("Product not found."))
                return
            bot.send_photo(
                message.chat.id,
                photo=product.image,
                caption=_(
                    f"{product.title}\n\n\t\t{product.description}\n\n{int(float(product.price)):,} UZS".replace(
                        ",", " "
                    )
                ),
                reply_markup=inline_keyboard,
            )
        first_name = message.from_user.first_name
        if message.from_user.last_name:
            first_name += f" {message.from_user.last_name}"

        bot.send_message(
            message.chat.id,
            _(
                f"[{first_name}](tg://user?id={message.from_user.id}) Welcome to the bot! You can search for products by clicking on the button below."
            ),
            parse_mode="Markdown",
            reply_markup=get_main_buttons(),
        )
    except Exception as e:
        bot.send_message(message.chat.id, _("An error occurred."))
        logger.error(f"Error in any_user: {e}")
