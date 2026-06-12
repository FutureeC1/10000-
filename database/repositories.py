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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
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
    if ShopRepository.get_shops_count() > 0:
        return
        
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
        
    # 1. Создаем магазин Keyllect
    keyllect_id = ShopRepository.create_shop(
        name="Keyllect",
        description="Магазин игровых аксессуаров премиум-класса. Клавиатуры, мышки, наушники, коврики.",
        logo=None,
        telegram_username="keyllect_shop",
        owner_id=keyllect_owner
    )
    
    # 2. Создаем магазин GameZoneBuild
    gzb_id = ShopRepository.create_shop(
        name="GameZoneBuild",
        description="Готовые игровые ПК, сборка компьютеров под заказ и качественные комплектующие.",
        logo=None,
        telegram_username="gamezone_build",
        owner_id=gzb_owner
    )

    
    # --- Товары для Keyllect ---
    ProductRepository.add_product(
        shop_id=keyllect_id,
        category="Клавиатуры",
        name="Механическая клавиатура Keyllect K80 RGB",
        description="Механическая клавиатура с переключателями Gateron Red, горячей заменой (Hot-swap) и настраиваемой RGB подсветкой.",
        price=950000.0,
        photo="https://images.unsplash.com/photo-1595225476474-87563907a212?w=600",
        stock_status=1
    )
    ProductRepository.add_product(
        shop_id=keyllect_id,
        category="Мышки",
        name="Беспроводная мышь Keyllect Phantom Wireless",
        description="Ультралегкая игровая мышь (55 грамм), сенсор PixArt 3395, до 26000 DPI, частота опроса 4K Hz.",
        price=650000.0,
        photo="https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=600",
        stock_status=1
    )
    ProductRepository.add_product(
        shop_id=keyllect_id,
        category="Наушники",
        name="Гарнитура Keyllect SoundBlast Pro 7.1",
        description="Игровые наушники с виртуальным объемным звуком 7.1, съемным микрофоном с шумоподавлением и мягкими амбушюрами.",
        price=890000.0,
        photo="https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=600",
        stock_status=1
    )
    
    # --- Товары для GameZoneBuild ---
    ProductRepository.add_product(
        shop_id=gzb_id,
        category="Готовые ПК",
        name="Игровой ПК GameZone Apex Elite",
        description="Сбалансированная сборка: Intel Core i5-13400F, NVIDIA RTX 4060 Ti 8GB, 16GB DDR5, 1TB NVMe SSD. Идеально для Full HD и 2K гейминга.",
        price=14500000.0,
        photo="https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=600",
        stock_status=1
    )
    ProductRepository.add_product(
        shop_id=gzb_id,
        category="Игровые ПК",
        name="Монстр-ПК GameZone Apex Overlord",
        description="Топовое решение: Intel Core i9-14900KF, NVIDIA RTX 4090 24GB, 64GB DDR5, 2TB SSD, кастомное водяное охлаждение.",
        price=45000000.0,
        photo="https://images.unsplash.com/photo-1624705002806-5d72df19c3ad?w=600",
        stock_status=1
    )
    ProductRepository.add_product(
        shop_id=gzb_id,
        category="Видеокарты",
        name="GeForce RTX 4070 Ti Super 16GB",
        description="Отличная видеокарта для игр в 4K разрешении с поддержкой трассировки лучей и DLSS 3.0.",
        price=12400000.0,
        photo="https://images.unsplash.com/photo-1582213782179-e0d53f98f2ca?w=600",
        stock_status=1
    )
    ProductRepository.add_product(
        shop_id=gzb_id,
        category="Процессоры",
        name="AMD Ryzen 7 7800X3D",
        description="Самый производительный игровой процессор на рынке с технологией 3D V-Cache.",
        price=5100000.0,
        photo="https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=600",
        stock_status=1
    )

