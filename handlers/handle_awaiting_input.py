from telegram import Update
from telegram.ext import ContextTypes
from api.currency_api import get_currency
from api.weather_api import get_weather
from handlers.show_main_buttons import show_main_buttons


async def handle_awaiting_input(update: Update, context: ContextTypes.DEFAULT_TYPE, user_text: str):
    if context.user_data.get("awaiting_weather"):
        del context.user_data['awaiting_weather']
        result = await get_weather(user_text)
    elif context.user_data.get('awaiting_currency'):
        del context.user_data['awaiting_currency']
        result = await get_currency(user_text)
    else:
        return False
    await update.message.reply_text(result, reply_markup= show_main_buttons(update.message.from_user.id))
    return True
