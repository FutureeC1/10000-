import csv
from io import StringIO
from aiogram import Bot
from config.config import ADMIN_ID
from database.repositories import OrderRepository, ProductRepository, UserRepository
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def export_orders_to_csv() -> bytes:
    orders_data = OrderRepository.get_all_orders()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'ID Заказа', 'User ID', 'Имя', 'Телефон', 'Адрес', 
        'ID Товара', 'Товар', 'Цена (сум/руб)', 'Статус', 'Дата'
    ])
    
    for order in orders_data:
        writer.writerow([
            order['id'],
            order['user_id'],
            order['full_name'],
            order['phone'],
            order['address'],
            order['product_id'],
            order['product_name'],
            order['product_price'],
            order['status'],
            order['created_at']
        ])
    
    output.seek(0)
    return output.read().encode('utf-8-sig')


async def create_new_order(bot: Bot, user_id: int, full_name: str, phone: str, 
                           address: str, product_id: int) -> Optional[int]:
    # Получаем товар
    product = ProductRepository.get_product_by_id(product_id)
    if not product:
        return None
        
    # Создаем заказ
    order_id = OrderRepository.create_order(
        user_id=user_id,
        full_name=full_name,
        phone=phone,
        address=address,
        product_id=product_id,
        status='Новый'
    )
    
    # Отправляем уведомление администратору
    if ADMIN_ID:
        try:
            # Формируем красивое сообщение для админа
            price_str = f"{product['price']} сум"
            if product['is_discount']:
                price_str = f"{product['price']} сум (🔥 Скидка, старая цена: {product['old_price']} сум)"
                
            admin_text = (
                f"📥 <b>Новый заказ #{order_id}</b>\n\n"
                f"👤 <b>Покупатель:</b> {full_name}\n"
                f"📞 <b>Телефон:</b> {phone}\n"
                f"📍 <b>Адрес доставки:</b> {address}\n\n"
                f"📦 <b>Товар:</b> {product['name']}\n"
                f"💰 <b>Цена:</b> {price_str}\n"
                f"⏱ <b>Статус:</b> Новый\n"
            )
            
            # Инлайн клавиатура для быстрого управления заказом администратором
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="✏️ Изменить статус", callback_data=f"adm_status_menu_{order_id}")
                ],
                [
                    InlineKeyboardButton(text="❌ Отменить заказ", callback_data=f"adm_change_status_{order_id}_Отменен"),
                    InlineKeyboardButton(text="✅ Завершить заказ", callback_data=f"adm_change_status_{order_id}_Завершен")
                ]
            ])
            
            await bot.send_message(ADMIN_ID, admin_text, reply_markup=keyboard, parse_mode="HTML")
        except Exception as e:
            print(f"Ошибка при отправке уведомления администратору: {e}")
            
    return order_id


async def notify_status_change(bot: Bot, order_id: int, new_status: str, user_id: int):
    status_emojis = {
        'Новый': '⏳',
        'Подтвержден': '✅',
        'В обработке': '⚙️',
        'Доставляется': '🚚',
        'Завершен': '🎉',
        'Отменен': '❌'
    }
    
    emoji = status_emojis.get(new_status, '🔔')
    order = OrderRepository.get_order_by_id(order_id)
    product_name = order['product_name'] if order else "Товар"
    
    msg_text = (
        f"{emoji} <b>Статус вашего заказа #{order_id} изменен!</b>\n\n"
        f"📦 <b>Товар:</b> {product_name}\n"
        f"🏷 <b>Новый статус:</b> {new_status}\n\n"
        f"Спасибо, что выбираете магазин Keyllect! ❤️"
    )
    
    try:
        await bot.send_message(user_id, msg_text, parse_mode="HTML")
    except Exception as e:
        print(f"Не удалось отправить уведомление о смене статуса пользователю {user_id}: {e}")
