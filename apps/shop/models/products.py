from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.shared.models.base import AbstractBaseModel


class Product(AbstractBaseModel):
    category = models.ForeignKey(
        "Category",
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name=_("Category"),
    )
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    description = models.TextField(verbose_name=_("Description"))
    price = models.DecimalField(
        max_digits=100, decimal_places=2, verbose_name=_("Price")
    )
    image = models.ImageField(upload_to="products", verbose_name=_("Image"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is active"))
    quantity = models.PositiveBigIntegerField(default=0, verbose_name=_("Quantity"))

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ("-created_at",)
        db_table = "products"

    def __str__(self):
        return str(self.title)
