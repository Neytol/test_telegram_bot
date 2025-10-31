import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_USER_ID
from database import get_all_users
from logger import logger



async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_USER_ID:
        await update.message.reply_text("❌ Доступ запрещён.")
        return

    if not context.args:
        await update.message.reply_text("Использование: /broadcast <текст>")
        return

    users = await get_all_users()
    message_text = " ".join(context.args)
    success = 0
    failed = 0

    for user in users:
        user_id = user["id"]
        try:
            await context.bot.send_message(chat_id=int(user_id), text=message_text)
            success += 1
            await asyncio.sleep(0.05)
        except Exception as e:
            logger.warning(f"Не удалось отправить {user_id}: {e}")
            failed += 1
    await update.message.reply_text(
        f"Рассылка завершена\n"
        f"Успешно {success}\n"
        f"Ошибка {failed}"
    )
