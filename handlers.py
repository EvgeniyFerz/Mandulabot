from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

import callbacks
import messages

# Функции для команд
async def start(update, context):
    await update.message.reply("Привет! Я ваш бот!")

async def help_command(update, context):
    await update.message.reply("Я помогу вам с чем угодно!")

def setup_handlers(app: Application):
    # Команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # Inline кнопки
    app.add_handler(CallbackQueryHandler(callbacks.button_handler))

    # Сообщения
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, messages.handle_text))
