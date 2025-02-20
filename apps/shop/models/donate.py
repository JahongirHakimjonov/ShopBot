from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.shared.models.base import AbstractBaseModel


class Donate(AbstractBaseModel):
    amount = models.DecimalField(
        max_digits=100, decimal_places=2, verbose_name=_("Amount")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Is active"))

    class Meta:
        verbose_name = _("Donate")
        verbose_name_plural = _("Donates")
        ordering = ("-created_at",)
        db_table = "donates"

    def __str__(self):
        return str(self.amount)
