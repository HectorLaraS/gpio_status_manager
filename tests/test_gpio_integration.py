from src.clients.netcloud_client import NetCloudClient
from src.services.gpio_service import extract_gpio_pins_from_configuration
from src.utils.gpio_signature import build_gpio_signature
from src.utils.gpio_mapper import get_status_key_for_pin
from src.repositories.gpio_profile_repository import (
    get_approved_profile_name_by_signature,
)


TEST_ROUTERS = [
    {
        "router_db_id": 1140,
        "router_netcloud_id": 2996050,
        "router_name": "WB Bridge Home Signal",
        "product_name": "IBR900-600M",
        "expected_profile": "PTC_WAYSIDE_LINE_POWER",
    },
    {
        "router_db_id": 1384,
        "router_netcloud_id": 2995627,
        "router_name": "SWITCH WEST GILLIAM",
        "product_name": "IBR900-600M",
        "expected_profile": "PTC_WAYSIDE_SOLAR",
    },
]


def main():
    print("=" * 70)
    print("GPIO STATUS MANAGER - INTEGRATION DIAGNOSTIC")
    print("=" * 70)

    client = NetCloudClient()

    for router in TEST_ROUTERS:
        print("\n" + "=" * 70)
        print(f"ROUTER: {router['router_name']}")
        print(f"SQL ID: {router['router_db_id']}")
        print(f"NETCLOUD ID: {router['router_netcloud_id']}")
        print("=" * 70)

        try:
            config_manager = client.get_configuration_manager_by_router(
                router["router_netcloud_id"]
            )

            pins = extract_gpio_pins_from_configuration(config_manager)

            if not pins:
                print("[FAIL] No GPIO pins found in configuration_manager")
                continue

            print("\nCONFIGURATION MANAGER")

            for pin, gpio_data in pins.items():
                print(
                    f"Pin={pin} | "
                    f"Name={gpio_data.get('gpio_name')} | "
                    f"Enabled={gpio_data.get('enabled')}"
                )

            signature_hash, pins_json = build_gpio_signature(pins)

            print("\nGPIO SIGNATURE")
            print(f"Signature Hash: {signature_hash}")

            approved_profile = get_approved_profile_name_by_signature(
                signature_hash
            )

            print("\nSQL PROFILE LOOKUP")
            print(f"Approved Profile: {approved_profile}")
            print(f"Expected Profile: {router['expected_profile']}")

            if approved_profile != router["expected_profile"]:
                print("[WARNING] Approved profile does not match expected!")

            print("\nGPIO MAPPER")

            for pin, gpio_data in pins.items():
                if not isinstance(gpio_data, dict):
                    continue

                if not gpio_data.get("enabled", False):
                    continue

                status_key, profile_name = get_status_key_for_pin(
                    product_name=router["product_name"],
                    config_pin=str(pin),
                    approved_profile_name=approved_profile,
                )

                print(
                    f"Pin={pin} | "
                    f"Profile={profile_name} | "
                    f"Status Key={status_key}"
                )

                if status_key == "CONNECTOR_INPUT":
                    print("[PASS] GPIO mapping correct")
                else:
                    print("[FAIL] GPIO mapping incorrect")

        except Exception as error:
            print(f"[ERROR] {type(error)._name_}: {error}")

    print("\n" + "=" * 70)
    print("DIAGNOSTIC COMPLETED - NO DATABASE CHANGES")
    print("=" * 70)


if __name__ == "__main__":
    main()