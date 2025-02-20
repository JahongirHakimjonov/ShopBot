from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin
from unfold.admin import ModelAdmin

from apps.shop.models.products import Product


@admin.register(Product)
class ProductsAdmin(ModelAdmin, TabbedTranslationAdmin):
    list_display = ["id", "title", "price", "quantity", "category", "created_at"]
    list_per_page = 50
    search_fields = ["title"]
    list_filter = ["created_at", "updated_at"]
    autocomplete_fields = ["category"]
