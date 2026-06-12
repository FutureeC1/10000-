import logging
# pyrefly: ignore [missing-import]
from aiogram import Router, F, Bot
# pyrefly: ignore [missing-import]
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.filters import Command, BaseFilter
from aiogram.fsm.context import FSMContext

from config.config import ADMIN_ID
from database.repositories import UserRepository, ProductRepository, OrderRepository
from bot.keyboards.inline import (
    get_admin_main_keyboard,
    get_admin_products_nav_keyboard,
    get_admin_order_status_keyboard,
    get_admin_orders_list_keyboard
)
from bot.keyboards.reply import get_main_menu
from bot.states.admin_states import AddProductStates, UpdatePriceStates, BroadcastStates
from services.stats_service import get_admin_stats
from services.order_service import notify_status_change, export_orders_to_csv
from aiogram.types import BufferedInputFile

router = Router()

class AdminFilter(BaseFilter):
    """Фильтр для проверки прав администратора."""
    async def __call__(self, obj) -> bool:
        user_id = obj.from_user.id
        return ADMIN_ID is not None and user_id == ADMIN_ID


# Применяем фильтр ко всем хендлерам роутера
router.message.filter(AdminFilter())
router.callback_query.filter(AdminFilter())


@router.message(Command("admin"))
@router.message(F.text == "⚙️ Админ-панель")
async def cmd_admin(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "⚙️ <b>Панель администратора магазина Keyllect</b>\n\n"
        "Выберите необходимое действие на клавиатуре ниже:",
        reply_markup=get_admin_main_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "adm_back")
