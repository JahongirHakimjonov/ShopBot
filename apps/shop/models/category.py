from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.shared.models.base import AbstractBaseModel


class Category(AbstractBaseModel):
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ["-created_at"]
        db_table = "category"

    def __str__(self):
        return str(self.name)
