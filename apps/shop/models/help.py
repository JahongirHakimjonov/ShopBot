from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.shared.models.base import AbstractBaseModel


class Help(AbstractBaseModel):
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    description = models.TextField(verbose_name=_("Description"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is active"))

    class Meta:
        verbose_name = _("Help")
        verbose_name_plural = _("Help")
        ordering = ("-created_at",)
        db_table = "help"

    def __str__(self):
        return str(self.title)
