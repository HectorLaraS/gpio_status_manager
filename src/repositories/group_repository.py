from typing import Any

from src.repositories.db import get_connection


def count_groups() -> int:
    query = """
        SELECT COUNT(*)
        FROM dbo.groups;
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        return cursor.fetchone()[0]


def count_active_groups() -> int:
    query = """
        SELECT COUNT(*)
        FROM dbo.groups
        WHERE is_active = 1;
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        return cursor.fetchone()[0]


def get_active_groups() -> list[dict[str, Any]]:
    query = """
        SELECT
            id,
            netcloud_id,
            name,
            is_active
        FROM dbo.groups
        WHERE is_active = 1
        ORDER BY name;
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)

        rows = cursor.fetchall()

        groups = []
        for row in rows:
            groups.append({
                "id": row.id,
                "netcloud_id": row.netcloud_id,
                "name": row.name,
                "is_active": bool(row.is_active),
            })

        return groups