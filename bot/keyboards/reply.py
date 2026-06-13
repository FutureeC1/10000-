from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from database.repositories import UserRepository
from config.localization import get_text, get_localized_category

def get_main_menu(user_id: int) -> ReplyKeyboardMarkup:
    """Генерирует главное Reply-меню клиента."""
    lang = UserRepository.get_user_language(user_id)
    keyboard_buttons = [
        [KeyboardButton(text=get_text('btn_shops', lang)), KeyboardButton(text=get_text('btn_orders', lang))],
        [KeyboardButton(text=get_text('btn_cart_menu', lang)), KeyboardButton(text=get_text('btn_favorites', lang))],
        [KeyboardButton(text=get_text('btn_lang', lang))]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard_buttons,
        resize_keyboard=True,
        placeholder="Выберите действие..." if lang == 'ru' else "Harakatni tanlang..."
    )


def get_shop_menu_keyboard(categories: list, lang: str = 'ru') -> ReplyKeyboardMarkup:
    """Генерирует Reply-меню для конкретного магазина, выводя категории в клавиатуру."""
    keyboard_buttons = []
    
    # Распределяем категории по 2 в ряд
    for i in range(0, len(categories), 2):
        row = []
        for cat in categories[i:i+2]:
            row.append(KeyboardButton(text=get_localized_category(cat, lang)))
        keyboard_buttons.append(row)
        
    # Добавляем функциональные кнопки
    keyboard_buttons.append([
        KeyboardButton(text=get_text('btn_search', lang)),
        KeyboardButton(text=get_text('btn_back_to_shops', lang))
    ])
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard_buttons,
        resize_keyboard=True,
        placeholder="Выберите категорию товаров..." if lang == 'ru' else "Mahsulot kategoriyasini tanlang..."
    )

