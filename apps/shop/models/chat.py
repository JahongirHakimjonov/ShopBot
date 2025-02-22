from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.shared.models.base import AbstractBaseModel


class Chat(AbstractBaseModel):
    name = models.CharField(
        max_length=255, verbose_name=_("Name"), null=True, blank=True
    )
    chat_id = models.BigIntegerField(verbose_name=_("Chat ID"), unique=True)
    type = models.CharField(
        max_length=255, verbose_name=_("Type"), null=True, blank=True
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Is active"))

    class Meta:
        verbose_name = _("Chat")
        verbose_name_plural = _("Chats")
        ordering = ("-created_at",)
        db_table = "chats"

    def __str__(self):
        return self.name
