import aiosqlite
from config import SUPER_ADMIN_ID

async def get_all_users():
    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute('SELECT * FROM users')
        return await cursor.fetchall()


async def get_all_requests():
    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute('SELECT * FROM requests ORDER BY id ASC')
        return await cursor.fetchall()


async def get_all_requests_page(page, limit):
    async with aiosqlite.connect('database.db') as conn:
        offset = page * limit
        cursor = await conn.execute(
            'SELECT * FROM requests ORDER BY id ASC LIMIT ? OFFSET ?',
            (limit, offset)
        )
        return await cursor.fetchall()


async def get_all_requests_count():
    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute('SELECT COUNT(*) FROM requests')
        result = await cursor.fetchone()
        return result[0]


async def get_new_requests():
    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute(
            "SELECT * FROM requests WHERE status = 'Новая' ORDER BY id DESC"
        )
        return await cursor.fetchall()


async def get_my_admin_requests(admin_id):
    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute(
            "SELECT * FROM requests WHERE admin_id = ? AND status = 'В работе' ORDER BY id DESC",
            (admin_id,)
        )
        return await cursor.fetchall()


async def get_admin_requests_count(admin_id):
    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute(
            "SELECT COUNT(*) FROM requests WHERE admin_id = ? AND status = 'В работе'",
            (admin_id,)
        )
        result = await cursor.fetchone()
        return result[0]


async def get_rejected_requests_page(page, limit):
    async with aiosqlite.connect('database.db') as conn:
        offset = page * limit
        cursor = await conn.execute(
            "SELECT * FROM requests WHERE status = 'Отклонено' ORDER BY id ASC LIMIT ? OFFSET ?",
            (limit, offset)
        )
        return await cursor.fetchall()


async def get_rejected_requests_count():
    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute(
            "SELECT COUNT(*) FROM requests WHERE status = 'Отклонено'"
        )
        result = await cursor.fetchone()
        return result[0]


async def take_request(request_id, admin_id):
    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute(
            "UPDATE requests SET admin_id = ?, status = 'В работе' "
            "WHERE id = ? AND status = 'Новая' "
            "AND (SELECT COUNT(*) FROM requests WHERE admin_id = ? AND status = 'В работе') < 3",
            (admin_id, request_id, admin_id)
        )
        await conn.commit()
        return cursor.rowcount > 0


async def complete_request(request_id, admin_id=None):
    async with aiosqlite.connect('database.db') as conn:
        if admin_id is not None:
            cursor = await conn.execute(
                "UPDATE requests SET status = 'Завершена' "
                "WHERE id = ? AND status = 'В работе' AND admin_id = ?",
                (request_id, admin_id)
            )
        else:
            cursor = await conn.execute(
                "UPDATE requests SET status = 'Завершена' "
                "WHERE id = ? AND status = 'В работе'",
                (request_id,)
            )
        await conn.commit()
        return cursor.rowcount > 0


async def get_request_by_id(request_id):
    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute(
            'SELECT * FROM requests WHERE id = ?',
            (request_id,)
        )
        return await cursor.fetchone()


async def get_admin_request_by_id(request_id, admin_id):
    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute(
            "SELECT * FROM requests WHERE id = ? AND status = 'В работе' AND admin_id = ?",
            (request_id, admin_id)
        )
        return await cursor.fetchone()


async def return_request(request_id, admin_id):
    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute(
            "UPDATE requests SET status = 'Новая', admin_id = NULL "
            "WHERE id = ? AND admin_id = ? AND status = 'В работе'",
            (request_id, admin_id)
        )
        await conn.commit()
        return cursor.rowcount > 0


async def return_rejected_request(request_id):
    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute(
            "UPDATE requests SET status = 'Новая', admin_id = NULL, reason = NULL "
            "WHERE id = ? AND status = 'Отклонено'",
            (request_id,)
        )
        await conn.commit()
        return cursor.rowcount > 0


async def get_statistics():
    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute(
            'SELECT status, COUNT(*) FROM requests GROUP BY status'
        )
        return await cursor.fetchall()


async def cancel_request(request_id, admin_id, reason):
    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute(
            "UPDATE requests SET status = 'Отклонено', reason = ? "
            "WHERE id = ? AND status = 'В работе' AND admin_id = ?",
            (reason, request_id, admin_id)
        )
        await conn.commit()
        return cursor.rowcount > 0


async def get_admin_priority(admin_id):
    if admin_id == SUPER_ADMIN_ID:
        return 4

    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute(
            "SELECT priority FROM admins WHERE admin_id = ?",
            (admin_id,)
        )

        admin = await cursor.fetchone()

        if admin is None:
            return 0

        return admin[0]


async def add_admin(admin_id, admin_role, admin_name, priority):
    async with aiosqlite.connect('database.db') as conn:
        try:
            await conn.execute(
                """
                INSERT INTO admins (admin_id, admin_role, admin_name, priority)
                VALUES (?, ?, ?, ?)
                """,
                (admin_id, admin_role, admin_name, priority)
            )
            await conn.commit()
            return True
        except aiosqlite.IntegrityError:
            return False


async def is_admin(admin_id):
    if admin_id == SUPER_ADMIN_ID:
        return True

    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute(
            "SELECT * FROM admins WHERE admin_id = ?",
            (admin_id,)
        )

        admin = await cursor.fetchone()

        return admin is not None
    