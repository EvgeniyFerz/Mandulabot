import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Ваш токен бота
TOKEN = os.getenv('TOKEN')

# URL для keep-alive
RENDER_URL = os.getenv('RENDER_URL')
