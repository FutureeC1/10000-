import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config.config import BOT_TOKEN, ADMIN_ID
from database.repositories import init_db, seed_default_data
from bot.handlers.user_handlers import router as user_router
from bot.handlers.admin_handlers import router as admin_router
from bot.handlers.owner_handlers import router as owner_router

async def main():
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    
    if not BOT_TOKEN:
        logging.error("BOT_TOKEN is missing! Please set it in .env file.")
        return

    # Инициализация базы данных (создание таблиц)
    logging.info("Initializing database...")
    init_db()
    
    # Наполнение дефолтными данными (если база пустая)
    if ADMIN_ID:
        logging.info("Seeding default multi-tenant data...")
        seed_default_data(ADMIN_ID)

    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Подключение роутеров обработчиков
    dp.include_router(user_router)
    dp.include_router(admin_router)
    dp.include_router(owner_router)

    # Запуск polling
    logging.info("Starting bot...")
    print("Keyllect Telegram Bot started successfully!")
    
    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped.")
