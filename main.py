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
    dp = Dispatcher()  # Создаём новый Dispatcher

init_bot()  # Вызываем init_bot() ДО объявления обработчиков!

# ======== Обработчики сообщений ========
@dp.message()
async def handle_message(message: types.Message):
    pass  # Здесь логика обработки сообщений

# ======== Жесткий сброс ========
async def hard_reset():
    global session, bot, dp
    try:
        if bot and not bot.session.closed:
            await bot.session.close()
        
        try:
            requests.post(f"https://api.telegram.org/bot{API_TOKEN}/deleteWebhook",
                          params={'drop_pending_updates': True}, timeout=5)
            requests.post(f"https://api.telegram.org/bot{API_TOKEN}/close", timeout=5)
        except requests.RequestException as e:
            logging.error(f"Ошибка сброса вебхука: {e}")

        # Пересоздание бота
        session = AiohttpSession()
        bot = Bot(token=API_TOKEN, session=session,
                  default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        dp = Dispatcher()

        await asyncio.sleep(3)
    except Exception as e:
        logging.error(f"Reset error: {e}")

# ======== Запуск бота ========
async def run_bot():
    await hard_reset()
    
    try:
        await dp.start_polling(
            bot,
            allowed_updates=None,
            timeout=30,
            relax=0.5
        )
    finally:
        if not bot.session.closed:
            await bot.session.close()

def run_flask():
    app.run(host='0.0.0.0', port=8080)

async def main():
    Thread(target=run_flask, daemon=True).start()
    await run_bot()

if __name__ == "__main__":
    try:
        requests.post(f"https://api.telegram.org/bot{API_TOKEN}/deleteWebhook",
                      params={'drop_pending_updates': True}, timeout=5)
    except requests.RequestException as e:
        logging.error(f"Ошибка при запуске: {e}")
    
    asyncio.run(main())
