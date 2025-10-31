from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import ADMIN_USER_ID


def show_main_buttons(user_id: int):
    keyboard = [
        [InlineKeyboardButton("🌤️ Погода", callback_data="weather")],
        [InlineKeyboardButton("💰 Курс валюты", callback_data="currency")],
    ]
    if str(user_id) == str(ADMIN_USER_ID):
        keyboard.append([InlineKeyboardButton("📊 Статистика",callback_data="stats")])
    return InlineKeyboardMarkup(keyboard)
