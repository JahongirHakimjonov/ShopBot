from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.shared.models.base import AbstractBaseModel


class News(AbstractBaseModel):
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    description = models.TextField(verbose_name=_("Description"))
    image = models.ImageField(
        upload_to="news", verbose_name=_("Image"), null=True, blank=True
    )

    class Meta:
        verbose_name = _("News")
        verbose_name_plural = _("News")
        ordering = ("-created_at",)
        db_table = "news"

    def __str__(self):
        return str(self.title)
