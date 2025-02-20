from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.shop.models.order import OrderItem


@receiver(post_save, sender=OrderItem)
def update_order_amount(sender, instance, created, **kwargs):
    instance.order.amount = OrderItem.objects.filter(order=instance.order).aggregate(
        total=models.Sum(models.F("price") * models.F("quantity"))
    )["total"]
    instance.order.save()
