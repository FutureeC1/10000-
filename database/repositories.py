import warnings
import warnings
import warnings
import warnings
from database.connection import get_db_connection
from typing import List, Dict, Any, Optional

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Таблица пользователей с ролями (SUPER_ADMIN, SHOP_OWNER, CUSTOMER)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            role TEXT DEFAULT 'CUSTOMER',
            language TEXT DEFAULT 'ru',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'ru'")
    except Exception:
        pass
    
    # 2. Таблица магазинов (tenant)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            logo TEXT,
            telegram_username TEXT,
            owner_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)
    
    # 3. Таблица товаров (привязана к shop_id)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            photo TEXT,
            stock_status INTEGER DEFAULT 1, -- 1 = В наличии, 0 = Нет в наличии
            is_discount INTEGER DEFAULT 0,
            old_price REAL,
            FOREIGN KEY (shop_id) REFERENCES shops(id) ON DELETE CASCADE
        )
    """)
    
    # 4. Таблица заказов (привязана к shop_id)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            full_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            product_id INTEGER NOT NULL,
            status TEXT DEFAULT 'Новый',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (shop_id) REFERENCES shops(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)
    
    # 5. Таблица избранного
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            PRIMARY KEY (user_id, product_id),
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()


class UserRepository:
    @staticmethod
    def add_user(user_id: int, username: Optional[str], full_name: Optional[str], role: str = 'CUSTOMER'):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Если пользователь уже существует, мы не перезаписываем его роль, если она отличается от CUSTOMER,
        # чтобы случайно не разжаловать админа/владельца.
        cursor.execute("""
            INSERT INTO users (user_id, username, full_name, role)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                full_name = excluded.full_name
        """, (user_id, username, full_name, role))
        conn.commit()
        conn.close()

    @staticmethod
    def update_user_role(user_id: int, role: str):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET role = ? WHERE user_id = ?", (role, user_id))
        conn.commit()
        conn.close()

    @staticmethod
    def update_user_language(user_id: int, language: str):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET language = ? WHERE user_id = ?", (language, user_id))
        conn.commit()
        conn.close()

    @staticmethod
    def get_user_language(user_id: int) -> str:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return row['language'] if row and row['language'] else 'ru'

    @staticmethod
    def get_user(user_id: int) -> Optional[dict]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_all_users() -> List[dict]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_users_count() -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM users")
        row = cursor.fetchone()
        conn.close()
        return row['cnt'] if row else 0


class ShopRepository:
    @staticmethod
    def create_shop(name: str, description: str, logo: Optional[str], 
                    telegram_username: Optional[str], owner_id: int) -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO shops (name, description, logo, telegram_username, owner_id)
            VALUES (?, ?, ?, ?, ?)
        """, (name, description, logo, telegram_username, owner_id))
        shop_id = cursor.lastrowid
        
        # Назначаем владельцу роль SHOP_OWNER, если он был CUSTOMER
        cursor.execute("UPDATE users SET role = 'SHOP_OWNER' WHERE user_id = ? AND role = 'CUSTOMER'", (owner_id,))
        
        conn.commit()
        conn.close()
        return shop_id

    @staticmethod
    def delete_shop(shop_id: int) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM shops WHERE id = ?", (shop_id,))
        rows = cursor.rowcount
        conn.commit()
        conn.close()
        return rows > 0

    @staticmethod
    def get_shop_by_id(shop_id: int) -> Optional[dict]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM shops WHERE id = ?", (shop_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_shop_by_name(name: str) -> Optional[dict]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM shops WHERE name = ?", (name,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_shops_by_owner(owner_id: int) -> List[dict]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM shops WHERE owner_id = ? ORDER BY id DESC", (owner_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_all_shops() -> List[dict]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM shops ORDER BY name")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_shops_count() -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM shops")
        row = cursor.fetchone()
        conn.close()
        return row['cnt'] if row else 0

    @staticmethod
    def is_shop_owner(user_id: int, shop_id: int) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM shops WHERE id = ? AND owner_id = ?", (shop_id, user_id))
        row = cursor.fetchone()
        conn.close()
        return row is not None


