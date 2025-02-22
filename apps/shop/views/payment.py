from click_up.models import ClickTransaction
from click_up.views import ClickWebhook
from payme.models import PaymeTransactions
from payme.views import PaymeWebHookAPIView
from rest_framework.permissions import AllowAny

from apps.shop.models.cart import Cart
from apps.shop.models.order import Order
from apps.shop.signals.signals import order_status_updated


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
        return self.response.CheckPerformTransaction(allow=True).as_resp()

    def handle_payment(self, params, success):
        transaction = PaymeTransactions.get_by_transaction_id(params["id"])
        order = Order.objects.get(id=transaction.account_id)
        order = update_order_status(order, success, success)
        Cart.objects.filter(user=order.user).delete()

        # Send signal for asynchronous notifications
        order_status_updated.send(sender=self.__class__, order=order, success=success)
        print(f"payment {'successful' if success else 'cancelled'} params: {params}")
        return order

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

        # Send signal for asynchronous notifications
        order_status_updated.send(sender=self.__class__, order=order, success=success)
        print(f"payment {'successful' if success else 'cancelled'} params: {params}")
        return order

    def successfully_payment(self, params):
        self.handle_payment(params, success=True)

    def cancelled_payment(self, params):
        self.handle_payment(params, success=False)
