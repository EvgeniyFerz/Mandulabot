import logging
import os
import asyncio
import datetime
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
RENDER_URL = "https://mandulabot.onrender.com"

# ======== Инициализация Flask ========
app = Flask(__name__)

@app.route('/')
def home():
    return f"""
    <h1>Бот @Mandula_robot активен</h1>
    <p>Последняя активность: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>Статус: <span style="color:green;">✔ Онлайн</span></p>
    """

# ======== Инициализация бота ========
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

# Создаем новую сессию с уникальными параметрами
session = AiohttpSession(api_timeout=30)
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML), session=session)
dp = Dispatcher()

# ======== Обработчики сообщений ========
@dp.message()
async def handle_message(message: types.Message):
    try:
        if message.chat.type != "private":
            return

        user = message.from_user
        username = f"@{user.username}" if user.username else user.id
        user_info = f"👤 {user.full_name} (ID: {user.id}, {username})"

        if message.text:
            await bot.send_message(CHANNEL_ID, f"📩 Сообщение\n\n{user_info}\n\n{message.text}")
        elif message.photo:
            await bot.send_photo(CHANNEL_ID, message.photo[-1].file_id, caption=f"📷 Фото\n\n{user_info}")
        elif message.document:
            await bot.send_document(CHANNEL_ID, message.document.file_id, caption=f"📄 Документ\n\n{user_info}")

        await message.reply("✅ Ваше сообщение переслано администратору!")

    except Exception as e:
        logging.error(f"Ошибка обработки сообщения: {e}", exc_info=True)
        await message.reply("⚠️ Произошла ошибка. Попробуйте позже.")

# ======== Запуск с полной защитой ========
async def reset_telegram_session():
    """Принудительный сброс всех предыдущих подключений"""
    try:
        # Закрываем все возможные предыдущие сессии
        await bot.session.close()
        await asyncio.sleep(2)
        
        # Сбрасываем webhook и updates через Telegram API
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.get_updates(offset=-1)
        
        # Дополнительный HTTP-сброс
        requests.post(f"https://api.telegram.org/bot{API_TOKEN}/close", timeout=5)
    except Exception as e:
        logging.warning(f"Ошибка при сбросе сессии: {e}")

async def bot_runner():
    """Основной цикл работы бота"""
    await reset_telegram_session()
    
    while True:
        try:
            logging.info("Запуск бота с новым экземпляром сессии...")
            await dp.start_polling(
                bot,
                none_stop=True,
                allowed_updates=dp.resolve_used_update_types(),
                timeout=25,
                relax=0.3,
                reset_webhook=True
            )
        except asyncio.CancelledError:
            logging.info("Получен сигнал остановки")
            break
        except Exception as e:
            logging.critical(f"Критическая ошибка: {type(e).__name__}: {e}", exc_info=True)
            await asyncio.sleep(10)
            await reset_telegram_session()

async def main():
    """Главная функция инициализации"""
    # Запуск Flask сервера
    flask_thread = Thread(
        target=lambda: app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False),
        daemon=True
    )
    flask_thread.start()

    # Основной цикл работы
    try:
        await bot_runner()
    finally:
        logging.info("Завершение работы...")
        await bot.session.close()
        await asyncio.sleep(1)

if __name__ == "__main__":
    # Принудительный сброс через API при старте
    try:
        requests.post(f"https://api.telegram.org/bot{API_TOKEN}/deleteWebhook", timeout=3)
        requests.post(f"https://api.telegram.org/bot{API_TOKEN}/close", timeout=3)
    except:
        pass

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Принудительная остановка")
    except Exception as e:
        logging.critical(f"Фатальная ошибка: {type(e).__name__}: {e}", exc_info=True)
    finally:
        logging.info("✅ Работа бота завершена")
