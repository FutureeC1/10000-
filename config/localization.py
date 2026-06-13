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
        'btn_favorites': "⭐ Избранное",
        'btn_cart_menu': "🛒 Корзина",
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
        'btn_favorites': "⭐ Sevimlilar",
        'btn_cart_menu': "🛒 Savat",
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


CATEGORIES_TRANSLATION = {
    'ru': {
        'Клавиатуры': 'Клавиатуры',
        'Коврики': 'Коврики',
        'Мышки': 'Мышки',
        'Наушники': 'Наушники',
        'Готовые ПК': 'Готовые ПК',
        'Видеокарты': 'Видеокарты',
        'Процессоры': 'Процессоры',
    },
    'uz': {
        'Клавиатуры': 'Klaviaturalar',
        'Коврики': 'Kovriklar',
        'Мышки': 'Sichqonchalar',
        'Наушники': 'Quloqchinlar',
        'Готовые ПК': 'Tayyor PKlar',
        'Видеокарты': 'Videokartalar',
        'Процессоры': 'Protsessorlar',
    }
}

SHOP_DESC_TRANSLATION = {
    'Keyllect': {
        'ru': 'Магазин игровых аксессуаров премиум-класса. Клавиатуры, мышки, наушники, коврики.',
        'uz': "Premium darajadagi o'yin aksessuarlari do'koni. Klaviaturalar, sichqonchalar, quloqchinlar, kovriklar."
    },
    'GameZoneBuild': {
        'ru': 'Готовые игровые ПК, сборка компьютеров под заказ и качественные комплектующие.',
        'uz': "Tayyor o'yin shaxsiy kompyuterlari, buyurtma asosida kompyuter yig'ish va sifatli butlovchi qismlar."
    }
}

def get_localized_category(category_name: str, lang: str = 'ru') -> str:
    """Возвращает переведенное название категории."""
    lang_dict = CATEGORIES_TRANSLATION.get(lang, CATEGORIES_TRANSLATION['ru'])
    return lang_dict.get(category_name, category_name)

def get_localized_shop_desc(shop_name: str, default_desc: str, lang: str = 'ru') -> str:
    """Возвращает переведенное описание магазина."""
    if shop_name in SHOP_DESC_TRANSLATION:
        return SHOP_DESC_TRANSLATION[shop_name].get(lang, default_desc)
    return default_desc


