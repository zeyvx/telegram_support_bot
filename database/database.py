import aiosqlite


async def _add_column(conn, table, column, definition):
    cursor = await conn.execute(f"PRAGMA table_info({table})")
    columns = {row[1] for row in await cursor.fetchall()}
    if column not in columns:
        await conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


async def init_db(conn):
    await conn.execute("PRAGMA foreign_keys = ON")

    await conn.execute("""
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY,
        language TEXT NOT NULL DEFAULT 'ru'
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
        created_at TEXT,
        completed_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    """)

    await conn.execute("""
    CREATE TABLE IF NOT EXISTS admins(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_id INTEGER NOT NULL UNIQUE,
        admin_name TEXT NOT NULL,
        admin_role TEXT DEFAULT 'admin',
        priority INTEGER DEFAULT 1
    )
    """)

    await conn.execute("""
    CREATE TABLE IF NOT EXISTS ratings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        request_id INTEGER NOT NULL UNIQUE,
        user_id INTEGER NOT NULL,
        admin_id INTEGER NOT NULL,
        rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
        created_at TEXT NOT NULL,
        FOREIGN KEY(request_id) REFERENCES requests(id) ON DELETE CASCADE,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    """)

    await _add_column(conn, 'users', 'language', "TEXT NOT NULL DEFAULT 'ru'")
    await _add_column(conn, 'requests', 'created_at', 'TEXT')
    await _add_column(conn, 'requests', 'completed_at', 'TEXT')

    await conn.execute(
        "UPDATE requests SET created_at = COALESCE(created_at, datetime('now')) "
        "WHERE created_at IS NULL"
    )

    await conn.execute("CREATE INDEX IF NOT EXISTS idx_requests_admin_status ON requests(admin_id, status)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_requests_completed_at ON requests(completed_at)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_ratings_admin ON ratings(admin_id)")

    await conn.commit()
