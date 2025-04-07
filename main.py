import logging
import os
import time  # заменили asyncio.sleep на time.sleep
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from flask import Flask
from threading import Thread

# Конфигурация
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
RENDER_URL = "https://mandulabot.onrender.com"

app = Flask(__name__)
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

async def reset_connection():
    """Полный сброс всех подключений"""
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.session.close()
    except:
        pass
    try:
        requests.post(f"https://api.telegram.org/bot{API_TOKEN}/deleteWebhook")
    except:
        pass

@app.route('/')
def home():
    return "Бот активен"

def keep_alive():
    while True:
        try:
            requests.get(RENDER_URL, timeout=5)
        except Exception as e:
            logging.warning(f"Ошибка при keep_alive: {e}")
        time.sleep(300)  # Пауза 5 минут

@dp.message()
async def handle_message(message: types.Message):
    try:
        if message.chat.type == "private":
            await bot.send_message(
                CHANNEL_ID,
                f"📩 Сообщение от {message.from_user.full_name}:\n{message.text}"
            )
            await message.reply("✅ Переслано администратору")
    except Exception as e:
        logging.error(f"Ошибка при обработке сообщения: {e}")

async def main():
    await reset_connection()
    
    # Запускаем Flask-сервер и keep_alive в отдельных потоках
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080), daemon=True).start()
    Thread(target=keep_alive, daemon=True).start()

    logging.info("Бот запущен")
    await dp.start_polling(
        bot,
        skip_updates=True,
        timeout=30,
        relax=0.5
    )

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
