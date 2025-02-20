from apps.shop.models.users import BotUsers
from django.utils.translation import activate, gettext as _


def set_language_code(telegram_id):
    if BotUsers.objects.filter(telegram_id=telegram_id).exists():
        user = BotUsers.objects.get(telegram_id=telegram_id)
        activate(user.language_code)
        return user.language_code
    else:
        activate("uz")
        return "uz"
