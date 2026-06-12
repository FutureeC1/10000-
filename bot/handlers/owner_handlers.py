import logging
import re
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, BufferedInputFile
from aiogram.filters import Command, BaseFilter
from aiogram.fsm.context import FSMContext

from database.repositories import UserRepository, ShopRepository, ProductRepository, OrderRepository
from bot.keyboards.reply import get_main_menu
from bot.keyboards.inline import (
    get_shop_owner_select_shop_keyboard,
    get_shop_owner_dashboard_keyboard,
    get_owner_products_nav_keyboard,
    get_owner_orders_list_keyboard,
    get_owner_order_status_keyboard
)
from bot.states.admin_states import AddProductStates, UpdatePriceStates
from services.stats_service import get_shop_owner_stats
from services.order_service import notify_status_change, export_shop_orders_to_csv
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()

class ShopOwnerFilter(BaseFilter):
    """Фильтр для проверки прав SHOP_OWNER (владельца магазина)."""
    async def __call__(self, obj) -> bool:
        user_id = obj.from_user.id
        
        # 1. Проверяем по .env конфигам
        from config.config import ADMIN_ID, KEYLLECT_OWNER_ID, GAMEZONEBUILD_OWNER_ID
        if ADMIN_ID is not None and user_id == ADMIN_ID:
            return True
            
        if user_id in [KEYLLECT_OWNER_ID, GAMEZONEBUILD_OWNER_ID]:
            return True
            
        # 2. Проверяем роль в БД
        user = UserRepository.get_user(user_id)
        if user and user['role'] in ['SHOP_OWNER', 'SUPER_ADMIN']:
            return True
            
        # 3. Либо проверяем, есть ли у него привязанные магазины в БД
        owned_shops = ShopRepository.get_shops_by_owner(user_id)
        return len(owned_shops) > 0



# Применяем фильтр ко всем хендлерам роутера
router.message.filter(ShopOwnerFilter())
router.callback_query.filter(ShopOwnerFilter())


@router.message(F.text.regexp(r"^/admin([a-zA-Z0-9_]+)1$"))
async def cmd_owner_secret_login(message: Message, state: FSMContext):
    await state.clear()
    match = re.match(r"^/admin([a-zA-Z0-9_]+)1$", message.text.strip())
    if not match:
        return
        
    shop_slug = match.group(1).lower().strip()
    
    # Получаем все магазины
    shops = ShopRepository.get_all_shops()
    target_shop = None
    for shop in shops:
        # Убираем пробелы, дефисы и приводим к нижнему регистру
        slug = shop['name'].lower().replace(" ", "").replace("_", "").replace("-", "")
        if slug == shop_slug:
            target_shop = shop
            break
            
    if not target_shop:
        await message.answer("❌ Магазин с таким кодом не найден в системе.")
        return
        
    # Проверяем права владельца или супер-админа
    user_id = message.from_user.id
    from config.config import get_shop_config, ADMIN_ID
    cfg = get_shop_config(target_shop['name'])
    
    is_owner = (user_id == cfg['owner_id'])
    is_super = (ADMIN_ID is not None and user_id == ADMIN_ID)

    
    if not is_owner and not is_super:
        await message.answer("❌ У вас нет прав для управления этим магазином.")
        return
        
    text = (
        f"💼 <b>Управление магазином «{target_shop['name']}»</b>\n\n"
        f"Используйте кнопки ниже для добавления товаров, просмотра заказов или аналитики:"
    )
    await message.answer(text, reply_markup=get_shop_owner_dashboard_keyboard(target_shop['id']), parse_mode="HTML")



