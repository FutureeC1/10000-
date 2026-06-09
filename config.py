import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
DB_PATH = "shop.db"

PRODUCTS = [
    {"id": 1, "name": "Эспрессо", "price": 2.50, "desc": "Крепкий классический эспрессо. Идеально для начала дня.", "image": "https://images.unsplash.com/photo-1510591509098-f4fdc6d0ff04?auto=format&fit=crop&w=800&q=80"},
    {"id": 2, "name": "Латте", "price": 3.50, "desc": "Нежный латте с густой молочной пенкой и мягким вкусом.", "image": "https://images.unsplash.com/photo-1570968915860-54d5c301fa9f?auto=format&fit=crop&w=800&q=80"},
    {"id": 3, "name": "Капучино", "price": 3.00, "desc": "Капучино с идеальным балансом кофе и молока.", "image": "https://images.unsplash.com/photo-1534778101976-62847782c213?auto=format&fit=crop&w=800&q=80"},
    {"id": 4, "name": "Круассан", "price": 2.00, "desc": "Свежий хрустящий французский круассан.", "image": "https://images.unsplash.com/photo-1555507036-ab1f4038808a?auto=format&fit=crop&w=800&q=80"},
]
