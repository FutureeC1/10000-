from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config.config import ADMIN_ID

def get_main_menu(user_id: int) -> ReplyKeyboardMarkup:
    keyboard_buttons = [
        [KeyboardButton(text="🛒 Каталог"), KeyboardButton(text="📦 Мои заказы")],
        [KeyboardButton(text="⭐ Избранное"), KeyboardButton(text="🔍 Поиск")],
        [KeyboardButton(text="ℹ️ О магазине"), KeyboardButton(text="📞 Контакты")]
    ]
    
    # Если пользователь админ, добавляем админ-панель
    if ADMIN_ID and user_id == ADMIN_ID:
        keyboard_buttons.append([KeyboardButton(text="⚙️ Админ-панель")])
        
    return ReplyKeyboardMarkup(
        keyboard=keyboard_buttons,
        resize_keyboard=True,
        placeholder="Выберите пункт меню..."
    )