@router.callback_query(F.data.startswith("own_manage_shop_"))
async def callback_own_manage_shop(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    shop_id = int(callback.data.split("_")[3])
    
    # Защита: проверяем, действительно ли пользователь владелец этого магазина
    if not ShopRepository.is_shop_owner(callback.from_user.id, shop_id) and UserRepository.get_user(callback.from_user.id)['role'] != 'SUPER_ADMIN':
        await callback.answer("У вас нет прав на управление этим магазином.", show_alert=True)
        return
        
    shop = ShopRepository.get_shop_by_id(shop_id)
    if not shop:
        await callback.answer("Магазин не найден.", show_alert=True)
        return
        
    text = (
        f"💼 <b>Управление магазином «{shop['name']}»</b>\n\n"
        f"Выберите необходимое действие:"
    )
    
    try:
        await callback.message.delete()
    except Exception:
        pass
        
    await callback.message.answer(text, reply_markup=get_shop_owner_dashboard_keyboard(shop_id), parse_mode="HTML")
    await callback.answer()


# ==========================================
# ДОБАВЛЕНИЕ ТОВАРА (FSM)
# ==========================================

@router.callback_query(F.data.startswith("own_add_product_"))
async def callback_own_add_product_start(callback: CallbackQuery, state: FSMContext):
    shop_id = int(callback.data.split("_")[3])
    await state.clear()
    await state.update_data(shop_id=shop_id)
    
    await callback.message.edit_text(
        "📦 <b>Добавление нового товара</b>\n\n"
        "Шаг 1 из 7: Введите <b>Категорию</b> товара (например: <code>Клавиатуры</code> или <code>Игровые ПК</code>):",
        parse_mode="HTML"
    )
    await state.set_state(AddProductStates.waiting_for_category)
    await callback.answer()


@router.message(AddProductStates.waiting_for_category)
async def process_add_product_category(message: Message, state: FSMContext):
    category = message.text.strip()
    if len(category) < 2:
        await message.answer("Пожалуйста, введите корректное название категории:")
        return
        
    await state.update_data(category=category)
    await message.answer("Шаг 2 из 7: Введите <b>Название</b> товара:")
    await state.set_state(AddProductStates.waiting_for_name)


@router.message(AddProductStates.waiting_for_name)
async def process_add_product_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("Пожалуйста, введите корректное название товара:")
        return
        
    await state.update_data(name=name)
    await message.answer("Шаг 3 из 7: Введите <b>Описание</b> товара:")
    await state.set_state(AddProductStates.waiting_for_description)


@router.message(AddProductStates.waiting_for_description)
async def process_add_product_desc(message: Message, state: FSMContext):
    description = message.text.strip()
    await state.update_data(description=description)
    await message.answer("Шаг 4 из 7: Введите <b>Цена</b> товара (только число, в сум):")
    await state.set_state(AddProductStates.waiting_for_price)


@router.message(AddProductStates.waiting_for_price)
async def process_add_product_price(message: Message, state: FSMContext):
    price_str = message.text.strip()
    try:
        price = float(price_str)
        if price <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Пожалуйста, введите корректное положительное число:")
        return
        
    await state.update_data(price=price)
    
    # Кнопки Да/Нет
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Да"), KeyboardButton(text="Нет")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Шаг 5 из 7: Сделать товар <b>акционным (со скидкой)</b>?", reply_markup=kb, parse_mode="HTML")
    await state.set_state(AddProductStates.waiting_for_is_discount)


@router.message(AddProductStates.waiting_for_is_discount)
async def process_add_product_is_discount(message: Message, state: FSMContext):
    choice = message.text.strip().lower()
    
    if choice == "да":
        await state.update_data(is_discount=1)
        await message.answer("Введите <b>старую цену</b> товара (которая будет зачеркнута):", reply_markup=get_main_menu(message.from_user.id), parse_mode="HTML")
        await state.set_state(AddProductStates.waiting_for_old_price)
    else:
        await state.update_data(is_discount=0, old_price=None)
        await message.answer(
            "Шаг 6 из 7: Отправьте <b>ссылку на фото товара</b> (или напишите «нет» для товара без фото):",
            reply_markup=get_main_menu(message.from_user.id),
            parse_mode="HTML"
        )
        await state.set_state(AddProductStates.waiting_for_photo)


@router.message(AddProductStates.waiting_for_old_price)
async def process_add_product_old_price(message: Message, state: FSMContext):
    price_str = message.text.strip()
    try:
        old_price = float(price_str)
    except ValueError:
        await message.answer("Введите корректное число:")
        return
        
    await state.update_data(old_price=old_price)
    await message.answer("Шаг 6 из 7: Отправьте <b>ссылку на фото товара</b> (или напишите «нет» для товара без фото):")
    await state.set_state(AddProductStates.waiting_for_photo)


@router.message(AddProductStates.waiting_for_photo)
async def process_add_product_photo(message: Message, state: FSMContext):
    photo = message.text.strip()
    if photo.lower() == "нет":
        photo = None
        
    await state.update_data(photo=photo)
    
    # Кнопки Да/Нет для наличия
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Да"), KeyboardButton(text="Нет")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Шаг 7 из 7: Товар <b>в наличии</b>?", reply_markup=kb, parse_mode="HTML")
    await state.set_state(AddProductStates.waiting_for_stock_status)


