import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, BaseFilter
from aiogram.fsm.context import FSMContext

from config.config import ADMIN_ID
from database.repositories import UserRepository, ShopRepository, ProductRepository, OrderRepository
from bot.keyboards.inline import (
    get_superadmin_main_keyboard,
    get_superadmin_delete_shops_keyboard
)
from bot.states.admin_states import AddShopStates
from services.stats_service import get_superadmin_stats

router = Router()

class SuperAdminFilter(BaseFilter):
    """Фильтр для проверки прав SUPER_ADMIN."""
    async def __call__(self, obj) -> bool:
        user_id = obj.from_user.id
        return ADMIN_ID is not None and user_id == ADMIN_ID


# Применяем фильтр ко всем хендлерам роутера супер-админа
router.message.filter(SuperAdminFilter())
router.callback_query.filter(SuperAdminFilter())


@router.message(Command("adminkeyllect"))
@router.message(F.text == "🛡 Супер-админка")
async def cmd_superadmin(message: Message, state: FSMContext):
    await state.clear()
    text = (
        "🛡 <b>Панель СУПЕР-АДМИНИСТРАТОРА платформы</b>\n\n"
        "Вы можете управлять магазинами системы, назначать владельцев и просматривать глобальную аналитику.\n\n"
        "Выберите необходимое действие:"
    )
    await message.answer(text, reply_markup=get_superadmin_main_keyboard(), parse_mode="HTML")


