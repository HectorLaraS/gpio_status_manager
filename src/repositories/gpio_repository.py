from typing import Any

from src.repositories.db import get_connection


def upsert_gpio_definition(
    router_db_id: int,
    config_pin: str,
    gpio_data: dict[str, Any],
    status_key: str | None = None,
    profile_name: str | None = None,
) -> int:
    query = """
        MERGE dbo.gpio_definitions AS target
        USING (
            SELECT
                ? AS router_id,
                ? AS config_pin,
                ? AS gpio_name,
                ? AS direction,
                ? AS high_state_name,
                ? AS low_state_name,
                ? AS alert_state,
                ? AS debounce,
                ? AS status_key,
                ? AS profile_name,
                ? AS enabled
        ) AS source
        ON target.router_id = source.router_id
           AND target.config_pin = source.config_pin

        WHEN MATCHED THEN
            UPDATE SET
                target.gpio_name = source.gpio_name,
                target.direction = source.direction,
                target.high_state_name = source.high_state_name,
                target.low_state_name = source.low_state_name,
                target.alert_state = source.alert_state,
                target.debounce = source.debounce,
                target.status_key = source.status_key,
                target.profile_name = source.profile_name,
                target.enabled = source.enabled,
                target.updated_at = SYSUTCDATETIME()

        WHEN NOT MATCHED THEN
            INSERT (
                router_id,
                config_pin,
                gpio_name,
                direction,
                high_state_name,
                low_state_name,
                alert_state,
                debounce,
                status_key,
                profile_name,
                enabled,
                created_at,
                updated_at
            )
            VALUES (
                source.router_id,
                source.config_pin,
                source.gpio_name,
                source.direction,
                source.high_state_name,
                source.low_state_name,
                source.alert_state,
                source.debounce,
                source.status_key,
                source.profile_name,
                source.enabled,
                SYSUTCDATETIME(),
                SYSUTCDATETIME()
            )

        OUTPUT inserted.id;
    """

    params = (
        router_db_id,
        str(config_pin),
        gpio_data.get("gpio_name"),
        gpio_data.get("direction", "in"),
        gpio_data.get("high_state_name"),
        gpio_data.get("low_state_name"),
        gpio_data.get("alert_state"),
        gpio_data.get("debounce"),
        status_key,
        profile_name,
        1 if gpio_data.get("enabled", False) else 0,
    )

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        conn.commit()

        return row[0]