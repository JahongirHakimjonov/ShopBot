from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.shared.models.base import AbstractBaseModel
from apps.shop.models.users import BotUsers


class Cart(AbstractBaseModel):
    user = models.ForeignKey(
        BotUsers,
        on_delete=models.CASCADE,
        related_name="carts",
        verbose_name=_("User"),
    )
    amount = models.DecimalField(
        max_digits=100,
        decimal_places=2,
        verbose_name=_("Amount"),
        default=0,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("Cart")
        verbose_name_plural = _("Carts")
        ordering = ("-created_at",)
        db_table = "carts"

    def __str__(self):
        return str(self.amount)


class CartItem(AbstractBaseModel):
    cart = models.ForeignKey(
        "Cart",
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("Cart"),
    )
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="cart_items",
        verbose_name=_("Product"),
    )
    quantity = models.PositiveBigIntegerField(default=0, verbose_name=_("Quantity"))
    amount = models.DecimalField(
        max_digits=100,
        decimal_places=2,
        verbose_name=_("Amount"),
        default=0,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("Cart item")
        verbose_name_plural = _("Cart items")
        ordering = ("-created_at",)
        db_table = "cart_items"

    def __str__(self):
        return str(self.cart)

    def save(self, *args, **kwargs):
        self.amount = self.product.price * self.quantity
        super().save(*args, **kwargs)
