from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.shared.models.base import AbstractBaseModel
from apps.shop.models.users import BotUsers


class PaymentMethodChoices(models.TextChoices):
    PAYNET = "PAYNET", _("Paynet")
    PAYME = "PAYME", _("Payme")
    CLICK = "CLICK", _("Click")


class Order(AbstractBaseModel):
    class Status(models.TextChoices):
        PENDING = "PENDING", _("Pending")
        COMPLETED = "COMPLETED", _("Completed")
        CANCELLED = "CANCELLED", _("Cancelled")

    class OrderType(models.TextChoices):
        DONATE = "DONATE", _("Donate")
        PRODUCT = "PRODUCT", _("Product")

    order_id = models.CharField(max_length=100, null=True, blank=True)
    order_type = models.CharField(
        max_length=20, choices=OrderType, default=OrderType.PRODUCT
    )
    status = models.CharField(
        max_length=20,
        choices=Status,
        default=Status.PENDING,
    )
    amount = models.DecimalField(
        max_digits=100, decimal_places=2, default=0, null=True, blank=True
    )
    user = models.ForeignKey(BotUsers, on_delete=models.CASCADE)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    payment_method = models.CharField(
        max_length=100,
        choices=PaymentMethodChoices,
        default=PaymentMethodChoices.PAYME,
    )
    payment_status = models.BooleanField(
        default=False, verbose_name=_("Payment Status")
    )

    def __str__(self):
        return f"{self.id} - {self.status} - {self.amount}"

    class Meta:
        db_table = "order"
        ordering = ["-created_at"]
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    @classmethod
    def pending_orders(cls):
        return cls.objects.filter(
            status=cls.Status.PENDING, order_type=cls.OrderType.PRODUCT
        ).count()


class OrderItem(AbstractBaseModel):
    order = models.ForeignKey("Order", on_delete=models.CASCADE)
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=100, decimal_places=2)

    def __str__(self):
        return f"{self.order} - {self.product} - {self.quantity}"

    class Meta:
        db_table = "order_item"
        ordering = ["-created_at"]
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")
