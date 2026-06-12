from aiogram.fsm.state import State, StatesGroup

class AddProductStates(StatesGroup):
    waiting_for_category = State()
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_price = State()
    waiting_for_is_discount = State()
    waiting_for_old_price = State()
    waiting_for_photo = State()
    waiting_for_is_available = State()

class UpdatePriceStates(StatesGroup):
    waiting_for_product_id = State()
    waiting_for_new_price = State()

class BroadcastStates(StatesGroup):
    waiting_for_message = State()
