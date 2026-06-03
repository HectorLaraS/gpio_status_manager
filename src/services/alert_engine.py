from datetime import datetime, timedelta

from src.repositories.alert_repository import (
    close_alert,
    create_alert,
    get_alert_by_id,
    get_alert_by_number,
    get_open_alert,
    get_open_alerts,
    update_alert_seen,
)
from src.services.webhook_engine import execute_alert_actions
from src.repositories.db import get_connection
from src.repositories.incident_rule_repository import get_active_incident_rules


def get_active_gpio_conditions() -> list[dict]:
    query = """
        SELECT
            gsc.router_id,
            gd.gpio_name,
            gsc.human_status,
            MIN(h.detected_at) AS first_detected_at,
            MAX(h.detected_at) AS last_detected_at
        FROM dbo.gpio_status_current gsc
        JOIN dbo.gpio_definitions gd
            ON gsc.gpio_definition_id = gd.id
        JOIN dbo.gpio_status_history h
            ON h.router_id = gsc.router_id
            AND h.gpio_definition_id = gsc.gpio_definition_id
            AND h.is_alert = 1
        WHERE gsc.is_alert = 1
        GROUP BY
            gsc.router_id,
            gd.gpio_name,
            gsc.human_status;
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

        return [
            {
                "router_id": row.router_id,
                "source": "GPIO",
                "match": f"{row.gpio_name}:{row.human_status}",
                "first_detected_at": row.first_detected_at,
                "last_detected_at": row.last_detected_at,
                "title": f"{row.gpio_name} - {row.human_status}",
                "description": (
                    f"GPIO alert detected: "
                    f"{row.gpio_name} = {row.human_status}"
                ),
            }
            for row in rows
        ]


def get_active_router_conditions() -> list[dict]:
    query = """
        SELECT
            id AS router_id,
            state,
            last_seen_at
        FROM dbo.routers
        WHERE is_active = 1
          AND (state IS NULL OR LOWER(state) <> 'online');
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

        return [
            {
                "router_id": row.router_id,
                "source": "ROUTER",
                "match": "offline",
                "first_detected_at": row.last_seen_at or datetime.utcnow(),
                "last_detected_at": datetime.utcnow(),
                "title": "Router Offline",
                "description": f"Router state is {row.state}",
            }
            for row in rows
        ]


def get_active_config_conditions() -> list[dict]:
    query = """
        SELECT
            id AS router_id,
            config_status,
            updated_at
        FROM dbo.routers
        WHERE is_active = 1
          AND (
                config_status IS NULL
                OR LOWER(config_status) LIKE '%pending%'
                OR LOWER(config_status) NOT LIKE '%sync%'
          );
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

        return [
            {
                "router_id": row.router_id,
                "source": "CONFIG",
                "match": "pending",
                "first_detected_at": row.updated_at or datetime.utcnow(),
                "last_detected_at": datetime.utcnow(),
                "title": "Config Pending / Not Synced",
                "description": f"Router config_status is {row.config_status}",
            }
            for row in rows
        ]


def rule_matches_condition(rule: dict, condition: dict) -> bool:
    if rule["alert_source"].lower() != condition["source"].lower():
        return False

    return rule["alert_match"].lower() == condition["match"].lower()


def condition_meets_duration(rule: dict, condition: dict) -> bool:
    first_detected_at = condition["first_detected_at"]

    if not first_detected_at:
        return False

    threshold = first_detected_at + timedelta(
        minutes=rule["duration_minutes"]
    )

    return datetime.utcnow() >= threshold


def evaluate_alert_condition(rule: dict, condition: dict) -> None:
    if not condition_meets_duration(rule, condition):
        return

    open_alert = get_open_alert(
        router_id=condition["router_id"],
        rule_id=rule["id"],
    )

    if open_alert:
        update_alert_seen(open_alert["id"])
        return

    alert_number = create_alert(
        router_id=condition["router_id"],
        rule_id=rule["id"],
        priority=rule["priority"],
        title=condition["title"],
        description=condition["description"],
    )

    print(
        f"ALERT CREATED | "
        f"alert_number={alert_number} | "
        f"router_id={condition['router_id']} | "
        f"rule={rule['rule_key']}"
    )

    alert = get_alert_by_number(alert_number)

    if alert:
        execute_alert_actions(
            event_type="ALERT_OPENED",
            alert=alert,
        )


def build_active_condition_keys(
    conditions: list[dict],
    rules: list[dict],
) -> set[tuple[int, int]]:
    active_keys = set()

    for condition in conditions:
        for rule in rules:
            if not rule_matches_condition(rule, condition):
                continue

            active_keys.add(
                (
                    condition["router_id"],
                    rule["id"],
                )
            )

    return active_keys


def close_resolved_alerts(
    conditions: list[dict],
    rules: list[dict],
) -> int:
    active_keys = build_active_condition_keys(
        conditions=conditions,
        rules=rules,
    )

    open_alerts = get_open_alerts()

    closed_count = 0

    for alert in open_alerts:
        alert_key = (
            alert["router_id"],
            alert["rule_id"],
        )

        if alert_key in active_keys:
            continue

        close_alert(alert["id"])

        closed_alert = get_alert_by_id(alert["id"])

        if closed_alert:
            execute_alert_actions(
                event_type="ALERT_CLOSED",
                alert=closed_alert,
            )

        closed_count += 1

        print(
            f"ALERT CLOSED | "
            f"alert_number={alert['alert_number']} | "
            f"router_id={alert['router_id']} | "
            f"rule_id={alert['rule_id']}"
        )

    return closed_count


def run_alert_engine() -> dict:
    stats = {
        "conditions_processed": 0,
        "alerts_evaluated": 0,
        "alerts_closed": 0,
    }

    rules = get_active_incident_rules()

    conditions = []
    conditions.extend(get_active_gpio_conditions())
    conditions.extend(get_active_router_conditions())
    conditions.extend(get_active_config_conditions())

    for condition in conditions:
        stats["conditions_processed"] += 1

        for rule in rules:
            if not rule_matches_condition(rule, condition):
                continue

            evaluate_alert_condition(rule, condition)
            stats["alerts_evaluated"] += 1

    closed_count = close_resolved_alerts(
        conditions=conditions,
        rules=rules,
    )

    stats["alerts_closed"] = closed_count

    print(
        f"ALERT ENGINE FINISHED | "
        f"conditions={stats['conditions_processed']} | "
        f"evaluated={stats['alerts_evaluated']} | "
        f"closed={stats['alerts_closed']}"
    )

    return stats