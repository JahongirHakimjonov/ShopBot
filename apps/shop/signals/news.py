from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.shop.models.news import News
from apps.shop.tasks.news import send_news_update_task


@receiver(post_save, sender=News)
def send_news_update(sender, instance, created, **kwargs):
    if created:
        send_news_update_task.delay(instance.id)
