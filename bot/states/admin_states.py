# pyrefly: ignore [missing-import]
from aiogram.fsm.state import State, StatesGroup

# Состояния для Супер-администратора
class AddShopStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_logo = State()
    waiting_for_telegram_username = State()
    waiting_for_owner_id = State()

# Состояния для Владельца магазина
class AddProductStates(StatesGroup):
    waiting_for_shop_id = State()
    waiting_for_category = State()
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_price = State()
    waiting_for_is_discount = State()
    waiting_for_old_price = State()
    waiting_for_photo = State()
    waiting_for_stock_status = State()

class UpdatePriceStates(StatesGroup):
    waiting_for_product_id = State()
    waiting_for_new_price = State()
