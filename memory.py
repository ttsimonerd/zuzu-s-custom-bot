import aiosqlite
import os

DB = "data/memory.db"

async def init_db():
    os.makedirs("data", exist_ok=True)

    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            channel_id TEXT,
            role TEXT,
            content TEXT
        )
        """)
        await db.commit()

async def add_message(user_id, channel_id, role, content):
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "INSERT INTO messages(user_id, channel_id, role, content) VALUES (?, ?, ?, ?)",
            (user_id, channel_id, role, content),
        )
        await db.commit()

async def get_recent(channel_id, limit=12):
    async with aiosqlite.connect(DB) as db:
        cursor = await db.execute(
            "SELECT role, content FROM messages WHERE channel_id=? ORDER BY id DESC LIMIT ?",
            (channel_id, limit),
        )
        rows = await cursor.fetchall()

    rows.reverse()
    return rows
