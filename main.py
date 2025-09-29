import logging
import os
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from flask import Flask
from threading import Thread
import sys

# Конфигурация
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = -1002011048351  # ID чата (супергруппы/канала)
TOPIC_ID = 108214         # ID топика "Заявки с Мандулы"

# Проверка обязательных переменных
if not API_TOKEN:
    logging.error("TELEGRAM_BOT_TOKEN не установлен")
    sys.exit(1)

app = Flask(__name__)
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# Глобальная переменная для отслеживания состояния
bot_started = False
flask_started = False

async def reset_connection():
    """Полный сброс всех подключений"""
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logging.info("Вебхук удален")
    except Exception as e:
        logging.error(f"Ошибка при удалении вебхука: {e}")
    
    try:
        response = requests.post(f"https://api.telegram.org/bot{API_TOKEN}/deleteWebhook", timeout=10)
        if response.status_code == 200:
            logging.info("Вебхук удален через API")
        else:
            logging.warning(f"Не удалось удалить вебхук через API: {response.status_code}")
    except Exception as e:
        logging.error(f"Ошибка при удалении вебхука через API: {e}")

@app.route('/')
def home():
    """Основная страница"""
    global flask_started
    return f"Бот активен. Flask: {flask_started}, Bot: {bot_started}"

@app.route('/health')
def health():
    """Эндпоинт для проверки здоровья приложения"""
    global bot_started, flask_started
    if flask_started:
        return "OK", 200
    else:
        return "Starting...", 202  # 202 Accepted вместо 503

@app.route('/ping')
def ping():
    """Простой эндпоинт для пинга"""
    return "pong", 200

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
        logging.error(f"Ошибка обработки сообщения: {e}")

async def start_bot():
    """Запуск бота"""
    global bot_started
    try:
        await reset_connection()
        logging.info("Подключения сброшены, запускаем поллинг...")
        
        bot_started = True
        await dp.start_polling(
            bot,
            skip_updates=True,
            timeout=30,
            relax=0.5
        )
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")
        bot_started = False

def run_flask():
    """Запуск Flask приложения"""
    global flask_started
    try:
        port = int(os.environ.get("PORT", 10000))
        logging.info(f"Запуск Flask на порту {port}")
        flask_started = True
        # Используем production-ready сервер вместо development
        from waitress import serve
        serve(app, host='0.0.0.0', port=port)
    except ImportError:
        # Если waitress не установлен, используем стандартный Flask
        app.run(host='0.0.0.0', port=port, debug=False, threaded=True)

async def main():
    """Основная функция запуска"""
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logging.info("Запуск приложения...")
    
    # Запуск Flask в отдельном потоке
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logging.info("Flask запускается в отдельном потоке")
    
    # Даем Flask время запуститься
    await asyncio.sleep(3)
    
    # Запуск бота
    logging.info("Запуск Telegram бота...")
    await start_bot()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен пользователем")
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")
