from typing import Any

from src.clients.ncos_client import NcosClient
from src.repositories.gpio_status_repository import (
    get_gpio_definitions_by_router,
    upsert_gpio_status_current,
)


def resolve_human_status(gpio_definition: dict[str, Any], raw_value: int | None) -> str | None:
    if raw_value is None:
        return None

    if raw_value == 1:
        return gpio_definition.get("high_state_name")

    if raw_value == 0:
        return gpio_definition.get("low_state_name")

    return str(raw_value)


def resolve_is_alert(gpio_definition: dict[str, Any], raw_value: int | None) -> bool:
    """
    Regla inicial:
    - Para inputs, asumimos que high_state_name representa alarma si no es estado normal.
    - Casos conocidos:
      Battery voltage: 1 = Bad => alerta
      Line power Crossing: 1 = Power off => alerta
      Solar Power: 0 = Battery Voltage Low => alerta
      Power reset relay es output, no alerta.
    """

    if raw_value is None:
        return False

    gpio_name = (gpio_definition.get("gpio_name") or "").lower()
    direction = (gpio_definition.get("direction") or "").lower()
    human_status = (resolve_human_status(gpio_definition, raw_value) or "").lower()

    if direction == "out":
        return False

    alert_keywords = [
        "bad",
        "off",
        "low",
        "alarm",
        "fail",
        "failure",
    ]

    return any(keyword in human_status for keyword in alert_keywords)


def sync_gpio_status_for_router(
    router_db_id: int,
    wan_ip: str,
) -> int:
    client = NcosClient()

    try:
        gpio_status = client.get_gpio_status(wan_ip)
    except RuntimeError as error:
        print(
            f"  WARNING | NCOS gpio status failed | "
            f"router_db_id={router_db_id} | wan_ip={wan_ip} | error={error}"
        )
        return 0

    gpio_definitions = get_gpio_definitions_by_router(router_db_id)

    total = 0

    for gpio_definition in gpio_definitions:
        status_key = gpio_definition.get("status_key")

        if not status_key:
            continue

        raw_value = gpio_status.get(status_key)

        if raw_value is None:
            continue

        try:
            raw_value = int(raw_value)
        except (TypeError, ValueError):
            pass

        human_status = resolve_human_status(
            gpio_definition=gpio_definition,
            raw_value=raw_value,
        )

        is_alert = resolve_is_alert(
            gpio_definition=gpio_definition,
            raw_value=raw_value,
        )

        print(
            f"CALLING UPSERT | "
            f"router={router_db_id} | "
            f"gpio={gpio_definition['id']} | "
            f"status_key={status_key} | "
            f"value={raw_value}"
        )

        upsert_gpio_status_current(
            router_db_id=router_db_id,
            gpio_definition_id=gpio_definition["id"],
            status_key=status_key,
            raw_value=raw_value,
            human_status=human_status,
            is_alert=is_alert,
        )

        total += 1

    return total