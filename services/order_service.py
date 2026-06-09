from aiogram import Bot
from config import ADMIN_ID, PRODUCTS
from db.database import create_order, clear_cart, get_cart, increment_user_orders, get_user_total_orders
import csv
from io import StringIO

def get_product_by_id(product_id: int):
    return next((p for p in PRODUCTS if p["id"] == product_id), None)

async def process_checkout(bot: Bot, user_id: int, username: str):
    cart_items = get_cart(user_id)
    if not cart_items:
        return False, "Ваша корзина пуста."
        
    items_to_save = []
    total_price = 0
    order_text_items = []
    
    for c_item in cart_items:
        p_id, qty = c_item
        product = get_product_by_id(p_id)
        if product:
            items_to_save.append({
                "name": product["name"],
                "quantity": qty,
                "price": product["price"]
            })
            total_price += product["price"] * qty
            order_text_items.append(f"{product['name']} (x{qty}) - ${product['price'] * qty:.2f}")

    # Check loyalty program (every 6th order)
    increment_user_orders(user_id)
    total_user_orders = get_user_total_orders(user_id)
    
    loyalty_text = ""
    if total_user_orders % 6 == 0:
         loyalty_text = "\n\n🎁 <b>Поздравляем! Это ваш 6-й заказ. Вы получаете бесплатный кофе или десерт при получении!</b>"
         
    username_str = username if username else str(user_id)
    order_id = create_order(user_id, total_price, items_to_save)
    clear_cart(user_id)
    
    # Notify Admin
    if ADMIN_ID:
        admin_text = (
            f"🛒 <b>Новый заказ #{order_id}</b>\n\n"
            f"👤 Клиент: @{username_str} ({user_id})\n"
            f"📦 Состав заказа:\n" + "\n".join(f"- {it}" for it in order_text_items) +
            f"\n\n💵 Сумма: ${total_price:.2f}"
        )
        try:
            from bot.keyboards.keyboards import get_admin_order_keyboard
            await bot.send_message(ADMIN_ID, admin_text, reply_markup=get_admin_order_keyboard(order_id), parse_mode="HTML")
        except Exception as e:
            print(f"Failed to notify admin: {e}")
            
    return True, f"✅ <b>Заказ #{order_id} успешно оформлен!</b>\n\nСумма: ${total_price:.2f}{loyalty_text}\n\nОжидайте уведомления о готовности."

def export_orders_to_csv(orders_data):
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Username', 'User ID', 'Total Price', 'Status', 'Created At', 'Items'])
    for row in orders_data:
        writer.writerow(row)
    
    output.seek(0)
    return output.read().encode('utf-8-sig') # returning bytes for aiogram