@router.message(AddProductStates.waiting_for_stock_status)
async def process_add_product_stock(message: Message, state: FSMContext):
    choice = message.text.strip().lower()
    stock_status = 1 if choice == "да" else 0
    
    data = await state.get_data()
    await state.clear()
    
    ProductRepository.add_product(
        shop_id=data['shop_id'],
        category=data['category'],
        name=data['name'],
        description=data['description'],
        price=data['price'],
        photo=data['photo'],
        stock_status=stock_status,
        is_discount=data['is_discount'],
        old_price=data.get('old_price')
    )
    
    main_menu = get_main_menu(message.from_user.id)
    await message.answer("✅ <b>Товар успешно добавлен в ваш магазин!</b>", reply_markup=main_menu, parse_mode="HTML")


# ==========================================
# ПРОСМОТР И УПРАВЛЕНИЕ ТОВАРАМИ ВЛАДЕЛЬЦЕМ
# ==========================================

def format_owner_product_text(product: dict) -> str:
    status_str = "✅ В наличии" if product['stock_status'] == 1 else "❌ Нет в наличии"
    price_text = f"Цена: {product['price']:,} сум"
    if product['is_discount']:
        price_text = f"Цена: {product['price']:,} сум (🔥 Скидка! Старая цена: {product['old_price']:,} сум)"
        
    text = (
        f"📦 <b>Товар: {product['name']}</b>\n"
        f"Категория: {product['category']}\n"
        f"Статус: {status_str}\n"
        f"{price_text}\n\n"
        f"📝 <b>Описание:</b>\n{product['description']}"
    )
    return text


@router.callback_query(F.data.startswith("own_list_products_"))
async def callback_own_list_products(callback: CallbackQuery):
    shop_id = int(callback.data.split("_")[3])
    products = ProductRepository.get_products_by_shop(shop_id)
    
    if not products:
        await callback.answer("В вашем магазине пока нет товаров.", show_alert=True)
        return
        
    product = products[0]
    text = format_owner_product_text(product)
    
    try:
        await callback.message.delete()
    except Exception:
        pass
        
    reply_markup = get_owner_products_nav_keyboard(product['id'], shop_id, 0, len(products))
    
    if product['photo']:
        await callback.message.answer_photo(photo=product['photo'], caption=text, reply_markup=reply_markup, parse_mode="HTML")
    else:
        await callback.message.answer(text, reply_markup=reply_markup, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("own_prod_nav_"))
async def callback_own_prod_nav(callback: CallbackQuery):
    _, _, _, shop_id_str, index_str = callback.data.split("_")
    shop_id = int(shop_id_str)
    index = int(index_str)
    
    products = ProductRepository.get_products_by_shop(shop_id)
    if not products or index >= len(products):
        await callback.answer("Ошибка навигации.", show_alert=True)
        return
        
    product = products[index]
    text = format_owner_product_text(product)
    reply_markup = get_owner_products_nav_keyboard(product['id'], shop_id, index, len(products))
    
    if product['photo']:
        media = InputMediaPhoto(media=product['photo'], caption=text, parse_mode="HTML")
        try:
            await callback.message.edit_media(media=media, reply_markup=reply_markup)
        except Exception:
            try:
                await callback.message.delete()
            except Exception:
                pass
            await callback.message.answer_photo(photo=product['photo'], caption=text, reply_markup=reply_markup, parse_mode="HTML")
    else:
        try:
            await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
        except Exception:
            try:
                await callback.message.delete()
            except Exception:
                pass
            await callback.message.answer(text, reply_markup=reply_markup, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("own_prod_avail_"))
async def callback_own_prod_avail(callback: CallbackQuery):
    parts = callback.data.split("_")
    product_id = int(parts[3])
    index = int(parts[4])
    
    product = ProductRepository.get_product_by_id(product_id)
    if not product:
        await callback.answer("Товар не найден.", show_alert=True)
        return
        
    # Переключаем статус
    new_status = 0 if product['stock_status'] == 1 else 1
    ProductRepository.update_product_stock(product_id, new_status)
    
    await callback.answer("Статус наличия успешно изменен!")
    
    # Обновляем сообщение
    product['stock_status'] = new_status
    text = format_owner_product_text(product)
    reply_markup = get_owner_products_nav_keyboard(product_id, product['shop_id'], index, len(ProductRepository.get_products_by_shop(product['shop_id'])))
    
    try:
        if product['photo']:
            await callback.message.edit_caption(caption=text, reply_markup=reply_markup, parse_mode="HTML")
        else:
            await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
    except Exception:
        pass


