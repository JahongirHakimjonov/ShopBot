from modeltranslation.translator import TranslationOptions, register

from apps.shop.models.news import News, NewsButton


@register(News)
class NewsTranslationOptions(TranslationOptions):
    fields = ("title", "description")


@register(NewsButton)
class NewsButtonTranslationOptions(TranslationOptions):
    fields = ("title",)