@router.callback_query(F.data == "sa_back")
async def callback_sa_back(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    text = (
        "🛡 <b>Панель СУПЕР-АДМИНИСТРАТОРА платформы</b>\n\n"
        "Выберите необходимое действие:"
    )
    await callback.message.edit_text(text, reply_markup=get_superadmin_main_keyboard(), parse_mode="HTML")
    await callback.answer()


# ==========================================
# ДОБАВЛЕНИЕ МАГАЗИНА (FSM)
# ==========================================

@router.callback_query(F.data == "sa_add_shop")
async def callback_sa_add_shop_start(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "📝 <b>Добавление нового магазина</b>\n\n"
        "Шаг 1 из 5: Введите <b>Название</b> магазина (например: <code>PC Builder</code>):",
        parse_mode="HTML"
    )
    await state.set_state(AddShopStates.waiting_for_name)
    await callback.answer()


@router.message(AddShopStates.waiting_for_name)
async def process_sa_shop_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("Пожалуйста, введите корректное название магазина:")
        return
        
    await state.update_data(name=name)
    await message.answer(
        "Шаг 2 из 5: Введите <b>Описание</b> магазина (какие товары продает, условия):"
    )
    await state.set_state(AddShopStates.waiting_for_description)


@router.message(AddShopStates.waiting_for_description)
async def process_sa_shop_desc(message: Message, state: FSMContext):
    description = message.text.strip()
    await state.update_data(description=description)
    await message.answer(
        "Шаг 3 из 5: Отправьте <b>ссылку на фото логотипа</b> магазина (или напишите «нет» для магазина без логотипа):"
    )
    await state.set_state(AddShopStates.waiting_for_logo)


@router.message(AddShopStates.waiting_for_logo)
async def process_sa_shop_logo(message: Message, state: FSMContext):
    logo = message.text.strip()
    if logo.lower() == "нет":
        logo = None
        
    await state.update_data(logo=logo)
    await message.answer(
        "Шаг 4 из 5: Введите <b>Telegram-username владельца</b> (например, <code>@owner_username</code>):"
    )
    await state.set_state(AddShopStates.waiting_for_telegram_username)


@router.message(AddShopStates.waiting_for_telegram_username)
async def process_sa_shop_username(message: Message, state: FSMContext):
    username = message.text.strip()
    if username.startswith('@'):
        username = username[1:]
        
    await state.update_data(telegram_username=username)
    await message.answer(
        "Шаг 5 из 5: Введите числовой <b>Telegram ID владельца</b> магазина (owner_id):\n"
        "<i>Владелец сможет управлять товарами и заказами этого магазина. Узнать ID можно через @userinfobot.</i>",
        parse_mode="HTML"
    )
    await state.set_state(AddShopStates.waiting_for_owner_id)


@router.message(AddShopStates.waiting_for_owner_id)
async def process_sa_shop_owner_id(message: Message, state: FSMContext):
    owner_id_str = message.text.strip()
    if not owner_id_str.isdigit():
        await message.answer("Пожалуйста, введите корректный числовой ID:")
        return
        
    owner_id = int(owner_id_str)
    data = await state.get_data()
    await state.clear()
    
    # Сначала убедимся, что пользователь есть в таблице users (или создадим запись)
    # Чтобы не нарушать FOREIGN KEY constraint в shops
    user = UserRepository.get_user(owner_id)
    if not user:
        UserRepository.add_user(owner_id, data['telegram_username'], f"Владелец {data['name']}", role='SHOP_OWNER')
    else:
        UserRepository.update_user_role(owner_id, 'SHOP_OWNER')
        
    # Создаем магазин
    shop_id = ShopRepository.create_shop(
        name=data['name'],
        description=data['description'],
        logo=data['logo'],
        telegram_username=data['telegram_username'],
        owner_id=owner_id
    )
    
    success_text = (
        f"✅ <b>Магазин создан успешно!</b>\n\n"
        f"🆔 ID магазина: {shop_id}\n"
        f"🏪 Название: {data['name']}\n"
        f"👤 Владелец ID: {owner_id}\n\n"
        f"Магазин теперь отображается в общем списке клиентов и готов к наполнению товарами."
    )
    await message.answer(success_text, parse_mode="HTML")


# ==========================================
# УДАЛЕНИЕ МАГАЗИНА
# ==========================================

@router.callback_query(F.data == "sa_list_shops_del")
async def callback_sa_list_shops_del(callback: CallbackQuery):
    shops = ShopRepository.get_all_shops()
    if not shops:
        await callback.answer("В системе нет созданных магазинов.", show_alert=True)
        return
        
    await callback.message.edit_text(
        "🗑 <b>Выберите магазин для безвозвратного удаления:</b>\n"
        "<i>Внимание! Все товары и заказы этого магазина также будут удалены.</i>",
        reply_markup=get_superadmin_delete_shops_keyboard(shops),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("sa_del_confirm_"))
async def callback_sa_del_confirm(callback: CallbackQuery):
    shop_id = int(callback.data.split("_")[3])
    
    shop = ShopRepository.get_shop_by_id(shop_id)
    if not shop:
        await callback.answer("Магазин уже удален.", show_alert=True)
        return
        
    ShopRepository.delete_shop(shop_id)
    await callback.answer(f"Магазин «{shop['name']}» успешно удален!", show_alert=True)
    
    # Возвращаемся в список
    shops = ShopRepository.get_all_shops()
    if not shops:
        await callback.message.edit_text(
            "🛡 <b>Панель СУПЕР-АДМИНИСТРАТОРА платформы</b>\n\n"
            "Все магазины удалены.",
            reply_markup=get_superadmin_main_keyboard(),
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text(
            "🗑 <b>Выберите магазин для безвозвратного удаления:</b>",
            reply_markup=get_superadmin_delete_shops_keyboard(shops),
            parse_mode="HTML"
        )


# ==========================================
# ГЛОБАЛЬНАЯ СТАТИСТИКА
# ==========================================

@router.callback_query(F.data == "sa_stats")
@router.message(Command("stats"))
async def callback_sa_stats(event):
    # Метод может быть вызван как CallbackQuery, так и Message
    is_callback = isinstance(event, CallbackQuery)
    message = event.message if is_callback else event
    
    stats = get_superadmin_stats()
    
    stats_text = (
        "📊 <b>Глобальная статистика SaaS платформы:</b>\n\n"
        f"🏪 Всего магазинов: {stats['shops_count']}\n"
        f"🎮 Всего товаров: {stats['products_count']}\n"
        f"📦 Всего заказов: {stats['orders_count']}\n"
        f"✅ Успешных заказов: {stats['completed_orders_count']}\n"
        f"👤 Всего клиентов в БД: {stats['clients_count']}\n"
    )
    
    if is_callback:
        # Добавим кнопку возврата
        keyboard = get_superadmin_main_keyboard()
        await message.edit_text(stats_text, reply_markup=keyboard, parse_mode="HTML")
        await event.answer()
    else:
        await message.answer(stats_text, parse_mode="HTML")
