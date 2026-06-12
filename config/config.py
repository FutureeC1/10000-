import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_PATH = os.getenv("DB_PATH", "shop.db")

# Глобальный супер-администратор всей платформы
try:
    ADMIN_ID = int(os.getenv("ADMIN_ID")) if os.getenv("ADMIN_ID") else None
except ValueError:
    ADMIN_ID = None

# Настройки для магазина KEYLLECT
try:
    KEYLLECT_OWNER_ID = int(os.getenv("KEYLLECT_OWNER_ID")) if os.getenv("KEYLLECT_OWNER_ID") else None
except ValueError:
    KEYLLECT_OWNER_ID = None
KEYLLECT_MANAGER_USERNAME = os.getenv("KEYLLECT_MANAGER_USERNAME", "Kas1mov_sa")

# Настройки для магазина GAMEZONEBUILD
try:
    GAMEZONEBUILD_OWNER_ID = int(os.getenv("GAMEZONEBUILD_OWNER_ID")) if os.getenv("GAMEZONEBUILD_OWNER_ID") else None
except ValueError:
    GAMEZONEBUILD_OWNER_ID = None
GAMEZONEBUILD_MANAGER_USERNAME = os.getenv("GAMEZONEBUILD_MANAGER_USERNAME", "Kas1mov_sa")

# Дефолтный менеджер платформы для совместимости импортов
MANAGER_USERNAME = os.getenv("MANAGER_USERNAME", "Kas1mov_sa")



def get_shop_config(shop_name_or_id) -> dict:
    """Возвращает настройки владельца и менеджера на основе названия или ID магазина."""
    name = str(shop_name_or_id).lower()
    
    if "keyllect" in name:
        return {
            "owner_id": KEYLLECT_OWNER_ID or ADMIN_ID,
            "manager_username": KEYLLECT_MANAGER_USERNAME
        }
    elif "gamezone" in name or "gzb" in name:
        return {
            "owner_id": GAMEZONEBUILD_OWNER_ID or ADMIN_ID,
            "manager_username": GAMEZONEBUILD_MANAGER_USERNAME
        }
    else:
        # По умолчанию возвращаем супер-админа
        return {
            "owner_id": ADMIN_ID,
            "manager_username": os.getenv("MANAGER_USERNAME", "Kas1mov_sa")
        }