@router.callback_query(F.data.startswith("own_prod_del_"))
async def callback_own_prod_del(callback: CallbackQuery):
    parts = callback.data.split("_")
    product_id = int(parts[3])
    index = int(parts[4])
    
    product = ProductRepository.get_product_by_id(product_id)
    if not product:
        await callback.answer("Товар уже удален.", show_alert=True)
        return
        
    shop_id = product['shop_id']
    ProductRepository.delete_product(product_id)
    await callback.answer("Товар успешно удален!", show_alert=True)
    
    # Возвращаемся к списку товаров
    products = ProductRepository.get_products_by_shop(shop_id)
    if not products:
        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.message.answer("📦 В вашем магазине не осталось товаров.", reply_markup=get_shop_owner_dashboard_keyboard(shop_id))
        return
        
    new_index = index if index < len(products) else 0
    new_product = products[new_index]
    text = format_owner_product_text(new_product)
    reply_markup = get_owner_products_nav_keyboard(new_product['id'], shop_id, new_index, len(products))
    
    if new_product['photo']:
        media = InputMediaPhoto(media=new_product['photo'], caption=text, parse_mode="HTML")
        try:
            await callback.message.edit_media(media=media, reply_markup=reply_markup)
        except Exception:
            try:
                await callback.message.delete()
            except Exception:
                pass
            await callback.message.answer_photo(photo=new_product['photo'], caption=text, reply_markup=reply_markup, parse_mode="HTML")
    else:
        try:
            await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
        except Exception:
            try:
                await callback.message.delete()
            except Exception:
                pass
            await callback.message.answer(text, reply_markup=reply_markup, parse_mode="HTML")


# ==========================================
# ИЗМЕНЕНИЕ ЦЕНЫ ТОВАРА (FSM)
# ==========================================

