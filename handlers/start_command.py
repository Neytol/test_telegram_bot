from telegram import Update
from telegram.ext import ContextTypes

from data_manager import register_user
from handlers.show_main_buttons import show_main_buttons


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    is_new = register_user(user.id, user.username, user.first_name)
    welcome = f"Привет {user.first_name}, рад познакомится! 👋" if is_new else f"С возвращением {user.first_name}! 👋"
    await update.message.reply_text(welcome, reply_markup= show_main_buttons(user.id))
