from typing import Any

from src.repositories.db import get_connection

def get_last_execution_by_type(execution_type: str) -> dict[str, Any] | None:
    query = """
        SELECT TOP 1
            execution_type,
            status,
            started_at,
            finished_at,
            DATEDIFF(SECOND, started_at, finished_at) AS duration_seconds,
            routers_processed,
            routers_success,
            routers_failed,
            notes
        FROM dbo.poll_executions
        WHERE execution_type = ?
        ORDER BY started_at DESC;
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, execution_type)
        row = cursor.fetchone()

        if not row:
            return None

        return {
            "execution_type": row.execution_type,
            "status": row.status,
            "started_at": row.started_at,
            "finished_at": row.finished_at,
            "duration_seconds": row.duration_seconds,
            "duration": format_duration(row.duration_seconds),
            "routers_processed": row.routers_processed,
            "routers_success": row.routers_success,
            "routers_failed": row.routers_failed,
            "notes": row.notes,
        }


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

def get_open_alerts_summary() -> dict[str, Any]:
    query = """
        SELECT
            COUNT(*) AS total_open,
            SUM(CASE WHEN priority = 'P1' THEN 1 ELSE 0 END) AS p1,
            SUM(CASE WHEN priority = 'P2' THEN 1 ELSE 0 END) AS p2,
            SUM(CASE WHEN priority = 'P3' THEN 1 ELSE 0 END) AS p3,
            SUM(CASE WHEN priority = 'P4' THEN 1 ELSE 0 END) AS p4,
            SUM(CASE WHEN priority = 'P5' THEN 1 ELSE 0 END) AS p5
        FROM dbo.alerts
        WHERE status = 'OPEN';
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        row = cursor.fetchone()

        return {
            "total_open": row.total_open or 0,
            "p1": row.p1 or 0,
            "p2": row.p2 or 0,
            "p3": row.p3 or 0,
            "p4": row.p4 or 0,
            "p5": row.p5 or 0,
        }


def get_alerts_by_type() -> list[dict[str, Any]]:
    query = """
        SELECT
            ir.rule_name,
            COUNT(*) AS total
        FROM dbo.alerts a
        JOIN dbo.incident_rules ir
            ON a.rule_id = ir.id
        WHERE a.status = 'OPEN'
        GROUP BY ir.rule_name
        ORDER BY total DESC;
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

        return [
            {
                "rule_name": row.rule_name,
                "total": row.total,
            }
            for row in rows
        ]


def get_recently_opened_alerts(limit: int = 20) -> list[dict[str, Any]]:
    query = """
        SELECT TOP (?)
            a.alert_number,
            a.status,
            a.priority,
            a.title,
            a.opened_at,
            a.last_detected_at,
            a.occurrence_count,
            r.name AS router_name,
            r.description AS router_description,
            ir.rule_name
        FROM dbo.alerts a
        JOIN dbo.routers r
            ON a.router_id = r.id
        JOIN dbo.incident_rules ir
            ON a.rule_id = ir.id
        WHERE a.status = 'OPEN'
        ORDER BY a.opened_at DESC;
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, limit)
        rows = cursor.fetchall()

        return [
            {
                "alert_number": row.alert_number,
                "status": row.status,
                "priority": row.priority,
                "title": row.title,
                "opened_at": row.opened_at,
                "last_detected_at": row.last_detected_at,
                "occurrence_count": row.occurrence_count,
                "router_name": row.router_name,
                "router_description": row.router_description,
                "rule_name": row.rule_name,
            }
            for row in rows
        ]


def get_recently_closed_alerts(limit: int = 20) -> list[dict[str, Any]]:
    query = """
        SELECT TOP (?)
            a.alert_number,
            a.status,
            a.priority,
            a.title,
            a.opened_at,
            a.closed_at,
            a.occurrence_count,
            r.name AS router_name,
            r.description AS router_description,
            ir.rule_name
        FROM dbo.alerts a
        JOIN dbo.routers r
            ON a.router_id = r.id
        JOIN dbo.incident_rules ir
            ON a.rule_id = ir.id
        WHERE a.status = 'CLOSED'
        ORDER BY a.closed_at DESC;
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, limit)
        rows = cursor.fetchall()

        return [
            {
                "alert_number": row.alert_number,
                "status": row.status,
                "priority": row.priority,
                "title": row.title,
                "opened_at": row.opened_at,
                "closed_at": row.closed_at,
                "occurrence_count": row.occurrence_count,
                "router_name": row.router_name,
                "router_description": row.router_description,
                "rule_name": row.rule_name,
            }
            for row in rows
        ]


def get_top_affected_routers(limit: int = 10) -> list[dict[str, Any]]:
    query = """
        SELECT TOP (?)
            r.name AS router_name,
            r.description AS router_description,
            COUNT(*) AS total_alerts
        FROM dbo.alerts a
        JOIN dbo.routers r
            ON a.router_id = r.id
        GROUP BY
            r.name,
            r.description
        ORDER BY total_alerts DESC;
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, limit)
        rows = cursor.fetchall()

        return [
            {
                "router_name": row.router_name,
                "router_description": row.router_description,
                "total_alerts": row.total_alerts,
            }
            for row in rows
        ]