from datetime import datetime
import aiosqlite

DB_PATH = "bot.db"

async def init_db():
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
        await db.commit()

async def register_user(user_id: int, username: str, first_name: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT 1 FROM users WHERE id = ?", (user_id,))
        exist = await  cursor.fetchone()

        if not exist:
            now = datetime.now().strftime("%Y-%m-%d %H-%M:%S")
            await db.execute(
                "INSERT INTO users (id, username, first_name, registered, last_activity) VALUES (?, ?, ?, ?, ?)",
                (user_id, username, first_name, now, now)
            )
            await db.commit()
            return True
        return False

async def increment_message_count(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        now = datetime.now().strftime("%Y-%m-%d %H-%M:%S")
        await db.execute(
            "UPDATE users SET message_count = message_count + 1, last_activity = ?, WHERE id = ?",
            (user_id, now)
        )
        await db.commit()

async def get_user(user_id: int):
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
                "last_activity": row[5]
            }
        return None


async def get_all_users():
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
                "last_activity": row[5]
            }
            for row in rows
        ]