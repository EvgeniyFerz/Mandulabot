import logging
import os
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from flask import Flask
from threading import Thread

# ======== Конфигурация ========
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

# Глобальные переменные объявлены в начале
session = None
bot = None
dp = None

# ======== Инициализация ========
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = Flask(__name__)

def init_bot():
    global session, bot, dp
    session = AiohttpSession()
    bot = Bot(token=API_TOKEN, session=session,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

# ======== Обработчики ========
@dp.message()
async def handle_message(message: types.Message):
    # Ваша логика обработки сообщений
    pass

# ======== Полный сброс вебхука ========
async def hard_reset():
    """Принудительный сброс всех подключений"""
    try:
        if bot and not bot.is_closed():
            await bot.session.close()
        
        # HTTP-запросы для гарантированного сброса
        requests.post(
            f"https://api.telegram.org/bot{API_TOKEN}/deleteWebhook",
            params={'drop_pending_updates': True},
            timeout=5
        )
        requests.post(
            f"https://api.telegram.org/bot{API_TOKEN}/close",
            timeout=5
        )
        
        # Инициализация новой сессии
        init_bot()
        await asyncio.sleep(3)
    except Exception as e:
        logging.error(f"Reset error: {e}")

# ======== Запуск ========
async def run_bot():
    await hard_reset()
    
    try:
        await dp.start_polling(
            bot,
            none_stop=True,
            allowed_updates=dp.resolve_used_update_types(),
            timeout=30,
            relax=0.5
        )
    finally:
        if not bot.is_closed():
            await bot.session.close()

def run_flask():
    app.run(host='0.0.0.0', port=8080)

async def main():
    init_bot()  # Инициализация бота
    Thread(target=run_flask, daemon=True).start()
    await run_bot()

if __name__ == "__main__":
    # Дополнительный жесткий сброс при старте
    requests.post(f"https://api.telegram.org/bot{API_TOKEN}/deleteWebhook",
                params={'drop_pending_updates': True})
    
    asyncio.run(main())
