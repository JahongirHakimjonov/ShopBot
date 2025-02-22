from django.dispatch import receiver

from apps.shop.signals.signals import order_status_updated
from apps.shop.tasks.payment import notify_admin_task, notify_user_task


@receiver(order_status_updated)
def order_status_updated_handler(sender, order, success, **kwargs):
    # Trigger async notifications via Celery
    notify_admin_task.delay(order.id)
    notify_user_task.delay(order.user.id, order.id, success)
