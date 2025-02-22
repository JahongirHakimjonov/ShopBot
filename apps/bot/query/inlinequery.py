import re

from django.contrib.sites.models import Site
from django.utils.translation import activate, gettext as _
from telebot.types import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    LinkPreviewOptions,
)

from apps.bot.logger import logger
from apps.bot.utils import update_or_create_user
from apps.bot.utils.bot_url import get_bot_url
from apps.bot.utils.language import set_language_code
from apps.shop.models.products import Product


def escape_markdown(text):
    """
    Escapes Telegram Markdown special characters.
    Special characters: '_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!'
    """
    escape_chars = r'_*[\]()~`>#+-=|{}.!'
    return re.sub(r'([{}])'.format(re.escape(escape_chars)), r'\\\1', text)


def query_text(bot, query):
    try:
        update_or_create_user(
            telegram_id=query.from_user.id,
            username=query.from_user.username,
            first_name=query.from_user.first_name,
            last_name=query.from_user.last_name,
            is_active=True,
        )
        activate(set_language_code(query.from_user.id))
        logger.info(f"User {query.from_user.id} selected a product category.")

        results = []
        products = Product.objects.filter(is_active=True, quantity__gt=0).order_by("-created_at")[:25]
        for product in products:
            # Construct thumbnail URL using current site domain
            get_current = Site.objects.get_current().domain
            thumbnail_url = f"https://{get_current}{product.image.url}"

            # Prepare bot URL and inline keyboard button
            bot_url = get_bot_url(bot)
            keyboard = InlineKeyboardMarkup()
            button = InlineKeyboardButton(
                text=_("Ko'rish"),
                url=f"{bot_url}?start={product.id}",
            )
            keyboard.add(button)

            # Escape dynamic content to prevent Markdown issues
            escaped_title = escape_markdown(product.title)
            escaped_description = escape_markdown(product.description)
            escaped_thumbnail = escape_markdown(thumbnail_url)
            formatted_price = f"{int(float(product.price)):,} UZS".replace(",", " ")

            # Compose the message text using Markdown
            message_text = (
                f"*{escaped_title}*\n\n"
                f"{escaped_description}\n\n"
                f"*{formatted_price}* [ ]({thumbnail_url})"
            )

            link_preview_options = LinkPreviewOptions(show_above_text=True)

            article_result = InlineQueryResultArticle(
                id=str(product.id),
                title=product.title,
                description=formatted_price,
                thumbnail_url=thumbnail_url,
                input_message_content=InputTextMessageContent(
                    message_text=message_text,
                    parse_mode="Markdown",
                    link_preview_options=link_preview_options,
                ),
                reply_markup=keyboard,
            )
            results.append(article_result)

        bot.answer_inline_query(query.id, results)
        logger.info(f"Inline query results sent to {query.from_user.id}")

    except Exception as e:
        bot.answer_inline_query(query.id, [])
        logger.error(f"Error while answering inline query: {e}")
