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
    if raw_value is None:
        return False

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
    print(
        f"ENTER sync_gpio_status_for_router | "
        f"router={router_db_id} | wan_ip={wan_ip}"
    )

    client = NcosClient()

    try:
        gpio_status = client.get_gpio_status(wan_ip)
        print(f"GPIO STATUS RAW | router={router_db_id} | data={gpio_status}")

        print(
            f"GPIO STATUS KEYS | "
            f"router={router_db_id} | "
            f"keys={list(gpio_status.keys())}"
        )

    except RuntimeError as error:
        print(
            f"  WARNING | NCOS gpio status failed | "
            f"router_db_id={router_db_id} | wan_ip={wan_ip} | error={error}"
        )
        return 0

    gpio_definitions = get_gpio_definitions_by_router(router_db_id)
    if not gpio_definitions:
        print(f"NO GPIO DEFINITIONS FOUND | router={router_db_id}")
        return 0

    print(
        f"GPIO DEFINITIONS FOUND | "
        f"router={router_db_id} | count={len(gpio_definitions)}"
    )
    if not gpio_definitions:
        print(
            f"NO GPIO DEFINITIONS FOUND | "
            f"router={router_db_id}"
        )
        return 0

    print(
        f"GPIO DEFINITIONS FOUND | "
        f"router={router_db_id} | "
        f"count={len(gpio_definitions)}"
    )

    print(
        f"GPIO DEFINITIONS FOUND | "
        f"router={router_db_id} | "
        f"count={len(gpio_definitions)}"
    )

    total = 0

    for gpio_definition in gpio_definitions:
        status_key = gpio_definition.get("status_key")

        if not status_key:
            print(
                f"SKIP GPIO | router={router_db_id} | "
                f"gpio={gpio_definition.get('id')} | reason=no_status_key"
            )
            continue

        raw_value = gpio_status.get(status_key)

        if raw_value is None:
            print(
                f"SKIP GPIO | router={router_db_id} | "
                f"gpio={gpio_definition.get('id')} | "
                f"status_key={status_key} | reason=raw_value_none"
            )
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
            f"value={raw_value} | "
            f"human={human_status} | "
            f"is_alert={is_alert}"
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

    print(
        f"EXIT sync_gpio_status_for_router | "
        f"router={router_db_id} | total={total}"
    )

    return total