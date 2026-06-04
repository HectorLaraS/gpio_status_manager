from typing import Any

from src.repositories.db import get_connection


def get_poll_execution_by_execution_id(
    execution_id: str,
) -> dict[str, Any] | None:
    query = """
        SELECT
            id,
            execution_id,
            execution_type,
            status,
            started_at,
            finished_at,
            groups_processed,
            routers_processed,
            routers_success,
            routers_failed,
            notes
        FROM dbo.poll_executions
        WHERE execution_id = ?;
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, execution_id)

        row = cursor.fetchone()

        if not row:
            return None

        return {
            "id": row.id,
            "execution_id": str(row.execution_id),
            "execution_type": row.execution_type,
            "status": row.status,
            "started_at": row.started_at,
            "finished_at": row.finished_at,
            "groups_processed": row.groups_processed,
            "routers_processed": row.routers_processed,
            "routers_success": row.routers_success,
            "routers_failed": row.routers_failed,
            "notes": row.notes,
        }

def get_poll_log_summary(
    execution_id: str,
) -> dict[str, int]:
    query = """
        SELECT
            level_name,
            COUNT(*) AS total
        FROM dbo.poll_logs
        WHERE execution_id = ?
        GROUP BY level_name;
    """

    summary = {
        "INFO": 0,
        "WARNING": 0,
        "ERROR": 0,
        "SUCCESS": 0,
    }

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, execution_id)

        rows = cursor.fetchall()

        for row in rows:
            summary[row.level_name.upper()] = row.total

    return summary

def get_poll_logs_by_execution_id(
    execution_id: str,
    limit: int = 500,
) -> list[dict[str, Any]]:
    query = f"""
        SELECT TOP ({limit})
            id,
            router_id,
            level_name,
            source,
            message,
            created_at
        FROM dbo.poll_logs
        WHERE execution_id = ?
        ORDER BY created_at DESC;
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, execution_id)

        rows = cursor.fetchall()

        return [
            {
                "id": row.id,
                "router_id": row.router_id,
                "level_name": row.level_name,
                "source": row.source,
                "message": row.message,
                "created_at": row.created_at,
            }
            for row in rows
        ]