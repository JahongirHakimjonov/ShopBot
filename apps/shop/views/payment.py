import os

from click_up.models import ClickTransaction
from click_up.views import ClickWebhook
from django.utils.translation import gettext as _
from payme.models import PaymeTransactions
from payme.types import response
from payme.views import PaymeWebHookAPIView
from rest_framework.permissions import AllowAny
from telebot import TeleBot

from apps.shop.models.cart import Cart
from apps.shop.models.order import Order

bot = TeleBot(os.getenv("BOT_TOKEN"))


def notify_user(user, message):
    if user.telegram_id:
        bot.send_message(chat_id=user.telegram_id, text=message)


def update_order_status(order, status, is_completed=False):
    order.payment_status = status
    order.status = Order.Status.COMPLETED if is_completed else Order.Status.CANCELLED
    order.save()
    return order


class PaymeCallBackAPIView(PaymeWebHookAPIView):
    permission_classes = [AllowAny]

    def check_perform_transaction(self, params):
        account = self.fetch_account(params)
        self.validate_amount(account, params.get("amount"))
        return response.CheckPerformTransaction(allow=True).as_resp()

    def handle_payment(self, params, success):
        transaction = PaymeTransactions.get_by_transaction_id(params["id"])
        order = Order.objects.get(id=transaction.account_id)
        order = update_order_status(order, success, success)
        Cart.objects.filter(user=order.user).delete()

        message = (
            _("Your order has been successfully paid. Order ID: {order_id}")
            if success
            else _("Your order has been cancelled. Order ID: {order_id}")
        )
        notify_user(order.user, message.format(order_id=order.id))

    def handle_successfully_payment(self, params, result, *args, **kwargs):
        self.handle_payment(params, success=True)

    def handle_cancelled_payment(self, params, result, *args, **kwargs):
        self.handle_payment(params, success=False)


class ClickWebhookAPIView(ClickWebhook):
    def handle_payment(self, params, success):
        transaction = ClickTransaction.objects.get(transaction_id=params.click_trans_id)
        order = Order.objects.get(id=transaction.account_id)
        order = update_order_status(order, success, success)
        Cart.objects.filter(user=order.user).delete()

        message = (
            _("Your order has been successfully paid. Order ID: {order_id}")
            if success
            else _("Your order has been cancelled. Order ID: {order_id}")
        )
        notify_user(order.user, message.format(order_id=order.id))
        print(f"payment {'successful' if success else 'cancelled'} params: {params}")

    def successfully_payment(self, params):
        self.handle_payment(params, success=True)

    def cancelled_payment(self, params):
        self.handle_payment(params, success=False)
