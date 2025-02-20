import os

############################################
# PAYME CONFIG
############################################
PAYME_ID = os.getenv("PAYME_ID")
PAYME_KEY = os.getenv("PAYME_KEY")
PAYME_ACCOUNT_FIELD = os.getenv("PAYME_ACCOUNT_FIELD", "order_id")
PAYME_AMOUNT_FIELD = os.getenv("PAYME_AMOUNT_FIELD", "amount")
PAYME_ACCOUNT_MODEL = os.getenv("PAYME_ACCOUNT_MODEL", "apps.shop.models.order.Order")
PAYME_SUCCESS_URL = os.getenv("PAYME_SUCCESS_URL")
PAYME_ONE_TIME_PAYMENT = os.getenv("PAYME_ONE_TIME_PAYMENT")
if PAYME_ONE_TIME_PAYMENT is not None:
    PAYME_ONE_TIME_PAYMENT = PAYME_ONE_TIME_PAYMENT.lower() in ["true", "1"]
else:
    PAYME_ONE_TIME_PAYMENT = False
PAYME_TEST_MODE = os.getenv("PAYME_TEST_MODE")
if PAYME_TEST_MODE is not None:
    PAYME_TEST_MODE = PAYME_TEST_MODE.lower() in ["true", "1"]
else:
    PAYME_TEST_MODE = False

############################################
# CLICK CONFIG
############################################
CLICK_SERVICE_ID = os.getenv("CLICK_SERVICE_ID")
CLICK_MERCHANT_ID = os.getenv("CLICK_MERCHANT_ID")
CLICK_SECRET_KEY = os.getenv("CLICK_SECRET_KEY")
CLICK_ACCOUNT_MODEL = os.getenv("CLICK_ACCOUNT_MODEL", "apps.shop.models.order.Order")
CLICK_AMOUNT_FIELD = os.getenv("CLICK_AMOUNT_FIELD", "amount")
CLICK_SUCCESS_URL = os.getenv("CLICK_SUCCESS_URL")
