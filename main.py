import logging
import os
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from flask import Flask
from threading import Thread

# Конфигурация
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = -1002011048351  # ID чата (супергруппы/канала)
TOPIC_ID = 108214         # ID топика "Заявки с Мандулы"
RENDER_URL = "https://mandulabot.onrender.com"

app = Flask(__name__)
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

async def reset_connection():
    """Полный сброс всех подключений"""
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.session.close()
    except Exception as e:
        logging.error(f"Ошибка при сбросе соединения: {e}")
    try:
        requests.post(f"https://api.telegram.org/bot{API_TOKEN}/deleteWebhook")
    except Exception as e:
        logging.error(f"Ошибка при удалении вебхука: {e}")

@app.route('/')
def home():
    return "Бот активен"

def keep_alive():
    """Поддержка работы на Render"""
    app.run(host='0.0.0.0', port=8080)

def format_user(user: types.User) -> str:
    """Форматирование информации о пользователе"""
    if user.username:
        return f"@{user.username}"
    else:
        full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        return f"<a href='tg://user?id={user.id}'>{full_name}</a>"

@dp.message()
async def handle_message(message: types.Message):
    """Обработка входящих сообщений"""
    try:
        if message.chat.type == "private":
            user_info = format_user(message.from_user)
            text_to_send = f"📩 Сообщение\n👤 {user_info}\n\n{message.text}"
            
            # Отправка в указанный топик чата
            await bot.send_message(
                chat_id=CHAT_ID,
                message_thread_id=TOPIC_ID,
                text=text_to_send
            )
            await message.reply("✅ Сообщение отправлено в топик 'Заявки с Мандулы'")
    except Exception as e:
        logging.error(f"Ошибка: {e}")

async def main():
    """Основная функция запуска бота"""
    await reset_connection()

    # Запуск Flask в отдельном потоке
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
