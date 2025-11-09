import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from config import TOKEN
from database import init_db, delete_user, set_favorite_city
from handlers.broadcast_command import broadcast_command
from handlers.button_handler import button_handler
from handlers.handle_message import handle_message
from handlers.start_command import start_command
from handlers.users_info import users_info
from logger import logger    

def main():
    asyncio.run(init_db())
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("delete", delete_user))
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("users_info", users_info))
    application.add_handler(CommandHandler("setcity", set_favorite_city))
    logger.info("Бот запущен...")
    application.run_polling()


if __name__ == "__main__":
    main()
