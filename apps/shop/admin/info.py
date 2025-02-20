from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin
from unfold.admin import ModelAdmin

from apps.shop.models.info import Info


@admin.register(Info)
class InfoAdmin(ModelAdmin, TabbedTranslationAdmin):
    list_display = ["id", "title", "created_at", "updated_at"]
    list_per_page = 50
    search_fields = ["title"]
    list_filter = ["created_at", "updated_at"]
