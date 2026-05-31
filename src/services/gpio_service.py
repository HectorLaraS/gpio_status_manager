from typing import Any

from src.clients.netcloud_client import NetCloudClient
from src.repositories.gpio_repository import upsert_gpio_definition
from src.utils.gpio_mapper import get_status_key_for_pin


def extract_gpio_pins_from_configuration(configuration_manager: dict[str, Any]) -> dict[str, Any]:
    """
    Extrae system.gpio_actions.pin desde configuration_manager.
    Primero intenta target, luego actual.
    """

    for source_key in ("target", "actual"):
        source_value = configuration_manager.get(source_key)

        if not source_value:
            continue

        if isinstance(source_value, list) and len(source_value) > 0:
            config_root = source_value[0]
        elif isinstance(source_value, dict):
            config_root = source_value
        else:
            continue

        pins = (
            config_root
            .get("system", {})
            .get("gpio_actions", {})
            .get("pin", {})
        )

        if pins:
            return pins

    return {}


def sync_gpio_definitions_for_router(
    router_db_id: int,
    router_netcloud_id: int,
    product_name: str | None,
) -> int:
    client = NetCloudClient()

    config_manager = client.get_configuration_manager_by_router(router_netcloud_id)
    pins = extract_gpio_pins_from_configuration(config_manager)

    total = 0

    for config_pin, gpio_data in pins.items():
        if not isinstance(gpio_data, dict):
            continue

        if not gpio_data.get("enabled", False):
            continue

        status_key, profile_name = get_status_key_for_pin(
            product_name=product_name,
            config_pin=str(config_pin),
        )

        upsert_gpio_definition(
            router_db_id=router_db_id,
            config_pin=str(config_pin),
            gpio_data=gpio_data,
            status_key=status_key,
            profile_name=profile_name,
        )

        total += 1

    return total