@router.callback_query(F.data.startswith("own_prod_price_"))
async def callback_own_prod_price_start(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    product_id = int(parts[3])
    index = int(parts[4])
    
    await state.clear()
    await state.update_data(product_id=product_id, index=index)
    
    await callback.message.answer("✏️ <b>Введите новую цену для товара (только число, в сум):</b>", parse_mode="HTML")
    await state.set_state(UpdatePriceStates.waiting_for_new_price)
    await callback.answer()


@router.message(UpdatePriceStates.waiting_for_new_price)
async def process_own_prod_new_price(message: Message, state: FSMContext):
    price_str = message.text.strip()
    try:
        new_price = float(price_str)
        if new_price <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число цены:")
        return
        
    data = await state.get_data()
    await state.clear()
    
    product = ProductRepository.get_product_by_id(data['product_id'])
    if not product:
        await message.answer("Товар не найден.")
        return
        
    ProductRepository.update_product_price(data['product_id'], new_price)
    await message.answer(f"✅ Цена товара «{product['name']}» успешно обновлена на {new_price:,} сум!")


# ==========================================
# УПРАВЛЕНИЕ СКИДКОЙ
# ==========================================

@router.callback_query(F.data.startswith("own_prod_discount_"))
async def callback_own_prod_discount(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    product_id = int(parts[3])
    index = int(parts[4])
    
    product = ProductRepository.get_product_by_id(product_id)
    if not product:
        await callback.answer("Товар не найден.", show_alert=True)
        return
        
    if product['is_discount'] == 1:
        # Убираем скидку
        ProductRepository.update_product_discount(product_id, 0, None)
        await callback.answer("Скидка отключена.")
        
        # Обновляем карточку
        product['is_discount'] = 0
        product['old_price'] = None
        text = format_owner_product_text(product)
        reply_markup = get_owner_products_nav_keyboard(product_id, product['shop_id'], index, len(ProductRepository.get_products_by_shop(product['shop_id'])))
        try:
            if product['photo']:
                await callback.message.edit_caption(caption=text, reply_markup=reply_markup, parse_mode="HTML")
            else:
                await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
        except Exception:
            pass
    else:
        # Запрашиваем старую цену для скидки
        await state.clear()
        await state.update_data(product_id=product_id, index=index)
        
        # По сути, новая цена будет текущей ценой товара, а старая цена будет той, которую мы зачеркнем.
        await callback.message.answer(
            f"Введите <b>старую цену</b> для товара «{product['name']}» (которая будет зачеркнута):\n"
            f"<i>Текущая цена: {product['price']:,} сум. Старая цена должна быть больше текущей.</i>",
            parse_mode="HTML"
        )
        # Мы можем использовать состояние UpdatePriceStates для ввода старой цены скидки, но лучше сделать простую ветку в хендлере.
        # Давайте создадим временное состояние в FSM
        await state.set_state(AddProductStates.waiting_for_old_price)
        await callback.answer()


@router.message(AddProductStates.waiting_for_old_price)
async def process_own_prod_discount_old_price(message: Message, state: FSMContext):
    # Данный хендлер может перехватывать ввод старой цены и для редактирования
    state_data = await state.get_data()
    if 'product_id' not in state_data:
        # Если это было добавление товара, FSM идет по своему пути
        return
        
    price_str = message.text.strip()
    try:
        old_price = float(price_str)
    except ValueError:
        await message.answer("Введите число:")
        return
        
    product_id = state_data['product_id']
    await state.clear()
    
    product = ProductRepository.get_product_by_id(product_id)
    if not product:
        await message.answer("Товар не найден.")
        return
        
    ProductRepository.update_product_discount(product_id, 1, old_price)
    await message.answer(f"✅ Товар «{product['name']}» теперь продается со скидкой! Старая цена: {old_price:,} сум.")


# ==========================================
# УПРАВЛЕНИЕ ЗАКАЗАМИ МАГАЗИНА (SHOP_OWNER)
# ==========================================

@router.callback_query(F.data.startswith("own_list_orders_"))
async def callback_own_list_orders(callback: CallbackQuery):
    shop_id = int(callback.data.split("_")[3])
    
    orders = OrderRepository.get_orders_by_shop(shop_id)
    if not orders:
        await callback.answer("В вашем магазине пока нет заказов.", show_alert=True)
        return
        
    # Выводим первую страницу заказов (по 6 штук на страницу)
    PAGE_SIZE = 6
    total_pages = (len(orders) + PAGE_SIZE - 1) // PAGE_SIZE
    
    page_orders = orders[0:PAGE_SIZE]
    reply_markup = get_owner_orders_list_keyboard(page_orders, shop_id, 0, total_pages)
    
    text = f"📥 <b>Список заказов вашего магазина (Всего: {len(orders)}):</b>"
    
    try:
        await callback.message.delete()
    except Exception:
        pass
        
    await callback.message.answer(text, reply_markup=reply_markup, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("own_orders_page_"))
async def callback_own_orders_page(callback: CallbackQuery):
    _, _, _, shop_id_str, page_str = callback.data.split("_")
    shop_id = int(shop_id_str)
    page = int(page_str)
    
    orders = OrderRepository.get_orders_by_shop(shop_id)
    PAGE_SIZE = 6
    total_pages = (len(orders) + PAGE_SIZE - 1) // PAGE_SIZE
    
    if page >= total_pages:
        page = 0
        
    start_idx = page * PAGE_SIZE
    page_orders = orders[start_idx:start_idx+PAGE_SIZE]
    reply_markup = get_owner_orders_list_keyboard(page_orders, shop_id, page, total_pages)
    
    text = f"📥 <b>Список заказов вашего магазина (Всего: {len(orders)}):</b>"
    try:
        await callback.message.edit_reply_markup(reply_markup=reply_markup)
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data.startswith("own_order_detail_"))
async def callback_own_order_detail(callback: CallbackQuery):
    order_id = int(callback.data.split("_")[3])
    order = OrderRepository.get_order_by_id(order_id)
    
    if not order:
        await callback.answer("Заказ не найден.", show_alert=True)
        return
        
    text = (
        f"📝 <b>Детали заказа #{order['id']}</b>\n\n"
        f"👤 <b>Покупатель:</b> {order['full_name']}\n"
        f"📞 <b>Телефон:</b> {order['phone']}\n"
        f"📍 <b>Адрес доставки:</b> {order['address']}\n\n"
        f"📦 <b>Товар:</b> {order['product_name']}\n"
        f"💰 <b>Цена товара:</b> {order['product_price']:,} сум\n"
        f"⏱ <b>Статус:</b> {order['status']}\n"
        f"📅 <b>Дата создания:</b> {order['created_at']}\n"
    )
    
    reply_markup = get_owner_order_status_keyboard(order_id, order['shop_id'])
    
    try:
        await callback.message.delete()
    except Exception:
        pass
        
    await callback.message.answer(text, reply_markup=reply_markup, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("own_status_menu_"))
async def callback_own_status_menu(callback: CallbackQuery):
    order_id = int(callback.data.split("_")[3])
    order = OrderRepository.get_order_by_id(order_id)
    if not order:
        await callback.answer("Заказ не найден.", show_alert=True)
        return
        
    reply_markup = get_owner_order_status_keyboard(order_id, order['shop_id'])
    await callback.message.edit_reply_markup(reply_markup=reply_markup)
    await callback.answer()


@router.callback_query(F.data.startswith("own_change_status_"))
async def callback_own_change_status(callback: CallbackQuery, bot: Bot):
    parts = callback.data.split("_")
    order_id = int(parts[3])
    new_status = parts[4]
    
    order = OrderRepository.get_order_by_id(order_id)
    if not order:
        await callback.answer("Заказ не найден.", show_alert=True)
        return
        
    # Обновляем в БД
    info = OrderRepository.update_order_status(order_id, new_status)
    if info:
        user_id, shop_id = info
        # Отправляем уведомление клиенту
        await notify_status_change(bot, order_id, new_status, user_id, shop_id)
        
    await callback.answer(f"Статус заказа #{order_id} изменен на «{new_status}»!", show_alert=True)
    
    # Возвращаемся к просмотру деталей заказа
    updated_order = OrderRepository.get_order_by_id(order_id)
    text = (
        f"📝 <b>Детали заказа #{updated_order['id']}</b>\n\n"
        f"👤 <b>Покупатель:</b> {updated_order['full_name']}\n"
        f"📞 <b>Телефон:</b> {updated_order['phone']}\n"
        f"📍 <b>Адрес доставки:</b> {updated_order['address']}\n\n"
        f"📦 <b>Товар:</b> {updated_order['product_name']}\n"
        f"💰 <b>Цена товара:</b> {updated_order['product_price']:,} сум\n"
        f"⏱ <b>Статус:</b> {updated_order['status']}\n"
        f"📅 <b>Дата создания:</b> {updated_order['created_at']}\n"
    )
    
    reply_markup = get_owner_order_status_keyboard(order_id, updated_order['shop_id'])
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
    except Exception:
        pass


# ==========================================
# ЭКСПОРТ В CSV
# ==========================================

@router.callback_query(F.data.startswith("own_export_csv_"))
async def callback_own_export_csv(callback: CallbackQuery):
    shop_id = int(callback.data.split("_")[3])
    
    csv_bytes = export_shop_orders_to_csv(shop_id)
    shop = ShopRepository.get_shop_by_id(shop_id)
    filename = f"orders_shop_{shop_id}.csv"
    if shop:
        filename = f"orders_{shop['name'].replace(' ', '_')}.csv"
        
    csv_file = BufferedInputFile(csv_bytes, filename=filename)
    
    try:
        await callback.message.answer_document(
            document=csv_file,
            caption=f"📋 Выгрузка всех заказов магазина «{shop['name'] if shop else shop_id}» в формате CSV."
        )
        await callback.answer("Файл отправлен!")
    except Exception as e:
        await callback.answer("Ошибка при отправке файла.", show_alert=True)
        print(f"Ошибка экспорта: {e}")


# ==========================================
# СТАТИСТИКА МАГАЗИНА
# ==========================================

@router.callback_query(F.data.startswith("own_stats_"))
async def callback_own_stats(callback: CallbackQuery):
    shop_id = int(callback.data.split("_")[2])
    shop = ShopRepository.get_shop_by_id(shop_id)
    if not shop:
        await callback.answer("Магазин не найден.", show_alert=True)
        return
        
    stats = get_shop_owner_stats(shop_id)
    
    text = (
        f"📊 <b>Статистика магазина «{shop['name']}»:</b>\n\n"
        f"📦 Всего товаров: {stats['products_count']}\n"
        f"📥 Всего заказов: {stats['orders_count']}\n"
        f"🎉 Завершенных заказов: {stats['completed_orders_count']}\n"
    )
    
    keyboard = get_shop_owner_dashboard_keyboard(shop_id)
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()
