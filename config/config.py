import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID")) if os.getenv("ADMIN_ID") else None
MANAGER_USERNAME = os.getenv("MANAGER_USERNAME", "keyllect_manager")
DB_PATH = os.getenv("DB_PATH", "shop.db")
