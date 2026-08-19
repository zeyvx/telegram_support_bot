import aiosqlite
from datetime import datetime
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
        cursor = await conn.execute(
            'SELECT * FROM requests ORDER BY id ASC LIMIT ? OFFSET ?',
            (limit, page * limit)
        )
        return await cursor.fetchall()


async def get_all_requests_count():
    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute('SELECT COUNT(*) FROM requests')
        row = await cursor.fetchone()
        return row[0]


async def get_new_requests():
    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute(
            "SELECT * FROM requests WHERE status = 'Новая' ORDER BY id ASC"
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
        row = await cursor.fetchone()
        return row[0]


async def get_rejected_requests_page(page, limit):
    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute(
            "SELECT * FROM requests WHERE status = 'Отклонено' ORDER BY id ASC LIMIT ? OFFSET ?",
            (limit, page * limit)
        )
        return await cursor.fetchall()


async def get_rejected_requests_count():
    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute(
            "SELECT COUNT(*) FROM requests WHERE status = 'Отклонено'"
        )
        row = await cursor.fetchone()
        return row[0]


async def take_request(request_id, admin_id):
    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute(
            "UPDATE requests SET admin_id = ?, status = 'В работе' "
            "WHERE id = ? AND status = 'Новая' "
            "AND (SELECT COUNT(*) FROM requests "
            "WHERE admin_id = ? AND status = 'В работе') < 3",
            (admin_id, request_id, admin_id)
        )
        await conn.commit()
        return cursor.rowcount > 0


async def complete_request(request_id, admin_id=None):
    completed_at = datetime.now().isoformat()

    async with aiosqlite.connect('database.db') as conn:
        if admin_id is not None:
            cursor = await conn.execute(
                "UPDATE requests SET status = 'Завершена', completed_at = ? "
                "WHERE id = ? AND status = 'В работе' AND admin_id = ?",
                (completed_at, request_id, admin_id)
            )
        else:
            cursor = await conn.execute(
                "UPDATE requests SET status = 'Завершена', completed_at = ? "
                "WHERE id = ? AND status = 'В работе'",
                (completed_at, request_id)
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
            'SELECT priority FROM admins WHERE admin_id = ?',
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
                'INSERT INTO admins (admin_id, admin_role, admin_name, priority) '
                'VALUES (?, ?, ?, ?)',
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
            'SELECT 1 FROM admins WHERE admin_id = ?',
            (admin_id,)
        )
        admin = await cursor.fetchone()

        if admin is not None:
            return True

        return False


async def get_admin_stats(admin_id):
    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute(
            "SELECT COUNT(CASE WHEN status = 'Завершена' THEN 1 END), "
            "COUNT(CASE WHEN status = 'Завершена' AND "
            "date(completed_at, '+5 hours') = date('now', '+5 hours') THEN 1 END) "
            "FROM requests WHERE admin_id = ?",
            (admin_id,)
        )
        processed_total, processed_today = await cursor.fetchone()

        cursor = await conn.execute(
            'SELECT COUNT(*), COALESCE(AVG(rating), 0) FROM ratings WHERE admin_id = ?',
            (admin_id,)
        )
        rating_count, average_rating = await cursor.fetchone()

        cursor = await conn.execute(
            "SELECT COUNT(*) FROM requests WHERE admin_id = ? AND status = 'В работе'",
            (admin_id,)
        )
        active_row = await cursor.fetchone()
        active = active_row[0]

    return {
        'processed_total': processed_total or 0,
        'processed_today': processed_today or 0,
        'rating_count': rating_count or 0,
        'average_rating': average_rating or 0,
        'active': active or 0
    }


async def get_admin_rating_rank(admin_id):
    rows = await get_admin_ranking()

    ranked = []
    for row in rows:
        if row[3] > 0:
            ranked.append(row)

    position = 1
    for row in ranked:
        if row[0] == admin_id:
            return position, len(ranked)
        position += 1

    return None, len(ranked)


async def get_admin_ranking():
    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute(
            "SELECT a.admin_id, a.admin_name, "
            "COALESCE((SELECT AVG(r.rating) FROM ratings r "
            "WHERE r.admin_id = a.admin_id), 0), "
            "(SELECT COUNT(*) FROM ratings r WHERE r.admin_id = a.admin_id), "
            "(SELECT COUNT(*) FROM requests q "
            "WHERE q.admin_id = a.admin_id AND q.status = 'Завершена') "
            "FROM admins a "
            "ORDER BY 3 DESC, 4 DESC, 5 DESC, a.admin_id ASC"
        )
        rows = await cursor.fetchall()

    super_admin_exists = False
    for row in rows:
        if row[0] == SUPER_ADMIN_ID:
            super_admin_exists = True
            break

    if not super_admin_exists:
        async with aiosqlite.connect('database.db') as conn:
            cursor = await conn.execute(
                "SELECT COALESCE((SELECT AVG(rating) FROM ratings WHERE admin_id = ?), 0), "
                "(SELECT COUNT(*) FROM ratings WHERE admin_id = ?), "
                "(SELECT COUNT(*) FROM requests WHERE admin_id = ? AND status = 'Завершена')",
                (SUPER_ADMIN_ID, SUPER_ADMIN_ID, SUPER_ADMIN_ID)
            )
            avg_rating, rating_count, processed = await cursor.fetchone()

        rows.append(
            (
                SUPER_ADMIN_ID,
                'Супер-админ',
                avg_rating or 0,
                rating_count or 0,
                processed or 0
            )
        )

    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            first = rows[i]
            second = rows[j]

            should_swap = False

            if second[2] > first[2]:
                should_swap = True
            elif second[2] == first[2] and second[3] > first[3]:
                should_swap = True
            elif second[2] == first[2] and second[3] == first[3] and second[4] > first[4]:
                should_swap = True
            elif (
                second[2] == first[2]
                and second[3] == first[3]
                and second[4] == first[4]
                and second[0] < first[0]
            ):
                should_swap = True

            if should_swap:
                rows[i] = second
                rows[j] = first

    return rows


async def add_rating(request_id, user_id, rating):
    if rating < 1 or rating > 5:
        return False

    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute(
            'SELECT user_id, admin_id, status FROM requests WHERE id = ?',
            (request_id,)
        )
        request = await cursor.fetchone()

        if request is None:
            return False

        if request[0] != user_id:
            return False

        if request[1] is None:
            return False

        if request[2] != 'Завершена':
            return False

        try:
            await conn.execute(
                'INSERT INTO ratings '
                '(request_id, user_id, admin_id, rating, created_at) '
                'VALUES (?, ?, ?, ?, ?)',
                (
                    request_id,
                    user_id,
                    request[1],
                    rating,
                    datetime.now().isoformat()
                )
            )
            await conn.commit()
            return True
        except aiosqlite.IntegrityError:
            return False


async def has_rating(request_id, user_id):
    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute(
            'SELECT 1 FROM ratings WHERE request_id = ? AND user_id = ?',
            (request_id, user_id)
        )
        rating = await cursor.fetchone()

        if rating is not None:
            return True

        return False
