from src.utils.gpio_mapper import get_status_key_for_pin

TEST_ROUTERS = [
    {
        "router_id": 1140,
        "product_name": "IBR900-600M",
        "config_pin": "1",
        "approved_profile_name": "PTC_WAYSIDE_LINE_POWER",
    },
    {
        "router_id": 1384,
        "product_name": "IBR900-600M",
        "config_pin": "1",
        "approved_profile_name": "PTC_WAYSIDE_SOLAR",
    },
]


def main():
    print("=" * 65)
    print("GPIO STATUS MANAGER - WAYSIDE DIAGNOSTIC")
    print("=" * 65)

    for router in TEST_ROUTERS:
        status_key, profile_name = get_status_key_for_pin(
            product_name=router["product_name"],
            config_pin=router["config_pin"],
            approved_profile_name=router["approved_profile_name"],
        )

        print(f"\nRouter ID: {router['router_id']}")
        print(f"Profile: {profile_name}")
        print(f"Config Pin: {router['config_pin']}")
        print(f"Status Key: {status_key}")

        if status_key == "CONNECTOR_INPUT":
            print("RESULT: PASS")
        else:
            print("RESULT: FAIL")


if __name__ == "__main__":
    main()