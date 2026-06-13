# pyrefly: ignore [missing-import]
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List
from config.localization import get_text

def get_language_keyboard() -> InlineKeyboardMarkup:
    """Генерирует клавиатуру выбора языка (Русский / O'zbekcha)."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz")
        ]
    ])


def get_shops_list_keyboard(shops: List[dict]) -> InlineKeyboardMarkup:
    """Список магазинов для клиента."""
    keyboard = []
    for shop in shops:
        keyboard.append([InlineKeyboardButton(text=f"🏪 {shop['name']}", callback_data=f"selectshop_{shop['id']}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_shop_categories_keyboard(shop_id: int, categories: List[str], lang: str = 'ru') -> InlineKeyboardMarkup:
    """Список категорий товаров в выбранном магазине."""
    keyboard = []
    for i in range(0, len(categories), 2):
        row = []
        for cat in categories[i:i+2]:
            row.append(InlineKeyboardButton(text=cat, callback_data=f"shopcat_{shop_id}_{cat}"))
        keyboard.append(row)
        
    keyboard.append([InlineKeyboardButton(text=get_text('btn_search', lang), callback_data=f"shopsearch_{shop_id}")])
    keyboard.append([InlineKeyboardButton(text=get_text('btn_back_to_shops', lang), callback_data="back_to_shops")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_product_detail_keyboard(product_id: int, shop_id: int, category: str, current_index: int, 
                                 total_count: int, is_fav: bool, is_available: bool, lang: str = 'ru') -> InlineKeyboardMarkup:
    """Карточка товара с пагинацией для клиента."""
    keyboard = []
    
    # Кнопки действия (Заказать, Избранное)
    action_row = []
    if is_available:
        action_row.append(InlineKeyboardButton(text=get_text('btn_add_to_cart', lang), callback_data=f"order_{shop_id}_{product_id}"))
    
    fav_text = get_text('btn_unfavorite', lang) if is_fav else get_text('btn_favorite', lang)
    action_row.append(InlineKeyboardButton(text=fav_text, callback_data=f"fav_{product_id}_{current_index}"))
    keyboard.append(action_row)
    
    # Пагинация
    pagination_row = []
    if total_count > 1:
        prev_idx = (current_index - 1) % total_count
        next_idx = (current_index + 1) % total_count
        pagination_row.append(InlineKeyboardButton(text="◀️", callback_data=f"nav_{shop_id}_{category}_{prev_idx}"))
        pagination_row.append(InlineKeyboardButton(text=f"{current_index + 1}/{total_count}", callback_data="ignore"))
        pagination_row.append(InlineKeyboardButton(text="➡️", callback_data=f"nav_{shop_id}_{category}_{next_idx}"))
        keyboard.append(pagination_row)
        
    keyboard.append([InlineKeyboardButton(text=get_text('btn_back', lang), callback_data=f"back_to_categories_{shop_id}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_favorites_keyboard(product_id: int, current_index: int, total_count: int, lang: str = 'ru') -> InlineKeyboardMarkup:
    """Клавиатура для просмотра Избранного."""
    keyboard = []
    
    # Кнопка Заказать и Удалить
    keyboard.append([
        InlineKeyboardButton(text=get_text('btn_add_to_cart', lang), callback_data=f"order_fav_{product_id}"),
        InlineKeyboardButton(text="❌ " + ("Удалить" if lang == 'ru' else "O'chirish"), callback_data=f"unfav_{product_id}_{current_index}")
    ])
    
    # Пагинация
    pagination_row = []
    if total_count > 1:
        prev_idx = (current_index - 1) % total_count
        next_idx = (current_index + 1) % total_count
        pagination_row.append(InlineKeyboardButton(text="◀️", callback_data=f"favnav_{prev_idx}"))
        pagination_row.append(InlineKeyboardButton(text=f"{current_index + 1}/{total_count}", callback_data="ignore"))
        pagination_row.append(InlineKeyboardButton(text="➡️", callback_data=f"favnav_{next_idx}"))
        keyboard.append(pagination_row)
        
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_confirm_order_keyboard(lang: str = 'ru') -> InlineKeyboardMarkup:
    """Подтверждение заказа."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ " + ("Подтверждаю" if lang == 'ru' else "Tasdiqlayman"), callback_data="confirm_order_yes"),
            InlineKeyboardButton(text="❌ " + ("Отмена" if lang == 'ru' else "Bekor qilish"), callback_data="confirm_order_no")
        ]
    ])


def get_support_keyboard(manager_username: str) -> InlineKeyboardMarkup:
    """Клавиатура поддержки."""
    if manager_username.startswith('@'):
        manager_username = manager_username[1:]
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📞 Связаться с поддержкой", url=f"https://t.me/{manager_username}")]
    ])


# ==========================================
# КЛАВИАТУРЫ СУПЕР-АДМИНИСТРАТОРА (SUPER_ADMIN)
# ==========================================

