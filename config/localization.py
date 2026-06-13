# config/localization.py

LOCALIZATION = {
    'ru': {
        'welcome_no_shops': "👋 <b>Добро пожаловать!</b>\n\n🏪 В системе пока нет зарегистрированных магазинов. Загляните позже!",
        'welcome_shops': "👋 <b>Добро пожаловать в мульти-магазинную платформу!</b>\n\nВыберите магазин из списка ниже, чтобы перейти в его каталог:",
        'shops_list_title': "🏪 <b>Список доступных магазинов:</b>\n\nВыберите магазин из списка ниже, чтобы перейти в его каталог:",
        'no_shops': "😔 В системе пока нет зарегистрированных магазинов. Загляните позже!",
        
        # Кнопки меню
        'btn_shops': "🏪 Магазины",
        'btn_orders': "📦 Мои заказы",
        'btn_lang': "🌐 Язык / Til",
        
        # Выбор языка
        'select_language': "🌐 <b>Выберите язык / Tilni tanlang:</b>",
        'language_selected': "✅ Язык успешно изменен на Русский!",
        
        # Магазин
        'shop_title': "🏪 <b>Магазин: {name}</b>\n📝 {description}\n\n📁 Выберите категорию товаров на клавиатуре внизу!",
        'btn_search': "🔍 Поиск по магазину",
        'btn_back_to_shops': "🔙 К списку магазинов",
        'btn_back': "🔙 Назад",
        'btn_add_to_cart': "🛒 Добавить в корзину",
        'btn_cart_view': "🛒 Корзина",
        'btn_favorite': "❤️ В избранное",
        'btn_unfavorite': "💔 Из избранного",
        'btn_checkout': "🛍 Оформить заказ",
        'btn_clear_cart': "🗑 Очистить корзину",
        
        # Корзина и Избранное
        'cart_empty': "🛒 Ваша корзина пуста.",
        'cart_title': "🛒 <b>Ваша корзина:</b>\n\n",
        'cart_item': "• <b>{name}</b> — {price:,.2f} UZS\n",
        'cart_total': "\n💵 <b>Итого к оплате:</b> {total:,.2f} UZS",
        'favorite_added': "❤️ Товар добавлен в избранное!",
        'favorite_removed': "💔 Товар удален из избранного!",
        'cart_added': "✅ Товар добавлен в корзину!",
        'cart_cleared': "🗑 Корзина очищена!",
        
        # Поиск
        'search_prompt': "🔍 <b>Введите название товара для поиска в этом магазине:</b>",
        'search_no_results': "🔍 По запросу «{query}» ничего не найдено.",
        'search_results': "🔍 Результаты поиска по запросу «{query}»:",
        
        # Оформление заказа
        'checkout_name_prompt': "👤 <b>Введите ваше имя:</b>",
        'checkout_phone_prompt': "📞 <b>Введите ваш номер телефона (в формате +998...):</b>",
        'checkout_address_prompt': "📍 <b>Введите адрес доставки:</b>",
        'checkout_confirm_prompt': (
            "📝 <b>Проверьте данные заказа:</b>\n\n"
            "👤 Имя: <b>{name}</b>\n"
            "📞 Телефон: <b>{phone}</b>\n"
            "📍 Адрес: <b>{address}</b>\n\n"
            "<b>Товары:</b>\n{products}\n"
            "💵 <b>Итого к оплате:</b> {total:,.2f} UZS\n\n"
            "Подтверждаете заказ?"
        ),
        'checkout_confirmed': "🎉 <b>Заказ успешно оформлен!</b>\n\nМенеджер свяжется с вами в ближайшее время.",
        
        # Мои заказы
        'my_orders_empty': "📦 У вас пока нет оформленных заказов.",
        'my_orders_title': "📦 <b>Ваши заказы:</b>\n\n",
        'order_format': (
            "🔢 <b>Заказ №{id}</b>\n"
            "🏪 Магазин: <b>{shop_name}</b>\n"
            "📦 Товар: <b>{product_name}</b>\n"
            "💵 Цена: {price:,.2f} UZS\n"
            "📊 Статус: <b>{status}</b>\n"
            "📅 Дата: {date}\n"
            "------------------------\n"
        ),
        
        # Владелец
        'owner_access_denied': "❌ У вас нет прав для управления этим магазином.",
        'owner_shop_not_found': "❌ Магазин с таким кодом не найден в системе.",
    },
    'uz': {
        'welcome_no_shops': "👋 <b>Xush kelibsiz!</b>\n\n🏪 Tizimda hali ro'yxatdan o'tgan do'konlar yo'q. Keyinroq kiring!",
        'welcome_shops': "👋 <b>Multi-do'kon platformasiga xush kelibsiz!</b>\n\nKatalogga o'tish uchun quyidagi ro'yxatdan do'konni tanlang:",
        'shops_list_title': "🏪 <b>Mavjud do'konlar ro'yxati:</b>\n\nKatalogga o'tish uchun quyidagi ro'yxatdan do'konni tanlang:",
        'no_shops': "😔 Tizimda hali ro'yxatdan o'tgan do'konlar yo'q. Keyinroq kiring!",
        
        # Кнопки меню
        'btn_shops': "🏪 Do'konlar",
        'btn_orders': "📦 Buyurtmalarim",
        'btn_lang': "🌐 Til / Язык",
        
        # Выбор языка
        'select_language': "🌐 <b>Tilni tanlang / Выберите язык:</b>",
        'language_selected': "✅ Til O'zbekchaga muvaffaqiyatli o'zgartirildi!",
        
        # Магазин
        'shop_title': "🏪 <b>Do'kon: {name}</b>\n📝 {description}\n\n📁 Quyidagi klaviaturadan mahsulot kategoriyasini tanlang!",
        'btn_search': "🔍 Do'kon bo'yicha qidiruv",
        'btn_back_to_shops': "🔙 Do'konlar ro'yxatiga",
        'btn_back': "🔙 Orqaga",
        'btn_add_to_cart': "🛒 Savatga qo'shish",
        'btn_cart_view': "🛒 Savat",
        'btn_favorite': "❤️ Sevimlilarga",
        'btn_unfavorite': "💔 Sevimlilardan o'chirish",
        'btn_checkout': "🛍 Buyurtma berish",
        'btn_clear_cart': "🗑 Savatni tozalash",
        
        # Корзина и Избранное
        'cart_empty': "🛒 Savatingiz bo'sh.",
        'cart_title': "🛒 <b>Savatingiz:</b>\n\n",
        'cart_item': "• <b>{name}</b> — {price:,.2f} UZS\n",
        'cart_total': "\n💵 <b>Jami to'lov:</b> {total:,.2f} UZS",
        'favorite_added': "❤️ Mahsulot sevimlilarga qo'shildi!",
        'favorite_removed': "💔 Mahsulot sevimlilardan o'chirildi!",
        'cart_added': "✅ Mahsulot savatga qo'shildi!",
        'cart_cleared': "🗑 Savat tozalandi!",
        
        # Поиск
        'search_prompt': "🔍 <b>Ushbu do'kondan qidirish uchun mahsulot nomini kiriting:</b>",
        'search_no_results': "🔍 «{query}» so'rovi bo'yicha hech narsa topilmadi.",
        'search_results': "🔍 «{query}» so'rovi bo'yicha qidiruv natijalari:",
        
        # Оформление заказа
        'checkout_name_prompt': "👤 <b>Ismingizni kiriting:</b>",
        'checkout_phone_prompt': "📞 <b>Telefon raqamingizni kiriting (+998... formatida):</b>",
        'checkout_address_prompt': "📍 <b>Yetkazib berish manzilini kiriting:</b>",
        'checkout_confirm_prompt': (
            "📝 <b>Buyurtma ma'lumotlarini tekshiring:</b>\n\n"
            "👤 Ism: <b>{name}</b>\n"
            "📞 Telefon: <b>{phone}</b>\n"
            "📍 Manzil: <b>{address}</b>\n\n"
            "<b>Mahsulotlar:</b>\n{products}\n"
            "💵 <b>Jami to'lov:</b> {total:,.2f} UZS\n\n"
            "Buyurtmani tasdiqlaysizmi?"
        ),
        'checkout_confirmed': "🎉 <b>Buyurtma muvaffaqiyatli rasmiylashtirildi!</b>\n\nTez orada menejer siz bilan bog'lanadi.",
        
        # Мои заказы
        'my_orders_empty': "📦 Sizda hali rasmiylashtirilgan buyurtmalar yo'q.",
        'my_orders_title': "📦 <b>Buyurtmalaringiz:</b>\n\n",
        'order_format': (
            "🔢 <b>Buyurtma №{id}</b>\n"
            "🏪 Do'kon: <b>{shop_name}</b>\n"
            "📦 Mahsulot: <b>{product_name}</b>\n"
            "💵 Narxi: {price:,.2f} UZS\n"
            "📊 Status: <b>{status}</b>\n"
            "📅 Sana: {date}\n"
            "------------------------\n"
        ),
        
        # Владелец
        'owner_access_denied': "❌ Sizda ushbu do'konni boshqarish huquqi yo'q.",
        'owner_shop_not_found': "❌ Tizimda bunday kodli do'kon topilmadi.",
    }
}

def get_text(key: str, lang: str = 'ru', **kwargs) -> str:
    """Возвращает локализованный текст по ключу."""
    lang_dict = LOCALIZATION.get(lang, LOCALIZATION['ru'])
    text_template = lang_dict.get(key, LOCALIZATION['ru'].get(key, key))
    try:
        return text_template.format(**kwargs)
    except Exception:
        return text_template