class ProductRepository:
    @staticmethod
    def add_product(shop_id: int, category: str, name: str, description: str, 
                    price: float, photo: Optional[str], stock_status: int = 1,
                    is_discount: int = 0, old_price: Optional[float] = None) -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO products (shop_id, category, name, description, price, photo, stock_status, is_discount, old_price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (shop_id, category, name, description, price, photo, stock_status, is_discount, old_price))
        product_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return product_id

    @staticmethod
    def get_product_by_name_and_shop(shop_id: int, name: str) -> Optional[dict]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE shop_id = ? AND name = ?", (shop_id, name))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def delete_product(product_id: int) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        rows = cursor.rowcount
        conn.commit()
        conn.close()
        return rows > 0

    @staticmethod
    def update_product_price(product_id: int, price: float) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE products SET price = ? WHERE id = ?", (price, product_id))
        rows = cursor.rowcount
        conn.commit()
        conn.close()
        return rows > 0

    @staticmethod
    def update_product_stock(product_id: int, stock_status: int) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE products SET stock_status = ? WHERE id = ?", (stock_status, product_id))
        rows = cursor.rowcount
        conn.commit()
        conn.close()
        return rows > 0

    @staticmethod
    def update_product_discount(product_id: int, is_discount: int, old_price: Optional[float]) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE products 
            SET is_discount = ?, old_price = ? 
            WHERE id = ?
        """, (is_discount, old_price, product_id))
        rows = cursor.rowcount
        conn.commit()
        conn.close()
        return rows > 0

    @staticmethod
    def get_product_by_id(product_id: int) -> Optional[dict]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_products_by_shop(shop_id: int) -> List[dict]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE shop_id = ? ORDER BY id DESC", (shop_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_products_by_category(shop_id: int, category: str) -> List[dict]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE shop_id = ? AND category = ? ORDER BY id DESC", (shop_id, category))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_categories_by_shop(shop_id: int) -> List[str]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM products WHERE shop_id = ? ORDER BY category", (shop_id,))
        rows = cursor.fetchall()
        conn.close()
        return [row['category'] for row in rows]

    @staticmethod
    def search_products(shop_id: int, query: str) -> List[dict]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM products 
            WHERE shop_id = ? AND name LIKE ? AND stock_status = 1 
            ORDER BY id DESC
        """, (shop_id, f"%{query}%"))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_products_count_by_shop(shop_id: int) -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM products WHERE shop_id = ?", (shop_id,))
        row = cursor.fetchone()
        conn.close()
        return row['cnt'] if row else 0

    @staticmethod
    def get_all_products_count() -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM products")
        row = cursor.fetchone()
        conn.close()
        return row['cnt'] if row else 0


