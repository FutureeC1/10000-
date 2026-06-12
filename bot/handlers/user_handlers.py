import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from config.config import MANAGER_USERNAME
from database.repositories import UserRepository, ShopRepository, ProductRepository, OrderRepository, FavoriteRepository
from bot.keyboards.reply import get_main_menu, get_shop_menu_keyboard
from bot.keyboards.inline import (
    get_shops_list_keyboard,
    get_shop_categories_keyboard,
    get_product_detail_keyboard,
    get_favorites_keyboard,
    get_confirm_order_keyboard,
    get_support_keyboard
)
from bot.states.user_states import OrderStates, SearchStates
from services.order_service import create_new_order

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name
    
    # Регистрируем пользователя
    UserRepository.add_user(user_id, username, full_name)
    
    shops = ShopRepository.get_all_shops()
    if not shops:
        await message.answer(
            "👋 <b>Добро пожаловать!</b>\n\n"
            "🏪 В системе пока нет зарегистрированных магазинов. Загляните позже!",
            reply_markup=get_main_menu(user_id),
            parse_mode="HTML"
        )
        return
        
    text = (
        "👋 <b>Добро пожаловать в мульти-магазинную платформу!</b>\n\n"
        "Выберите магазин из списка ниже, чтобы перейти в его каталог:"
    )
    await message.answer(text, reply_markup=get_shops_list_keyboard(shops), parse_mode="HTML")



@router.message(F.text == "🏪 Магазины")
@router.message(Command("shops"))
async def cmd_shops(message: Message):
    shops = ShopRepository.get_all_shops()
    if not shops:
        await message.answer("😔 В системе пока нет зарегистрированных магазинов. Загляните позже!")
        return
        
    text = (
        "🏪 <b>Список доступных магазинов:</b>\n\n"
        "Выберите магазин из списка ниже, чтобы перейти в его каталог:"
    )
    await message.answer(text, reply_markup=get_shops_list_keyboard(shops), parse_mode="HTML")


