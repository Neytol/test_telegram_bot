from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
from data_manager import load_users, increment_message_count, register_user
from weather_api import get_weather
from currency_api import get_currency
from dotenv import load_dotenv
import logging
import sys
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log", encoding='utf-8'),  # Логи в файл
        logging.StreamHandler(sys.stdout)  # И в консоль
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

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
        await update.callback_query.edit_message_text(await get_weather("москва"), reply_markup=show_main_buttons())
    if query.data == "piter":
        await update.callback_query.edit_message_text(await get_weather("санкт-петербург"),
                                                      reply_markup=show_main_buttons())
    if query.data == "usd":
        await update.callback_query.edit_message_text(await get_currency("USD"), reply_markup=show_main_buttons())
    if query.data == "eur":
        await update.callback_query.edit_message_text(await get_currency("EUR"), reply_markup=show_main_buttons())


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    is_new = register_user(user.id, user.username, user.first_name)
    welcome = f"Привет {user.first_name}, рад познакомится! 👋" if is_new else f"С возвращением {user.first_name}! 👋"
    await update.message.reply_text(welcome, reply_markup=show_main_buttons())


def show_main_buttons():
    keyboard = [
        [InlineKeyboardButton("🌤️ Погода", callback_data="weather")],
        [InlineKeyboardButton("💰 Курс валюты", callback_data="currency")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


async def handle_awaiting_input(update: Update, context: ContextTypes.DEFAULT_TYPE, user_text: str):
    if context.user_data.get("awaiting_weather"):
        context.user_data["awaiting_weather"] = False
        result = await get_weather(user_text)
    elif context.user_data.get("awaiting_currency"):
        context.user_data["awaiting_currency"] = False
        result = await get_currency(user_text)
    else:
        return False

    await update.message.reply_text(result, reply_markup=show_main_buttons())
    return True


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


def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT, handle_message))
    application.add_handler(CallbackQueryHandler(button_handler))
    logger.info("Бот запущен...")
    application.run_polling()


if __name__ == "__main__":
    main()
