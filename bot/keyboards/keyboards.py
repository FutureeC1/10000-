from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from config import PRODUCTS

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛍 Каталог")],
            [KeyboardButton(text="🛒 Корзина"), KeyboardButton(text="📦 Мои заказы")],
            [KeyboardButton(text="ℹ️ О нас")]
        ],
        resize_keyboard=True
    )

def get_product_keyboard(product_id: int, current_index: int = 0, total_products: int = 1) -> InlineKeyboardMarkup:
    prev_index = current_index - 1 if current_index > 0 else total_products - 1
    next_index = current_index + 1 if current_index < total_products - 1 else 0
    
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ В корзину", callback_data=f"add_{product_id}")],
            [
                InlineKeyboardButton(text="⬅️", callback_data=f"catalog_{prev_index}"),
                InlineKeyboardButton(text=f"{current_index + 1} / {total_products}", callback_data="ignore"),
                InlineKeyboardButton(text="➡️", callback_data=f"catalog_{next_index}")
            ]
        ]
    )

def get_cart_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Оформить заказ", callback_data="checkout")],
            [InlineKeyboardButton(text="🗑 Очистить корзину", callback_data="clear_cart")]
        ]
    )

def get_admin_order_keyboard(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Выполнен", callback_data=f"admin_done_{order_id}")]
        ]
    )
