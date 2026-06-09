import sqlite3
from typing import List, Tuple, Any
from config import DB_PATH

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            total_orders INTEGER DEFAULT 0
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total_price REAL NOT NULL,
            status TEXT DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cart (
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1,
            PRIMARY KEY (user_id, product_id)
        )
    """)
    
    conn.commit()
    conn.close()

def register_user(user_id: int, username: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    conn.close()

def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    conn.close()
    return [u[0] for u in users]

def increment_user_orders(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET total_orders = total_orders + 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_user_total_orders(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT total_orders FROM users WHERE user_id = ?", (user_id,))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else 0

def add_to_cart(user_id: int, product_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO cart (user_id, product_id, quantity)
        VALUES (?, ?, 1)
        ON CONFLICT(user_id, product_id) DO UPDATE SET quantity = quantity + 1
    """, (user_id, product_id))
    conn.commit()
    conn.close()

def get_cart(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT product_id, quantity FROM cart WHERE user_id = ?", (user_id,))
    res = cursor.fetchall()
    conn.close()
    return res

def clear_cart(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def create_order(user_id: int, total_price: float, items: list) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO orders (user_id, total_price) VALUES (?, ?)", (user_id, total_price))
    order_id = cursor.lastrowid
    
    for item in items:
        cursor.execute("""
            INSERT INTO order_items (order_id, product_name, quantity, price)
            VALUES (?, ?, ?, ?)
        """, (order_id, item['name'], item['quantity'], item['price']))
        
    conn.commit()
    conn.close()
    return order_id

def update_order_status(order_id: int, status: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
    cursor.execute("SELECT user_id FROM orders WHERE id = ?", (order_id,))
    res = cursor.fetchone()
    conn.commit()
    conn.close()
    return res[0] if res else None

def get_user_orders(user_id: int):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, total_price, status, created_at FROM orders WHERE user_id = ? ORDER BY id DESC LIMIT 5", (user_id,))
    res = cursor.fetchall()
    conn.close()
    return res

def get_all_orders_for_export():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT o.id, u.username, o.user_id, o.total_price, o.status, o.created_at,
               GROUP_CONCAT(oi.product_name || ' (x' || oi.quantity || ')', ', ')
        FROM orders o
        JOIN users u ON o.user_id = u.user_id
        JOIN order_items oi ON o.id = oi.order_id
        GROUP BY o.id
        ORDER BY o.id DESC
    """)
    res = cursor.fetchall()
    conn.close()
    return res
