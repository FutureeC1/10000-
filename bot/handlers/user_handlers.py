import logging
# pyrefly: ignore [missing-import]
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from config.config import MANAGER_USERNAME
from database.repositories import UserRepository, ProductRepository, OrderRepository, FavoriteRepository
from bot.keyboards.reply import get_main_menu
from bot.keyboards.inline import (
    get_categories_keyboard,
    get_product_detail_keyboard,
    get_favorites_keyboard,
    get_confirm_order_keyboard,
    get_manager_keyboard
)
from bot.states.user_states import OrderStates, SearchStates
from services.order_service import create_new_order

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name
    
    # Регистрируем/обновляем пользователя в БД
    UserRepository.add_user(user_id, username, full_name)
    
    welcome_text = (
        "👋 <b>Добро пожаловать в Keyllect!</b>\n\n"
        "Мы — магазин премиальных игровых и компьютерных аксессуаров. "
        "У нас вы найдете лучшие клавиатуры, мышки, наушники и коврики.\n\n"
        "🛒 Воспользуйтесь меню ниже для навигации по магазину."
    )
    await message.answer(welcome_text, reply_markup=get_main_menu(user_id), parse_mode="HTML")


@router.message(F.text == "🛒 Каталог")
@router.message(Command("catalog"))
async def cmd_catalog(message: Message):
    categories = ProductRepository.get_categories()
    if not categories:
        await message.answer("😔 В магазине пока нет товаров. Загляните позже!")
        return
        
    await message.answer(
        "📁 <b>Выберите категорию товаров:</b>",
        reply_markup=get_categories_keyboard(categories),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "back_to_categories")
async def callback_back_to_categories(callback: CallbackQuery):
    categories = ProductRepository.get_categories()
    if not categories:
        await callback.message.edit_text("😔 В магазине пока нет товаров. Загляните позже!")
        return
        
    # Если сообщение с фото (карточка товара), то edit_text не сработает напрямую.
    # Поэтому мы удалим карточку товара и отправим новое сообщение с категориями, чтобы не спамить.
    try:
        await callback.message.delete()
    except Exception:
        pass
        
    await callback.message.answer(
        "📁 <b>Выберите категорию товаров:</b>",
        reply_markup=get_categories_keyboard(categories),
        parse_mode="HTML"
    )
    await callback.answer()


def format_product_text(product: dict) -> str:
    """Форматирует карточку товара."""
    status_str = "✅ В наличии" if product['is_available'] else "❌ Нет в наличии"
    
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
        f"Категория: {product['category']}\n"
        f"Наличие: {status_str}\n\n"
        f"📝 <b>Описание:</b>\n{product['description']}\n\n"
        f"{price_text}"
    )
    return text


@router.callback_query(F.data.startswith("cat_"))
async def callback_select_category(callback: CallbackQuery):
    category = callback.data.split("_")[1]
    products = ProductRepository.get_products_by_category(category)
    
    if not products:
        await callback.answer("В этой категории нет товаров.", show_alert=True)
        return
        
    product = products[0]
    is_fav = FavoriteRepository.is_favorite(callback.from_user.id, product['id'])
    text = format_product_text(product)
    
    # Удаляем меню категорий
    try:
        await callback.message.delete()
    except Exception:
        pass
        
    # Отправляем карточку первого товара с фото
    if product['photo']:
        await callback.message.answer_photo(
            photo=product['photo'],
            caption=text,
            reply_markup=get_product_detail_keyboard(
                product_id=product['id'],
                category=category,
                current_index=0,
                total_count=len(products),
                is_fav=is_fav,
                is_available=bool(product['is_available'])
            ),
            parse_mode="HTML"
        )
    else:
        await callback.message.answer(
            text,
            reply_markup=get_product_detail_keyboard(
                product_id=product['id'],
                category=category,
                current_index=0,
                total_count=len(products),
                is_fav=is_fav,
                is_available=bool(product['is_available'])
            ),
            parse_mode="HTML"
        )
    await callback.answer()


