from telegram import Update
from telegram.ext import ContextTypes

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer("Кнопка нажата!")
