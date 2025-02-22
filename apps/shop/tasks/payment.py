import os

from celery import shared_task
from django.utils.translation import gettext as _
from telebot import TeleBot

bot = TeleBot(os.getenv("BOT_TOKEN"))


@shared_task
def send_telegram_notification(chat_id, text, parse_mode="Markdown"):
    return bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)


@shared_task
def send_telegram_location(chat_id, latitude, longitude, text):
    location_message = bot.send_location(
        chat_id=chat_id, latitude=latitude, longitude=longitude
    )
    return bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="Markdown",
        reply_to_message_id=location_message.message_id,
    )


@shared_task
def notify_admin_task(order_id):
    from apps.shop.models.chat import Chat
    from apps.shop.models.order import Order, OrderItem

    chats = Chat.objects.filter(is_active=True)
    if not chats.exists():
        return

    order = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    your_cart_text = _("Products")
    total_text = _("Total")

    items_text = []
    for index, item in enumerate(order_items, start=1):
        items_text.append(
            f"№{index} - *{item.product.title}*\n"
            f"{item.quantity} x {int(float(item.product.price)):,} = *{int(float(item.amount)):,} UZS*".replace(
                ",", " "
            )
        )
    text = (
        f"{your_cart_text}:\n\n{'-' * 20}\n\n"
        f"{chr(10).join(items_text)}\n\n{'-' * 20}\n\n"
        f"{total_text}: *{int(float(order.amount)):,} UZS*".replace(",", " ")
    )

    # Send location and then notification message to each active chat
    for chat in chats:
        send_telegram_location.delay(
            chat.chat_id, order.latitude, order.longitude, text
        )


@shared_task
def notify_user_task(user_id, order_id, success):
    from apps.shop.models.order import Order

    order = Order.objects.get(id=order_id)
    user = order.user
    message = (
        _("Your order has been successfully paid. Order ID: {order_id}")
        if success
        else _("Your order has been cancelled. Order ID: {order_id}")
    )
    if user.telegram_id:
        send_telegram_notification.delay(
            user.telegram_id, message.format(order_id=order.id)
        )
