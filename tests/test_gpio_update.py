from src.clients.netcloud_client import NetCloudClient
from src.services.gpio_service import extract_gpio_pins_from_configuration
from src.utils.gpio_signature import build_gpio_signature
from src.utils.gpio_mapper import get_status_key_for_pin
from src.repositories.gpio_profile_repository import (
    get_approved_profile_name_by_signature,
)
from src.repositories.gpio_repository import upsert_gpio_definition


TEST_ROUTERS = [
    {
        "router_db_id": 1140,
        "router_netcloud_id": 2996050,
        "product_name": "IBR900-600M",
        "expected_profile": "PTC_WAYSIDE_LINE_POWER",
    },
    {
        "router_db_id": 1384,
        "router_netcloud_id": 2995627,
        "product_name": "IBR900-600M",
        "expected_profile": "PTC_WAYSIDE_SOLAR",
    },
]


def main():
    client = NetCloudClient()

    print("=" * 65)
    print("GPIO STATUS MANAGER - CONTROLLED UPDATE")
    print("=" * 65)

    for router in TEST_ROUTERS:
        router_id = router["router_db_id"]

        print(f"\nRouter SQL ID: {router_id}")

        try:
            config = client.get_configuration_manager_by_router(
                router["router_netcloud_id"]
            )

            pins = extract_gpio_pins_from_configuration(config)

            if not pins:
                print("[FAIL] No GPIO configuration found")
                continue

            signature_hash, _ = build_gpio_signature(pins)

            approved_profile = get_approved_profile_name_by_signature(
                signature_hash
            )

            if approved_profile != router["expected_profile"]:
                print(
                    f"[FAIL] Unexpected profile: {approved_profile}"
                )
                continue

            gpio_data = pins.get("1")

            if not isinstance(gpio_data, dict):
                print("[FAIL] GPIO pin 1 not found")
                continue

            if not gpio_data.get("enabled", False):
                print("[FAIL] GPIO pin 1 is not enabled")
                continue

            status_key, profile_name = get_status_key_for_pin(
                product_name=router["product_name"],
                config_pin="1",
                approved_profile_name=approved_profile,
            )

            print(f"Profile: {profile_name}")
            print(f"Status Key: {status_key}")

            if status_key != "CONNECTOR_INPUT":
                print("[FAIL] Unexpected status key")
                continue

            record_id = upsert_gpio_definition(
                router_db_id=router_id,
                config_pin="1",
                gpio_data=gpio_data,
                status_key=status_key,
                profile_name=profile_name,
            )

            print(f"[UPDATED] GPIO Definition ID: {record_id}")

        except Exception as error:
            print(f"[ERROR] {type(error)._name_}: {error}")

    print("\nControlled update completed.")


if __name__ == "__main__":
    main()