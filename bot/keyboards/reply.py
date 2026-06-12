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


def get_shop_menu_keyboard(categories: list) -> ReplyKeyboardMarkup:
    """Генерирует Reply-меню для конкретного магазина, выводя категории в клавиатуру."""
    keyboard_buttons = []
    
    # Распределяем категории по 2 в ряд
    for i in range(0, len(categories), 2):
        row = []
        for cat in categories[i:i+2]:
            row.append(KeyboardButton(text=cat))
        keyboard_buttons.append(row)
        
    # Добавляем функциональные кнопки
    keyboard_buttons.append([
        KeyboardButton(text="🔍 Поиск по магазину"),
        KeyboardButton(text="🔙 К списку магазинов")
    ])
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard_buttons,
        resize_keyboard=True,
        placeholder="Выберите категорию товаров..."
    )

