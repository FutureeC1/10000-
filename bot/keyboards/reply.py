# pyrefly: ignore [missing-import]
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config.config import ADMIN_ID
from database.repositories import UserRepository, ShopRepository

def get_main_menu(user_id: int) -> ReplyKeyboardMarkup:
    # Базовые кнопки для клиента
    keyboard_buttons = [
        [KeyboardButton(text="🏪 Магазины"), KeyboardButton(text="📦 Мои заказы")],
        [KeyboardButton(text="📞 Поддержка")]
    ]
    
    # 1. Проверяем роль SUPER_ADMIN
    if ADMIN_ID and user_id == ADMIN_ID:
        keyboard_buttons.append([KeyboardButton(text="🛡 Супер-админка")])
    else:
        # 2. Проверяем роль SHOP_OWNER (владелец хотя бы одного магазина)
        user = UserRepository.get_user(user_id)
        if user and user['role'] == 'SHOP_OWNER':
            keyboard_buttons.append([KeyboardButton(text="💼 Мой магазин")])
        else:
            # На случай, если он владелец, но роль не проставилась
            owned_shops = ShopRepository.get_shops_by_owner(user_id)
            if owned_shops:
                keyboard_buttons.append([KeyboardButton(text="💼 Мой магазин")])
                
    return ReplyKeyboardMarkup(
        keyboard=keyboard_buttons,
        resize_keyboard=True,
        placeholder="Выберите действие..."
    )
