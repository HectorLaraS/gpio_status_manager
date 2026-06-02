from typing import Any

from src.repositories.db import get_connection


def get_gpio_definitions_by_router(router_db_id: int) -> list[dict[str, Any]]:
    query = """
        SELECT
            id,
            router_id,
            config_pin,
            gpio_name,
            direction,
            high_state_name,
            low_state_name,
            status_key,
            profile_name,
            enabled
        FROM dbo.gpio_definitions
        WHERE router_id = ?
          AND enabled = 1
          AND status_key IS NOT NULL
        ORDER BY config_pin;
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, router_db_id)
        rows = cursor.fetchall()

        return [
            {
                "id": row.id,
                "router_id": row.router_id,
                "config_pin": row.config_pin,
                "gpio_name": row.gpio_name,
                "direction": row.direction,
                "high_state_name": row.high_state_name,
                "low_state_name": row.low_state_name,
                "status_key": row.status_key,
                "profile_name": row.profile_name,
                "enabled": bool(row.enabled),
            }
            for row in rows
        ]

def insert_gpio_status_history(
    router_db_id: int,
    gpio_definition_id: int,
    status_key: str,
    raw_value: int | str | None,
    human_status: str | None,
    is_alert: bool,
) -> None:
    query = """
        INSERT INTO dbo.gpio_status_history (
            router_id,
            gpio_definition_id,
            status_key,
            raw_value,
            human_status,
            is_alert,
            detected_at
        )
        VALUES (
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            SYSUTCDATETIME()
        );
    """

    params = (
        router_db_id,
        gpio_definition_id,
        status_key,
        None if raw_value is None else str(raw_value),
        human_status,
        1 if is_alert else 0,
    )

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()

def upsert_gpio_status_current(
    router_db_id: int,
    gpio_definition_id: int,
    status_key: str,
    raw_value: int | None,
    human_status: str | None,
    is_alert: bool,
) -> int:
    query = """
        MERGE dbo.gpio_status_current AS target
        USING (
            SELECT
                ? AS router_id,
                ? AS gpio_definition_id,
                ? AS status_key,
                ? AS raw_value,
                ? AS human_status,
                ? AS is_alert
        ) AS source
        ON target.gpio_definition_id = source.gpio_definition_id

        WHEN MATCHED THEN
            UPDATE SET
                target.router_id = source.router_id,
                target.status_key = source.status_key,
                target.raw_value = source.raw_value,
                target.human_status = source.human_status,
                target.is_alert = source.is_alert,
                target.checked_at = SYSUTCDATETIME(),
                target.updated_at = SYSUTCDATETIME()

        WHEN NOT MATCHED THEN
            INSERT (
                router_id,
                gpio_definition_id,
                status_key,
                raw_value,
                human_status,
                is_alert,
                checked_at,
                updated_at
            )
            VALUES (
                source.router_id,
                source.gpio_definition_id,
                source.status_key,
                source.raw_value,
                source.human_status,
                source.is_alert,
                SYSUTCDATETIME(),
                SYSUTCDATETIME()
            )

        OUTPUT inserted.id;
    """

    history_query = """
        INSERT INTO dbo.gpio_status_history (
            router_id,
            gpio_definition_id,
            status_key,
            raw_value,
            human_status,
            is_alert,
            detected_at
        )
        VALUES (
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            SYSUTCDATETIME()
        );
    """

    params = (
        router_db_id,
        gpio_definition_id,
        status_key,
        raw_value,
        human_status,
        1 if is_alert else 0,
    )

    history_params = (
        router_db_id,
        gpio_definition_id,
        status_key,
        None if raw_value is None else str(raw_value),
        human_status,
        1 if is_alert else 0,
    )

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(query, params)
        row = cursor.fetchone()

        if row is None:
            raise RuntimeError(
                f"No row returned from gpio_status_current MERGE "
                f"router_id={router_db_id}, gpio_definition_id={gpio_definition_id}"
            )

        status_current_id = row[0]

        cursor.execute(history_query, history_params)

        conn.commit()

        return status_current_id