async def callback_admin_back(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(
        "⚙️ <b>Панель администратора магазина Keyllect</b>\n\n"
        "Выберите необходимое действие на клавиатуре ниже:",
        reply_markup=get_admin_main_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


# ==========================================
# СТАТИСТИКА
# ==========================================

@router.message(Command("stats"))
@router.callback_query(F.data == "adm_stats")
async def cmd_stats(event, state: FSMContext):
    await state.clear()
    stats = get_admin_stats()
    
    text = (
        "📊 <b>Статистика магазина Keyllect:</b>\n\n"
        f"👥 <b>Всего клиентов:</b> {stats['clients_count']}\n"
        f"📦 <b>Всего товаров:</b> {stats['products_count']}\n"
        f"🛒 <b>Всего заказов:</b> {stats['orders_count']}\n"
        f"🎉 <b>Завершенных заказов:</b> {stats['completed_orders_count']}\n"
    )
    
    if isinstance(event, CallbackQuery):
        await event.message.answer(text, reply_markup=get_admin_main_keyboard(), parse_mode="HTML")
        await event.answer()
    else:
        await event.answer(text, reply_markup=get_admin_main_keyboard(), parse_mode="HTML")


# ==========================================
# ДОБАВЛЕНИЕ ТОВАРА (FSM)
# ==========================================

@router.callback_query(F.data == "adm_add_product")
async def start_add_product(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    categories = ProductRepository.get_categories()
    
    cat_text = ""
    if categories:
        cat_text = "Доступные категории:\n" + "\n".join(f"• <code>{c}</code>" for c in categories) + "\n\n"
        
    await callback.message.answer(
        "➕ <b>Добавление нового товара</b>\n\n"
        f"{cat_text}"
        "Введите <b>категорию</b> товара (например: Клавиатуры, Мышки, Наушники, Коврики):",
        parse_mode="HTML"
    )
    await state.set_state(AddProductStates.waiting_for_category)
    await callback.answer()


@router.message(AddProductStates.waiting_for_category)
async def process_add_category(message: Message, state: FSMContext):
    category = message.text.strip()
    await state.update_data(category=category)
    await message.answer("Введите <b>название</b> товара:")
    await state.set_state(AddProductStates.waiting_for_name)


@router.message(AddProductStates.waiting_for_name)
async def process_add_name(message: Message, state: FSMContext):
    name = message.text.strip()
    await state.update_data(name=name)
    await message.answer("Введите <b>описание</b> товара:")
    await state.set_state(AddProductStates.waiting_for_description)


@router.message(AddProductStates.waiting_for_description)
async def process_add_desc(message: Message, state: FSMContext):
    desc = message.text.strip()
    await state.update_data(description=desc)
    await message.answer("Введите <b>цену</b> товара (только число, в сум):")
    await state.set_state(AddProductStates.waiting_for_price)


@router.message(AddProductStates.waiting_for_price)
async def process_add_price(message: Message, state: FSMContext):
    try:
        price = float(message.text.strip().replace(" ", ""))
    except ValueError:
        await message.answer("Некорректная цена. Введите число:")
        return
        
    await state.update_data(price=price)
    
    # Спрашиваем про акцию
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Да"), KeyboardButton(text="Нет")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Сделать товар <b>акционным</b> (со скидкой)?", reply_markup=kb, parse_mode="HTML")
    await state.set_state(AddProductStates.waiting_for_is_discount)


@router.message(AddProductStates.waiting_for_is_discount)
async def process_add_is_discount(message: Message, state: FSMContext):
    choice = message.text.strip().lower()
    
    # Возвращаем главное меню Reply
    main_menu_kb = get_main_menu(message.from_user.id)
    
    if choice == "да":
        await state.update_data(is_discount=1)
        await message.answer("Введите <b>старую цену</b> товара (которая будет зачеркнута):", reply_markup=main_menu_kb)
        await state.set_state(AddProductStates.waiting_for_old_price)
    else:
        await state.update_data(is_discount=0, old_price=None)
        await message.answer(
            "Отправьте <b>фото товара</b> (или вставьте прямую ссылку на изображение, либо напишите «нет» для создания товара без фото):",
            reply_markup=main_menu_kb
        )
        await state.set_state(AddProductStates.waiting_for_photo)


@router.message(AddProductStates.waiting_for_old_price)
async def process_add_old_price(message: Message, state: FSMContext):
    try:
        old_price = float(message.text.strip().replace(" ", ""))
    except ValueError:
        await message.answer("Некорректная цена. Введите число:")
        return
        
    await state.update_data(old_price=old_price)
    await message.answer("Отправьте <b>фото товара</b> (картинкой в чат, или вставьте ссылку, либо напишите «нет»):")
    await state.set_state(AddProductStates.waiting_for_photo)


@router.message(AddProductStates.waiting_for_photo)
async def process_add_photo(message: Message, state: FSMContext):
    photo = None
    if message.photo:
        photo = message.photo[-1].file_id
    elif message.text and message.text.strip().lower() != "нет":
        photo = message.text.strip()
        
    await state.update_data(photo=photo)
    
    # Спрашиваем наличие
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="В наличии"), KeyboardButton(text="Нет в наличии")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Укажите статус <b>наличия</b> товара:", reply_markup=kb, parse_mode="HTML")
    await state.set_state(AddProductStates.waiting_for_is_available)


@router.message(AddProductStates.waiting_for_is_available)
async def process_add_is_available(message: Message, state: FSMContext):
    choice = message.text.strip().lower()
    is_available = 1 if "в наличии" in choice else 0
    await state.update_data(is_available=is_available)
    
    data = await state.get_data()
    await state.clear()
    
    # Сохраняем в БД
    product_id = ProductRepository.add_product(
        category=data['category'],
        name=data['name'],
        description=data['description'],
        price=data['price'],
        photo=data['photo'],
        is_discount=data['is_discount'],
        old_price=data.get('old_price'),
        is_available=data['is_available']
    )
    
    # Возвращаем главное меню
    main_menu_kb = get_main_menu(message.from_user.id)
    await message.answer(
        f"✅ <b>Товар успешно добавлен (ID: {product_id})!</b>", 
        reply_markup=main_menu_kb, 
        parse_mode="HTML"
    )
    
    # Показываем карточку созданного товара
    status_str = "✅ В наличии" if data['is_available'] else "❌ Нет в наличии"
    price_text = f"Цена: {data['price']:,} сум"
    if data['is_discount']:
        price_text = f"🔥 Скидка!\n<s>Старая цена: {data.get('old_price'):,} сум</s>\nНовая цена: {data['price']:,} сум"
        
    text = (
        f"📦 <b>Новый товар добавлен в каталог:</b>\n\n"
        f"🎮 {data['name']}\n"
        f"Категория: {data['category']}\n"
        f"Статус: {status_str}\n"
        f"Описание: {data['description']}\n"
        f"{price_text}"
    )
    
    if data['photo']:
        await message.answer_photo(photo=data['photo'], caption=text, reply_markup=get_admin_main_keyboard(), parse_mode="HTML")
    else:
        await message.answer(text, reply_markup=get_admin_main_keyboard(), parse_mode="HTML")


# ==========================================
# УПРАВЛЕНИЕ ТОВАРАМИ (Каталог админа)
# ==========================================

def format_admin_product_text(product: dict) -> str:
    status_str = "✅ В наличии" if product['is_available'] else "❌ Нет в наличии"
    price_text = f"Цена: {product['price']:,} сум"
    if product['is_discount']:
        price_text = f"🔥 Скидка!\n<s>Старая цена: {product['old_price']:,} сум</s>\nНовая цена: {product['price']:,} сум"
        
    text = (
        f"🛠 <b>Управление товаром (ID: {product['id']})</b>\n\n"
        f"🎮 <b>{product['name']}</b>\n"
        f"Категория: {product['category']}\n"
        f"Наличие: {status_str}\n\n"
        f"📝 <b>Описание:</b>\n{product['description']}\n\n"
        f"{price_text}"
    )
    return text


@router.callback_query(F.data == "adm_manage_products")
async def callback_manage_products(callback: CallbackQuery):
    products = ProductRepository.get_all_products()
    if not products:
        await callback.answer("В базе данных нет товаров.", show_alert=True)
        return
        
    product = products[0]
    text = format_admin_product_text(product)
    reply_markup = get_admin_products_nav_keyboard(product['id'], 0, len(products))
    
    try:
        await callback.message.delete()
    except Exception:
        pass
        
    if product['photo']:
        await callback.message.answer_photo(photo=product['photo'], caption=text, reply_markup=reply_markup, parse_mode="HTML")
    else:
        await callback.message.answer(text, reply_markup=reply_markup, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("adm_prod_nav_"))
async def callback_admin_prod_nav(callback: CallbackQuery):
    index = int(callback.data.split("_")[3])
    products = ProductRepository.get_all_products()
    
    if not products:
        await callback.message.edit_text("Товары отсутствуют.")
        await callback.answer()
        return
        
    product = products[index % len(products)]
    text = format_admin_product_text(product)
    reply_markup = get_admin_products_nav_keyboard(product['id'], index, len(products))
    
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


@router.callback_query(F.data.startswith("adm_prod_avail_"))
async def callback_admin_prod_avail(callback: CallbackQuery):
    parts = callback.data.split("_")
    product_id = int(parts[3])
    index = int(parts[4])
    
    product = ProductRepository.get_product_by_id(product_id)
    if not product:
        await callback.answer("Товар не найден", show_alert=True)
        return
        
    new_avail = 0 if product['is_available'] else 1
    ProductRepository.update_product_availability(product_id, new_avail)
    await callback.answer(f"Статус наличия изменен!")
    
    # Обновляем карточку
    product = ProductRepository.get_product_by_id(product_id)
    text = format_admin_product_text(product)
    reply_markup = get_admin_products_nav_keyboard(product_id, index, len(ProductRepository.get_all_products()))
    
    try:
        await callback.message.edit_caption(caption=text, reply_markup=reply_markup, parse_mode="HTML")
    except Exception:
        try:
            await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
        except Exception:
            pass


@router.callback_query(F.data.startswith("adm_prod_discount_"))
async def callback_admin_prod_discount(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    product_id = int(parts[3])
    index = int(parts[4])
    
    product = ProductRepository.get_product_by_id(product_id)
    if not product:
        await callback.answer("Товар не найден", show_alert=True)
        return
        
    if product['is_discount']:
        # Если скидка есть - отключаем её
        ProductRepository.update_product_discount(product_id, 0, None)
        await callback.answer("Скидка отключена")
        
        # Обновляем карточку
        product = ProductRepository.get_product_by_id(product_id)
        text = format_admin_product_text(product)
        reply_markup = get_admin_products_nav_keyboard(product_id, index, len(ProductRepository.get_all_products()))
        try:
            await callback.message.edit_caption(caption=text, reply_markup=reply_markup, parse_mode="HTML")
        except Exception:
            try:
                await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
            except Exception:
                pass
    else:
        # Если скидки нет - запрашиваем старую цену
        await state.update_data(product_id=product_id, index=index)
        await callback.message.answer(
            f"Установим скидку для <b>{product['name']}</b>.\n"
            f"Текущая цена: <code>{product['price']:,} сум</code>.\n"
            f"Введите <b>старую цену</b> (зачеркнутую):",
            parse_mode="HTML"
        )
        await state.set_state(AddProductStates.waiting_for_old_price) # переиспользуем стейт
        await callback.answer()


# Хендлер ввода старой цены при обновлении скидки
@router.message(AddProductStates.waiting_for_old_price)
async def process_update_old_price(message: Message, state: FSMContext):
    state_data = await state.get_data()
    if 'product_id' not in state_data:
        # Это было добавление товара, а не редактирование
        return
        
    product_id = state_data['product_id']
    index = state_data['index']
    
    try:
        old_price = float(message.text.strip().replace(" ", ""))
    except ValueError:
        await message.answer("Некорректная цена. Введите число:")
        return
        
    await state.clear()
    
    ProductRepository.update_product_discount(product_id, 1, old_price)
    await message.answer("🔥 Скидка успешно установлена!")
    
    # Показываем карточку товара
    product = ProductRepository.get_product_by_id(product_id)
    text = format_admin_product_text(product)
    reply_markup = get_admin_products_nav_keyboard(product_id, index, len(ProductRepository.get_all_products()))
    
    if product['photo']:
        await message.answer_photo(photo=product['photo'], caption=text, reply_markup=reply_markup, parse_mode="HTML")
    else:
        await message.answer(text, reply_markup=reply_markup, parse_mode="HTML")


@router.callback_query(F.data.startswith("adm_prod_price_"))
async def callback_admin_prod_price_start(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    product_id = int(parts[3])
    index = int(parts[4])
    
    product = ProductRepository.get_product_by_id(product_id)
    if not product:
        await callback.answer("Товар не найден", show_alert=True)
        return
        
    await state.update_data(product_id=product_id, index=index)
    await callback.message.answer(
        f"Редактирование цены для <b>{product['name']}</b>.\n"
        f"Текущая цена: <code>{product['price']:,} сум</code>.\n"
        f"Введите <b>новую цену</b>:",
        parse_mode="HTML"
    )
    await state.set_state(UpdatePriceStates.waiting_for_new_price)
    await callback.answer()


@router.message(UpdatePriceStates.waiting_for_new_price)
async def process_update_price(message: Message, state: FSMContext):
    data = await state.get_data()
    product_id = data['product_id']
    index = data['index']
    
    try:
        new_price = float(message.text.strip().replace(" ", ""))
    except ValueError:
        await message.answer("Некорректная цена. Введите число:")
        return
        
    await state.clear()
    ProductRepository.update_product_price(product_id, new_price)
    await message.answer("✅ Цена товара успешно обновлена!")
    
    product = ProductRepository.get_product_by_id(product_id)
    text = format_admin_product_text(product)
    reply_markup = get_admin_products_nav_keyboard(product_id, index, len(ProductRepository.get_all_products()))
    
    if product['photo']:
        await message.answer_photo(photo=product['photo'], caption=text, reply_markup=reply_markup, parse_mode="HTML")
    else:
        await message.answer(text, reply_markup=reply_markup, parse_mode="HTML")


@router.callback_query(F.data.startswith("adm_prod_del_"))
async def callback_admin_prod_delete(callback: CallbackQuery):
    parts = callback.data.split("_")
    product_id = int(parts[3])
    index = int(parts[4])
    
    ProductRepository.delete_product(product_id)
    await callback.answer("🗑 Товар удален")
    
    products = ProductRepository.get_all_products()
    if not products:
        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.message.answer("Все товары удалены из базы данных.", reply_markup=get_admin_main_keyboard())
        return
        
    new_index = index if index < len(products) else 0
    product = products[new_index]
    text = format_admin_product_text(product)
    reply_markup = get_admin_products_nav_keyboard(product['id'], new_index, len(products))
    
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


# ==========================================
# УПРАВЛЕНИЕ ЗАКАЗАМИ
# ==========================================

@router.callback_query(F.data == "adm_list_orders")
@router.callback_query(F.data.startswith("adm_orders_page_"))
async def callback_list_orders(callback: CallbackQuery):
    page = 0
    if callback.data.startswith("adm_orders_page_"):
        page = int(callback.data.split("_")[3])
        
    orders = OrderRepository.get_all_orders()
    if not orders:
        await callback.answer("Заказы в системе отсутствуют.", show_alert=True)
        return
        
    orders_per_page = 5
    total_pages = (len(orders) + orders_per_page - 1) // orders_per_page
    page = page % total_pages
    
    start_idx = page * orders_per_page
    end_idx = start_idx + orders_per_page
    page_orders = orders[start_idx:end_idx]
    
    text = (
        f"📦 <b>Список заказов (Страница {page + 1} из {total_pages})</b>\n"
        f"Всего заказов в системе: {len(orders)}\n\n"
        "Нажмите на кнопку заказа, чтобы открыть детальное управление или изменить статус:"
    )
    
    reply_markup = get_admin_orders_list_keyboard(page_orders, page, total_pages)
    
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
    except Exception:
        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.message.answer(text, reply_markup=reply_markup, parse_mode="HTML")
        
    await callback.answer()


@router.callback_query(F.data.startswith("adm_order_detail_"))
async def callback_order_detail(callback: CallbackQuery):
    order_id = int(callback.data.split("_")[3])
    order = OrderRepository.get_order_by_id(order_id)
    
    if not order:
        await callback.answer("Заказ не найден.", show_alert=True)
        return
        
    price_str = f"{order['product_price']:,} сум"
    
    text = (
        f"🔍 <b>Детали заказа #{order['id']}</b>\n\n"
        f"👤 <b>ФИО получателя:</b> {order['full_name']}\n"
        f"📞 <b>Телефон:</b> {order['phone']}\n"
        f"📍 <b>Адрес доставки:</b> {order['address']}\n\n"
        f"📦 <b>Товар:</b> {order['product_name']}\n"
        f"💰 <b>Сумма:</b> {price_str}\n"
        f"⏱ <b>Текущий статус:</b> {order['status']}\n"
        f"📅 <b>Дата создания:</b> {order['created_at']}\n\n"
        "Выберите новый статус для заказа ниже:"
    )
    
    reply_markup = get_admin_order_status_keyboard(order_id)
    
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
    except Exception:
        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.message.answer(text, reply_markup=reply_markup, parse_mode="HTML")
        
    await callback.answer()


@router.callback_query(F.data.startswith("adm_status_menu_"))
async def callback_status_menu(callback: CallbackQuery):
    order_id = int(callback.data.split("_")[3])
    reply_markup = get_admin_order_status_keyboard(order_id)
    
    try:
        await callback.message.edit_reply_markup(reply_markup=reply_markup)
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data.startswith("adm_change_status_"))
async def callback_change_status(callback: CallbackQuery, bot: Bot):
    parts = callback.data.split("_")
    order_id = int(parts[3])
    new_status = parts[4]
    
    # Обновляем статус
    user_id = OrderRepository.update_order_status(order_id, new_status)
    await callback.answer(f"Статус изменен на '{new_status}'")
    
    # Уведомляем клиента
    if user_id:
        await notify_status_change(bot, order_id, new_status, user_id)
        
    # Возвращаемся к деталям заказа
    order = OrderRepository.get_order_by_id(order_id)
    price_str = f"{order['product_price']:,} сум"
    text = (
        f"🔍 <b>Детали заказа #{order['id']} (Статус обновлен!)</b>\n\n"
        f"👤 <b>ФИО получателя:</b> {order['full_name']}\n"
        f"📞 <b>Телефон:</b> {order['phone']}\n"
        f"📍 <b>Адрес доставки:</b> {order['address']}\n\n"
        f"📦 <b>Товар:</b> {order['product_name']}\n"
        f"💰 <b>Сумма:</b> {price_str}\n"
        f"⏱ <b>Текущий статус:</b> {order['status']}\n"
        f"📅 <b>Дата создания:</b> {order['created_at']}\n\n"
        "Выберите новый статус для заказа ниже:"
    )
    reply_markup = get_admin_order_status_keyboard(order_id)
    
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
    except Exception:
        pass


# ==========================================
# ЭКСПОРТ В CSV
# ==========================================

@router.message(Command("export"))
async def cmd_export_orders(message: Message):
    csv_bytes = export_orders_to_csv()
    if not csv_bytes:
        await message.answer("Заказы для экспорта отсутствуют.")
        return
        
    file = BufferedInputFile(csv_bytes, filename="keyllect_orders.csv")
    await message.answer_document(file, caption="📊 <b>Выгрузка всех заказов магазина (CSV)</b>", parse_mode="HTML")


# ==========================================
# РАССЫЛКА (FSM)
# ==========================================

@router.callback_query(F.data == "adm_broadcast")
@router.message(Command("broadcast"))
async def start_broadcast(event, state: FSMContext):
    await state.clear()
    text = (
        "📢 <b>Создание массовой рассылки</b>\n\n"
        "Введите текст сообщения, которое увидят все клиенты бота.\n"
        "Вы можете использовать HTML-разметку (например, &lt;b&gt;жирный&lt;/b&gt;)."
    )
    
    if isinstance(event, CallbackQuery):
        await event.message.answer(text, parse_mode="HTML")
        await event.answer()
    else:
        await event.answer(text, parse_mode="HTML")
        
    await state.set_state(BroadcastStates.waiting_for_message)


@router.message(BroadcastStates.waiting_for_message)
async def process_broadcast_message(message: Message, state: FSMContext, bot: Bot):
    broadcast_text = message.text.strip()
    await state.clear()
    
    if not broadcast_text:
        await message.answer("Текст сообщения пуст. Рассылка отменена.")
        return
        
    users = UserRepository.get_all_users()
    if not users:
        await message.answer("В базе данных нет пользователей для рассылки.")
        return
        
    await message.answer(f"⏳ Начинаю рассылку для {len(users)} пользователей...")
    
    success_count = 0
    for user_id in users:
        try:
            await bot.send_message(
                chat_id=user_id,
                text=f"📢 <b>Уведомление от Keyllect:</b>\n\n{broadcast_text}",
                parse_mode="HTML"
            )
            success_count += 1
        except Exception as e:
            logging.debug(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
            
    await message.answer(
        f"✅ <b>Рассылка завершена!</b>\n\n"
        f"Успешно доставлено: {success_count} из {len(users)}",
        reply_markup=get_admin_main_keyboard(),
        parse_mode="HTML"
    )
