import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config.config import BOT_TOKEN
from database.repositories import init_db
from bot.handlers.user_handlers import router as user_router
from bot.handlers.admin_handlers import router as admin_router

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

    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Подключение роутеров обработчиков
    dp.include_router(user_router)
    dp.include_router(admin_router)

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
