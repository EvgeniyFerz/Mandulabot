import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Ваш токен бота
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# URL для keep-alive
WEBHOOK_HOST = os.getenv('WEBHOOK_HOST')
