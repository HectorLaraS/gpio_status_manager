from typing import Any

from src.repositories.db import get_connection


def format_duration(seconds: int | None) -> str:
    if seconds is None:
        return "N/A"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60

    if hours > 0:
        return f"{hours}h {minutes}m {remaining_seconds}s"

    if minutes > 0:
        return f"{minutes}m {remaining_seconds}s"

    return f"{remaining_seconds}s"


def get_poll_executions(limit: int = 200) -> list[dict[str, Any]]:
    query = f"""
        SELECT TOP ({limit})
            id,
            execution_id,
            execution_type,
            status,
            started_at,
            finished_at,
            DATEDIFF(SECOND, started_at, finished_at) AS duration_seconds,
            groups_processed,
            routers_processed,
            routers_success,
            routers_failed,
            notes
        FROM dbo.poll_executions
        ORDER BY started_at DESC;
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

        return [
            {
                "id": row.id,
                "execution_id": row.execution_id,
                "execution_type": row.execution_type,
                "status": row.status,
                "started_at": row.started_at,
                "finished_at": row.finished_at,
                "duration": format_duration(row.duration_seconds),
                "groups_processed": row.groups_processed,
                "routers_processed": row.routers_processed,
                "routers_success": row.routers_success,
                "routers_failed": row.routers_failed,
                "notes": row.notes,
            }
            for row in rows
        ]