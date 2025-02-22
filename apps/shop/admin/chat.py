from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.shop.models.chat import Chat


@admin.register(Chat)
class ChatAdmin(ModelAdmin):
    list_display = ["id", "name", "chat_id", "type", "is_active", "created_at"]
    list_per_page = 50
    search_fields = ["name", "chat_id"]
    list_filter = ["is_active"]
