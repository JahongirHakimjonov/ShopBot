from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.shop.models.donate import Donate


@admin.register(Donate)
class DonateAdmin(ModelAdmin):
    list_display = ["id", "amount", "created_at", "updated_at"]
    list_per_page = 50
    list_filter = ["created_at", "updated_at"]
