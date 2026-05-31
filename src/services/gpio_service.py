from typing import Any

from src.clients.netcloud_client import NetCloudClient
from src.repositories.gpio_repository import upsert_gpio_definition
from src.utils.gpio_mapper import get_status_key_for_pin
from src.repositories.gpio_profile_repository import (
    link_candidate_router,
    upsert_profile_candidate,
)
from src.utils.gpio_signature import (
    build_gpio_signature,
    build_suggested_profile_name,
)

from src.repositories.gpio_profile_repository import (
    get_approved_profile_name_by_signature,
    link_candidate_router,
    upsert_profile_candidate,
)


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
    router_name: str | None = None,
    group_db_id: int | None = None,
    group_name: str | None = None,
) -> int:
    client = NetCloudClient()

    try:
        config_manager = client.get_configuration_manager_by_router(router_netcloud_id)
    except RuntimeError as error:
        print(
            f"  WARNING | configuration_manager failed | "
            f"router_netcloud_id={router_netcloud_id} | error={error}"
        )
        return 0

    pins = extract_gpio_pins_from_configuration(config_manager)

    if pins:
        signature_hash, pins_json = build_gpio_signature(pins)
        approved_profile_name = get_approved_profile_name_by_signature(signature_hash)
        suggested_profile_name = build_suggested_profile_name(
            product_name=product_name,
            signature_hash=signature_hash,
        )

        candidate_id = upsert_profile_candidate(
            signature_hash=signature_hash,
            suggested_profile_name=suggested_profile_name,
            product_name=product_name,
            sample_router_id=router_db_id,
            sample_router_name=router_name,
            sample_group_id=group_db_id,
            sample_group_name=group_name,
            pins_json=pins_json,
        )

        link_candidate_router(
            candidate_id=candidate_id,
            router_id=router_db_id,
        )

    total = 0

    for config_pin, gpio_data in pins.items():
        if not isinstance(gpio_data, dict):
            continue

        if not gpio_data.get("enabled", False):
            continue

        status_key, auto_profile_name = get_status_key_for_pin(
            product_name=product_name,
            config_pin=str(config_pin),
        )

        profile_name = approved_profile_name or auto_profile_name

        upsert_gpio_definition(
            router_db_id=router_db_id,
            config_pin=str(config_pin),
            gpio_data=gpio_data,
            status_key=status_key,
            profile_name=profile_name,
        )

        total += 1

    return total