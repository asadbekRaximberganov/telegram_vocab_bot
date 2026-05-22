import asyncio
import logging
import os

import aiohttp
from aiohttp import web
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

# Render servis URL — environment variable dan olinadi
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL", "")


# ─── Keep-alive ping ──────────────────────────────────────────────────────────

async def keep_alive_ping():
    """Har 25 sekundda o'ziga ping yuborib Render ni uyg'otib turadi"""
    if not RENDER_URL:
        logger.info("RENDER_EXTERNAL_URL topilmadi, keep-alive o'chirilgan")
        return

    url = f"{RENDER_URL}/ping"
    logger.info(f"Keep-alive boshlandi: {url}")

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)):
                    pass
            except Exception:
                pass
            await asyncio.sleep(25)


# ─── HTTP server (ping endpoint) ─────────────────────────────────────────────

async def handle_ping(request):
    return web.Response(text="OK")


async def start_http_server():
    """Render ning health check va keep-alive uchun HTTP server"""
    app = web.Application()
    app.router.add_get("/ping", handle_ping)
    app.router.add_get("/", handle_ping)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"HTTP server port {port} da ishlamoqda")


# ─── Asosiy funksiya ──────────────────────────────────────────────────────────

async def main():
    os.makedirs(BOOKS_DIR, exist_ok=True)
    os.makedirs("data", exist_ok=True)

    await init_db()

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN topilmadi! .env faylni tekshiring.")

    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(book.router)
    dp.include_router(quiz.router)
    dp.include_router(results.router)

    # HTTP server va keep-alive ni parallel ishga tushirish
    await start_http_server()
    asyncio.create_task(keep_alive_ping())

    logger.info("Bot ishga tushmoqda...")

    try:
        await dp.start_polling(bot, drop_pending_updates=True)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())