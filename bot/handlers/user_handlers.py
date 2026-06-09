from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.filters import CommandStart, Command
from bot.keyboards.keyboards import get_main_menu_keyboard, get_product_keyboard, get_cart_keyboard
from services.order_service import process_checkout, get_product_by_id
from db.database import register_user, add_to_cart, get_cart, clear_cart, get_user_orders
from config import PRODUCTS

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    register_user(message.from_user.id, message.from_user.username)
    text = (
        "Добро пожаловать в наш магазин! 👋\n"
        "Воспользуйтесь меню ниже для навигации."
    )
    await message.answer(text, reply_markup=get_main_menu_keyboard())

@router.message(F.text == "🛍 Каталог")
@router.message(Command("catalog"))
async def cmd_catalog(message: Message):
    if not PRODUCTS:
        return
    product = PRODUCTS[0]
    text = f"<b>{product['name']}</b>\n\n{product['desc']}\n\nЦена: ${product['price']:.2f}"
    await message.answer_photo(
        photo=product["image"],
        caption=text,
        reply_markup=get_product_keyboard(product['id'], 0, len(PRODUCTS)),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("catalog_"))
async def process_catalog_pagination(callback: CallbackQuery):
    index = int(callback.data.split("_")[1])
    product = PRODUCTS[index]
    text = f"<b>{product['name']}</b>\n\n{product['desc']}\n\nЦена: ${product['price']:.2f}"
    
    media = InputMediaPhoto(media=product["image"], caption=text, parse_mode="HTML")
    await callback.message.edit_media(
        media=media,
        reply_markup=get_product_keyboard(product['id'], index, len(PRODUCTS))
    )

@router.callback_query(F.data == "ignore")
async def process_ignore(callback: CallbackQuery):
    await callback.answer()

@router.callback_query(F.data.startswith("add_"))
async def process_add_to_cart(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    add_to_cart(callback.from_user.id, product_id)
    await callback.answer("Товар добавлен в корзину! 🛒", show_alert=False)

@router.message(F.text == "🛒 Корзина")
async def show_cart(message: Message):
    cart_items = get_cart(message.from_user.id)
    if not cart_items:
        await message.answer("Ваша корзина пуста. Перейдите в каталог, чтобы выбрать товары.")
        return
        
    text = "<b>🛒 Ваша корзина:</b>\n\n"
    total = 0
    for c_item in cart_items:
        p_id, qty = c_item
        product = get_product_by_id(p_id)
        if product:
            item_total = product['price'] * qty
            total += item_total
            text += f"- {product['name']} (x{qty}) = ${item_total:.2f}\n"
            
    text += f"\n<b>Итого: ${total:.2f}</b>"
    await message.answer(text, reply_markup=get_cart_keyboard(), parse_mode="HTML")

@router.callback_query(F.data == "clear_cart")
async def process_clear_cart(callback: CallbackQuery):
    clear_cart(callback.from_user.id)
    await callback.message.edit_text("Корзина очищена 🗑")

@router.callback_query(F.data == "checkout")
async def process_checkout_callback(callback: CallbackQuery):
    await callback.message.edit_reply_markup()
    success, result_text = await process_checkout(
        bot=callback.bot,
        user_id=callback.from_user.id,
        username=callback.from_user.username
    )
    await callback.message.answer(result_text, parse_mode="HTML")

@router.message(F.text == "📦 Мои заказы")
async def show_orders(message: Message):
    orders = get_user_orders(message.from_user.id)
    if not orders:
        await message.answer("У вас еще нет заказов.")
        return
    
    text = "<b>📦 Ваши последние заказы:</b>\n\n"
    for o in orders:
        status_emoji = "⏳" if o['status'] == 'new' else "✅"
        text += f"Заказ #{o['id']} - ${o['total_price']:.2f} [{status_emoji} {o['status']}]\n"
        text += f"Дата: {o['created_at']}\n\n"
        
    await message.answer(text, parse_mode="HTML")

@router.message(F.text == "ℹ️ О нас")
async def show_about(message: Message):
    text = (
        "☕️ <b>Лучшая кофейня в городе!</b>\n\n"
        "Мы готовим кофе из свежеобжаренных зерен.\n"
        "График работы: Пн-Вс, 08:00 - 22:00\n\n"
        "🎁 <b>Программа лояльности:</b>\n"
        "Каждый 6-й заказ мы дарим бесплатный кофе или десерт!"
    )
    await message.answer(text, parse_mode="HTML")
