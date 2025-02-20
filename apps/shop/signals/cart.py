from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.shop.models.cart import CartItem


@receiver(post_save, sender=CartItem)
def update_cart_amount(sender, instance, created, **kwargs):
    instance.cart.amount = CartItem.objects.filter(cart=instance.cart).aggregate(
        total=models.Sum(models.F("product__price") * models.F("quantity"))
    )["total"]
    instance.cart.save()
