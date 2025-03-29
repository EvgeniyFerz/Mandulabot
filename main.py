import logging
import os
import asyncio
import datetime
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from flask import Flask
from threading import Thread
import time

# ======== Конфигурация ========
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
REPLIT_URL = "https://mandulabot.onrender.com/"  # Ваш публичный URL

# ======== Flask сервер ========
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

# ======== Инициализация бота ========
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# ======== Обработчики сообщений ========
@dp.message()
async def handle_message(message: types.Message):
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

# ======== Запуск ========
async def main():
    # Запускаем Flask
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080), daemon=True).start()

    # Запускаем автопинг
    Thread(target=keep_alive, daemon=True).start()

    # Запускаем бота
    logging.info("Бот запущен и работает 24/7")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
