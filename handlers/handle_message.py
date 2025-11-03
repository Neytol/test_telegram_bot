from telegram import Update
from telegram.ext import ContextTypes
from database import increment_message_count, get_all_users, register_user, get_user
from handlers.handle_awaiting_input import handle_awaiting_input
from handlers.start_command import start_command
from logger import logger


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_text = update.message.text

    if await handle_awaiting_input(update, context, user_text):
        return
    try:
        user_data = await get_user(user.id)
        if user_data is None:
            await start_command(update,context)
            return
        await increment_message_count(user.id)
        await update.message.reply_text("Используй /start")
    except Exception as e:
        logger.warning(e)
