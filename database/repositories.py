from database.connection import get_db_connection
from typing import List, Dict, Any, Optional

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Таблица товаров
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            photo TEXT,
            is_discount INTEGER DEFAULT 0,
            old_price REAL,
            is_available INTEGER DEFAULT 1
        )
    """)
    
    # Таблица заказов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            full_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            product_id INTEGER NOT NULL,
            status TEXT DEFAULT 'Новый',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)
    
    # Таблица избранного
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
    """Репозиторий для работы с пользователями.
    Для перехода на PostgreSQL/SaaS достаточно переписать этот класс,
    сохраняя интерфейс методов, и добавить фильтрацию по shop_id."""
    
    @staticmethod
    def add_user(user_id: int, username: Optional[str], full_name: Optional[str]):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (user_id, username, full_name)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                full_name = excluded.full_name
        """, (user_id, username, full_name))
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
    def get_all_users() -> List[int]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users")
        rows = cursor.fetchall()
        conn.close()
        return [row['user_id'] for row in rows]

    @staticmethod
    def get_users_count() -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM users")
        row = cursor.fetchone()
        conn.close()
        return row['cnt'] if row else 0


class ProductRepository:
    """Репозиторий для работы с товарами."""

    @staticmethod
    def add_product(category: str, name: str, description: str, price: float, 
                    photo: str, is_discount: int = 0, old_price: Optional[float] = None, 
                    is_available: int = 1) -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO products (category, name, description, price, photo, is_discount, old_price, is_available)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (category, name, description, price, photo, is_discount, old_price, is_available))
        product_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return product_id

    @staticmethod
    def delete_product(product_id: int) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        return rows_affected > 0

    @staticmethod
    def update_product_price(product_id: int, price: float) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE products SET price = ? WHERE id = ?", (price, product_id))
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        return rows_affected > 0

    @staticmethod
    def update_product_availability(product_id: int, is_available: int) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE products SET is_available = ? WHERE id = ?", (is_available, product_id))
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        return rows_affected > 0

    @staticmethod
    def update_product_discount(product_id: int, is_discount: int, old_price: Optional[float]) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE products 
            SET is_discount = ?, old_price = ? 
            WHERE id = ?
        """, (is_discount, old_price, product_id))
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        return rows_affected > 0

    @staticmethod
    def get_product_by_id(product_id: int) -> Optional[dict]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_products_by_category(category: str) -> List[dict]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE category = ? ORDER BY id DESC", (category,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_all_products() -> List[dict]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_categories() -> List[str]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM products ORDER BY category")
        rows = cursor.fetchall()
        conn.close()
        return [row['category'] for row in rows]

    @staticmethod
    def search_products(query: str) -> List[dict]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE name LIKE ? AND is_available = 1 ORDER BY id DESC", (f"%{query}%",))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_products_count() -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM products")
        row = cursor.fetchone()
        conn.close()
        return row['cnt'] if row else 0


class OrderRepository:
    """Репозиторий для работы с заказами."""

    @staticmethod
    def create_order(user_id: int, full_name: str, phone: str, address: str, 
                     product_id: int, status: str = 'Новый') -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO orders (user_id, full_name, phone, address, product_id, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, full_name, phone, address, product_id, status))
        order_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return order_id

    @staticmethod
    def update_order_status(order_id: int, status: str) -> Optional[int]:
        """Обновляет статус заказа и возвращает user_id для уведомления."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
        cursor.execute("SELECT user_id FROM orders WHERE id = ?", (order_id,))
        row = cursor.fetchone()
        conn.commit()
        conn.close()
        return row['user_id'] if row else None

    @staticmethod
    def get_order_by_id(order_id: int) -> Optional[dict]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.*, p.name as product_name, p.price as product_price
            FROM orders o
            JOIN products p ON o.product_id = p.id
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
            SELECT o.*, p.name as product_name, p.price as product_price
            FROM orders o
            JOIN products p ON o.product_id = p.id
            WHERE o.user_id = ?
            ORDER BY o.id DESC
        """, (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_all_orders() -> List[dict]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.*, p.name as product_name, p.price as product_price
            FROM orders o
            JOIN products p ON o.product_id = p.id
            ORDER BY o.id DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_orders_count() -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM orders")
        row = cursor.fetchone()
        conn.close()
        return row['cnt'] if row else 0

    @staticmethod
    def get_completed_orders_count() -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM orders WHERE status = 'Завершен'")
        row = cursor.fetchone()
        conn.close()
        return row['cnt'] if row else 0


class FavoriteRepository:
    """Репозиторий для работы с избранными товарами."""

    @staticmethod
    def add_to_favorites(user_id: int, product_id: int) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO favorites (user_id, product_id)
                VALUES (?, ?)
            """, (user_id, product_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding to favorites: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def remove_from_favorites(user_id: int, product_id: int) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM favorites 
            WHERE user_id = ? AND product_id = ?
        """, (user_id, product_id))
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        return rows_affected > 0

    @staticmethod
    def is_favorite(user_id: int, product_id: int) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 1 FROM favorites 
            WHERE user_id = ? AND product_id = ?
        """, (user_id, product_id))
        row = cursor.fetchone()
        conn.close()
        return row is not None

    @staticmethod
    def get_user_favorites(user_id: int) -> List[dict]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*
            FROM favorites f
            JOIN products p ON f.product_id = p.id
            WHERE f.user_id = ? AND p.is_available = 1
            ORDER BY p.id DESC
        """, (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
