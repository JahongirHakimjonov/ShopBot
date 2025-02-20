from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.shop.models.news import News


@admin.register(News)
class NewsAdmin(ModelAdmin):
    list_display = ["id", "title", "created_at", "updated_at"]
    list_per_page = 50
    search_fields = ["title"]
    list_filter = ["created_at", "updated_at"]
