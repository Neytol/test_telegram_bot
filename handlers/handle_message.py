from telegram import Update
from telegram.ext import ContextTypes

from data_manager import increment_message_count, load_users
from handlers.handle_awaiting_input import handle_awaiting_input
from handlers.start_command import start_command
from logger import logger


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_text = update.message.text
    increment_message_count(user.id)

    if await handle_awaiting_input(update, context, user_text):
        return

    users = load_users()
    user_id_str = str(user.id)
    try:
        if user_id_str not in users:
            await start_command(update, context)
            return
        else:
            await update.message.reply_text("Я пока умею только приветствовать! Используй /help")
    except Exception as e:
        logger.error(f"Необработанная ошибка в handle_message: {e}", exc_info=True)
        try:
            await update.message.reply_text("⚠️ Произошла ошибка. Админ уже чинит!")
        except:
            pass
