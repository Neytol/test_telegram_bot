from telegram import Update
from telegram.ext import ContextTypes
from database import increment_message_count, get_all_users, register_user
from handlers.handle_awaiting_input import handle_awaiting_input
from handlers.start_command import start_command
from logger import logger


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_text = update.message.text
    users = await get_all_users()
    try:
        if len(users) == 0:
            await start_command(update, context)
            return
        for u in users:
            if user.id != u['id']:
                await start_command(update,context)
                return

        if await handle_awaiting_input(update, context, user_text):
            return
        await increment_message_count(user.id)
        await update.message.reply_text("Используй /start")
    except Exception as e:
        logger.warning(e)
