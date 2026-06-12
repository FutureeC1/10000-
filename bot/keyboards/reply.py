from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config.config import ADMIN_ID

def get_main_menu(user_id: int) -> ReplyKeyboardMarkup:
    keyboard_buttons = [
        [KeyboardButton(text="🛒 Каталог"), KeyboardButton(text="📦 Мои заказы")],
        [KeyboardButton(text="⭐ Избранное"), KeyboardButton(text="🔍 Поиск")],
        [KeyboardButton(text="ℹ️ О магазине"), KeyboardButton(text="📞 Контакты")]
    ]
        
    return ReplyKeyboardMarkup(
        keyboard=keyboard_buttons,
        resize_keyboard=True,
        placeholder="Выберите пункт меню..."
    )