@router.callback_query(F.data == "back_to_shops")
async def callback_back_to_shops(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    shops = ShopRepository.get_all_shops()
    if not shops:
        await callback.message.edit_text("😔 В системе пока нет зарегистрированных магазинов. Загляните позже!")
        return
        
    text = (
        "🏪 <b>Список доступных магазинов:</b>\n\n"
        "Выберите магазин из списка ниже, чтобы перейти в его каталог:"
    )
    try:
        await callback.message.delete()
    except Exception:
        pass
        
    # Восстанавливаем главное меню
    await callback.message.answer("Вы вышли из магазина.", reply_markup=get_main_menu(callback.from_user.id))
    await callback.message.answer(text, reply_markup=get_shops_list_keyboard(shops), parse_mode="HTML")
    await callback.answer()



@router.callback_query(F.data.startswith("selectshop_"))
@router.callback_query(F.data.startswith("back_to_categories_"))
async def callback_select_shop(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    shop_id = int(parts[1]) if parts[0] == "selectshop" else int(parts[3])
    
    # Сохраняем текущий просматриваемый магазин в состояние
    await state.update_data(current_shop_id=shop_id)
    
    shop = ShopRepository.get_shop_by_id(shop_id)
    if not shop:
        await callback.answer("Магазин не найден.", show_alert=True)
        return
        
    categories = ProductRepository.get_categories_by_shop(shop_id)
    if not categories:
        await callback.answer("В этом магазине пока нет товаров.", show_alert=True)
        return
        
    text = (
        f"🏪 <b>Магазин: {shop['name']}</b>\n"
        f"📝 {shop['description'] or 'Описание отсутствует.'}\n\n"
        f"📁 <b>Выберите категорию товаров на клавиатуре внизу!</b>"
    )
    
    try:
        await callback.message.delete()
    except Exception:
        pass
        
    reply_markup = get_shop_menu_keyboard(categories)
    
    if shop['logo']:
        await callback.message.answer_photo(
            photo=shop['logo'],
            caption=text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    else:
        await callback.message.answer(
            text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    await callback.answer()




def format_product_text(product: dict, shop_name: str) -> str:
    status_str = "✅ В наличии" if product['stock_status'] == 1 else "❌ Нет в наличии"
    
    price_text = ""
    if product['is_discount']:
        price_text = (
            f"🔥 <b>Скидка!</b>\n"
            f"<s>Старая цена: {product['old_price']:,} сум</s>\n"
            f"<b>Новая цена: {product['price']:,} сум</b>"
        )
    else:
        price_text = f"<b>Цена: {product['price']:,} сум</b>"
        
    text = (
        f"🎮 <b>{product['name']}</b>\n"
        f"🏪 Магазин: {shop_name}\n"
        f"Категория: {product['category']}\n"
        f"Наличие: {status_str}\n\n"
        f"📝 <b>Описание:</b>\n{product['description']}\n\n"
        f"{price_text}"
    )
    return text


@router.callback_query(F.data.startswith("shopcat_"))
async def callback_select_category(callback: CallbackQuery):
    _, shop_id_str, category = callback.data.split("_")
    shop_id = int(shop_id_str)
    
    shop = ShopRepository.get_shop_by_id(shop_id)
    if not shop:
        await callback.answer("Магазин не найден.", show_alert=True)
        return
        
    products = ProductRepository.get_products_by_category(shop_id, category)
    if not products:
        await callback.answer("В этой категории нет товаров.", show_alert=True)
        return
        
    product = products[0]
    is_fav = FavoriteRepository.is_favorite(callback.from_user.id, product['id'])
    text = format_product_text(product, shop['name'])
    
    try:
        await callback.message.delete()
    except Exception:
        pass
        
    reply_markup = get_product_detail_keyboard(
        product_id=product['id'],
        shop_id=shop_id,
        category=category,
        current_index=0,
        total_count=len(products),
        is_fav=is_fav,
        is_available=(product['stock_status'] == 1)
    )
    
    if product['photo']:
        await callback.message.answer_photo(
            photo=product['photo'],
            caption=text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    else:
        await callback.message.answer(
            text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    await callback.answer()


@router.callback_query(F.data.startswith("nav_"))
async def callback_nav_products(callback: CallbackQuery):
    _, shop_id_str, category, index_str = callback.data.split("_")
    shop_id = int(shop_id_str)
    index = int(index_str)
    
    shop = ShopRepository.get_shop_by_id(shop_id)
    products = ProductRepository.get_products_by_category(shop_id, category)
    
    if not products or index >= len(products) or not shop:
        await callback.answer("Ошибка навигации.", show_alert=True)
        return
        
    product = products[index]
    is_fav = FavoriteRepository.is_favorite(callback.from_user.id, product['id'])
    text = format_product_text(product, shop['name'])
    
    reply_markup = get_product_detail_keyboard(
        product_id=product['id'],
        shop_id=shop_id,
        category=category,
        current_index=index,
        total_count=len(products),
        is_fav=is_fav,
        is_available=(product['stock_status'] == 1)
    )
    
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


@router.callback_query(F.data.startswith("fav_"))
async def callback_toggle_favorite(callback: CallbackQuery):
    _, product_id_str, index_str = callback.data.split("_")
    product_id = int(product_id_str)
    index = int(index_str)
    
    user_id = callback.from_user.id
    product = ProductRepository.get_product_by_id(product_id)
    if not product:
        await callback.answer("Товар не найден.", show_alert=True)
        return
        
    is_currently_fav = FavoriteRepository.is_favorite(user_id, product_id)
    
    if is_currently_fav:
        FavoriteRepository.remove_from_favorites(user_id, product_id)
        await callback.answer("💔 Удалено из Избранного")
        is_fav = False
    else:
        FavoriteRepository.add_to_favorites(user_id, product_id)
        await callback.answer("⭐ Добавлено в Избранное")
        is_fav = True
        
    # Обновляем клавиатуру
    products = ProductRepository.get_products_by_category(product['shop_id'], product['category'])
    reply_markup = get_product_detail_keyboard(
        product_id=product_id,
        shop_id=product['shop_id'],
        category=product['category'],
        current_index=index,
        total_count=len(products),
        is_fav=is_fav,
        is_available=(product['stock_status'] == 1)
    )
    try:
        await callback.message.edit_reply_markup(reply_markup=reply_markup)
    except Exception:
        pass


# ==========================================
# ПОИСК В МАГАЗИНЕ
# ==========================================

@router.callback_query(F.data.startswith("shopsearch_"))
async def callback_search_shop_start(callback: CallbackQuery, state: FSMContext):
    shop_id = int(callback.data.split("_")[1])
    await state.clear()
    await state.update_data(search_shop_id=shop_id)
    
    await callback.message.answer("🔍 <b>Введите название товара для поиска в этом магазине:</b>", parse_mode="HTML")
    await state.set_state(SearchStates.waiting_for_query)
    await callback.answer()


@router.message(SearchStates.waiting_for_query)
async def process_search_query(message: Message, state: FSMContext):
    state_data = await state.get_data()
    shop_id = state_data['search_shop_id']
    query = message.text.strip()
    
    await state.clear()
    
    shop = ShopRepository.get_shop_by_id(shop_id)
    if not shop:
        await message.answer("Магазин не найден.")
        return
        
    products = ProductRepository.search_products(shop_id, query)
    if not products:
        await message.answer("😔 По вашему запросу ничего не найдено в этом магазине.")
        return
        
    product = products[0]
    is_fav = FavoriteRepository.is_favorite(message.from_user.id, product['id'])
    text = format_product_text(product, shop['name'])
    
    reply_markup = get_product_detail_keyboard(
        product_id=product['id'],
        shop_id=shop_id,
        category=product['category'],
        current_index=0,
        total_count=len(products),
        is_fav=is_fav,
        is_available=(product['stock_status'] == 1)
    )
    
    await message.answer(f"🔍 <b>Результаты поиска по запросу «{query}»:</b>", parse_mode="HTML")
    if product['photo']:
        await message.answer_photo(photo=product['photo'], caption=text, reply_markup=reply_markup, parse_mode="HTML")
    else:
        await message.answer(text, reply_markup=reply_markup, parse_mode="HTML")


# ==========================================
# ИЗБРАННОЕ (ДОСТУПНО ПО КОМАНДЕ /favorites)
# ==========================================

@router.message(Command("favorites"))
async def cmd_favorites(message: Message):
    user_id = message.from_user.id
    favorites = FavoriteRepository.get_user_favorites(user_id)
    
    if not favorites:
        await message.answer("⭐ <b>Ваш список избранного пуст.</b>\nДобавляйте товары в избранное прямо из каталога магазинов!", parse_mode="HTML")
        return
        
    product = favorites[0]
    text = format_product_text(product, product['shop_name'])
    
    reply_markup = get_favorites_keyboard(
        product_id=product['id'],
        current_index=0,
        total_count=len(favorites)
    )
    
    if product['photo']:
        await message.answer_photo(photo=product['photo'], caption=text, reply_markup=reply_markup, parse_mode="HTML")
    else:
        await message.answer(text, reply_markup=reply_markup, parse_mode="HTML")


@router.callback_query(F.data.startswith("favnav_"))
async def callback_fav_nav(callback: CallbackQuery):
    index = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    favorites = FavoriteRepository.get_user_favorites(user_id)
    
    if not favorites:
        await callback.message.edit_text("⭐ Ваше избранное пусто.")
        await callback.answer()
        return
        
    product = favorites[index % len(favorites)]
    text = format_product_text(product, product['shop_name'])
    
    reply_markup = get_favorites_keyboard(
        product_id=product['id'],
        current_index=index,
        total_count=len(favorites)
    )
    
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


@router.callback_query(F.data.startswith("unfav_"))
async def callback_fav_remove(callback: CallbackQuery):
    _, product_id_str, index_str = callback.data.split("_")
    product_id = int(product_id_str)
    index = int(index_str)
    
    user_id = callback.from_user.id
    FavoriteRepository.remove_from_favorites(user_id, product_id)
    await callback.answer("💔 Удалено из Избранного")
    
    favorites = FavoriteRepository.get_user_favorites(user_id)
    if not favorites:
        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.message.answer("⭐ <b>Ваш список избранного пуст.</b>", parse_mode="HTML")
        return
        
    new_index = index if index < len(favorites) else 0
    product = favorites[new_index]
    text = format_product_text(product, product['shop_name'])
    
    reply_markup = get_favorites_keyboard(
        product_id=product['id'],
        current_index=new_index,
        total_count=len(favorites)
    )
    
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
# ПОДДЕРЖКА И ЗАКАЗЫ КЛИЕНТА
# ==========================================

@router.message(F.text == "📞 Поддержка")
async def cmd_support(message: Message, state: FSMContext):
    state_data = await state.get_data()
    shop_id = state_data.get('current_shop_id')
    
    manager_username = MANAGER_USERNAME
    shop_name = "платформы"
    
    if shop_id:
        shop = ShopRepository.get_shop_by_id(shop_id)
        if shop:
            from config.config import get_shop_config
            cfg = get_shop_config(shop['name'])
            manager_username = cfg['manager_username']
            shop_name = f"магазина «{shop['name']}»"
            
    text = (
        f"📞 <b>Служба поддержки {shop_name}</b>\n\n"
        "Если у вас возникли вопросы по работе магазина, качеству товаров или оформлению заказов, "
        "нажмите на кнопку ниже, чтобы связаться с дежурным менеджером."
    )
    await message.answer(text, reply_markup=get_support_keyboard(manager_username), parse_mode="HTML")



@router.message(F.text == "📦 Мои заказы")
async def cmd_my_orders(message: Message):
    user_id = message.from_user.id
    orders = OrderRepository.get_user_orders(user_id)
    
    if not orders:
        await message.answer("📦 <b>У вас пока нет заказов.</b>\nСамое время выбрать магазин и сделать первую покупку! 😉", parse_mode="HTML")
        return
        
    text = "<b>📦 Ваша история заказов:</b>\n\n"
    
    status_emojis = {
        'Новый': '⏳',
        'Подтвержден': '✅',
        'В обработке': '⚙️',
        'Доставляется': '🚚',
        'Завершен': '🎉',
        'Отменен': '❌'
    }
    
    for order in orders[:15]:
        emoji = status_emojis.get(order['status'], '🔔')
        text += (
            f"🔹 <b>Заказ #{order['id']} в «{order['shop_name']}»</b>\n"
            f"🛒 Товар: {order['product_name']}\n"
            f"💰 Цена: {order['product_price']:,} сум\n"
            f"⏱ Статус: {emoji} {order['status']}\n"
            f"📅 Дата: {order['created_at']}\n\n"
        )
        
    await message.answer(text, parse_mode="HTML")


# ==========================================
# ОФОРМЛЕНИЕ ЗАКАЗА (FSM)
# ==========================================

@router.callback_query(F.data.startswith("order_"))
async def start_order_fsm(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    
    if parts[1] == "fav":
        # Заказ из избранного
        product_id = int(parts[2])
        product = ProductRepository.get_product_by_id(product_id)
        if not product:
            await callback.answer("Товар не найден.", show_alert=True)
            return
        shop_id = product['shop_id']
    else:
        # Обычный заказ
        shop_id = int(parts[1])
        product_id = int(parts[2])
        product = ProductRepository.get_product_by_id(product_id)
        
    if not product:
        await callback.answer("Товар не найден.", show_alert=True)
        return
        
    if product['stock_status'] == 0:
        await callback.answer("Извините, этого товара нет в наличии.", show_alert=True)
        return
        
    await state.clear()
    await state.update_data(shop_id=shop_id, product_id=product_id)
    
    try:
        await callback.message.delete()
    except Exception:
        pass
        
    await callback.message.answer(
        "📝 <b>Оформление заказа</b>\n\n"
        "Шаг 1 из 3: Введите ваше <b>Имя и Фамилию</b>:",
        parse_mode="HTML"
    )
    await state.set_state(OrderStates.waiting_for_name)
    await callback.answer()


@router.message(OrderStates.waiting_for_name)
async def process_order_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("Пожалуйста, введите имя (минимум 2 символа):")
        return
        
    await state.update_data(name=name)
    await message.answer(
        "Шаг 2 из 3: Введите ваш <b>номер телефона</b> для связи:\n"
        "Пример: <code>+998901234567</code>",
        parse_mode="HTML"
    )
    await state.set_state(OrderStates.waiting_for_phone)


@router.message(OrderStates.waiting_for_phone)
async def process_order_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    if len(phone) < 7:
        await message.answer("Пожалуйста, введите корректный номер телефона:")
        return
        
    await state.update_data(phone=phone)
    await message.answer(
        "Шаг 3 из 3: Введите <b>адрес доставки</b> (город, улица, дом, квартира):",
        parse_mode="HTML"
    )
    await state.set_state(OrderStates.waiting_for_address)


@router.message(OrderStates.waiting_for_address)
async def process_order_address(message: Message, state: FSMContext):
    address = message.text.strip()
    if len(address) < 5:
        await message.answer("Пожалуйста, введите более подробный адрес:")
        return
        
    await state.update_data(address=address)
    
    data = await state.get_data()
    product = ProductRepository.get_product_by_id(data['product_id'])
    shop = ShopRepository.get_shop_by_id(data['shop_id'])
    
    if not product or not shop:
        await message.answer("Произошла ошибка, товар не найден. Начните заново с выбора магазина.")
        await state.clear()
        return
        
    price_str = f"{product['price']:,} сум"
    if product['is_discount']:
        price_str = f"{product['price']:,} сум (скидка 🔥)"
        
    preview_text = (
        "🧐 <b>Проверьте правильность введенных данных:</b>\n\n"
        f"🏪 <b>Магазин:</b> {shop['name']}\n"
        f"📦 <b>Товар:</b> {product['name']}\n"
        f"💰 <b>Стоимость:</b> {price_str}\n\n"
        f"👤 <b>Получатель:</b> {data['name']}\n"
        f"📞 <b>Телефон:</b> {data['phone']}\n"
        f"📍 <b>Адрес доставки:</b> {address}\n\n"
        "Все верно? Подтвердите заказ."
    )
    
    await message.answer(preview_text, reply_markup=get_confirm_order_keyboard(), parse_mode="HTML")
    await state.set_state(OrderStates.waiting_for_confirm)


@router.callback_query(F.data.startswith("confirm_order_"), OrderStates.waiting_for_confirm)
async def process_order_confirm(callback: CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[2]
    
    if action == "no":
        await callback.message.edit_text("❌ <b>Оформление заказа отменено.</b>", parse_mode="HTML")
        await state.clear()
        await callback.answer()
        return
        
    data = await state.get_data()
    await state.clear()
    
    order_id = await create_new_order(
        bot=callback.bot,
        shop_id=data['shop_id'],
        user_id=callback.from_user.id,
        full_name=data['name'],
        phone=data['phone'],
        address=data['address'],
        product_id=data['product_id']
    )
    
    if order_id:
        success_text = (
            f"🎉 <b>Заказ #{order_id} успешно оформлен!</b>\n\n"
            "Владелец магазина уведомлен о новом заказе и скоро свяжется с вами.\n"
            "Вы будете получать уведомления об изменении статуса вашего заказа здесь. 🔔"
        )
        await callback.message.edit_text(success_text, parse_mode="HTML")
    else:
        await callback.message.edit_text("😔 К сожалению, произошла ошибка при оформлении заказа. Попробуйте еще раз.")
        
    await callback.answer()


# ==========================================
# ОБРАБОТЧИКИ НАЖАТИЙ REPLY-МЕНЮ МАГАЗИНА
# ==========================================

async def show_category_products(message: Message, shop_id: int, category: str, state: FSMContext):
    shop = ShopRepository.get_shop_by_id(shop_id)
    if not shop:
        await message.answer("Магазин не найден.")
        return
        
    products = ProductRepository.get_products_by_category(shop_id, category)
    if not products:
        await message.answer("В этой категории нет товаров.")
        return
        
    product = products[0]
    is_fav = FavoriteRepository.is_favorite(message.from_user.id, product['id'])
    text = format_product_text(product, shop['name'])
    
    reply_markup = get_product_detail_keyboard(
        product_id=product['id'],
        shop_id=shop_id,
        category=category,
        current_index=0,
        total_count=len(products),
        is_fav=is_fav,
        is_available=(product['stock_status'] == 1)
    )
    
    if product['photo']:
        await message.answer_photo(
            photo=product['photo'],
            caption=text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    else:
        await message.answer(
            text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )


@router.message(F.text)
async def process_shop_menu_click(message: Message, state: FSMContext):
    text = message.text.strip()
    
    state_data = await state.get_data()
    shop_id = state_data.get('current_shop_id')
    
    if shop_id:
        categories = ProductRepository.get_categories_by_shop(shop_id)
        
        # 1. Если кликнули по категории
        if text in categories:
            await show_category_products(message, shop_id, text, state)
            return
            
        # 2. Если кликнули по поиску
        if text == "🔍 Поиск по магазину":
            await state.update_data(search_shop_id=shop_id)
            await message.answer("🔍 <b>Введите название товара для поиска в этом магазине:</b>", parse_mode="HTML")
            await state.set_state(SearchStates.waiting_for_query)
            return
            
        # 3. Если кликнули по возврату к списку магазинов
        if text == "🔙 К списку магазинов":
            await state.clear()
            shops = ShopRepository.get_all_shops()
            if not shops:
                await message.answer("😔 В системе пока нет зарегистрированных магазинов. Загляните позже!", reply_markup=get_main_menu(message.from_user.id))
                return
                
            text_msg = (
                "🏪 <b>Список доступных магазинов:</b>\n\n"
                "Выберите магазин из списка ниже, чтобы перейти в его каталог:"
            )
            await message.answer("Вы вышли из магазина.", reply_markup=get_main_menu(message.from_user.id))
            await message.answer(text_msg, reply_markup=get_shops_list_keyboard(shops), parse_mode="HTML")
            return

