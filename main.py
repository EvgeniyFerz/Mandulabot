import logging
import os
import asyncio
import datetime
import requests
import time
from threading import Thread
from flask import Flask

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.types import Message

# ======== Конфигурация ========
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
REPLIT_URL = "https://mandulabot.onrender.com/"  # Публичный URL

# ======== Flask-сервер ========
app = Flask(__name__)

@app.route('/')
def home():
    return f"""
    <h1>Бот @Mandula_robot активен</h1>
    <p>Последняя активность: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>Статус: <span style="color:green;">✔ Онлайн</span></p>
    """

# ======== Автопинг ========
def keep_alive():
    while True:
        try:
            requests.get(REPLIT_URL, timeout=5)
            logging.info("Пинг отправлен для поддержания активности")
        except Exception as e:
            logging.warning(f"Ошибка пинга: {e}")
        time.sleep(300)  # Пинг каждые 5 минут

# ======== Логирование и инициализация ========
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# ======== Хендлер /start ========
async def handle_start(message: Message):
    welcome_text = (
        "Это бот <b>Mandula corporation</b> (https://t.me/mandula_corporation) — объединение админов ЖЦА-психологии и саморазвития.\n\n"
        "Напишите в одном сообщении:\n"
        "- ссылку на ваш канал\n"
        "- что хотите взять (лента, рассылка, сториз)\n"
        "- где хотите взять — во всех каналах или только в некоторых"
    )
    await message.reply(welcome_text)

# ======== Хендлер на все входящие сообщения ========
async def handle_message(message: Message):
    try:
        if message.chat.type != "private":
            return

        user = message.from_user
        username = f"@{user.username}" if user.username else "без username"
        user_info = f"👤 {user.full_name} ({username})"

        if message.text:
            await bot.send_message(CHANNEL_ID, f"📩 Сообщение\n\n{user_info}\n\n{message.text}")
        elif message.photo:
            await bot.send_photo(CHANNEL_ID, message.photo[-1].file_id, caption=f"📷 Фото\n\n{user_info}")
        elif message.document:
            await bot.send_document(CHANNEL_ID, message.document.file_id, caption=f"📄 Документ\n\n{user_info}")

        await message.reply("✅ Ваше сообщение переслано администратору!")

    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.reply("⚠️ Произошла ошибка. Попробуйте позже.")

# ======== Регистрация хендлеров ========
dp.message.register(handle_start, CommandStart())
dp.message.register(handle_message, F.chat.type == "private")

# ======== Запуск ========
async def main():
    # Запускаем Flask-сервер
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080), daemon=True).start()

    # Запускаем автопинг
    Thread(target=keep_alive, daemon=True).start()

    # Запускаем бота
    logging.info("Бот запущен и работает 24/7")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
