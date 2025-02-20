from payme.models import PaymeTransactions
from payme.types import response
from payme.views import PaymeWebHookAPIView
from rest_framework.permissions import AllowAny

from apps.shop.models.order import Order


class PaymeCallBackAPIView(PaymeWebHookAPIView):
    permission_classes = [AllowAny]

    def check_perform_transaction(self, params):
        account = self.fetch_account(params)
        self.validate_amount(account, params.get("amount"))
        result = response.CheckPerformTransaction(allow=True)
        return result.as_resp()

    def handle_successfully_payment(self, params, result, *args, **kwargs):
        transaction = PaymeTransactions.get_by_transaction_id(
            transaction_id=params["id"]
        )
        self.update_order_status(transaction.account_id, True)

    def handle_cancelled_payment(self, params, result, *args, **kwargs):
        transaction = PaymeTransactions.get_by_transaction_id(
            transaction_id=params["id"]
        )
        if transaction.state == PaymeTransactions.CANCELED:
            self.update_order_status(transaction.account_id, False)

    def update_order_status(self, account_id, status):
        order = Order.objects.get(id=account_id)
        order.payment_status = status
        order.user.is_premium = status
        order.user.save()
        order.save()
        return order
