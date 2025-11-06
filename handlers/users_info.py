from telegram import Update
from telegram.ext import ContextTypes
from database import get_all_users


async def users_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = await get_all_users()
    if len(users) == 0:
        await update.message.reply_text("Пользователей нет")
        return
    else:
        for u in users:
            await update.message.reply_text(f"""
            "id": {u['id']},
            "username": {u['username']},
            "first_name": {u['first_name']},
            "message_count": {u['message_count']},
            "registered": {u['registered']},
            "last_activity": {u['last_activity']}
            """)