import os
import sys


# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")  # noqa

# Initialize Django
import django

django.setup()

import time

import requests
from apps.bot.conf import TOKEN
from apps.bot.filters import AdminFilter
from apps.bot.handlers.user import start_handler
from apps.bot.middlewares import antispam_func
from apps.bot.handlers.register import handle_message, handle_callback_query
from telebot import TeleBot, apihelper
from apps.bot.query.inlinequery import query_text
from apps.bot.logger import logger


# Log a message to indicate the bot is starting
logger.info("Starting bot...")


# Enable middleware
apihelper.ENABLE_MIDDLEWARE = True
logger.info("Middlewares enabled")

# I recommend increasing num_threads
bot = TeleBot(TOKEN, num_threads=17)
logger.info("Bot created")


def register_handlers(bot: TeleBot):
    bot.register_message_handler(
        start_handler, commands=["start"], admin=False, pass_bot=True
    )
    bot.register_message_handler(handle_message, content_types=["text"], pass_bot=True)
    bot.register_callback_query_handler(
        lambda call: handle_callback_query(call, bot), lambda call: True
    )


register_handlers(bot)
logger.info("Handlers registered")


# Inline query
bot.register_inline_handler(
    callback=lambda query: query_text(bot, query), func=lambda query: True
)
logger.info("Inline query handler registered")


# Middlewares
bot.register_middleware_handler(antispam_func, update_types=["message"])
logger.info("Middlewares registered")

# Custom filters
bot.add_custom_filter(AdminFilter())
logger.info("Custom filters registered")


def run():
    retry_delay = 1  # Initial delay in seconds

    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except requests.exceptions.ReadTimeout:
            logger.error("Read timeout occurred. Retrying...")
        except requests.exceptions.ConnectTimeout:
            logger.error("Connection timeout occurred. Retrying in 15 seconds...")
            time.sleep(15)
        except requests.exceptions.ConnectionError:
            logger.error("Network is unreachable. Retrying in 30 seconds...")
            time.sleep(30)
        except requests.exceptions.RequestException as e:
            logger.error(
                f"Network error occurred: {e}. Retrying in {retry_delay} seconds..."
            )
            time.sleep(retry_delay)
            retry_delay = min(
                retry_delay * 2, 60
            )  # Exponential backoff, max 60 seconds
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise


if __name__ == "__main__":
    logger.info("Bot is running...")
    logger.info("Press Ctrl + C to stop the bot")
    run()
    logger.info("Bot stopped")
