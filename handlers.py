from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

import commands
import callbacks
import messages

def setup_handlers(app: Application):
    # Команды
    app.add_handler(CommandHandler("start", commands.start))
    app.add_handler(CommandHandler("help", commands.help_command))

    # Inline кнопки
    app.add_handler(CallbackQueryHandler(callbacks.button_handler))

    # Сообщения
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, messages.handle_text))
