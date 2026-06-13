import logging
# pyrefly: ignore [missing-import]
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
    get_support_keyboard,
    get_language_keyboard
)
from bot.states.user_states import OrderStates, SearchStates
from services.order_service import create_new_order
from config.localization import get_text

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name
    
    # Регистрируем пользователя
    UserRepository.add_user(user_id, username, full_name)
    
    # Сначала всегда предлагаем выбрать язык
    await message.answer(
        "🌐 <b>Выберите язык / Tilni tanlang:</b>",
        reply_markup=get_language_keyboard(),
        parse_mode="HTML"
    )


@router.message(F.text.in_({"🌐 Язык / Til", "🌐 Til / Язык", "🌐 Язык / Tillar"}))
async def cmd_change_language(message: Message):
    user_id = message.from_user.id
    lang = UserRepository.get_user_language(user_id)
    await message.answer(
        get_text('select_language', lang),
        reply_markup=get_language_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("lang_"))
async def callback_select_language(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    user_id = callback.from_user.id
    UserRepository.update_user_language(user_id, lang)
    
    welcome_text = get_text('language_selected', lang)
    await callback.answer(welcome_text)
    
    shops = ShopRepository.get_all_shops()
    if not shops:
        await callback.message.answer(
            get_text('welcome_no_shops', lang),
            reply_markup=get_main_menu(user_id),
            parse_mode="HTML"
        )
    else:
        # Отправляем главное меню с кнопками
        await callback.message.answer(
            get_text('welcome_shops', lang),
            reply_markup=get_main_menu(user_id),
            parse_mode="HTML"
        )
        # Отправляем список магазинов
        await callback.message.answer(
            get_text('shops_list_title', lang),
            reply_markup=get_shops_list_keyboard(shops),
            parse_mode="HTML"
        )
    
    try:
        await callback.message.delete()
    except Exception:
        pass



@router.message(F.text.in_({"🏪 Магазины", "🏪 Do'konlar"}))
@router.message(Command("shops"))
async def cmd_shops(message: Message):
    user_id = message.from_user.id
    lang = UserRepository.get_user_language(user_id)
    shops = ShopRepository.get_all_shops()
    if not shops:
        await message.answer(get_text('no_shops', lang))
        return
        
    text = get_text('shops_list_title', lang)
    await message.answer(text, reply_markup=get_shops_list_keyboard(shops), parse_mode="HTML")


@router.callback_query(F.data == "back_to_shops")
async def callback_back_to_shops(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback.from_user.id
    lang = UserRepository.get_user_language(user_id)
    shops = ShopRepository.get_all_shops()
    if not shops:
        await callback.answer(get_text('no_shops', lang))
        return
        
    text = get_text('shops_list_title', lang)
    try:
        await callback.message.delete()
    except Exception:
        pass
        
    # Восстанавливаем главное меню
    exit_text = "Вы вышли из магазина." if lang == 'ru' else "Do'kondan chiqdingiz."
    await callback.message.answer(exit_text, reply_markup=get_main_menu(user_id))
    await callback.message.answer(text, reply_markup=get_shops_list_keyboard(shops), parse_mode="HTML")
    await callback.answer()



@router.callback_query(F.data.startswith("selectshop_"))
@router.callback_query(F.data.startswith("back_to_categories_"))
async def callback_select_shop(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    shop_id = int(parts[1]) if parts[0] == "selectshop" else int(parts[3])
    
    # Сохраняем текущий просматриваемый магазин в состояние
    await state.update_data(current_shop_id=shop_id)
    
    user_id = callback.from_user.id
    lang = UserRepository.get_user_language(user_id)
    
    shop = ShopRepository.get_shop_by_id(shop_id)
    if not shop:
        shop_not_found_text = "Магазин не найден." if lang == 'ru' else "Do'kon topilmadi."
        await callback.answer(shop_not_found_text, show_alert=True)
        return
        
    categories = ProductRepository.get_categories_by_shop(shop_id)
    if not categories:
        no_products_text = "В этом магазине пока нет товаров." if lang == 'ru' else "Ushbu do'konda hozircha mahsulotlar yo'q."
        await callback.answer(no_products_text, show_alert=True)
        return
        
    text = get_text('shop_title', lang, name=shop['name'], description=shop['description'] or ('Описание отсутствует.' if lang == 'ru' else 'Tavsif mavjud emas.'))
    
    try:
        await callback.message.delete()
    except Exception:
        pass
        
    reply_markup = get_shop_menu_keyboard(categories, lang)
    
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




def format_product_text(product: dict, shop_name: str, lang: str = 'ru') -> str:
    status_str = "✅ В наличии" if lang == 'ru' else "✅ Mavjud"
    if product['stock_status'] != 1:
        status_str = "❌ Нет в наличии" if lang == 'ru' else "❌ Mavjud emas"
        
    price_text = ""
    currency_str = "UZS"
    if product['is_discount']:
        price_text = (
            f"🔥 <b>Скидка!</b>\n" if lang == 'ru' else f"🔥 <b>Chegirma!</b>\n"
        )
        old_price_label = "Старая цена" if lang == 'ru' else "Eski narxi"
        new_price_label = "Новая цена" if lang == 'ru' else "Yangi narxi"
        price_text += (
            f"<s>{old_price_label}: {product['old_price']:,} {currency_str}</s>\n"
            f"<b>{new_price_label}: {product['price']:,} {currency_str}</b>"
        )
    else:
        price_label = "Цена" if lang == 'ru' else "Narxi"
        price_text = f"<b>{price_label}: {product['price']:,} {currency_str}</b>"
        
    shop_label = "Магазин" if lang == 'ru' else "Do'kon"
    cat_label = "Категория" if lang == 'ru' else "Kategoriya"
    stock_label = "Наличие" if lang == 'ru' else "Holati"
    desc_label = "Описание" if lang == 'ru' else "Tavsif"
    
    text = (
        f"🎮 <b>{product['name']}</b>\n"
        f"🏪 {shop_label}: {shop_name}\n"
        f"{cat_label}: {product['category']}\n"
        f"{stock_label}: {status_str}\n\n"
        f"📝 <b>{desc_label}:</b>\n{product['description']}\n\n"
        f"{price_text}"
    )
    return text


@router.callback_query(F.data.startswith("shopcat_"))
async def callback_select_category(callback: CallbackQuery):
    _, shop_id_str, category = callback.data.split("_")
    shop_id = int(shop_id_str)
    
    user_id = callback.from_user.id
    lang = UserRepository.get_user_language(user_id)
    
    shop = ShopRepository.get_shop_by_id(shop_id)
    if not shop:
        shop_not_found_text = "Магазин не найден." if lang == 'ru' else "Do'kon topilmadi."
        await callback.answer(shop_not_found_text, show_alert=True)
        return
        
    products = ProductRepository.get_products_by_category(shop_id, category)
    if not products:
        no_products_text = "В этой категории нет товаров." if lang == 'ru' else "Ushbu kategoriyada mahsulotlar yo'q."
        await callback.answer(no_products_text, show_alert=True)
        return
        
    product = products[0]
    is_fav = FavoriteRepository.is_favorite(user_id, product['id'])
    text = format_product_text(product, shop['name'], lang)
    
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
        is_available=(product['stock_status'] == 1),
        lang=lang
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
    
    user_id = callback.from_user.id
    lang = UserRepository.get_user_language(user_id)
    
    shop = ShopRepository.get_shop_by_id(shop_id)
    products = ProductRepository.get_products_by_category(shop_id, category)
    
    if not products or index >= len(products) or not shop:
        nav_error_text = "Ошибка навигации." if lang == 'ru' else "Navigatsiya xatosi."
        await callback.answer(nav_error_text, show_alert=True)
        return
        
    product = products[index]
    is_fav = FavoriteRepository.is_favorite(user_id, product['id'])
    text = format_product_text(product, shop['name'], lang)
    
    reply_markup = get_product_detail_keyboard(
        product_id=product['id'],
        shop_id=shop_id,
        category=category,
        current_index=index,
        total_count=len(products),
        is_fav=is_fav,
        is_available=(product['stock_status'] == 1),
        lang=lang
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
    lang = UserRepository.get_user_language(user_id)
    
    product = ProductRepository.get_product_by_id(product_id)
    if not product:
        not_found_text = "Товар не найден." if lang == 'ru' else "Mahsulot topilmadi."
        await callback.answer(not_found_text, show_alert=True)
        return
        
    is_currently_fav = FavoriteRepository.is_favorite(user_id, product_id)
    
    if is_currently_fav:
        FavoriteRepository.remove_from_favorites(user_id, product_id)
        await callback.answer(get_text('favorite_removed', lang))
        is_fav = False
    else:
        FavoriteRepository.add_to_favorites(user_id, product_id)
        await callback.answer(get_text('favorite_added', lang))
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
        is_available=(product['stock_status'] == 1),
        lang=lang
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
    
    user_id = callback.from_user.id
    lang = UserRepository.get_user_language(user_id)
    
    await callback.message.answer(get_text('search_prompt', lang), parse_mode="HTML")
    await state.set_state(SearchStates.waiting_for_query)
    await callback.answer()


@router.message(SearchStates.waiting_for_query)
async def process_search_query(message: Message, state: FSMContext):
    state_data = await state.get_data()
    shop_id = state_data['search_shop_id']
    query = message.text.strip()
    
    await state.clear()
    
    user_id = message.from_user.id
    lang = UserRepository.get_user_language(user_id)
    
    shop = ShopRepository.get_shop_by_id(shop_id)
    if not shop:
        await message.answer("Магазин не найден." if lang == 'ru' else "Do'kon topilmadi.")
        return
        
    products = ProductRepository.search_products(shop_id, query)
    if not products:
        await message.answer(get_text('search_no_results', lang, query=query))
        return
        
    product = products[0]
    is_fav = FavoriteRepository.is_favorite(user_id, product['id'])
    text = format_product_text(product, shop['name'], lang)
    
    reply_markup = get_product_detail_keyboard(
        product_id=product['id'],
        shop_id=shop_id,
        category=product['category'],
        current_index=0,
        total_count=len(products),
        is_fav=is_fav,
        is_available=(product['stock_status'] == 1),
        lang=lang
    )
    
    await message.answer(get_text('search_results', lang, query=query), parse_mode="HTML")
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
    lang = UserRepository.get_user_language(user_id)
    favorites = FavoriteRepository.get_user_favorites(user_id)
    
    if not favorites:
        empty_text = (
            "⭐ <b>Ваш список избранного пуст.</b>\nДобавляйте товары в избранное прямо из каталога магазинов!"
            if lang == 'ru' else
            "⭐ <b>Sevimlilaringiz ro'yxati bo'sh.</b>\nMahsulotlarni to'g'ridan-to'g'ri do'konlar katalogidan sevimlilarga qo'shing!"
        )
        await message.answer(empty_text, parse_mode="HTML")
        return
        
    product = favorites[0]
    text = format_product_text(product, product['shop_name'], lang)
    
    reply_markup = get_favorites_keyboard(
        product_id=product['id'],
        current_index=0,
        total_count=len(favorites),
        lang=lang
    )
    
    if product['photo']:
        await message.answer_photo(photo=product['photo'], caption=text, reply_markup=reply_markup, parse_mode="HTML")
    else:
        await message.answer(text, reply_markup=reply_markup, parse_mode="HTML")


@router.callback_query(F.data.startswith("favnav_"))
async def callback_fav_nav(callback: CallbackQuery):
    index = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    lang = UserRepository.get_user_language(user_id)
    favorites = FavoriteRepository.get_user_favorites(user_id)
    
    if not favorites:
        empty_text = "⭐ Ваше избранное пусто." if lang == 'ru' else "⭐ Sevimlilaringiz bo'sh."
        await callback.message.edit_text(empty_text)
        await callback.answer()
        return
        
    product = favorites[index % len(favorites)]
    text = format_product_text(product, product['shop_name'], lang)
    
    reply_markup = get_favorites_keyboard(
        product_id=product['id'],
        current_index=index,
        total_count=len(favorites),
        lang=lang
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
    lang = UserRepository.get_user_language(user_id)
    FavoriteRepository.remove_from_favorites(user_id, product_id)
    await callback.answer(get_text('favorite_removed', lang))
    
    favorites = FavoriteRepository.get_user_favorites(user_id)
    if not favorites:
        try:
            await callback.message.delete()
        except Exception:
            pass
        empty_text = "⭐ <b>Ваш список избранного пуст.</b>" if lang == 'ru' else "⭐ <b>Sevimlilaringiz ro'yxati bo'sh.</b>"
        await callback.message.answer(empty_text, parse_mode="HTML")
        return
        
    new_index = index if index < len(favorites) else 0
    product = favorites[new_index]
    text = format_product_text(product, product['shop_name'], lang)
    
    reply_markup = get_favorites_keyboard(
        product_id=product['id'],
        current_index=new_index,
        total_count=len(favorites),
        lang=lang
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



@router.message(F.text.in_({"📦 Мои заказы", "📦 Buyurtmalarim"}))
async def cmd_my_orders(message: Message):
    user_id = message.from_user.id
    lang = UserRepository.get_user_language(user_id)
    orders = OrderRepository.get_user_orders(user_id)
    
    if not orders:
        empty_text = (
            "📦 <b>У вас пока нет заказов.</b>\nСамое время выбрать магазин и сделать первую покупку! 😉"
            if lang == 'ru' else
            "📦 <b>Sizda hali buyurtmalar yo'q.</b>\nDo'konni tanlab birinchi xaridni amalga oshirish vaqti keldi! 😉"
        )
        await message.answer(empty_text, parse_mode="HTML")
        return
        
    text = "<b>📦 Ваша история заказов:</b>\n\n" if lang == 'ru' else "<b>📦 Buyurtmalaringiz tarixi:</b>\n\n"
    
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
        status_val = order['status']
        if lang == 'uz':
            status_translations = {
                'Новый': 'Yangi',
                'Подтвержден': 'Tasdiqlangan',
                'В обработке': 'Jarayonda',
                'Доставляется': 'Yetkazilmoqda',
                'Завершен': 'Yakunlangan',
                'Отменен': 'Bekor qilingan'
            }
            status_val = status_translations.get(status_val, status_val)
            
        shop_label = "da" if lang == 'uz' else "в"
        item_label = "Mahsulot" if lang == 'uz' else "Товар"
        price_label = "Narxi" if lang == 'uz' else "Цена"
        status_label = "Holati" if lang == 'uz' else "Статус"
        date_label = "Sana" if lang == 'uz' else "Дата"
        
        text += (
            f"🔹 <b>Заказ #{order['id']} {order['shop_name']} {shop_label}</b>\n"
            f"🛒 {item_label}: {order['product_name']}\n"
            f"💰 {price_label}: {order['product_price']:,} сум\n"
            f"⏱ {status_label}: {emoji} {status_val}\n"
            f"📅 {date_label}: {order['created_at']}\n\n"
        )
        
    await message.answer(text, parse_mode="HTML")


# ==========================================
# ОФОРМЛЕНИЕ ЗАКАЗА (FSM)
# ==========================================

@router.callback_query(F.data.startswith("order_"))
async def start_order_fsm(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    user_id = callback.from_user.id
    lang = UserRepository.get_user_language(user_id)
    
    if parts[1] == "fav":
        # Заказ из избранного
        product_id = int(parts[2])
        product = ProductRepository.get_product_by_id(product_id)
        if not product:
            not_found_text = "Товар не найден." if lang == 'ru' else "Mahsulot topilmadi."
            await callback.answer(not_found_text, show_alert=True)
            return
        shop_id = product['shop_id']
    else:
        # Обычный заказ
        shop_id = int(parts[1])
        product_id = int(parts[2])
        product = ProductRepository.get_product_by_id(product_id)
        
    if not product:
        not_found_text = "Товар не найден." if lang == 'ru' else "Mahsulot topilmadi."
        await callback.answer(not_found_text, show_alert=True)
        return
        
    if product['stock_status'] == 0:
        not_available_text = "Извините, этого товара нет в наличии." if lang == 'ru' else "Kechirasiz, ushbu mahsulot mavjud emas."
        await callback.answer(not_available_text, show_alert=True)
        return
        
    await state.clear()
    await state.update_data(shop_id=shop_id, product_id=product_id)
    
    try:
        await callback.message.delete()
    except Exception:
        pass
        
    step1_text = (
        "📝 <b>Оформление заказа</b>\n\n"
        "Шаг 1 из 3: Введите ваше <b>Имя и Фамилию</b>:"
        if lang == 'ru' else
        "📝 <b>Buyurtmani rasmiylashtirish</b>\n\n"
        "1-qadam (3 dan): <b>Ism va familiyangizni</b> kiriting:"
    )
    await callback.message.answer(step1_text, parse_mode="HTML")
    await state.set_state(OrderStates.waiting_for_name)
    await callback.answer()


@router.message(OrderStates.waiting_for_name)
async def process_order_name(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = UserRepository.get_user_language(user_id)
    name = message.text.strip()
    if len(name) < 2:
        error_name = "Пожалуйста, введите имя (минимум 2 символа):" if lang == 'ru' else "Iltimos, ismingizni kiriting (kamida 2 ta belgi):"
        await message.answer(error_name)
        return
        
    await state.update_data(name=name)
    step2_text = (
        "Шаг 2 из 3: Введите ваш <b>номер телефона</b> для связи:\n"
        "Пример: <code>+998901234567</code>"
        if lang == 'ru' else
        "2-qadam (3 dan): Bog'lanish uchun <b>telefon raqamingizni</b> kiriting:\n"
        "Masalan: <code>+998901234567</code>"
    )
    await message.answer(step2_text, parse_mode="HTML")
    await state.set_state(OrderStates.waiting_for_phone)


@router.message(OrderStates.waiting_for_phone)
async def process_order_phone(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = UserRepository.get_user_language(user_id)
    phone = message.text.strip()
    if len(phone) < 7:
        error_phone = "Пожалуйста, введите корректный номер телефона:" if lang == 'ru' else "Iltimos, to'g'ri telefon raqamini kiriting:"
        await message.answer(error_phone)
        return
        
    await state.update_data(phone=phone)
    step3_text = (
        "Шаг 3 из 3: Введите <b>адрес доставки</b> (город, улица, дом, квартира):"
        if lang == 'ru' else
        "3-qadam (3 dan): <b>Yetkazib berish manzilini</b> kiriting (shahar, ko'cha, uy, xonadon):"
    )
    await message.answer(step3_text, parse_mode="HTML")
    await state.set_state(OrderStates.waiting_for_address)


@router.message(OrderStates.waiting_for_address)
async def process_order_address(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = UserRepository.get_user_language(user_id)
    address = message.text.strip()
    if len(address) < 5:
        error_address = "Пожалуйста, введите более подробный адрес:" if lang == 'ru' else "Iltimos, batafsilroq manzilni kiriting:"
        await message.answer(error_address)
        return
        
    await state.update_data(address=address)
    
    data = await state.get_data()
    product = ProductRepository.get_product_by_id(data['product_id'])
    shop = ShopRepository.get_shop_by_id(data['shop_id'])
    
    if not product or not shop:
        error_not_found = (
            "Произошла ошибка, товар не найден. Начните заново с выбора магазина."
            if lang == 'ru' else
            "Xatolik yuz berdi, mahsulot topilmadi. Do'konni tanlashdan boshlab qaytadan urinib ko'ring."
        )
        await message.answer(error_not_found)
        await state.clear()
        return
        
    price_str = f"{product['price']:,} сум" if lang == 'ru' else f"{product['price']:,} so'm"
    if product['is_discount']:
        price_str += " (скидка 🔥)" if lang == 'ru' else " (chegirma 🔥)"
        
    preview_text = (
        "🧐 <b>Проверьте правильность введенных данных:</b>\n\n"
        f"🏪 <b>Магазин:</b> {shop['name']}\n"
        f"📦 <b>Товар:</b> {product['name']}\n"
        f"💰 <b>Стоимость:</b> {price_str}\n\n"
        f"👤 <b>Получатель:</b> {data['name']}\n"
        f"📞 <b>Телефон:</b> {data['phone']}\n"
        f"📍 <b>Адрес доставки:</b> {address}\n\n"
        "Все верно? Подтвердите заказ."
        if lang == 'ru' else
        "🧐 <b>Kiritilgan ma'lumotlarni tekshiring:</b>\n\n"
        f"🏪 <b>Do'kon:</b> {shop['name']}\n"
        f"📦 <b>Mahsulot:</b> {product['name']}\n"
        f"💰 <b>Narxi:</b> {price_str}\n\n"
        f"👤 <b>Qabul qiluvchi:</b> {data['name']}\n"
        f"📞 <b>Telefon:</b> {data['phone']}\n"
        f"📍 <b>Yetkazib berish manzili:</b> {address}\n\n"
        "Hammasi to'g'rimi? Buyurtmani tasdiqlang."
    )
    
    await message.answer(preview_text, reply_markup=get_confirm_order_keyboard(lang), parse_mode="HTML")
    await state.set_state(OrderStates.waiting_for_confirm)


@router.callback_query(F.data.startswith("confirm_order_"), OrderStates.waiting_for_confirm)
async def process_order_confirm(callback: CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[2]
    user_id = callback.from_user.id
    lang = UserRepository.get_user_language(user_id)
    
    if action == "no":
        cancel_text = "❌ <b>Оформление заказа отменено.</b>" if lang == 'ru' else "❌ <b>Buyurtma berish bekor qilindi.</b>"
        await callback.message.edit_text(cancel_text, parse_mode="HTML")
        await state.clear()
        await callback.answer()
        return
        
    data = await state.get_data()
    await state.clear()
    
    order_id = await create_new_order(
        bot=callback.bot,
        shop_id=data['shop_id'],
        user_id=user_id,
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
            if lang == 'ru' else
            f"🎉 <b>Buyurtma #{order_id} muvaffaqiyatli rasmiylashtirildi!</b>\n\n"
            "Do'kon egasi yangi buyurtma haqida xabardor qilindi va tez orada siz bilan bog'lanadi.\n"
            "Buyurtmangiz holati o'zgarganda bu yerda xabar olasiz. 🔔"
        )
        await callback.message.edit_text(success_text, parse_mode="HTML")
    else:
        error_text = (
            "😔 К сожалению, произошла ошибка при оформлении заказа. Попробуйте еще раз."
            if lang == 'ru' else
            "😔 Afsuski, buyurtmani rasmiylashtirishda xatolik yuz berdi. Qaytadan urinib ko'ring."
        )
        await callback.message.edit_text(error_text)
        
    await callback.answer()


# ==========================================
# ОБРАБОТЧИКИ НАЖАТИЙ REPLY-МЕНЮ МАГАЗИНА
# ==========================================

async def show_category_products(message: Message, shop_id: int, category: str, state: FSMContext):
    user_id = message.from_user.id
    lang = UserRepository.get_user_language(user_id)
    shop = ShopRepository.get_shop_by_id(shop_id)
    if not shop:
        await message.answer("Магазин не найден." if lang == 'ru' else "Do'kon topilmadi.")
        return
        
    products = ProductRepository.get_products_by_category(shop_id, category)
    if not products:
        await message.answer("В этой категории нет товаров." if lang == 'ru' else "Ushbu kategoriyada mahsulotlar yo'q.")
        return
        
    product = products[0]
    is_fav = FavoriteRepository.is_favorite(user_id, product['id'])
    text = format_product_text(product, shop['name'], lang)
    
    reply_markup = get_product_detail_keyboard(
        product_id=product['id'],
        shop_id=shop_id,
        category=category,
        current_index=0,
        total_count=len(products),
        is_fav=is_fav,
        is_available=(product['stock_status'] == 1),
        lang=lang
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


@router.message(F.text & ~F.text.startswith("/"))
async def process_shop_menu_click(message: Message, state: FSMContext):
    text = message.text.strip()
    user_id = message.from_user.id
    lang = UserRepository.get_user_language(user_id)
    
    state_data = await state.get_data()
    shop_id = state_data.get('current_shop_id')
    
    if shop_id:
        categories = ProductRepository.get_categories_by_shop(shop_id)
        
        # 1. Если кликнули по категории
        if text in categories:
            await show_category_products(message, shop_id, text, state)
            return
            
        # 2. Если кликнули по поиску
        if text in {"🔍 Поиск по магазину", "🔍 Do'kon bo'yicha qidiruv"}:
            await state.update_data(search_shop_id=shop_id)
            await message.answer(get_text('search_prompt', lang), parse_mode="HTML")
            await state.set_state(SearchStates.waiting_for_query)
            return
            
        # 3. Если кликнули по возврату к списку магазинов
        if text in {"🔙 К списку магазинов", "🔙 Do'konlar ro'yxatiga"}:
            await state.clear()
            shops = ShopRepository.get_all_shops()
            if not shops:
                await message.answer(get_text('no_shops', lang), reply_markup=get_main_menu(user_id))
                return
                
            text_msg = get_text('shops_list_title', lang)
            exit_text = "Вы вышли из магазина." if lang == 'ru' else "Do'kondan chiqdingiz."
            await message.answer(exit_text, reply_markup=get_main_menu(user_id))
            await message.answer(text_msg, reply_markup=get_shops_list_keyboard(shops), parse_mode="HTML")
            return

