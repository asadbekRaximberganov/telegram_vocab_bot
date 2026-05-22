import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, BOOKS_DIR
from database import init_db
from handlers import start, admin, book, quiz, results

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    # Kerakli papkalarni yaratish
    os.makedirs(BOOKS_DIR, exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # Ma'lumotlar bazasini ishga tushirish
    await init_db()

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN topilmadi! .env faylni tekshiring.")

    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Routerlarni ulash
    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(book.router)
    dp.include_router(quiz.router)
    dp.include_router(results.router)

    logger.info("Bot ishga tushmoqda...")

    try:
        await dp.start_polling(bot, drop_pending_updates=True)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
