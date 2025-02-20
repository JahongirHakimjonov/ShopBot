from modeltranslation.translator import TranslationOptions, register

from apps.shop.models.help import Help


@register(Help)
class HelpTranslationOptions(TranslationOptions):
    fields = ("title", "description")
