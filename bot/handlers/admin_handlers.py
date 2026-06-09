from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.filters import Command
from config import ADMIN_ID
from db.database import update_order_status, get_all_orders_for_export, get_all_users
from services.order_service import export_orders_to_csv

router = Router()

def is_admin(user_id):
    return str(user_id) == str(ADMIN_ID)

@router.callback_query(F.data.startswith("admin_done_"))
async def admin_done_order(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет прав.", show_alert=True)
        return
        
    order_id = int(callback.data.split("_")[2])
    user_id = update_order_status(order_id, "completed")
    
    await callback.message.edit_reply_markup()
    await callback.message.reply(f"✅ Статус заказа #{order_id} изменен на 'Выполнен'.")
    
    if user_id:
        try:
            await callback.bot.send_message(user_id, f"✅ <b>Ваш заказ #{order_id} выполнен и готов к выдаче!</b>", parse_mode="HTML")
        except:
            pass

@router.message(Command("export"))
async def export_orders(message: Message):
    if not is_admin(message.from_user.id):
        return
        
    orders_data = get_all_orders_for_export()
    if not orders_data:
        await message.answer("Нет заказов для выгрузки.")
        return
        
    csv_bytes = export_orders_to_csv(orders_data)
    file = BufferedInputFile(csv_bytes, filename="orders_export.csv")
    await message.answer_document(file, caption="📊 Выгрузка всех заказов (CSV)")

@router.message(Command("broadcast"))
async def broadcast_message(message: Message):
    if not is_admin(message.from_user.id):
        return
        
    text_to_send = message.text.replace("/broadcast", "").strip()
    if not text_to_send:
        await message.answer("Пожалуйста, введите текст для рассылки после команды /broadcast.\nПример: /broadcast Скидка 10% на все!")
        return
        
    users = get_all_users()
    success_count = 0
    
    for u_id in users:
        try:
            await message.bot.send_message(u_id, f"📢 <b>Уведомление от магазина:</b>\n\n{text_to_send}", parse_mode="HTML")
            success_count += 1
        except:
            pass
            
    await message.answer(f"✅ Рассылка завершена! Успешно отправлено {success_count} из {len(users)} пользователям.")
