import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from db.database import init_db
from bot.handlers.user_handlers import router as user_router
from bot.handlers.admin_handlers import router as admin_router

async def main():
    logging.basicConfig(level=logging.INFO)
    
    if not BOT_TOKEN:
        logging.error("BOT_TOKEN is missing! Please set it in .env file.")
        return

    # Initialize Database
    init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Include routers
    dp.include_router(user_router)
    dp.include_router(admin_router)

    # Start polling
    print("Bot is starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped.")
