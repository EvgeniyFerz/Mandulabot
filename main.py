import logging
import os
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from flask import Flask
from threading import Thread
import time

# ======== Конфигурация ========
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

# Глобальные переменные
bot_instance = None
dp_instance = None

# ======== Инициализация ========
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

app = Flask(__name__)

def initialize_bot():
    """Инициализация бота с уникальной сессией"""
    global bot_instance, dp_instance
    
    # Закрываем предыдущую сессию если существует
    if bot_instance and not bot_instance.is_closed:
        try:
            asyncio.get_event_loop().run_until_complete(bot_instance.close())
        except:
            pass
    
    # Создаем новую сессию с уникальным ID
    session = AiohttpSession()
    bot_instance = Bot(
        token=API_TOKEN,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp_instance = Dispatcher()

    # Регистрация обработчиков
    @dp_instance.message()
    async def handle_message(message: types.Message):
        # Ваша логика обработки сообщений
        pass

# ======== Полный сброс соединения ========
async def hard_reset():
    """Полный сброс всех соединений с Telegram"""
    try:
        # 1. Закрываем текущую сессию
        if bot_instance and not bot_instance.is_closed:
            await bot_instance.close()
            await asyncio.sleep(2)
        
        # 2. HTTP-сброс через API
        for _ in range(3):  # 3 попытки
            try:
                requests.post(
                    f"https://api.telegram.org/bot{API_TOKEN}/deleteWebhook",
                    params={'drop_pending_updates': True},
                    timeout=5
                )
                requests.post(
                    f"https://api.telegram.org/bot{API_TOKEN}/close",
                    timeout=5
                )
                break
            except:
                await asyncio.sleep(1)
        
        # 3. Полная переинициализация
        initialize_bot()
        await asyncio.sleep(3)
        
    except Exception as e:
        logging.critical(f"HARD RESET ERROR: {e}")

# ======== Защищенный запуск бота ========
async def run_polling():
    """Основной цикл работы с защитой от конфликтов"""
    await hard_reset()
    
    restart_count = 0
    while restart_count < 5:  # Максимум 5 перезапусков
        try:
            logging.info(f"Starting polling (attempt {restart_count + 1})")
            await dp_instance.start_polling(
                bot_instance,
                none_stop=True,
                timeout=25,
                relax=0.3,
                reset_webhook=True,
                allowed_updates=types.Update.ALL_TYPES
            )
        except asyncio.CancelledError:
            break
        except Exception as e:
            logging.error(f"Polling error: {e}")
            restart_count += 1
            await hard_reset()
            await asyncio.sleep(5)
        else:
            break

# ======== Flask сервер ========
def run_flask():
    app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)

# ======== Главная функция ========
async def main():
    initialize_bot()
    
    # Запускаем Flask в отдельном потоке
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Основной цикл работы бота
    await run_polling()
    
    # Корректное завершение
    if bot_instance and not bot_instance.is_closed:
        await bot_instance.close()

if __name__ == "__main__":
    # Принудительный сброс при старте
    try:
        requests.post(
            f"https://api.telegram.org/bot{API_TOKEN}/deleteWebhook",
            params={'drop_pending_updates': True},
            timeout=5
        )
    except:
        pass
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
    except Exception as e:
        logging.critical(f"Fatal error: {e}")
    finally:
        logging.info("Shutdown completed")
