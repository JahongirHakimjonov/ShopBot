from django.db.models import Count, Q
from django.utils.translation import activate
from django.utils.translation import gettext as _
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, Message

from apps.bot.handlers.cart import handle_cart
from apps.bot.keyboard import get_main_buttons
from apps.bot.logger import logger
from apps.bot.utils import update_or_create_user
from apps.bot.utils.language import set_language_code
from apps.shop.models.cart import Cart, CartItem
from apps.shop.models.category import Category
from apps.shop.models.products import Product
from apps.shop.models.users import BotUsers


def handle_category(message: Message, bot: TeleBot):
    activate(set_language_code(message.from_user.id))
    update_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        is_active=True,
    )
    logger.info(f"User {message.from_user.id} selected a product category.")

    categories = Category.objects.annotate(
        product_count=Count("products", filter=Q(products__quantity__gt=0))
    ).filter(product_count__gt=0, is_active=True)

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton(text=_("Cart")))
    row = []
    for index, category in enumerate(categories):
        row.append(KeyboardButton(text=category.name))
        if (index + 1) % 2 == 0:
            keyboard.add(*row)
            row = []

    if row:
        keyboard.add(*row)
    keyboard.add(KeyboardButton(text=_("Home")))

    bot.send_message(
        message.chat.id, _("Please select a category:"), reply_markup=keyboard
    )

    # Pass the bot instance to the next handler
    bot.register_next_step_handler(message, handle_product, bot)


def handle_product(message: Message, bot: TeleBot, category_name: str = None):
    activate(set_language_code(message.from_user.id))
    update_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        is_active=True,
    )
    logger.info(f"User {message.from_user.id} selected a product.")

    if message.text == _("Home"):
        bot.send_message(
            message.chat.id, _("Welcome to the bot!"), reply_markup=get_main_buttons()
        )
        return

    if message.text == _("Cart"):
        return handle_cart(message, bot)

    if category_name:
        products = Product.objects.filter(
            Q(category__name_uz=category_name) | Q(category__name_ru=category_name),
            quantity__gt=0,
            is_active=True,
        )
    else:
        products = Product.objects.filter(
            Q(category__name_uz=message.text) | Q(category__name_ru=message.text),
            quantity__gt=0,
            is_active=True,
        )

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton(text=_("Home")), KeyboardButton(text=_("Cart")))
    row = []
    for index, product in enumerate(products):  # renamed variable to avoid shadowing
        row.append(KeyboardButton(text=product.title))
        if (index + 1) % 2 == 0:
            keyboard.add(*row)
            row = []

    if row:
        keyboard.add(*row)
    keyboard.add(KeyboardButton(text=_("Back")))

    bot.send_message(
        message.chat.id, _("Please select a product:"), reply_markup=keyboard
    )

    bot.register_next_step_handler(message, handle_product_count, bot)


def handle_product_count(message: Message, bot: TeleBot):
    activate(set_language_code(message.from_user.id))
    update_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        is_active=True,
    )
    logger.info(f"User {message.from_user.id} selected a product count.")

    if message.text == _("Home"):
        bot.send_message(
            message.chat.id, _("Welcome to the bot!"), reply_markup=get_main_buttons()
        )
        return

    if message.text == _("Cart"):
        return handle_cart(message, bot)

    if message.text == _("Back"):
        return handle_category(message, bot)

    product = Product.objects.filter(
        Q(title_uz=message.text) | Q(title_ru=message.text) | Q(title=message.text),
        quantity__gt=0,
        is_active=True,
    ).first()

    if not product:
        bot.send_message(message.chat.id, _("Product not found."))
        return

    if product.quantity == 0:
        bot.send_message(message.chat.id, _("Product is out of stock."))
        return

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton(text=_("Back")))
    row = []
    max_count = min(product.quantity, 10)
    for count in range(1, max_count + 1):
        row.append(KeyboardButton(text=str(count)))
        if count % 2 == 0:
            keyboard.add(*row)
            row = []

    if row:
        keyboard.add(*row)
    keyboard.add(KeyboardButton(text=_("Home")))

    caption = _("{title}\n\n\t\t{description}\n\nPrice: *{price} UZS*").format(
        title=product.title,
        description=product.description,
        price=f"{int(float(product.price)):,}".replace(",", " "),
    )

    bot.send_photo(
        message.chat.id, product.image, caption=caption, parse_mode="Markdown"
    )

    bot.send_message(
        message.chat.id, _("Please select the quantity:"), reply_markup=keyboard
    )

    bot.register_next_step_handler(
        message, lambda msg: create_cart_item(msg, bot, product)
    )


def create_cart_item(message: Message, bot: TeleBot, product: Product):
    activate(set_language_code(message.from_user.id))
    update_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        is_active=True,
    )

    if message.text == _("Home"):
        bot.send_message(
            message.chat.id, _("Welcome to the bot!"), reply_markup=get_main_buttons()
        )
        return

    if message.text == _("Back"):
        return handle_product(message, bot, category_name=product.category.name)

    try:
        quantity = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, _("Invalid quantity selected."))
        return

    if quantity <= 0 or quantity > product.quantity:
        bot.send_message(message.chat.id, _("Invalid quantity selected."))
        return

    user = BotUsers.objects.get(telegram_id=message.from_user.id)

    cart, created = Cart.objects.get_or_create(user=user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, product=product, defaults={"quantity": quantity}
    )
    cart_item.quantity = quantity
    cart_item.save()

    bot.send_message(message.chat.id, _("Product added to cart."))

    # # Continue to the main menu
    handle_category(message, bot)
