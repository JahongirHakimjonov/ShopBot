from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.admin import TabularInline
from unfold.decorators import display

from apps.shop.models.order import Order, OrderItem, PaymentMethodChoices


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    autocomplete_fields = ["product"]


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = [
        "id",
        "user",
        "status_color",
        "payment_color",
        "order_type_color",
        "payment_status",
        "created_at",
    ]
    list_per_page = 50
    search_fields = ["user__telegram_id"]
    list_filter = ["status", "payment_method", "order_type", "payment_status"]
    autocomplete_fields = ["user"]
    inlines = [OrderItemInline]

    @display(
        description=_("Status"),
        label={
            Order.Status.PENDING: "warning",
            Order.Status.COMPLETED: "success",
            Order.Status.CANCELLED: "danger",
        },
    )
    def status_color(self, obj):
        return obj.status, obj.get_status_display()

    @display(
        description=_("Payment Method"),
        label={
            PaymentMethodChoices.PAYME: "primary",
            PaymentMethodChoices.PAYNET: "primary",
            PaymentMethodChoices.CLICK: "primary",
        },
    )
    def payment_color(self, obj):
        return obj.payment_method, obj.get_payment_method_display()

    @display(
        description=_("Order Type"),
        label={
            Order.OrderType.PRODUCT: "info",
            Order.OrderType.DONATE: "info",
        },
    )
    def order_type_color(self, obj):
        return obj.order_type, obj.get_order_type_display()


@admin.register(OrderItem)
class OrderItemAdmin(ModelAdmin):
    list_display = ["id", "order", "product", "quantity", "price", "created_at"]
    list_per_page = 50
    search_fields = ["order__user__telegram_id"]
    autocomplete_fields = ["order", "product"]
