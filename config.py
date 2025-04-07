import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Токен вашего Telegram-бота
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# URL для keep-alive
WEBHOOK_HOST = os.getenv('WEBHOOK_HOST')

# Идентификатор канала
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')
