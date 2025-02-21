from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


def user_has_group_or_permission(user, permission):
    if user.is_superuser:
        return True

    group_names = user.groups.values_list("name", flat=True)
    if not group_names:
        return True

    return user.groups.filter(permissions__codename=permission).exists()


PAGES = [
    {
        "seperator": True,
        "items": [
            {
                "title": _("Home"),
                "icon": "home",
                "link": reverse_lazy("admin:index"),
            },
        ],
    },
    {
        "seperator": True,
        "title": _("Users"),
        "items": [
            {
                "title": _("Groups"),
                "icon": "person_add",
                "link": reverse_lazy("admin:auth_group_changelist"),
                "permission": lambda request: user_has_group_or_permission(
                    request.user, "view_group"
                ),
            },
            {
                "title": _("Users"),
                "icon": "person_add",
                "link": reverse_lazy("admin:auth_user_changelist"),
                "permission": lambda request: user_has_group_or_permission(
                    request.user, "view_user"
                ),
            },
        ],
    },
    {
        "seperator": True,
        "title": _("Bot Users"),
        "items": [
            {
                "title": _("Bot Users"),
                "icon": "smart_toy",
                "link": reverse_lazy("admin:shop_botusers_changelist"),
                "permission": lambda request: user_has_group_or_permission(
                    request.user, "view_botusers"
                ),
            },
        ],
    },
    {
        "seperator": True,
        "title": _("MilliyTech Shop"),
        "items": [
            {
                "title": _("Category"),
                "icon": "category",
                "link": reverse_lazy("admin:shop_category_changelist"),
                "permission": lambda request: user_has_group_or_permission(
                    request.user, "view_category"
                ),
            },
            {
                "title": _("Products"),
                "icon": "inventory",
                "link": reverse_lazy("admin:shop_product_changelist"),
                "permission": lambda request: user_has_group_or_permission(
                    request.user, "view_product"
                ),
            },
            {
                "title": _("Donate"),
                "icon": "paid",
                "link": reverse_lazy("admin:shop_donate_changelist"),
                "permission": lambda request: user_has_group_or_permission(
                    request.user, "view_donate"
                ),
            },
        ],
    },
    {
        "seperator": True,
        "title": _("MilliyTech Shop Additional"),
        "items": [
            {
                "title": _("Order"),
                "icon": "shopping_cart",
                "link": reverse_lazy("admin:shop_order_changelist"),
                "permission": lambda request: user_has_group_or_permission(
                    request.user, "view_order"
                ),
                "badge": lambda: __import__(
                    "apps.shop.models.order"
                ).shop.models.order.Order.pending_orders(),
            },
            {
                "title": _("Cart"),
                "icon": "local_mall",
                "link": reverse_lazy("admin:shop_cart_changelist"),
                "permission": lambda request: user_has_group_or_permission(
                    request.user, "view_cart"
                ),
            },
            {
                "title": _("Info"),
                "icon": "info",
                "link": reverse_lazy("admin:shop_info_changelist"),
                "permission": lambda request: user_has_group_or_permission(
                    request.user, "view_info"
                ),
            },
            {
                "title": _("News"),
                "icon": "brand_awareness",
                "link": reverse_lazy("admin:shop_news_changelist"),
                "permission": lambda request: user_has_group_or_permission(
                    request.user, "view_news"
                ),
            },
            {
                "title": _("Help"),
                "icon": "accessibility_new",
                "link": reverse_lazy("admin:shop_help_changelist"),
                "permission": lambda request: user_has_group_or_permission(
                    request.user, "view_help"
                ),
            },
        ],
    },
]

TABS = [
    {
        "models": [
            "shop.cart",
            "shop.cartitem",
        ],
        "items": [
            {
                "title": _("Cart"),
                "link": reverse_lazy("admin:shop_cart_changelist"),
            },
            {
                "title": _("Cart Item"),
                "link": reverse_lazy("admin:shop_cartitem_changelist"),
            },
        ],
    },
    {
        "models": [
            "shop.order",
            "shop.orderitem",
        ],
        "items": [
            {
                "title": _("Cart"),
                "link": reverse_lazy("admin:shop_order_changelist"),
            },
            {
                "title": _("Cart Item"),
                "link": reverse_lazy("admin:shop_orderitem_changelist"),
            },
        ],
    },
    {
        "models": [
            "shop.news",
            "shop.newsbutton",
        ],
        "items": [
            {
                "title": _("News"),
                "link": reverse_lazy("admin:shop_news_changelist"),
            },
            {
                "title": _("News Button"),
                "link": reverse_lazy("admin:shop_newsbutton_changelist"),
            },
        ],
    },
]
