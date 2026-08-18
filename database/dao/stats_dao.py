import aiosqlite


async def get_admin_stats(admin_id):
    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute(
            """
            SELECT
                COUNT(CASE WHEN status = 'Завершена' THEN 1 END),
                COUNT(CASE WHEN status = 'Завершена'
                           AND date(completed_at) = date('now', '+5 hours') THEN 1 END),
                COUNT(CASE WHEN status = 'В работе' THEN 1 END)
            FROM requests
            WHERE admin_id = ?
            """,
            (admin_id,)
        )
        processed_total, processed_today, active = await cursor.fetchone()

        cursor = await conn.execute(
            """
            SELECT COUNT(*), COALESCE(AVG(rating), 0)
            FROM ratings
            WHERE admin_id = ?
            """,
            (admin_id,)
        )
        rating_count, average_rating = await cursor.fetchone()

        return {
            'processed_total': processed_total or 0,
            'processed_today': processed_today or 0,
            'active': active or 0,
            'rating_count': rating_count or 0,
            'average_rating': average_rating or 0,
        }


async def get_admin_ranking():
    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.execute(
            """
            SELECT
                a.admin_id,
                a.admin_name,
                COALESCE((
                    SELECT AVG(r.rating)
                    FROM ratings r
                    WHERE r.admin_id = a.admin_id
                ), 0) AS avg_rating,
                (
                    SELECT COUNT(*)
                    FROM ratings r
                    WHERE r.admin_id = a.admin_id
                ) AS rating_count,
                (
                    SELECT COUNT(*)
                    FROM requests req
                    WHERE req.admin_id = a.admin_id
                      AND req.status = 'Завершена'
                ) AS processed
            FROM admins a
            ORDER BY
                CASE WHEN rating_count > 0 THEN 0 ELSE 1 END,
                avg_rating DESC,
                rating_count DESC,
                processed DESC,
                a.admin_name COLLATE NOCASE ASC
            """
        )
        return await cursor.fetchall()


async def get_admin_rank(admin_id):
    rows = await get_admin_ranking()
    for position, row in enumerate(rows, 1):
        if row[0] == admin_id and row[3] > 0:
            return position, len(rows)
    return None, len(rows)
