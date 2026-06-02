from typing import Any

from src.repositories.db import get_connection


def update_incident_rule(
    rule_id: int,
    duration_minutes: int,
    priority: str,
    is_active: bool,
) -> None:

    query = """
        UPDATE dbo.incident_rules
        SET
            duration_minutes = ?,
            priority = ?,
            is_active = ?,
            updated_at = SYSUTCDATETIME()
        WHERE id = ?;
    """

    params = (
        duration_minutes,
        priority,
        int(is_active),
        rule_id,
    )

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()

def get_incident_rules() -> list[dict[str, Any]]:
    query = """
        SELECT
            id,
            rule_key,
            rule_name,
            alert_source,
            alert_match,
            duration_minutes,
            priority,
            is_active
        FROM dbo.incident_rules
        ORDER BY rule_name;
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)

        rows = cursor.fetchall()

        return [
            {
                "id": row.id,
                "rule_key": row.rule_key,
                "rule_name": row.rule_name,
                "alert_source": row.alert_source,
                "alert_match": row.alert_match,
                "duration_minutes": row.duration_minutes,
                "priority": row.priority,
                "is_active": bool(row.is_active),
            }
            for row in rows
        ]