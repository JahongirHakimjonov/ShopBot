from modeltranslation.translator import TranslationOptions, register

from apps.shop.models.category import Category


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ("name",)
