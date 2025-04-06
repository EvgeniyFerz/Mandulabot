import os
import logging
import asyncio
import datetime
import requests
import time

from flask import Flask, request

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.types import Update

# ======== Конфигурация ========
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# ======== Инициализация ========
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
app = Flask(__name__)

# ======== Flask маршруты ========
@app.route("/")
def index():
    return f"""
    <h1>Бот @Mandula_robot активен</h1>
    <p>Последняя активность: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>Статус: <span style="color:green;">✔ Онлайн</span></p>
    """

@app.route(WEBHOOK_PATH, methods=["POST"])
async def webhook():
    try:
        request_data = request.get_data().decode("utf-8")
        update = Update.model_validate_json(request_data)
        await dp.feed_update(bot, update)
    except Exception as e:
        logging.error(f"Ошибка при обработке webhook: {e}")
    return {"status": "ok"}

# ======== Автопинг ========
async def keep_alive():
    while True:
        try:
            requests.get(WEBHOOK_HOST)
            logging.info("✅ Пинг отправлен для поддержания активности")
        except Exception as e:
            logging.warning(f"⚠️ Ошибка пинга: {e}")
        await asyncio.sleep(300)  # Каждые 5 минут

# ======== Хендлеры ========
async def handle_start(message: types.Message):
    welcome_text = (
        "Это бот <b>Mandula corporation</b> (https://t.me/mandula_corporation) — объединение админов ЖЦА-психологии и саморазвития.\n\n"
        "Напишите в одном сообщении:\n"
        "- ссылку на ваш канал\n"
        "- что хотите взять (лента, рассылка, сториз)\n"
        "- где хотите взять — во всех каналах или только в некоторых"
    )
    await message.reply(welcome_text)

async def handle_message(message: types.Message):
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

# ======== Регистрация хендлеров ========
dp.message.register(handle_start, CommandStart())
dp.message.register(handle_message, F.chat.type == "private")

# ======== Запуск ========
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"✅ Webhook установлен: {WEBHOOK_URL}")

async def main():
    await on_startup()

    # Запуск Flask-сервера
    loop = asyncio.get_running_loop()
    from threading import Thread
    Thread(target=lambda: app.run(host="0.0.0.0", port=8080), daemon=True).start()

    # Запуск автопинга
    asyncio.create_task(keep_alive())

    # Постоянное ожидание
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
