from typing import Any
from src.repositories.db import get_connection


def get_dashboard_summary() -> dict[str, Any]:
    query = """
        SELECT
            COUNT(DISTINCT r.id) AS total_routers,
            SUM(CASE WHEN r.state = 'online' THEN 1 ELSE 0 END) AS online_routers,
            SUM(CASE WHEN r.state <> 'online' OR r.state IS NULL THEN 1 ELSE 0 END) AS offline_routers,
            SUM(CASE WHEN gsc.is_alert = 1 THEN 1 ELSE 0 END) AS gpio_alerts
        FROM dbo.routers r
        LEFT JOIN dbo.gpio_status_current gsc
            ON r.id = gsc.router_id
        WHERE r.is_active = 1;
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        row = cursor.fetchone()

        return {
            "total_routers": row.total_routers or 0,
            "online_routers": row.online_routers or 0,
            "offline_routers": row.offline_routers or 0,
            "gpio_alerts": row.gpio_alerts or 0,
        }


def get_dashboard_routers() -> list[dict[str, Any]]:
    query = """
        SELECT
            r.id AS router_id,
            r.name,
            r.description,
            g.name AS group_name,
            r.state,
            r.config_status,
            r.full_product_name,
            w.ipv4_address,
            COUNT(gsc.id) AS gpio_count,
            SUM(CASE WHEN gsc.is_alert = 1 THEN 1 ELSE 0 END) AS alert_count,
            MAX(gsc.checked_at) AS last_check
        FROM dbo.routers r
        LEFT JOIN dbo.groups g
            ON r.group_id = g.id
        LEFT JOIN dbo.router_wan_interfaces w
            ON r.id = w.router_id
            AND w.is_selected = 1
        LEFT JOIN dbo.gpio_status_current gsc
            ON r.id = gsc.router_id
        WHERE r.is_active = 1
        GROUP BY
            r.id,
            r.name,
            r.description,
            g.name,
            r.state,
            r.config_status,
            r.full_product_name,
            w.ipv4_address
        ORDER BY alert_count DESC, r.name;
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

        return [
            {
                "router_id": row.router_id,
                "name": row.name,
                "description": row.description,
                "group_name": row.group_name,
                "state": row.state,
                "config_status": row.config_status,
                "full_product_name": row.full_product_name,
                "ipv4_address": row.ipv4_address,
                "gpio_count": row.gpio_count or 0,
                "alert_count": row.alert_count or 0,
                "last_check": row.last_check,
            }
            for row in rows
        ]