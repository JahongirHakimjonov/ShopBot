from telebot.custom_filters import SimpleCustomFilter

from apps.shop.models.users import BotUsers, RoleChoices


class AdminFilter(SimpleCustomFilter):
    """
    Filter for admin users
    """

    key = "admin"

    def check(self, message):
        admins = BotUsers.objects.exclude(role=RoleChoices.USER).values_list(
            "telegram_id", flat=True
        )
        return message.from_user.id in admins
