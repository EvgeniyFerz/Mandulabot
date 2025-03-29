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
RENDER_URL = "https://mandulabot.onrender.com"  # URL вашего бота на Render

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
            requests.get(RENDER_URL, timeout=5)
            logging.info("Пинг отправлен для поддержания активности")
        except Exception as e:
            logging.warning(f"Ошибка пинга: {e}")
        time.sleep(300)  # Пинг каждые 5 минут

# ======== Инициализация бота ========
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
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
        username = f"@{user.username}" if user.username else f"ID:{user.id}"
        user_info = f"👤 {user.full_name} ({username})"

        if message.text:
            await bot.send_message(CHANNEL_ID, f"📩 Сообщение\n\n{user_info}\n\n{message.text}")
        elif message.photo:
            await bot.send_photo(CHANNEL_ID, message.photo[-1].file_id, caption=f"📷 Фото\n\n{user_info}")
        elif message.document:
            await bot.send_document(CHANNEL_ID, message.document.file_id, caption=f"📄 Документ\n\n{user_info}")

        await message.reply("✅ Ваше сообщение переслано администратору!")

    except Exception as e:
        logging.error(f"Ошибка обработки сообщения: {e}")
        await message.reply("⚠️ Произошла ошибка. Попробуйте позже.")

# ======== Запуск ========
async def main():
    # Принудительный сброс вебхука перед запуском
    try:
        requests.post(
            f"https://api.telegram.org/bot{API_TOKEN}/deleteWebhook",
            params={'drop_pending_updates': True},
            timeout=5
        )
    except Exception as e:
        logging.warning(f"Ошибка сброса вебхука: {e}")

    # Запускаем Flask
    Thread(
        target=lambda: app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False),
        daemon=True
    ).start()

    # Запускаем автопинг
    Thread(target=keep_alive, daemon=True).start()

    # Запускаем бота с защитой от конфликтов
    logging.info("Бот запущен и работает на Render")
    await dp.start_polling(bot, none_stop=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен пользователем")
    except Exception as e:
        logging.critical(f"Фатальная ошибка: {e}")
