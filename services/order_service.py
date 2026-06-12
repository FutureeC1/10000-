import csv
from io import StringIO
from aiogram import Bot
from database.repositories import OrderRepository, ProductRepository, ShopRepository
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Optional

def export_all_orders_to_csv() -> bytes:
    """Экспорт всех заказов системы (для SUPER_ADMIN)."""
    orders_data = OrderRepository.get_all_orders()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'ID Заказа', 'Магазин ID', 'Магазин', 'User ID', 'Имя', 'Телефон', 'Адрес', 
        'ID Товара', 'Товар', 'Цена (сум)', 'Статус', 'Дата'
    ])
    
    for order in orders_data:
        writer.writerow([
            order['id'],
            order['shop_id'],
            order['shop_name'],
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


def export_shop_orders_to_csv(shop_id: int) -> bytes:
    """Экспорт заказов конкретного магазина (для SHOP_OWNER)."""
    orders_data = OrderRepository.get_orders_by_shop(shop_id)
    shop = ShopRepository.get_shop_by_id(shop_id)
    shop_name = shop['name'] if shop else f"Shop #{shop_id}"
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'ID Заказа', 'Магазин', 'User ID', 'Имя', 'Телефон', 'Адрес', 
        'ID Товара', 'Товар', 'Цена (сум)', 'Статус', 'Дата'
    ])
    
    for order in orders_data:
        writer.writerow([
            order['id'],
            shop_name,
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


async def create_new_order(bot: Bot, shop_id: int, user_id: int, full_name: str, 
                           phone: str, address: str, product_id: int) -> Optional[int]:
    # Получаем товар
    product = ProductRepository.get_product_by_id(product_id)
    if not product:
        return None
        
    # Создаем заказ в БД
    order_id = OrderRepository.create_order(
        shop_id=shop_id,
        user_id=user_id,
        full_name=full_name,
        phone=phone,
        address=address,
        product_id=product_id,
        status='Новый'
    )
    
    # Находим магазин и его владельца
    shop = ShopRepository.get_shop_by_id(shop_id)
    if not shop:
        return order_id
        
    owner_id = shop['owner_id']
    
    # Отправляем уведомление Владельцу Магазина (а не супер-админу!)
    try:
        price_str = f"{product['price']:,} сум"
        if product['is_discount']:
            price_str = f"{product['price']:,} сум (🔥 Скидка, старая цена: {product['old_price']:,} сум)"
            
        owner_text = (
            f"📥 <b>Новый заказ #{order_id} в магазине «{shop['name']}»</b>\n\n"
            f"👤 <b>Покупатель:</b> {full_name}\n"
            f"📞 <b>Телефон:</b> {phone}\n"
            f"📍 <b>Адрес доставки:</b> {address}\n\n"
            f"📦 <b>Товар:</b> {product['name']}\n"
            f"💰 <b>Цена:</b> {price_str}\n"
            f"⏱ <b>Статус:</b> Новый\n"
        )
        
        # Инлайн клавиатура для быстрого управления заказом владельцем магазина
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                # adm_status_menu_ у нас останется, но мы обработаем его в owner_handlers.py!
                InlineKeyboardButton(text="✏️ Изменить статус", callback_data=f"own_status_menu_{order_id}")
            ],
            [
                InlineKeyboardButton(text="❌ Отменить", callback_data=f"own_change_status_{order_id}_Отменен"),
                InlineKeyboardButton(text="✅ Завершить", callback_data=f"own_change_status_{order_id}_Завершен")
            ]
        ])
        
        await bot.send_message(owner_id, owner_text, reply_markup=keyboard, parse_mode="HTML")
    except Exception as e:
        print(f"Ошибка при отправке уведомления владельцу магазина: {e}")
        
    return order_id


async def notify_status_change(bot: Bot, order_id: int, new_status: str, user_id: int, shop_id: int):
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
    shop = ShopRepository.get_shop_by_id(shop_id)
    
    shop_name = shop['name'] if shop else "Магазин"
    product_name = order['product_name'] if order else "Товар"
    
    msg_text = (
        f"{emoji} <b>Статус вашего заказа #{order_id} изменен!</b>\n\n"
        f"🏪 <b>Магазин:</b> {shop_name}\n"
        f"📦 <b>Товар:</b> {product_name}\n"
        f"🏷 <b>Новый статус:</b> {new_status}\n\n"
        f"Спасибо за покупку! ❤️"
    )
    
    try:
        await bot.send_message(user_id, msg_text, parse_mode="HTML")
    except Exception as e:
        print(f"Не удалось отправить уведомление о смене статуса пользователю {user_id}: {e}")
