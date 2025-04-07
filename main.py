import asyncio
import logging
import os
import time
from threading import Thread

import requests
from flask import Flask
from telegram import Bot
from telegram.ext import Application

from config import TELEGRAM_BOT_TOKEN, WEBHOOK_HOST
from handlers import setup_handlers

# Настройка логгирования
logging.basicConfig(level=logging.INFO)

# Flask приложение
app = Flask(__name__)

@app.route('/')
def index():
    return 'Бот работает!'

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# Поддержание активности на Render
def keep_alive():
    logging.info("Запускаю keep_alive")
    while True:
        try:
            requests.get(RENDER_URL, timeout=5)
            logging.info("Ping sent to keep alive")
        except Exception as e:
            logging.warning(f"Ошибка при keep_alive: {e}")
        time.sleep(300)

# Основной запуск бота
async def main():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Подключаем хендлеры
    setup_handlers(application)

    # Запускаем Flask и keep_alive в отдельных потоках
    Thread(target=run_flask, daemon=True).start()
    Thread(target=keep_alive, daemon=True).start()

    logging.info("Бот запускается...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    await application.updater.idle()

if __name__ == "__main__":
    asyncio.run(main())
