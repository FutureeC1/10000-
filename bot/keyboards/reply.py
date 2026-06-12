from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu(user_id: int) -> ReplyKeyboardMarkup:
    """Генерирует главное Reply-меню клиента. 
    Оно одинаково для всех пользователей в целях безопасности (скрытие админ-панелей)."""
    keyboard_buttons = [
        [KeyboardButton(text="🏪 Магазины"), KeyboardButton(text="📦 Мои заказы")],
        [KeyboardButton(text="📞 Поддержка")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard_buttons,
        resize_keyboard=True,
        placeholder="Выберите действие..."
    )
