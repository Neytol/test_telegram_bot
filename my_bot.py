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
        logging.StreamHandler(sys.stdout)                 # И в консоль
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")


# async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     # if "help" in update.callback_query.data:
#     #     await update.callback_query.edit_message_text("Тут пока ничего нет")
#     # elif "about" in update.callback_query.data:
#     #     await update.callback_query.edit_message_text("Этот бот создан для обучения!")
#     # await update.callback_query.answer()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # help_button = InlineKeyboardButton("Помощь", callback_data = "help")
    # about_button = InlineKeyboardButton("О боте", callback_data = "about")

    user = update.message.from_user
    is_new = register_user(user.id, user.username, user.first_name)

    welcome = f"Привет {user.first_name}, рад познакомится! 👋" if is_new else f"С возвращением {user.first_name}! 👋"

    reply_keyboard = ReplyKeyboardMarkup([
        ["Погода 🌤️", "Курс валют 💰"],
        ["Случайное число 🎲"], ["Показвать профиль"]
    ],resize_keyboard=True)

    # inline_keyboard = InlineKeyboardMarkup([
    #     [help_button],
    #     [about_button]
    # ])
    # await update.message.reply_text(f"{welcome} Выбери действие:", reply_markup=inline_keyboard)
    await update.message.reply_text(f"{welcome}", reply_markup=reply_keyboard)


async def show_main_keyboard(update: Update):
    reply_keyboard = ReplyKeyboardMarkup([
        ["Погода 🌤️", "Курс валют 💰"],
        ["Случайное число 🎲"],["Показать профиль"]
    ], resize_keyboard=True)
    await update.message.reply_text("Выбери действие: ",reply_markup=reply_keyboard)



async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_text = update.message.text
    user_text_lower = user_text.lower()
    increment_message_count(user.id)


    users = load_users()
    user_id_str = str(user.id)

    if user_id_str not in users:
        await start_command(update, context)
        return

    if user_text == "Погода 🌤️":
        weather_keyboard = ReplyKeyboardMarkup([
            ["Москва"],
            ["Санкт-Петербург"]
        ], resize_keyboard=True)
        await update.message.reply_text("В каком городе ты хочешь проверить погоду?", reply_markup=weather_keyboard)
    elif user_text == "Москва":
            await update.message.reply_text(await get_weather(user_text))
            await show_main_keyboard(update)
    elif user_text == "Санкт-Петербург":
        await update.message.reply_text(await get_weather(user_text))
        await show_main_keyboard(update)
    elif user_text == "Курс валют 💰":
        currency_keyboard = ReplyKeyboardMarkup([
            ["Курс доллара 💵"],
            ["Курс евро 💶"]
        ], resize_keyboard=True)
        await update.message.reply_text("Выбери валюту:", reply_markup=currency_keyboard)
    elif user_text == "Курс доллара 💵":
        await update.message.reply_text(await get_currency(user_text))
        await show_main_keyboard(update)
    elif user_text == "Курс евро 💶":
        await update.message.reply_text(await get_currency(user_text))
        await show_main_keyboard(update)
    elif user_text == "Случайное число 🎲":
        import random
        number = random.randint(1,100)
        await update.message.reply_text(f"Твое число: {number}")
    elif "привет" in user_text_lower:
        await update.message.reply_text("И тебе привет! 👋")
    elif "как дела" in user_text_lower:
        await update.message.reply_text("У меня всё отлично! А у тебя?")
    else:
        await update.message.reply_text("Я пока умею только приветствовать! Используй /help")


def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT, handle_message))

    # application.add_handler(CallbackQueryHandler(button_click))

    print("Бот запущен...")


    application.run_polling()


if __name__ == "__main__":
    main()

