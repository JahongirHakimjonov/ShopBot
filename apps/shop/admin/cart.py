from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from apps.shop.models.cart import Cart, CartItem


class CartItemInline(TabularInline):
    model = CartItem
    extra = 0
    show_change_link = True
    autocomplete_fields = ["product"]


@admin.register(Cart)
class CartAdmin(ModelAdmin):
    list_display = ["id", "user", "amount", "created_at", "updated_at"]
    list_per_page = 50
    autocomplete_fields = ["user"]
    search_fields = ["user__telegram_id"]
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(ModelAdmin):
    list_display = ["id", "cart", "product", "quantity", "created_at", "updated_at"]
    list_per_page = 50
    autocomplete_fields = ["cart", "product"]
