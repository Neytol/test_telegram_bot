from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from api.currency_api import get_currency
from api.weather_api import get_weather
from config import ADMIN_USER_ID
from database import get_all_users
from handlers.show_main_buttons import show_main_buttons
from logger import logger


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        if query.data == "weather":
            weather_buttons = [
                [InlineKeyboardButton("Москва", callback_data="moscow")],
                [InlineKeyboardButton("Санкт-Петербург", callback_data="piter")]
            ]
            reply_markup = InlineKeyboardMarkup(weather_buttons)
            await query.edit_message_text("🌤️ Напиши название города:", reply_markup=reply_markup)
            context.user_data["awaiting_weather"] = True
            return
        if query.data == "currency":
            currency_buttons = [
                [InlineKeyboardButton("Курс доллара 💵", callback_data="usd")],
                [InlineKeyboardButton("Курс евро 💶", callback_data="eur")]
            ]
            reply_markup = InlineKeyboardMarkup(currency_buttons)
            await query.edit_message_text("Выберите валюту:", reply_markup=reply_markup)
            context.user_data["awaiting_currency"] = True
            return
        if query.data == "moscow":
            await update.callback_query.edit_message_text(await get_weather("москва"), reply_markup= show_main_buttons(query.from_user.id))
        if query.data == "piter":
            await update.callback_query.edit_message_text(await get_weather("санкт-петербург"),
                                                          reply_markup=  show_main_buttons(query.from_user.id))
        if query.data == "usd":
            await update.callback_query.edit_message_text(await get_currency("USD"), reply_markup=  show_main_buttons(query.from_user.id))
        if query.data == "eur":
            await update.callback_query.edit_message_text(await get_currency("EUR"), reply_markup=  show_main_buttons(query.from_user.id))
        if query.data == "stats":
            if update.callback_query.from_user.id != ADMIN_USER_ID:
                return update.callback_query.edit_message_text("Доступ запрещен", show_main_buttons(query.from_user.id))
            users =  await get_all_users()
            total_users = len(users)
            total_messages = sum(user.get("message_count", 0) for user in users.values())
            text = f"Статистика:\n"f"Колличество пользователей: {total_users}\n"f"Колличество сообщений: {total_messages}"
            await update.callback_query.edit_message_text(text, reply_markup= show_main_buttons(query.from_user.id))
    except Exception as e:
        logger.error(e)
