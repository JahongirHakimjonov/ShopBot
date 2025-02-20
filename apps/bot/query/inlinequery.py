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
        products = Product.objects.filter(is_active=True, quantity__gt=0).order_by(
            "-created_at"
        )[:25]
        for product in products:
            # thumbnail_url = f"{os.getenv('BASE_URL')}{product.image.url}"
            thumbnail_url = "https://child-protection.felixits.uz/media/avatars/IMG_20240406_200729_995.jpg"
            bot_url = get_bot_url(bot)
            keyboard = InlineKeyboardMarkup()
            button = InlineKeyboardButton(
                text=_("Ko'rish"),
                url=f"{bot_url}?start={product.id}",
            )
            keyboard.add(button)
            product_id = str(product.id)
            link_preview_options = LinkPreviewOptions(show_above_text=True)
            article_result = InlineQueryResultArticle(
                id=product_id,
                title=product.title,
                description=f"{int(float(product.price)):,} UZS".replace(",", " "),
                thumbnail_url=thumbnail_url,
                input_message_content=InputTextMessageContent(
                    message_text=f"*{product.title}*\n\n\t\t{product.description}\n\n{int(float(product.price)):,}[ ]({thumbnail_url})UZS".replace(
                        ",", " "
                    ),
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
