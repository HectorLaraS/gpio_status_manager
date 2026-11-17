import json
from pathlib import Path

from src.clients.ncos_client import NcosClient
from src.utils.gpio_mapper import get_status_key_for_pin


# Router que estamos investigando
ROUTER_DB_ID = 798
ROUTER_NAME = "West Bienville Control Point"
WAN_IP = "10.240.179.253"
PRODUCT_NAME = "IBR900-600M"
CONFIG_PIN = "1"


def main():
    print("=" * 80)
    print("GPIO STATUS MANAGER - DIAGNOSTIC TEST")
    print("=" * 80)

    print(f"Router DB ID : {ROUTER_DB_ID}")
    print(f"Router Name  : {ROUTER_NAME}")
    print(f"WAN IP       : {WAN_IP}")
    print(f"Product      : {PRODUCT_NAME}")
    print(f"Config Pin   : {CONFIG_PIN}")
    print("=" * 80)

    # 1. Verificar archivo de perfiles
    profile_path = Path("config/gpio_profiles.json")

    print("\n[1] GPIO PROFILE FILE")
    print(f"Path exists: {profile_path.exists()}")
    print(f"Absolute path: {profile_path.resolve()}")

    # 2. Comprobar mapeo del pin
    print("\n[2] GPIO PIN MAPPING")

    status_key, profile_name = get_status_key_for_pin(
        product_name=PRODUCT_NAME,
        config_pin=CONFIG_PIN,
    )

    print(f"Profile name : {profile_name}")
    print(f"Status key   : {status_key}")

    if status_key is None:
        print("WARNING: No status_key mapping found for this pin.")

    # 3. Consultar NCOS
    print("\n[3] NCOS GPIO STATUS")

    client = NcosClient()

    try:
        gpio_status = client.get_gpio_status(WAN_IP)

        print("GPIO response:")
        print(json.dumps(gpio_status, indent=4))

        if not gpio_status:
            print("WARNING: NCOS returned no GPIO data.")
        else:
            print(f"GPIO keys found: {len(gpio_status)}")

            for key, value in gpio_status.items():
                print(f"  {key} = {value}")

    except Exception as error:
        print(f"ERROR: NCOS request failed: {error}")

    print("\n" + "=" * 80)
    print("DIAGNOSTIC FINISHED")
    print("=" * 80)


if __name__ == "__main__":
    main()