from django.dispatch import Signal

# Signal to be sent after an order's payment status is updated.
# Receivers will be passed the order instance and a boolean 'success'.
order_status_updated = Signal()