def get_superadmin_main_keyboard() -> InlineKeyboardMarkup:
    """Панель Супер-админа."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Создать магазин", callback_data="sa_add_shop"),
            InlineKeyboardButton(text="🗑 Удалить магазин", callback_data="sa_list_shops_del")
        ],
        [
            InlineKeyboardButton(text="📊 Статистика системы", callback_data="sa_stats")
        ]
    ])


def get_superadmin_delete_shops_keyboard(shops: List[dict]) -> InlineKeyboardMarkup:
    """Список магазинов для удаления."""
    keyboard = []
    for shop in shops:
        keyboard.append([
            InlineKeyboardButton(text=f"❌ Удалить {shop['name']}", callback_data=f"sa_del_confirm_{shop['id']}")
        ])
    keyboard.append([InlineKeyboardButton(text="📁 В супер-админку", callback_data="sa_back")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# ==========================================
# КЛАВИАТУРЫ ВЛАДЕЛЬЦА МАГАЗИНА (SHOP_OWNER)
# ==========================================

def get_shop_owner_select_shop_keyboard(shops: List[dict]) -> InlineKeyboardMarkup:
    """Выбор магазина для управления владельцем (если их несколько)."""
    keyboard = []
    for shop in shops:
        keyboard.append([InlineKeyboardButton(text=f"🛠 {shop['name']}", callback_data=f"own_manage_shop_{shop['id']}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_shop_owner_dashboard_keyboard(shop_id: int) -> InlineKeyboardMarkup:
    """Панель управления конкретным магазином."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Добавить товар", callback_data=f"own_add_product_{shop_id}"),
            InlineKeyboardButton(text="📦 Управление товарами", callback_data=f"own_list_products_{shop_id}")
        ],
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data=f"own_stats_{shop_id}"),
            InlineKeyboardButton(text="📥 Список заказов", callback_data=f"own_list_orders_{shop_id}")
        ]
    ])


def get_owner_products_nav_keyboard(product_id: int, shop_id: int, current_index: int, 
                                     total_count: int) -> InlineKeyboardMarkup:
    """Управление товарами для владельца магазина с пагинацией."""
    keyboard = []
    
    # Действия
    keyboard.append([
        InlineKeyboardButton(text="✏️ Цена", callback_data=f"own_prod_price_{product_id}_{current_index}"),
        InlineKeyboardButton(text="🔔 Наличие", callback_data=f"own_prod_avail_{product_id}_{current_index}"),
        InlineKeyboardButton(text="🔥 Скидка", callback_data=f"own_prod_discount_{product_id}_{current_index}")
    ])
    keyboard.append([
        InlineKeyboardButton(text="❌ Удалить товар", callback_data=f"own_prod_del_{product_id}_{current_index}")
    ])
    
    # Пагинация
    pagination_row = []
    if total_count > 1:
        prev_idx = (current_index - 1) % total_count
        next_idx = (current_index + 1) % total_count
        pagination_row.append(InlineKeyboardButton(text="◀️", callback_data=f"own_prod_nav_{shop_id}_{prev_idx}"))
        pagination_row.append(InlineKeyboardButton(text=f"{current_index + 1}/{total_count}", callback_data="ignore"))
        pagination_row.append(InlineKeyboardButton(text="➡️", callback_data=f"own_prod_nav_{shop_id}_{next_idx}"))
        keyboard.append(pagination_row)
        
    keyboard.append([InlineKeyboardButton(text="📁 В меню магазина", callback_data=f"own_manage_shop_{shop_id}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_owner_orders_list_keyboard(orders: List[dict], shop_id: int, current_page: int, 
                                    total_pages: int) -> InlineKeyboardMarkup:
    """Список заказов магазина для владельца."""
    keyboard = []
    
    for order in orders:
        keyboard.append([
            InlineKeyboardButton(
                text=f"Заказ #{order['id']} - {order['status']} ({order['product_price']:,} сум)",
                callback_data=f"own_order_detail_{order['id']}"
            )
        ])
        
    # Пагинация по страницам
    nav_row = []
    if total_pages > 1:
        prev_page = (current_page - 1) % total_pages
        next_page = (current_page + 1) % total_pages
        nav_row.append(InlineKeyboardButton(text="◀️", callback_data=f"own_orders_page_{shop_id}_{prev_page}"))
        nav_row.append(InlineKeyboardButton(text=f"{current_page + 1}/{total_pages}", callback_data="ignore"))
        nav_row.append(InlineKeyboardButton(text="➡️", callback_data=f"own_orders_page_{shop_id}_{next_page}"))
        keyboard.append(nav_row)
        
    keyboard.append([
        InlineKeyboardButton(text="📊 Экспорт CSV", callback_data=f"own_export_csv_{shop_id}"),
        InlineKeyboardButton(text="📁 В меню", callback_data=f"own_manage_shop_{shop_id}")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_owner_order_status_keyboard(order_id: int, shop_id: int) -> InlineKeyboardMarkup:
    """Клавиатура смены статуса заказа для владельца."""
    statuses = ['Новый', 'Подтвержден', 'В обработке', 'Доставляется', 'Завершен', 'Отменен']
    keyboard = []
    
    for i in range(0, len(statuses), 2):
        row = []
        for status in statuses[i:i+2]:
            row.append(InlineKeyboardButton(text=status, callback_data=f"own_change_status_{order_id}_{status}"))
        keyboard.append(row)
        
    keyboard.append([InlineKeyboardButton(text="📁 Назад к заказам", callback_data=f"own_list_orders_{shop_id}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
