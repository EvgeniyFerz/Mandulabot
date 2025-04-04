import os
import logging
import asyncio
import datetime
import requests

from flask import Flask, request

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.types import Update

# ======== Конфигурация ========
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
WEBHOOK_HOST = os.getenv("REPLIT_URL")  # или https://название-проекта.onrender.com
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
    return f"<h1>Бот @Mandula_robot на Webhook</h1><p>{datetime.datetime.now()}</p>"

@app.route(WEBHOOK_PATH, methods=["POST"])
async def webhook():
    try:
        request_data = request.get_data().decode("utf-8")
        update = Update.model_validate_json(request_data)
        await dp.feed_update(bot, update)
    except Exception as e:
        logging.error(f"Ошибка при обработке webhook: {e}")
    return {"status": "ok"}

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

# ======== Установка Webhook и запуск ========
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Webhook установлен: {WEBHOOK_URL}")

async def main():
    await on_startup()
    app.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    asyncio.run(main())
