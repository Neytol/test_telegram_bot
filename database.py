from datetime import datetime
import aiosqlite
from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_USER_ID

DB_PATH = "bot.db"


async def init_db():
    """Инициализирует базу данных при запуске бота.

    Создаёт таблицу `users`, если она не существует, с полями:
    id, username, first_name, message_count, registered, last_activity.
    Также добавляет колонку `favorite_city`, если её ещё нет.
    Используется `aiosqlite` для асинхронного подключения.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                 id INTEGER PRIMARY KEY,
                 username TEXT,
                 first_name TEXT,
                 message_count INTEGER DEFAULT 0,
                 registered TEXT,
                 last_activity TEXT
            )
        """)
        try:
            await db.execute("ALTER TABLE users ADD COLUMN favorite_city TEXT")
        except aiosqlite.OperationalError as e:
            if "duplicate column name" in str(e):
                pass
            else:
                raise
        await db.commit()


async def register_user(user_id: int, username: str, first_name: str) -> bool:
    """Регистрирует нового пользователя в базе данных.

    Args:
        user_id (int): Уникальный идентификатор пользователя Telegram.
        username (str): Имя пользователя (username) из Telegram.
        first_name (str): Имя пользователя (first_name) из Telegram.

    Returns:
        bool: True, если пользователь был успешно добавлен; False, если уже существует.

    Регистрация включает сохранение времени регистрации и последней активности.
    Поле `favorite_city` инициализируется как None.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT 1 FROM users WHERE id = ?", (user_id,))
        exist = await cursor.fetchone()

        if not exist:
            now = datetime.now().strftime("%Y-%m-%d %H-%M:%S")
            await db.execute(
                "INSERT INTO users (id, username, first_name, registered, last_activity, favorite_city) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, username, first_name, now, now, None)
            )
            await db.commit()
            return True
        return False


async def increment_message_count(user_id: int):
    """Увеличивает счётчик сообщений пользователя и обновляет время последней активности.

    Args:
        user_id (int): Уникальный идентификатор пользователя Telegram.

    Операция выполняется атомарно в рамках одной транзакции.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        now = datetime.now().strftime("%Y-%m-%d %H-%M:%S")
        await db.execute(
            "UPDATE users SET message_count = message_count + 1, last_activity = ? WHERE id = ?",
            (now, user_id)
        )
        await db.commit()


async def get_user(user_id: int):
    """Получает информацию о пользователе по его ID.

    Args:
        user_id (int): Уникальный идентификатор пользователя Telegram.

    Returns:
        dict or None: Словарь с данными пользователя, если найден, иначе None.
        Ключи словаря: 'id', 'username', 'first_name', 'message_count', 'registered',
        'last_activity', 'favorite_city'.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = await cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "username": row[1],
                "first_name": row[2],
                "message_count": row[3],
                "registered": row[4],
                "last_activity": row[5],
                "favorite_city": row[6]
            }
        return None


async def get_all_users():
    """Получает список всех зарегистрированных пользователей.

    Returns:
        list of dict: Список словарей с данными всех пользователей.
        Каждый словарь содержит те же поля, что и в `get_user`.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT * FROM users")
        rows = await cursor.fetchall()
        return [
            {
                "id": row[0],
                "username": row[1],
                "first_name": row[2],
                "message_count": row[3],
                "registered": row[4],
                "last_activity": row[5],
                "favorite_city": row[6]
            }
            for row in rows
        ]


async def delete_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды удаления пользователя из базы данных.

    Доступно только для администратора (ID из config.ADMIN_USER_ID).

    Args:
        update (Update): Объект обновления от Telegram.
        context (ContextTypes.DEFAULT_TYPE): Контекст выполнения команды.

    Поведение:
        - Проверяет права доступа.
        - Ожидает ID пользователя как аргумент.
        - Удаляет пользователя из БД, если он существует.
        - Отправляет соответствующие сообщения в чат.
    """
    if update.message.from_user.id != ADMIN_USER_ID:
        await update.message.reply_text("❌ Доступ запрещён.")
        return
    if not context.args:
        await update.message.reply_text("Использование: /delete <Имя пользователя>")
        return
    try:
        user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("ID должен быть числом")
        return
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT 1 FROM users WHERE id = ?", (user_id,))
        exist = await cursor.fetchone()
        if not exist:
            await update.message.reply_text(f"Пользователь с id {user_id} не найден")
            return
        await db.execute("DELETE FROM users WHERE id = ?", (user_id,))
        await db.commit()
        await update.message.reply_text(f"Пользователь {user_id} удален из базы")


async def set_favorite_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды установки любимого города пользователя.

    Args:
        update (Update): Объект обновления от Telegram.
        context (ContextTypes.DEFAULT_TYPE): Контекст выполнения команды.

    Поведение:
        - Ожидает название города как аргумент команды.
        - Обновляет поле `favorite_city` для текущего пользователя.
        - Подтверждает установку города в чате.
    """
    if not context.args:
        await update.message.reply_text("Использование: /setcity <город>")
        return
    city = " ".join(context.args)
    user_id = update.message.from_user.id

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET favorite_city = ? WHERE id = ?", (city, user_id,))
        await db.commit()
    await update.message.reply_text(f"Город по умолчанию {city}")
