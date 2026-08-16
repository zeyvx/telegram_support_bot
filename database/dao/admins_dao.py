import aiosqlite


async def get_all_users():
    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute("SELECT * FROM users")
        return await cursor.fetchall()


async def get_all_requests():
    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute("SELECT * FROM requests ORDER BY id DESC")
        return await cursor.fetchall()


async def get_new_requests():
    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute("SELECT * FROM requests WHERE status = 'Новая' ORDER BY id DESC")
        return await cursor.fetchall()


async def get_my_admin_requests(admin_id):
    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute(
            "SELECT * FROM requests WHERE admin_id = ? AND status = 'В работе' ORDER BY id DESC",
            (admin_id,)
        )
        return await cursor.fetchall()


async def take_request(request_id, admin_id):
    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute(
            "UPDATE requests SET admin_id = ?, status = 'В работе' "
            "WHERE id = ? AND status = 'Новая'",
            (admin_id, request_id)
        )
        await conn.commit()
        return cursor.rowcount > 0


async def complete_request(request_id, admin_id):
    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute(
            "UPDATE requests SET status = 'Завершена' "
            "WHERE id = ? AND status = 'В работе' AND admin_id = ?",
            (request_id, admin_id)
        )
        await conn.commit()
        return cursor.rowcount > 0


async def get_request_by_id(request_id):
    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute("SELECT * FROM requests WHERE id = ?", (request_id,))
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


async def get_statistics():
    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute("SELECT status, COUNT(*) FROM requests GROUP BY status")
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