PRODUCT_DESC_TRANSLATION = {
    'AJJAZ AK 820 AS Механическая ': {
        'ru': "Ajazz AK820 Dual Tone — это эргономичная и стильная механическая клавиатура, выполненная в компактном 75% форм-факторе. Благодаря продуманной раскладке из 82 клавиш она сохраняет стрелки и функциональный ряд F-кнопок, экономя до 25% пространства на рабочем столе. Главной особенностью модели является инновационная пятислойная система шумоподавления (Five Layer Noise Reduction), которая эффективно поглощает вибрации, обеспечивая мягкий ход клавиш и благородный, глухой звук при печати. В правом верхнем углу расположен элегантный металлический поворотный регулятор для плавной настройки громкости ПК. Клавиатура оснащена мягкой белой подсветкой клавиш, поддерживает функцию полного анти-гостинга (Anti-Ghosting) для точной регистрации одновременных нажатий и подключается через надежный съемный кабель USB Type-C.",
        'uz': "Ajazz AK820 Dual Tone — bu ixcham 75% formatda ishlab chiqarilgan ergonomik va zamonaviy mexanik klaviatura. 82 ta tugmachadan iborat o'ylangan joylashuvi tufayli u strelkalar va funksional F-tugmalar qatorini saqlab qoladi va ish stolidagi joyni 25% gacha tejaydi. Modelning asosiy xususiyati besh qatlamli shovqinni kamaytirish tizimi (Five Layer Noise Reduction) bo'lib, u tebranishlarni samarali yutadi, tugmachalarning yumshoq bosilishini va yoqimli tovushni ta'minlaydi. O'ng tomonda ovoz balandligini sozlash uchun aylanadigan metall regulyator joylashgan. Klaviatura oq yorug'lik bilan jihozlangan va olinadigan USB Type-C kabeli orqali ulanadi."
    },
    'CYBERLYNX RX75 PRO': {
        'ru': "Cyberlynx RX75 Pro в бело-голубом исполнении — это эстетичная и технологичная беспроводная механическая клавиатура, выполненная в популярном 75% форм-факторе. Модель сочетает в себе нежную пастельную расцветку, продвинутую конструкцию Gasket Mount и широкие возможности кастомизации благодаря идущим в комплекте дополнительным лавандовым кейкапам. Благодаря пятислойному шумоподавлению и премиальным механическим переключателям, клавиатура обеспечивает мягкий, изолированный от лишних вибраций ход клавиш и тихий, «чистый» звук при печати. Наличие боковых полупрозрачных RGB-полос создает потрясающий эффект рассеянного свечения на рабочем столе. Модель поддерживает три режима подключения (2.4 ГГц, Bluetooth и проводной Type-C), оснащена удобным металлическим роллером для регулировки звука и мощной батареей на 4000 мАч.",
        'uz': "Cyberlynx RX75 Pro oq-ko'k rangdagi — bu ommabop 75% formatdagi estetik va texnologik simsiz mexanik klaviatura. Model pastel ranglar, ilg'or Gasket Mount dizayni va lavanda rangidagi qo'shimcha tugmalar bilan ta'minlangan. Besh qatlamli shovqinni yutish tizimi va yuqori sifatli mexanik svitchlar tufayli u yumshoq va jim bosilishni ta'minlaydi. Ish stoli uchun RGB yon chiroqlari ajoyib nur taratadi. Model uch xil ulanish rejimini (2.4 GHz, Bluetooth va simli Type-C) qo'llab-quvvatlaydi, ovozni sozlash regulyatori va 4000 mA/soat quvvatli akkumulyatorga ega."
    },
    'Игровая мышь Xinmeng Zero 1 Max': {
        'ru': "Xinmeng Zero 1 Max — это ультралегкая беспроводная игровая мышь премиального уровня, созданная для максимальной точности в соревновательных киберспортивных дисциплинах. Обладая весом всего 53 грамма, девайс идеально оптимизирован для игроков с маленькими и средними ладонями, гарантируя безупречный контроль и маневренность. Мышь оснащена передовым оптическим сенсором PixArt PAW3395 и контроллером CX52860, что позволяет активировать технологию Dual 8K (частоту опроса до 8000 Гц как по проводу, так и по воздуху) для нулевой задержки ввода. Встроенные оптические переключатели Kailh на 100 миллионов нажатий имеют рекордное время отклика в 0.2 мс и полностью исключают случайные дабл-клики. Энергоэффективная начинка обеспечивает потрясающую автономность — более 125 часов active-гейминга на одном заряде.",
        'uz': "Xinmeng Zero 1 Max — bu professional kiber-sportchilar uchun mo'ljallangan, juda yengil simsiz premium o'yin sichqonchasi. Og'irligi bor-yo'g'i 53 gramm bo'lib, kichik va o'rta kaftli o'yinchilar uchun mukammal nazorat va tezkorlikni kafolatlaydi. Sichqoncha PixArt PAW3395 optik sensori va Dual 8K texnologiyasi (simli va simsiz holatda 8000 Hz gacha chastota) bilan jihozlangan. Kailh optik svitchlari 100 million bosishga chidamli va 0.2 ms javob qaytarish tezligiga ega. Energiyani tejaydigan tizimi bir marta quvvatlash orqali 125 soatdan ortiq faol ishlashni ta'minlaydi."
    },
    'ATK A9 NB ULTRA': {
        'ru': "ATK A9 NB Ultra — это беспроводная игровая мышь премиум-класса, разработанная для профессиональных киберспортсменов и требовательных геймеров. Главной особенностью этой версии является комплектная магнитная док-станция (ATK GEAR), которая служит не только стильным элементом рабочего стола для беспроводной зарядки мыши, но и обеспечивает невероятную частоту опроса до 8000 Гц (8K Polling Rate), сводя задержку ввода практически к нулю. Мышь имеет выверенную симметричную форму корпуса, подходящую для любого типа хвата (ладонного, когтевого или пальцевого). Сверхлегкая конструкция, топовый оптический сенсор флагманского уровня и долговечные оптические переключатели обеспечивают феноменальную точность, молниеносный отклик и безупречный трекинг в самых динамичных соревновательных шутерах.",
        'uz': "ATK A9 NB Ultra — bu professional kiber-sportchilar va talabchan geymerlar uchun ishlab chiqilgan simsiz premium o'yin sichqonchasi. Ushbu versiyaning asosiy xususiyati magnitli quvvatlash stansiyasi (ATK GEAR) hisoblanib, u sichqonchani simsiz quvvatlaydi va 8000 Hz gacha (8K Polling Rate) chastota bilan ta'minlab, kechikishlarni nolga tushiradi. Sichqoncha simmetrik korpusga ega bo'lib, har qanday tutish uslubiga mos keladi. Yuqori aniqlikdagi optik sensor va chidamli svitchlar dinamik o'yinlarda ajoyib aniqlikni ta'minlaydi."
    },
    'MCHOSE X9 Наушники ': {
        'ru': "MCHOSE X9 — это полноразмерные беспроводные игровые наушники флагманского уровня, созданные для полного погружения в игровой процесс. Гарнитура поддерживает три режима подключения: сверхбыстрый радиоканал 2.4 ГГц с минимальной задержкой звука для киберспорта, универсальный Bluetooth для смартфонов и ноутбуков, а также классический проводной режим. Мощные динамики с поддержкой виртуального объемного звука 7.1 позволяют идеально позиционировать шаги и выстрелы врагов в пространстве. Высокочувствительный гибкий микрофон с функцией шумоподавления гарантирует кристально чистую связь с тиммейтами. Мягкое регулируемое оголовье и эргономичные амбушюры снижают давление на голову, обеспечивая комфорт на протяжении всего дня, а стильная светодиодная подсветка на чашах подчеркивает премиальный геймерский статус девайса.",
        'uz': "MCHOSE X9 — bu o'yin jarayoniga to'liq sho'ng'ish uchun yaratilgan simsiz premium o'yin quloqchinlari. Uch xil ulanish rejimini qo'llab-quvvatlaydi: kiber-sport uchun 2.4 GHz tezkor radio-kanal, Bluetooth va simli ulanish. Virtual 7.1 hajmli ovoz tizimi raqiblar qadamlari va otilgan o'qlarni aniq yo'naltirish imkonini beradi. Shovqinni yutuvchi mikrofon jamoa bilan aniq aloqani ta'minlaydi. Yumshoq va ergonomik ambushyuralar kun bo'yi qulaylik yaratadi, LED yoritgich esa geymerlik uslubini to'ldiradi."
    },
    'HyperX Cloud III (проводные наушники)': {
        'ru': "HyperX Cloud III — это эволюция легендарной игровой гарнитуры Cloud II, созданная для геймеров, которым требуется безупречное качество звука, абсолютный комфорт и надежность. Наушники оснащены обновленными 53-мм динамиками, расположенными под анатомическим углом, что обеспечивает чистый, детализированный звук и мощный бас. Фирменная мягкая пена HyperX с эффектом памяти в амбушюрах и оголовье гарантирует максимальное удобство даже во время многочасовых игровых марафонов. Прочная металлическая конструкция легко выдерживает активное ежедневное использование. Модель получила улучшенный 10-мм съемный микрофон с функцией шумоподавления и встроенным сетчатым поп-фильтром для идеально чистой передачи голоса. Благодаря поддержке пространственного звука DTS Headphone:X Spatial Audio и универсальному набору интерфейсов (3.5 мм, USB-C, USB-A), гарнитура совместима с ПК, консолями и мобильными устройствами.",
        'uz': "HyperX Cloud III — afsonaviy Cloud II garniturasining yangilangan versiyasi bo'lib, mukammal ovoz sifati va uzoq muddatli qulaylikni ta'minlaydi. Quloqchinlar 53 mm o'lchamdagi yangilangan anatomik dinamiklar bilan jihozlangan. Xotira effektiga ega bo'lgan yumshoq HyperX ko'pigi ko'p soatlik o'yinlarda ham boshda qulay joylashishini kafolatlaydi. Kuchli metall konstruksiya kundalik faol foydalanishga bardosh beradi. Shovqinni tozalovchi 10 mm mikrofon ovozni tiniq uzatadi. DTS Headphone:X Spatial Audio va universal ulanish imkoniyati (3.5 mm, USB-C, USB-A) uni kompyuter, konsollar va telefonlarga ulashga imkon beradi."
    },
    'Коврик для мыши ATK Sky XSoft eSport Gaming': {
        'ru': "Высококлассный игровой коврик ATK Sky Xsoft Esports разработан специально для профессиональных геймеров и киберспортсменов. Мягкая подложка Xsoft из высокотехнологичного полиуретана обеспечивает идеальное сцепление с поверхностью стола и максимальный комфорт для запястья во время длительных игровых сессий. Особая текстура тканевого покрытия гарантирует безупречный баланс скорости (Speed) и контроля (Control), позволяя мыши идеально считывать микродвижения. Прошитые края по периметру защищают коврик от износа и расслоения, значительно продлевая срок его службы.",
        'uz': "Professional geymerlar va kiber-sportchilar uchun maxsus ishlab chiqilgan yuqori darajadagi ATK Sky Xsoft Esports o'yin gilamchasi. Yuqori texnologiyali poliuretandandan tayyorlangan yumshoq Xsoft asosi stol yuzasiga mahkam yopishadi va bilak uchun maksimal qulaylik yaratadi. Maxsus mato qoplamasi tezlik (Speed) va nazorat (Control) muvozanatini saqlab, sichqonchaning har bir harakatini aniq uzatadi. Tikilgan chetlari gilamchani tez eskirishdan himoya qiladi."
    },
    'Основные характеристики игрового коврика GravaStar ': {
        'ru': "GravaStar Gaming Mouse Pad XXL — это огромный игровой коврик премиум-класса, разработанный для создания стильного и функционального игрового пространства. Имея внушительные размеры 800×400 мм, он легко вмещает полноразмерную клавиатуру и оставляет огромную площадь для свободного перемещения мыши. Уникальный футуристический дизайн с геометрическими узорами и фирменным слоганом бренда идеально дополняет любую современную геймерскую сборку. Высококачественная гладкая тканевая поверхность обеспечивает безупречный баланс скорости скольжения и точности остановки (Speed/Control), снижая трение ножек мыши. Прорезиненное основание надежно фиксирует коврик на столе, предотвращая его смещение даже во время самых жестких игровых сессий, а плотная прошивка краев гарантирует долгий срок службы без растрепывания.",
        'uz': "GravaStar Gaming Mouse Pad XXL — bu zamonaviy va funksional geymerlik maydonini yaratish uchun mo'ljallangan katta hajmli premium o'yin gilamchasi. 800x400 mm o'lchamlari bilan u to'liq o'lchamli klaviaturani osongina sig'diradi va sichqoncha uchun juda ko'p joy qoldiradi. Futurististik dizayni har qanday zamonaviy o'yin tizimini bezaydi. Silliq mato qoplamasi tezlik va to'xtash muvozanatini (Speed/Control) ta'minlaydi. Rezina asosi esa qattiq o'yinlar paytida gilamcha siljishining oldini oladi."
    },
    'Готовая сборка с rtx5060 8gb': {
        'ru': "✔️Manitor 27 280hz\n✔️Plata B760 gigabyte \n✔️Cpu  i5 14400f\n✔️Cool rgb\n✔️DDR4 16gb \n✔️ssd/nvme 512 gb \n✔️gpu rtx5060 8gb \n✔️Keys 4fan\n✔️Blok 750w\n✔️Klava mehanika\n✔️Mishka rg  logitech102\n✔️Naushni rapoo\n✔️Korik 90x40 \n✔️Stul loft\n✔️Mebel loft\n✔️Setavoy mantaj+gigabyte\n✔️pilot mantaj uz kabel 2.5\n✔️Windows Runpadpro ",
        'uz': "✔️Monitor 27 280hz\n✔️Plata B760 gigabyte\n✔️Cpu i5 14400f\n✔️Kuler RGB\n✔️DDR4 16gb\n✔️SSD/NVMe 512 gb\n✔️Gpu rtx5060 8gb\n✔️Keys 4fan\n✔️Blok 750w\n✔️Klaviatur mehanika\n✔️Sichqoncha Logitech G102\n✔️Quloqchin Rapoo\n✔️Gilamcha 90x40\n✔️Stul loft\n✔️Mebel loft\n✔️Set montaji+gigabyte\n✔️Pilot montaj uz kabel 2.5\n✔️Windows Runpadpro"
    },
    'Монстр-ПК GameZone Apex Overlord': {
        'ru': "Топовое решение: Intel Core i9-14900KF, NVIDIA RTX 4090 24GB, 64GB DDR5, 2TB SSD, кастомное водяное охлаждение.",
        'uz': "Eng yuqori yechim: Intel Core i9-14900KF, NVIDIA RTX 4090 24GB, 64GB DDR5, 2TB SSD, maxsus suvli sovutish tizimi."
    },
    'GeForce RTX 4070 Ti Super 16GB': {
        'ru': "Отличная видеокарта для игр в 4K разрешении с поддержкой трассировки лучей и DLSS 3.0.",
        'uz': "4K o'yinlar uchun ajoyib videokarta bo'lib, nurlar trayektoriyasi (Ray Tracing) va DLSS 3.0 texnologiyasini qo'llab-quvvatlaydi."
    },
    'AMD Ryzen 7 7800X3D': {
        'ru': "Самый производительный игровой процессор на рынке с технологией 3D V-Cache.",
        'uz': "Bozordagi eng kuchli o'yin protsessori bo'lib, 3D V-Cache texnologiyasiga ega."
    }
}

def get_localized_product_desc(product_name: str, default_desc: str, lang: str = 'ru') -> str:
    """Возвращает переведенное описание товара."""
    if product_name in PRODUCT_DESC_TRANSLATION:
        return PRODUCT_DESC_TRANSLATION[product_name].get(lang, default_desc)
    return default_desc