@router.callback_query(F.data.startswith("nav_"))
async def callback_nav_products(callback: CallbackQuery):
    _, category, index_str = callback.data.split("_")
    index = int(index_str)
    
    products = ProductRepository.get_products_by_category(category)
    if not products or index >= len(products):
        await callback.answer("Ошибка навигации.", show_alert=True)
        return
        
    product = products[index]
    is_fav = FavoriteRepository.is_favorite(callback.from_user.id, product['id'])
    text = format_product_text(product)
    
    reply_markup = get_product_detail_keyboard(
        product_id=product['id'],
        category=category,
        current_index=index,
        total_count=len(products),
        is_fav=is_fav,
        is_available=bool(product['is_available'])
    )
    
    # Редактируем существующее сообщение для чистого UX
    if product['photo']:
        media = InputMediaPhoto(media=product['photo'], caption=text, parse_mode="HTML")
        try:
            await callback.message.edit_media(media=media, reply_markup=reply_markup)
        except Exception:
            # Если не получается отредактировать медиа, удаляем старое и шлем новое
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
    reply_markup = get_product_detail_keyboard(
        product_id=product_id,
        category=product['category'],
        current_index=index,
        total_count=len(ProductRepository.get_products_by_category(product['category'])),
        is_fav=is_fav,
        is_available=bool(product['is_available'])
    )
    try:
        await callback.message.edit_reply_markup(reply_markup=reply_markup)
    except Exception:
        pass


@router.message(F.text == "⭐ Избранное")
async def cmd_favorites(message: Message):
    user_id = message.from_user.id
    favorites = FavoriteRepository.get_user_favorites(user_id)
    
    if not favorites:
        await message.answer("⭐ <b>Ваш список избранного пуст.</b>\nДобавляйте товары в избранное прямо из каталога!", parse_mode="HTML")
        return
        
    product = favorites[0]
    text = format_product_text(product)
    
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
        await callback.message.edit_text("⭐ Ваша корзина избранного пуста.")
        await callback.answer()
        return
        
    product = favorites[index % len(favorites)]
    text = format_product_text(product)
    
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
    text = format_product_text(product)
    
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


