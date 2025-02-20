from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin
from unfold.admin import ModelAdmin

from apps.shop.models.category import Category


@admin.register(Category)
class CategoryAdmin(ModelAdmin, TabbedTranslationAdmin):
    list_display = ["id", "name", "created_at", "updated_at"]
    list_per_page = 50
    search_fields = ["name"]
    list_filter = ["created_at", "updated_at"]
