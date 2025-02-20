from django.urls import path

from apps.shop.views.payment import PaymeCallBackAPIView

urlpatterns = [
    path("webhok/payme/", PaymeCallBackAPIView.as_view(), name="payme-webhook"),
    path("webhok/click/", PaymeCallBackAPIView.as_view(), name="click-webhook"),
]
