import aiosqlite
import sqlite3
from datetime import datetime


async def add_user(user_id):
    try:
        async with aiosqlite.connect('database.db') as conn:
            await conn.execute(
                "INSERT OR IGNORE INTO users(user_id, language) VALUES (?, 'ru')",
                (user_id,)
            )
            await conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False


async def get_user(user_id):
    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute(
            "SELECT user_id, language FROM users WHERE user_id = ?",
            (user_id,)
        )
        return await cursor.fetchone()


async def get_language(user_id):
    user = await get_user(user_id)

    if user is None:
        return 'ru'

    if user[1] == 'ru' or user[1] == 'uz':
        return user[1]

    return 'ru'


async def set_language(user_id, language):
    if language != 'ru' and language != 'uz':
        return False

    async with aiosqlite.connect('database.db') as conn:
        await conn.execute(
            "INSERT INTO users(user_id, language) VALUES (?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET language = excluded.language",
            (user_id, language)
        )
        await conn.commit()
        return True


async def add_request(user_id, category, request, file_id, file_type=None):
    created_at = datetime.now().isoformat()

    async with aiosqlite.connect('database.db') as conn:
        await conn.execute(
            "INSERT INTO requests "
            "(user_id, category, request, file_id, file_type, created_at) "
            "VALUES (?,?,?,?,?,?)",
            (user_id, category, request, file_id, file_type, created_at)
        )
        await conn.commit()


async def get_my_requests(user_id):
    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute(
            "SELECT * FROM requests WHERE user_id = ? ORDER BY id DESC",
            (user_id,)
        )
        return await cursor.fetchall()


async def cancel_own_request(request_id, user_id):
    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute(
            "UPDATE requests SET status = 'Отменена' "
            "WHERE id = ? AND user_id = ? AND status = 'Новая'",
            (request_id, user_id)
        )
        await conn.commit()
        return cursor.rowcount > 0