class OrderRepository:
    @staticmethod
    def create_order(shop_id: int, user_id: int, full_name: str, phone: str, 
                     address: str, product_id: int, status: str = 'Новый') -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO orders (shop_id, user_id, full_name, phone, address, product_id, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (shop_id, user_id, full_name, phone, address, product_id, status))
        order_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return order_id

    @staticmethod
    def update_order_status(order_id: int, status: str) -> Optional[tuple]:
        """Обновляет статус заказа. Возвращает (user_id, shop_id) для уведомлений."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
        cursor.execute("SELECT user_id, shop_id FROM orders WHERE id = ?", (order_id,))
        row = cursor.fetchone()
        conn.commit()
        conn.close()
        return (row['user_id'], row['shop_id']) if row else None

    @staticmethod
    def get_order_by_id(order_id: int) -> Optional[dict]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.*, p.name as product_name, p.price as product_price, s.name as shop_name
            FROM orders o
            JOIN products p ON o.product_id = p.id
            JOIN shops s ON o.shop_id = s.id
            WHERE o.id = ?
        """, (order_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_user_orders(user_id: int) -> List[dict]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.*, p.name as product_name, p.price as product_price, s.name as shop_name
            FROM orders o
            JOIN products p ON o.product_id = p.id
            JOIN shops s ON o.shop_id = s.id
            WHERE o.user_id = ?
            ORDER BY o.id DESC
        """, (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_orders_by_shop(shop_id: int) -> List[dict]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.*, p.name as product_name, p.price as product_price
            FROM orders o
            JOIN products p ON o.product_id = p.id
            WHERE o.shop_id = ?
            ORDER BY o.id DESC
        """, (shop_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_all_orders() -> List[dict]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.*, p.name as product_name, p.price as product_price, s.name as shop_name
            FROM orders o
            JOIN products p ON o.product_id = p.id
            JOIN shops s ON o.shop_id = s.id
            ORDER BY o.id DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_orders_count_by_shop(shop_id: int) -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM orders WHERE shop_id = ?", (shop_id,))
        row = cursor.fetchone()
        conn.close()
        return row['cnt'] if row else 0

    @staticmethod
    def get_completed_orders_count_by_shop(shop_id: int) -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM orders WHERE shop_id = ? AND status = 'Завершен'", (shop_id,))
        row = cursor.fetchone()
        conn.close()
        return row['cnt'] if row else 0

    @staticmethod
    def get_all_orders_count() -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM orders")
        row = cursor.fetchone()
        conn.close()
        return row['cnt'] if row else 0

    @staticmethod
    def get_all_completed_orders_count() -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM orders WHERE status = 'Завершен'")
        row = cursor.fetchone()
        conn.close()
        return row['cnt'] if row else 0


class FavoriteRepository:
    @staticmethod
    def add_to_favorites(user_id: int, product_id: int) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT OR IGNORE INTO favorites (user_id, product_id) VALUES (?, ?)", (user_id, product_id))
            conn.commit()
            return True
        except Exception:
            return False
        finally:
            conn.close()

    @staticmethod
    def remove_from_favorites(user_id: int, product_id: int) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM favorites WHERE user_id = ? AND product_id = ?", (user_id, product_id))
        rows = cursor.rowcount
        conn.commit()
        conn.close()
        return rows > 0

    @staticmethod
    def is_favorite(user_id: int, product_id: int) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM favorites WHERE user_id = ? AND product_id = ?", (user_id, product_id))
        row = cursor.fetchone()
        conn.close()
        return row is not None

    @staticmethod
    def get_user_favorites(user_id: int) -> List[dict]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, s.name as shop_name
            FROM favorites f
            JOIN products p ON f.product_id = p.id
            JOIN shops s ON p.shop_id = s.id
            WHERE f.user_id = ? AND p.stock_status = 1
            ORDER BY p.id DESC
        """, (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


def seed_default_data(admin_id: int):
    """Наполнение базы данных начальными магазинами и товарами при первом запуске."""
    from config.config import KEYLLECT_OWNER_ID, GAMEZONEBUILD_OWNER_ID
    
    # Создаем запись супер-админа
    UserRepository.add_user(admin_id, "admin", "Платформа Администратор", role='SUPER_ADMIN')
    
    # Определяем ID владельцев
    keyllect_owner = KEYLLECT_OWNER_ID or admin_id
    gzb_owner = GAMEZONEBUILD_OWNER_ID or admin_id
    
    # Добавляем владельцев как пользователей в БД
    if not UserRepository.get_user(keyllect_owner):
        UserRepository.add_user(keyllect_owner, "keyllect_owner", "Владелец Keyllect", role='SHOP_OWNER')
    else:
        UserRepository.update_user_role(keyllect_owner, 'SHOP_OWNER')
        
    if not UserRepository.get_user(gzb_owner):
        UserRepository.add_user(gzb_owner, "gamezone_owner", "Владелец GameZoneBuild", role='SHOP_OWNER')
    else:
        UserRepository.update_user_role(gzb_owner, 'SHOP_OWNER')
        
    # 1. Создаем или получаем магазин Keyllect
    keyllect = ShopRepository.get_shop_by_name("Keyllect")
    if not keyllect:
        keyllect_id = ShopRepository.create_shop(
            name="Keyllect",
            description="Магазин игровых аксессуаров премиум-класса. Клавиатуры, мышки, наушники, коврики.",
            logo=None,
            telegram_username="keyllect_shop",
            owner_id=keyllect_owner
        )
    else:
        keyllect_id = keyllect['id']
        
    # 2. Создаем или получаем магазин GameZoneBuild
    gzb = ShopRepository.get_shop_by_name("GameZoneBuild")
    if not gzb:
        gzb_id = ShopRepository.create_shop(
            name="GameZoneBuild",
            description="Готовые игровые ПК, сборка компьютеров под заказ и качественные комплектующие.",
            logo=None,
            telegram_username="gamezone_build",
            owner_id=gzb_owner
        )
    else:
        gzb_id = gzb['id']

    # Вспомогательная функция для безопасного добавления товаров
    def add_product_if_not_exists(shop_id, category, name, description, price, photo, stock_status=1):
        if not ProductRepository.get_product_by_name_and_shop(shop_id, name):
            ProductRepository.add_product(
                shop_id=shop_id,
                category=category,
                name=name,
                description=description,
                price=price,
                photo=photo,
                stock_status=stock_status
            )
















    # --- Товары для Keyllect ---
    # клавиатуры
    add_product_if_not_exists(
        shop_id=keyllect_id,
        category="Клавиатуры",
        name="AJJAZ AK 820 AS Механическая ",
        description="Ajazz AK820 Dual Tone — это эргономичная и стильная механическая клавиатура, выполненная в компактном 75% форм-факторе. Благодаря продуманной раскладке из 82 клавиш она сохраняет стрелки и функциональный ряд F-кнопок, экономя до 25% пространства на рабочем столе. Главной особенностью модели является инновационная пятислойная система шумоподавления (Five Layer Noise Reduction), которая эффективно поглощает вибрации, обеспечивая мягкий ход клавиш и благородный, глухой звук при печати. В правом верхнем углу расположен элегантный металлический поворотный регулятор для плавной настройки громкости ПК. Клавиатура оснащена мягкой белой подсветкой клавиш, поддерживает функцию полного анти-гостинга (Anti-Ghosting) для точной регистрации одновременных нажатий и подключается через надежный съемный кабель USB Type-C.",
        price=445000,
        photo="https://cdn.phototourl.com/free/2026-06-13-a30176dc-9efe-411f-8883-41e8dba68976.jpg"
    )
    add_product_if_not_exists(
        shop_id=keyllect_id,
        category="Клавиатуры",
        name="CYBERLYNX RX75 PRO",
        description="Cyberlynx RX75 Pro в бело-голубом исполнении — это эстетичная и технологичная беспроводная механическая клавиатура, выполненная в популярном 75% форм-факторе. Модель сочетает в себе нежную пастельную расцветку, продвинутую конструкцию Gasket Mount и широкие возможности кастомизации благодаря идущим в комплекте дополнительным лавандовым кейкапам. Благодаря пятислойному шумоподавлению и премиальным механическим переключателям, клавиатура обеспечивает мягкий, изолированный от лишних вибраций ход клавиш и тихий, «чистый» звук при печати. Наличие боковых полупрозрачных RGB-полос создает потрясающий эффект рассеянного свечения на рабочем столе. Модель поддерживает три режима подключения (2.4 ГГц, Bluetooth и проводной Type-C), оснащена удобным металлическим роллером для регулировки звука и мощной батареей на 4000 мАч.",
        price=496000,
        photo="https://cdn.phototourl.com/free/2026-06-13-de69f743-0fac-48d9-abbc-39df5dc2baf5.jpg"
    )

    # мышки
    add_product_if_not_exists(
        shop_id=keyllect_id,
        category="Мышки",
        name="Игровая мышь Xinmeng Zero 1 Max",
        description="Xinmeng Zero 1 Max — это ультралегкая беспроводная игровая мышь премиального уровня, созданная для максимальной точности в соревновательных киберспортивных дисциплинах. Обладая весом всего 53 грамма, девайс идеально оптимизирован для игроков с маленькими и средними ладонями, гарантируя безупречный контроль и маневренность. Мышь оснащена передовым оптическим сенсором PixArt PAW3395 и контроллером CX52860, что позволяет активировать технологию Dual 8K (частоту опроса до 8000 Гц как по проводу, так и по воздуху) для нулевой задержки ввода. Встроенные оптические переключатели Kailh на 100 миллионов нажатий имеют рекордное время отклика в 0.2 мс и полностью исключают случайные дабл-клики. Энергоэффективная начинка обеспечивает потрясающую автономность — более 125 часов активного гейминга на одном заряде.",
        price=480000,
        photo="https://cdn.phototourl.com/free/2026-06-13-6cadf989-e14f-41f7-acd8-d79e6aaee993.jpg"
    )
    add_product_if_not_exists(
        shop_id=keyllect_id,
        category="Мышки",
        name="ATK A9 NB ULTRA",
        description="ATK A9 NB Ultra — это беспроводная игровая мышь премиум-класса, разработанная для профессиональных киберспортсменов и требовательных геймеров. Главной особенностью этой версии является комплектная магнитная док-станция (ATK GEAR), которая служит не только стильным элементом рабочего стола для беспроводной зарядки мыши, но и обеспечивает невероятную частоту опроса до 8000 Гц (8K Polling Rate), сводя задержку ввода практически к нулю. Мышь имеет выверенную симметричную форму корпуса, подходящую для любого типа хвата (ладонного, когтевого или пальцевого). Сверхлегкая конструкция, топовый оптический сенсор флагманского уровня и долговечные оптические переключатели обеспечивают феноменальную точность, молниеносный отклик и безупречный трекинг в самых динамичных соревновательных шутерах.",
        price=994000,
        photo="https://cdn.phototourl.com/free/2026-06-13-cf2ba9bf-0dab-4ef9-949b-2246eb99b646.jpg"
    )   

    # наушники
    add_product_if_not_exists(
        shop_id=keyllect_id,
        category="Наушники",
        name="MCHOSE X9 Наушники ",
        description="MCHOSE X9 — это полноразмерные беспроводные игровые наушники флагманского уровня, созданные для полного погружения в игровой процесс. Гарнитура поддерживает три режима подключения: сверхбыстрый радиоканал 2.4 ГГц с минимальной задержкой звука для киберспорта, универсальный Bluetooth для смартфонов и ноутбуков, а также классический проводной режим. Мощные динамики с поддержкой виртуального объемного звука 7.1 позволяют идеально позиционировать шаги и выстрелы врагов в пространстве. Высокочувствительный гибкий микрофон с функцией шумоподавления гарантирует кристально чистую связь с тиммейтами. Мягкое регулируемое оголовье и эргономичные амбушюры снижают давление на голову, обеспечивая комфорт на протяжении всего дня, а стильная светодиодная подсветка на чашах подчеркивает премиальный геймерский статус девайса.",
        price=730000,
        photo="https://cdn.phototourl.com/free/2026-06-13-cc169591-f5bf-411e-a63f-ffb349ff0af8.jpg"
    )
    add_product_if_not_exists(
        shop_id=keyllect_id,
        category="Наушники",
        name="HyperX Cloud III (проводные наушники)",
        description="HyperX Cloud III — это эволюция легендарной игровой гарнитуры Cloud II, созданная для геймеров, которым требуется безупречное качество звука, абсолютный комфорт и надежность. Наушники оснащены обновленными 53-мм динамиками, расположенными под анатомическим углом, что обеспечивает чистый, детализированный звук и мощный бас. Фирменная мягкая пена HyperX с эффектом памяти в амбушюрах и оголовье гарантирует максимальное удобство даже во время многочасовых игровых марафонов. Прочная металлическая конструкция легко выдерживает активное ежедневное использование. Модель получила улучшенный 10-мм съемный микрофон с функцией шумоподавления и встроенным сетчатым поп-фильтром для идеально чистой передачи голоса. Благодаря поддержке пространственного звука DTS Headphone:X Spatial Audio и универсальному набору интерфейсов (3.5 мм, USB-C, USB-A), гарнитура совместима с ПК, консолями и мобильными устройствами.",
        price=1114000,
        photo="https://cdn.phototourl.com/free/2026-06-13-0c19a77a-9fd9-4532-86b2-dc415dcb7f69.jpg"
    )
    
    # коврики
    add_product_if_not_exists(
        shop_id=keyllect_id,
        category="Коврики",
        name="Коврик для мыши ATK Sky XSoft eSport Gaming",
        description="Высококлассный игровой коврик ATK Sky Xsoft Esports разработан специально для профессиональных геймеров и киберспортсменов. Мягкая подложка Xsoft из высокотехнологичного полиуретана обеспечивает идеальное сцепление с поверхностью стола и максимальный комфорт для запястья во время длительных игровых сессий. Особая текстура тканевого покрытия гарантирует безупречный баланс скорости (Speed) и контроля (Control), позволяя мыши идеально считывать микродвижения. Прошитые края по периметру защищают коврик от износа и расслоения, значительно продлевая срок его службы.",
        price=240000,
        photo="https://cdn.phototourl.com/free/2026-06-13-677eb4c7-401e-4bd6-943b-2c07193ec9e5.jpg"
    )

    add_product_if_not_exists(
        shop_id=keyllect_id,
        category="Коврики",
        name="Основные характеристики игрового коврика GravaStar ",
        description="GravaStar Gaming Mouse Pad XXL — это огромный игровой коврик премиум-класса, разработанный для создания стильного и функционального игрового пространства. Имея внушительные размеры 800×400 мм, он легко вмещает полноразмерную клавиатуру и оставляет огромную площадь для свободного перемещения мыши. Уникальный футуристический дизайн с геометрическими узорами и фирменным слоганом бренда идеально дополняет любую современную геймерскую сборку. Высококачественная гладкая тканевая поверхность обеспечивает безупречный баланс скорости скольжения и точности остановки (Speed/Control), снижая трение ножек мыши. Прорезиненное основание надежно фиксирует коврик на столе, предотвращая его смещение даже во время самых жестких игровых сессий, а плотная прошивка краев гарантирует долгий срок службы без растрепывания.",
        price=130000,
        photo="https://cdn.phototourl.com/free/2026-06-13-29dd83e3-038b-4b37-8525-864f914191b2.jpg"
    )



















    # --- Товары для GameZoneBuild ---
    add_product_if_not_exists(
        shop_id=gzb_id,
        category="Готовые ПК",
        name="Готовая сборка с rtx5060 8gb",
        description="✔️Manitor 27 280hz\n✔️Plata B760 gigabyte \n✔️Cpu  i5 14400f\n✔️Cool rgb\n✔️DDR4 16gb \n✔️ssd/nvme 512 gb \n✔️gpu rtx5060 8gb \n✔️Keys 4fan\n✔️Blok 750w\n✔️Klava mehanika\n✔️Mishka rg  logitech102\n✔️Naushni rapoo\n✔️Korik 90x40 \n✔️Stul loft\n✔️Mebel loft\n✔️Setavoy mantaj+gigabyte\n✔️pilot mantaj uz kabel 2.5\n✔️Windows Runpadpro ",
        price=1170,
        photo="https://cdn.phototourl.com/free/2026-06-13-e6329297-49c6-4f26-9858-4925e14397ff.jpg"
    )
    add_product_if_not_exists(
        shop_id=gzb_id,
        category="Готовые ПК",
        name="Монстр-ПК GameZone Apex Overlord",
        description="Топовое решение: Intel Core i9-14900KF, NVIDIA RTX 4090 24GB, 64GB DDR5, 2TB SSD, кастомное водяное охлаждение.",
        price=3600.0,
        photo="https://images.unsplash.com/photo-1624705002806-5d72df19c3ad?w=600"
    )
    add_product_if_not_exists(
        shop_id=gzb_id,
        category="Видеокарты",
        name="GeForce RTX 4070 Ti Super 16GB",
        description="Отличная видеокарта для игр в 4K разрешении с поддержкой трассировки лучей и DLSS 3.0.",
        price=990.0,
        photo="https://images.unsplash.com/photo-1582213782179-e0d53f98f2ca?w=600"
    )
    add_product_if_not_exists(
        shop_id=gzb_id,
        category="Процессоры",
        name="AMD Ryzen 7 7800X3D",
        description="Самый производительный игровой процессор на рынке с технологией 3D V-Cache.",
        price=410.0,
        photo="https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=600"
    )

    # Принудительно обновим существующие цены в БД на доллары, если они были сохранены в сумах
    import sqlite3
    from config.config import DATABASE_PATH
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET price = 1150.0 WHERE shop_id = ? AND name = ? AND price > 100000", (gzb_id, "Игровой ПК GameZone Apex Elite"))
    conn.commit()
    conn.close()


