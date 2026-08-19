import aiosqlite


async def get_admin_stats(admin_id):
    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute(
            """
            SELECT
                COUNT(CASE WHEN status = 'Завершена' THEN 1 END),
                COUNT(CASE WHEN status = 'Завершена' AND date(completed_at, '+5 hours') = date('now', '+5 hours') THEN 1 END),
                COUNT(CASE WHEN status = 'В работе' THEN 1 END)
            FROM requests WHERE admin_id = ?
            """, (admin_id,)
        )
        processed_total, processed_today, active = await cursor.fetchone()

        cursor = await conn.execute(
            "SELECT COUNT(*), COALESCE(AVG(rating), 0) FROM ratings WHERE admin_id = ?",
            (admin_id,)
        )
        rating_count, average_rating = await cursor.fetchone()

        cursor = await conn.execute(
            "SELECT COUNT(*) FROM requests WHERE admin_id = ? AND status = 'Отклонено'",
            (admin_id,)
        )
        rejected = (await cursor.fetchone())[0]

        cursor = await conn.execute("SELECT status, COUNT(*) FROM requests GROUP BY status")
        rows = await cursor.fetchall()

    overall_total = 0
    overall_new = 0
    overall_active = 0
    overall_completed = 0
    overall_rejected = 0
    overall_cancelled = 0

    for row in rows:
        status = row[0]
        count = row[1]
        overall_total += count

        if status == 'Новая':
            overall_new = count
        elif status == 'В работе':
            overall_active = count
        elif status == 'Завершена':
            overall_completed = count
        elif status == 'Отклонено':
            overall_rejected = count
        elif status == 'Отменена':
            overall_cancelled = count

    return {
        'processed_total': processed_total or 0,
        'processed_today': processed_today or 0,
        'active': active or 0,
        'rejected': rejected or 0,
        'rating_count': rating_count or 0,
        'average_rating': average_rating or 0,
        'overall_total': overall_total,
        'overall_new': overall_new,
        'overall_active': overall_active,
        'overall_completed': overall_completed,
        'overall_rejected': overall_rejected,
        'overall_cancelled': overall_cancelled,
    }


async def get_admin_ranking():
    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute(
            """
            SELECT
                a.admin_id,
                a.admin_name,
                COALESCE((SELECT AVG(r.rating) FROM ratings r WHERE r.admin_id = a.admin_id), 0),
                (SELECT COUNT(*) FROM ratings r WHERE r.admin_id = a.admin_id),
                (SELECT COUNT(*) FROM requests req WHERE req.admin_id = a.admin_id AND req.status = 'Завершена')
            FROM admins a
            ORDER BY 3 DESC, 4 DESC, 5 DESC, a.admin_name COLLATE NOCASE ASC
            """
        )
        rows = await cursor.fetchall()

    return rows


async def get_admin_rank(admin_id):
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
