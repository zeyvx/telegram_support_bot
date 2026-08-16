import aiosqlite


async def init_db(conn):
    await conn.execute("PRAGMA foreign_keys = ON")

    await conn.execute("""
CREATE TABLE IF NOT EXISTS users(
                        user_id INTEGER PRIMARY KEY,
                        phone TEXT UNIQUE
                        )
                        """)

    await conn.execute("""
CREATE TABLE IF NOT EXISTS requests(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        category TEXT NOT NULL,
                        request TEXT NOT NULL,
                        file_id TEXT,
                        status TEXT DEFAULT 'Новая',
                        admin_id INTEGER NULL,
                        reason TEXT NULL,
                        file_type TEXT NULL,
                        FOREIGN KEY(user_id) REFERENCES users(user_id)
                        )
""")

    cursor = await conn.execute("PRAGMA table_info(requests)")
    columns = await cursor.fetchall()
    column_names = [column[1] for column in columns]

    if "file_type" not in column_names:
        await conn.execute("ALTER TABLE requests ADD COLUMN file_type TEXT NULL")

    await conn.commit()