@router.message(F.text == "🔍 Поиск")
async def cmd_search(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🔍 <b>Введите название товара или ключевое слово для поиска:</b>", parse_mode="HTML")
    await state.set_state(SearchStates.waiting_for_query)


@router.message(SearchStates.waiting_for_query)
async def process_search_query(message: Message, state: FSMContext):
    query = message.text.strip()
    if not query:
        await message.answer("Пожалуйста, введите корректный запрос.")
        return
        
    products = ProductRepository.search_products(query)
    await state.clear()
    
    if not products:
        await message.answer("😔 Товары по вашему запросу не найдены. Попробуйте другое слово.")
        return
        
    product = products[0]
    is_fav = FavoriteRepository.is_favorite(message.from_user.id, product['id'])
    text = format_product_text(product)
    
    reply_markup = get_product_detail_keyboard(
        product_id=product['id'],
        category=product['category'],
        current_index=0,
        total_count=len(products),
        is_fav=is_fav,
        is_available=bool(product['is_available'])
    )
    
    await message.answer(f"🔍 <b>Результаты поиска по запросу «{query}»:</b>", parse_mode="HTML")
    if product['photo']:
        await message.answer_photo(photo=product['photo'], caption=text, reply_markup=reply_markup, parse_mode="HTML")
    else:
        await message.answer(text, reply_markup=reply_markup, parse_mode="HTML")


@router.message(F.text == "ℹ️ О магазине")
async def cmd_about(message: Message):
    text = (
        "ℹ️ <b>О магазине Keyllect</b>\n\n"
        "Добро пожаловать в <b>Keyllect</b> — ваш надежный партнер в мире гейминга и высоких технологий! 🎮\n\n"
        "Мы специализируемся на продаже игровых девайсов экстра-класса:\n"
        "• ⌨️ Механические и мембранные клавиатуры с кастомной подсветкой\n"
        "• 🖱 Ультралегкие эргономичные мыши для киберспорта\n"
        "• 🎧 Наушники с кристально чистым объемным звуком 7.1\n"
        "• 🗺 Профессиональные коврики любых размеров с отличным покрытием Control/Speed\n\n"
        "🌟 <b>Наши преимущества:</b>\n"
        "• Только оригинальная продукция ведущих мировых брендов\n"
        "• Быстрая доставка прямо до двери\n"
        "• Гарантия качества на весь ассортимент\n\n"
        "Соберите свой идеальный сетап вместе с Keyllect! 🚀"
    )
    await message.answer(text, parse_mode="HTML")


@router.message(F.text == "📞 Контакты")
async def cmd_contacts(message: Message):
    text = (
        "📞 <b>Контакты магазина Keyllect</b>\n\n"
        "📍 <b>Адрес шоурума:</b> г. Ташкент, ул. Амира Темура, 42 (ориентир: станция метро Алайский рынок)\n"
        "⏰ <b>Режим работы:</b> Ежедневно с 10:00 до 21:00\n"
        "📞 <b>Телефон поддержки:</b> +998 (90) 123-45-67\n"
        "📧 <b>E-mail:</b> support@keyllect.uz\n\n"
        "💬 Возникли вопросы по заказу или ассортименту? Наш менеджер всегда на связи и готов помочь!"
    )
    await message.answer(
        text, 
        reply_markup=get_manager_keyboard(MANAGER_USERNAME), 
        parse_mode="HTML"
    )


@router.message(F.text == "📦 Мои заказы")
async def cmd_my_orders(message: Message):
    user_id = message.from_user.id
    orders = OrderRepository.get_user_orders(user_id)
    
    if not orders:
        await message.answer("📦 <b>У вас пока нет заказов.</b>\nСамое время сделать первый заказ в каталоге! 😉", parse_mode="HTML")
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
    
    for order in orders[:10]: # Показываем последние 10 заказов
        emoji = status_emojis.get(order['status'], '🔔')
        text += (
            f"🔹 <b>Заказ #{order['id']}</b>\n"
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
    data_parts = callback.data.split("_")
    product_id = int(data_parts[1]) if len(data_parts) == 2 else int(data_parts[2])
    
    product = ProductRepository.get_product_by_id(product_id)
    if not product:
        await callback.answer("Товар не найден.", show_alert=True)
        return
        
    if not product['is_available']:
        await callback.answer("Извините, этого товара нет в наличии.", show_alert=True)
        return
        
    await state.clear()
    await state.update_data(product_id=product_id)
    
    # Удаляем карточку, чтобы перейти к вводу FSM (или пишем сообщение о начале заказа)
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
        await message.answer("Пожалуйста, введите корректное имя (минимум 2 символа):")
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
    # Простая валидация
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
    
    # Показываем превью заказа
    data = await state.get_data()
    product = ProductRepository.get_product_by_id(data['product_id'])
    
    if not product:
        await message.answer("Произошла ошибка, товар не найден. Пожалуйста, начните заново.")
        await state.clear()
        return
        
    price_str = f"{product['price']:,} сум"
    if product['is_discount']:
        price_str = f"{product['price']:,} сум (скидка 🔥)"
        
    preview_text = (
        "🧐 <b>Проверьте правильность введенных данных:</b>\n\n"
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
        user_id=callback.from_user.id,
        full_name=data['name'],
        phone=data['phone'],
        address=data['address'],
        product_id=data['product_id']
    )
    
    if order_id:
        success_text = (
            f"🎉 <b>Заказ #{order_id} успешно оформлен!</b>\n\n"
            "Наш менеджер свяжется с вами в ближайшее время для подтверждения доставки.\n"
            "Вы будете получать автоматические уведомления об изменении статуса вашего заказа в этом чате. 🔔"
        )
        await callback.message.edit_text(success_text, parse_mode="HTML")
    else:
        await callback.message.edit_text("😔 К сожалению, произошла ошибка при оформлении заказа. Попробуйте еще раз.")
        
    await callback.answer()
