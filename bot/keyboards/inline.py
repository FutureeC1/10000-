from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List

def get_manager_keyboard(username: str) -> InlineKeyboardMarkup:
    """Кнопка для связи с менеджером."""
    # Убираем @ если есть
    if username.startswith('@'):
        username = username[1:]
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📞 Написать менеджеру", url=f"https://t.me/{username}")
        ]
    ])

def get_categories_keyboard(categories: List[str]) -> InlineKeyboardMarkup:
    """Клавиатура со списком категорий."""
    keyboard = []
    # Отображаем категории по 2 в ряд
    for i in range(0, len(categories), 2):
        row = []
        for cat in categories[i:i+2]:
            row.append(InlineKeyboardButton(text=cat, callback_data=f"cat_{cat}"))
        keyboard.append(row)
        
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_product_detail_keyboard(product_id: int, category: str, current_index: int, 
                                 total_count: int, is_fav: bool, is_available: bool) -> InlineKeyboardMarkup:
    """Клавиатура для карточки товара с пагинацией."""
    keyboard = []
    
    # Кнопки действия (Заказать, Избранное)
    action_row = []
    if is_available:
        action_row.append(InlineKeyboardButton(text="🛒 Заказать", callback_data=f"order_{product_id}"))
    
    fav_text = "❌ Убрать из Избранного" if is_fav else "⭐ В Избранное"
    action_row.append(InlineKeyboardButton(text=fav_text, callback_data=f"fav_{product_id}_{current_index}"))
    keyboard.append(action_row)
    
    # Кнопки пагинации
    pagination_row = []
    if total_count > 1:
        prev_idx = (current_index - 1) % total_count
        next_idx = (current_index + 1) % total_count
        pagination_row.append(InlineKeyboardButton(text="◀️", callback_data=f"nav_{category}_{prev_idx}"))
        pagination_row.append(InlineKeyboardButton(text=f"{current_index + 1}/{total_count}", callback_data="ignore"))
        pagination_row.append(InlineKeyboardButton(text="➡️", callback_data=f"nav_{category}_{next_idx}"))
        keyboard.append(pagination_row)
        
    # Кнопка возврата к списку категорий
    keyboard.append([InlineKeyboardButton(text="📁 К категориям", callback_data="back_to_categories")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_favorites_keyboard(product_id: int, current_index: int, total_count: int) -> InlineKeyboardMarkup:
    """Клавиатура для товаров из Избранного."""
    keyboard = []
    
    # Кнопки действия
    keyboard.append([
        InlineKeyboardButton(text="🛒 Заказать", callback_data=f"order_fav_{product_id}"),
        InlineKeyboardButton(text="❌ Удалить", callback_data=f"unfav_{product_id}_{current_index}")
    ])
    
    # Пагинация по избранному
    pagination_row = []
    if total_count > 1:
        prev_idx = (current_index - 1) % total_count
        next_idx = (current_index + 1) % total_count
        pagination_row.append(InlineKeyboardButton(text="◀️", callback_data=f"favnav_{prev_idx}"))
        pagination_row.append(InlineKeyboardButton(text=f"{current_index + 1}/{total_count}", callback_data="ignore"))
        pagination_row.append(InlineKeyboardButton(text="➡️", callback_data=f"favnav_{next_idx}"))
        keyboard.append(pagination_row)
        
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_confirm_order_keyboard() -> InlineKeyboardMarkup:
    """Подтверждение заказа."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтверждаю", callback_data="confirm_order_yes"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="confirm_order_no")
        ]
    ])

def get_admin_main_keyboard() -> InlineKeyboardMarkup:
    """Главная админ-клавиатура."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Добавить товар", callback_data="adm_add_product"),
            InlineKeyboardButton(text="🗑 Управление товарами", callback_data="adm_manage_products")
        ],
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data="adm_stats"),
            InlineKeyboardButton(text="📦 Просмотр заказов", callback_data="adm_list_orders")
        ],
        [
            InlineKeyboardButton(text="📢 Сделать рассылку", callback_data="adm_broadcast")
        ]
    ])

def get_admin_products_nav_keyboard(product_id: int, current_index: int, total_count: int) -> InlineKeyboardMarkup:
    """Навигация по товарам для админа."""
    keyboard = []
    
    # Действия над товаром
    keyboard.append([
        InlineKeyboardButton(text="✏️ Цена", callback_data=f"adm_prod_price_{product_id}_{current_index}"),
        InlineKeyboardButton(text="🔔 Наличие", callback_data=f"adm_prod_avail_{product_id}_{current_index}"),
        InlineKeyboardButton(text="🔥 Скидка", callback_data=f"adm_prod_discount_{product_id}_{current_index}")
    ])
    keyboard.append([
        InlineKeyboardButton(text="❌ Удалить товар", callback_data=f"adm_prod_del_{product_id}_{current_index}")
    ])
    
    # Пагинация
    pagination_row = []
    if total_count > 1:
        prev_idx = (current_index - 1) % total_count
        next_idx = (current_index + 1) % total_count
        pagination_row.append(InlineKeyboardButton(text="◀️", callback_data=f"adm_prod_nav_{prev_idx}"))
        pagination_row.append(InlineKeyboardButton(text=f"{current_index + 1}/{total_count}", callback_data="ignore"))
        pagination_row.append(InlineKeyboardButton(text="➡️", callback_data=f"adm_prod_nav_{next_idx}"))
        keyboard.append(pagination_row)
        
    keyboard.append([InlineKeyboardButton(text="📁 В админку", callback_data="adm_back")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_admin_order_status_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора статуса заказа."""
    statuses = ['Новый', 'Подтвержден', 'В обработке', 'Доставляется', 'Завершен', 'Отменен']
    keyboard = []
    
    # По 2 кнопки в ряд
    for i in range(0, len(statuses), 2):
        row = []
        for status in statuses[i:i+2]:
            row.append(InlineKeyboardButton(text=status, callback_data=f"adm_change_status_{order_id}_{status}"))
        keyboard.append(row)
        
    keyboard.append([InlineKeyboardButton(text="📁 К заказам", callback_data="adm_list_orders")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_admin_orders_list_keyboard(orders: List[dict], current_page: int, total_pages: int) -> InlineKeyboardMarkup:
    """Список заказов с пагинацией."""
    keyboard = []
    
    # Список заказов (кнопка на каждый заказ)
    for order in orders:
        keyboard.append([
            InlineKeyboardButton(
                text=f"Заказ #{order['id']} - {order['status']} ({order['product_price']} сум)",
                callback_data=f"adm_order_detail_{order['id']}"
            )
        ])
        
    # Пагинация по страницам
    nav_row = []
    if total_pages > 1:
        prev_page = (current_page - 1) % total_pages
        next_page = (current_page + 1) % total_pages
        nav_row.append(InlineKeyboardButton(text="◀️", callback_data=f"adm_orders_page_{prev_page}"))
        nav_row.append(InlineKeyboardButton(text=f"{current_page + 1}/{total_pages}", callback_data="ignore"))
        nav_row.append(InlineKeyboardButton(text="➡️", callback_data=f"adm_orders_page_{next_page}"))
        keyboard.append(nav_row)
        
    keyboard.append([InlineKeyboardButton(text="📁 В админку", callback_data="adm_back")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
