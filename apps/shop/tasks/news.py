import os
import time

from celery import shared_task
from django.conf import settings
from telebot import TeleBot
from telebot.apihelper import ApiTelegramException
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from apps.bot.logger import logger
from apps.bot.utils.send_message import send_reply
from apps.shop.models.news import News, NewsButton
from apps.shop.models.users import BotUsers

bot = TeleBot(os.getenv("BOT_TOKEN"))


@shared_task()
def send_news_update_task(news_id):
    time.sleep(1)
    instance = News.objects.get(id=news_id)
    buttons = NewsButton.objects.filter(news=instance)
    keyboard = None
    if buttons.exists():
        keyboard = InlineKeyboardMarkup(row_width=1)
        for button in buttons:
            logger.info(f"Sending news update to {button.url} users")
            keyboard.add(InlineKeyboardButton(text=button.title, url=button.url))

    text = f"*{instance.title}*\n\n{instance.description}"

    image = None
    if instance.image:
        try:
            image_url = instance.image.url
            if image_url.strip():
                image_path = os.path.join(settings.MEDIA_ROOT, instance.image.name)
                if os.path.exists(image_path):
                    image = image_url
                    logger.info(f"Image URL: {image}")
                else:
                    logger.error(f"Image file does not exist: {image_path}")
        except Exception as e:
            logger.error(f"Error retrieving image URL: {e}")
            image = None

    user_ids = BotUsers.objects.values_list("telegram_id", flat=True)
    for telegram_id in user_ids:
        try:
            send_reply(
                bot=bot,
                user_id=telegram_id,
                text=text,
                reply_markup=keyboard,
                image=image,
            )
            time.sleep(0.3)
        except ApiTelegramException as e:
            if e.error_code == 403:
                logger.error(f"User {telegram_id} has blocked the bot.")
                BotUsers.objects.filter(telegram_id=telegram_id).update(is_active=False)
            else:
                logger.error(f"An error occurred: {e}")
        except Exception as e:
            logger.error(f"Error while sending news to user {telegram_id}: {e}")
