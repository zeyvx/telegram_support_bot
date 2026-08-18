import aiosqlite


async def init_db(conn):
    await conn.execute("PRAGMA foreign_keys = ON")

    await conn.execute("""
CREATE TABLE IF NOT EXISTS users(
                        user_id INTEGER PRIMARY KEY
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

    await conn.execute("""
CREATE TABLE IF NOT EXISTS admins(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        admin_id INTEGER NOT NULL UNIQUE,
                        admin_name TEXT NOT NULL,
                        admin_role TEXT DEFAULT "admin",
                        priority INTEGER DEFAULT 1
                        )
""")

    await conn.commit()
