from modeltranslation.translator import TranslationOptions, register

from apps.shop.models.products import Product


@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ("title", "description")
