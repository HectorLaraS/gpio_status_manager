from datetime import datetime
from typing import Any

from src.repositories.db import get_connection

def get_alert_by_id(alert_id: int) -> dict[str, Any] | None:
    query = """
        SELECT
            a.id,
            a.alert_number,
            a.status,
            a.priority,
            a.title,
            a.router_id,
            a.rule_id,
            a.last_detected_at,
            a.description,
            a.opened_at,
            a.closed_at,
            a.occurrence_count,
            a.external_system,
            a.external_ticket,
            a.external_url,
            r.name AS router_name,
            r.description AS router_description,
            ir.rule_name
        FROM dbo.alerts a
        JOIN dbo.routers r
            ON a.router_id = r.id
        JOIN dbo.incident_rules ir
            ON a.rule_id = ir.id
        WHERE a.id = ?;
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, alert_id)
        row = cursor.fetchone()

        if not row:
            return None

        return {
            "id": row.id,
            "alert_number": row.alert_number,
            "status": row.status,
            "priority": row.priority,
            "title": row.title,
            "router_id": row.router_id,
            "rule_id": row.rule_id,
            "last_detected_at": row.last_detected_at,
            "description": row.description,
            "opened_at": row.opened_at,
            "closed_at": row.closed_at,
            "occurrence_count": row.occurrence_count,
            "external_system": row.external_system,
            "external_ticket": row.external_ticket,
            "external_url": row.external_url,
            "router_name": row.router_name,
            "router_description": row.router_description,
            "rule_name": row.rule_name,
        }


def update_alert_external_reference(
    alert_id: int,
    external_system: str | None,
    external_ticket: str | None,
    external_url: str | None,
) -> None:
    query = """
        UPDATE dbo.alerts
        SET
            external_system = ?,
            external_ticket = ?,
            external_url = ?,
            updated_at = SYSUTCDATETIME()
        WHERE id = ?;
    """

    params = (
        external_system,
        external_ticket,
        external_url,
        alert_id,
    )

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()

def generate_alert_number() -> str:
    now = datetime.now()
    prefix = now.strftime("ALR-%y%m")

    query = """
        SELECT COUNT(*)
        FROM dbo.alerts
        WHERE alert_number LIKE ?;
    """

    like_pattern = f"{prefix}%"

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, like_pattern)
        count = cursor.fetchone()[0]

    next_number = count + 1

    return f"{prefix}{next_number:06d}"


def get_open_alert(
    router_id: int,
    rule_id: int,
) -> dict[str, Any] | None:
    query = """
        SELECT
            id,
            alert_number,
            status,
            priority,
            router_id,
            rule_id,
            title,
            description,
            opened_at,
            closed_at,
            first_detected_at,
            last_detected_at,
            occurrence_count,
            external_system,
            external_ticket
        FROM dbo.alerts
        WHERE router_id = ?
          AND rule_id = ?
          AND status = 'OPEN';
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, router_id, rule_id)
        row = cursor.fetchone()

        if not row:
            return None

        return {
            "id": row.id,
            "alert_number": row.alert_number,
            "status": row.status,
            "priority": row.priority,
            "router_id": row.router_id,
            "rule_id": row.rule_id,
            "title": row.title,
            "description": row.description,
            "opened_at": row.opened_at,
            "closed_at": row.closed_at,
            "first_detected_at": row.first_detected_at,
            "last_detected_at": row.last_detected_at,
            "occurrence_count": row.occurrence_count,
            "external_system": row.external_system,
            "external_ticket": row.external_ticket,
        }


def create_alert(
    router_id: int,
    rule_id: int,
    priority: str,
    title: str,
    description: str | None,
) -> str:
    alert_number = generate_alert_number()

    query = """
        INSERT INTO dbo.alerts (
            alert_number,
            status,
            priority,
            router_id,
            rule_id,
            title,
            description,
            opened_at,
            first_detected_at,
            last_detected_at,
            occurrence_count,
            created_at,
            updated_at
        )
        VALUES (
            ?,
            'OPEN',
            ?,
            ?,
            ?,
            ?,
            ?,
            SYSUTCDATETIME(),
            SYSUTCDATETIME(),
            SYSUTCDATETIME(),
            1,
            SYSUTCDATETIME(),
            SYSUTCDATETIME()
        );
    """

    params = (
        alert_number,
        priority,
        router_id,
        rule_id,
        title,
        description,
    )

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()

    return alert_number


def update_alert_seen(
    alert_id: int,
) -> None:
    query = """
        UPDATE dbo.alerts
        SET
            last_detected_at = SYSUTCDATETIME(),
            occurrence_count = occurrence_count + 1,
            updated_at = SYSUTCDATETIME()
        WHERE id = ?;
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, alert_id)
        conn.commit()


def close_alert(
    alert_id: int,
) -> None:
    query = """
        UPDATE dbo.alerts
        SET
            status = 'CLOSED',
            closed_at = SYSUTCDATETIME(),
            updated_at = SYSUTCDATETIME()
        WHERE id = ?;
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, alert_id)
        conn.commit()

def get_alert_by_number(alert_number: str) -> dict[str, Any] | None:
    query = """
        SELECT
            a.id,
            a.alert_number,
            a.status,
            a.priority,
            a.router_id,
            a.rule_id,
            a.title,
            a.description,
            a.opened_at,
            a.closed_at,
            a.last_detected_at,
            a.occurrence_count,
            a.external_system,
            a.external_ticket,
            a.external_url,
            r.name AS router_name,
            r.description AS router_description,
            ir.rule_name
        FROM dbo.alerts a
        JOIN dbo.routers r
            ON a.router_id = r.id
        JOIN dbo.incident_rules ir
            ON a.rule_id = ir.id
        WHERE a.alert_number = ?;
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, alert_number)
        row = cursor.fetchone()

        if not row:
            return None

        return {
            "id": row.id,
            "alert_number": row.alert_number,
            "status": row.status,
            "priority": row.priority,
            "router_id": row.router_id,
            "rule_id": row.rule_id,
            "title": row.title,
            "description": row.description,
            "opened_at": row.opened_at,
            "closed_at": row.closed_at,
            "last_detected_at": row.last_detected_at,
            "occurrence_count": row.occurrence_count,
            "external_system": row.external_system,
            "external_ticket": row.external_ticket,
            "external_url": row.external_url,
            "router_name": row.router_name,
            "router_description": row.router_description,
            "rule_name": row.rule_name,
        }

def get_open_alerts() -> list[dict[str, Any]]:
    query = """
        SELECT
            a.id,
            a.alert_number,
            a.status,
            a.priority,
            a.router_id,
            a.rule_id,
            a.title,
            a.description,
            a.opened_at,
            a.last_detected_at,
            a.occurrence_count,
            a.external_system,
            a.external_ticket,
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
        cursor.execute(query)
        rows = cursor.fetchall()

        return [
            {
                "id": row.id,
                "alert_number": row.alert_number,
                "status": row.status,
                "priority": row.priority,
                "router_id": row.router_id,
                "rule_id": row.rule_id,
                "title": row.title,
                "description": row.description,
                "opened_at": row.opened_at,
                "last_detected_at": row.last_detected_at,
                "occurrence_count": row.occurrence_count,
                "external_system": row.external_system,
                "external_ticket": row.external_ticket,
                "router_name": row.router_name,
                "router_description": row.router_description,
                "rule_name": row.rule_name,
            }
            for row in rows
        ]