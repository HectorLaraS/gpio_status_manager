
import json
from pathlib import Path

from src.utils.gpio_mapper import (
    load_gpio_profiles,
    get_status_key_for_pin,
)

BASE_DIR = Path(__file__).resolve().parent
PROFILE_FILE = BASE_DIR / "config" / "gpio_profiles.json"

PRODUCT = "IBR900-600M"

EXPECTED_PROFILES = {
    "PTC_CROSSING_STANDARD": {
        "2": "SATA_GPIO_1",
        "3": "SATA_GPIO_2",
        "4": "SATA_GPIO_3",
    },
    "PTC_CROSSING_PARTIAL": {
        "2": "SATA_GPIO_1",
        "3": "SATA_GPIO_2",
    },
    "PTC_WAYSIDE_LINE_POWER": {
        "1": "CONNECTOR_INPUT",
    },
    "PTC_WAYSIDE_SOLAR": {
        "1": "CONNECTOR_INPUT",
    },
}


def main():
    print("=" * 65)
    print("GPIO STATUS MANAGER - PROFILE DIAGNOSTIC")
    print("=" * 65)

    print(f"\nWorking directory: {Path.cwd()}")
    print(f"Expected JSON path: {PROFILE_FILE.resolve()}")
    print(f"JSON exists: {PROFILE_FILE.exists()}")

    if not PROFILE_FILE.exists():
        print("\n[ERROR] gpio_profiles.json not found!")
        return

    with open(PROFILE_FILE, encoding="utf-8") as file:
        disk_profiles = json.load(file)

    loaded_profiles = load_gpio_profiles()

    print("\nProfiles found on disk:")
    for name in disk_profiles:
        print(f"  - {name}")

    print("\nProfiles loaded by gpio_mapper:")
    for name in loaded_profiles:
        print(f"  - {name}")

    if disk_profiles != loaded_profiles:
        print("\n[WARNING] Loaded profiles differ from disk!")
        print("Check relative paths and working directory.")
    else:
        print("\n[OK] Mapper is loading the expected JSON.")

    print("\n" + "=" * 65)
    print("PROFILE MAPPING TEST")
    print("=" * 65)

    passed = 0
    failed = 0

    for profile_name, expected_pins in EXPECTED_PROFILES.items():
        print(f"\nPROFILE: {profile_name}")

        if profile_name not in loaded_profiles:
            print("  [FAIL] Profile not found!")
            failed += len(expected_pins)
            continue

        for pin, expected_key in expected_pins.items():
            status_key, selected_profile = get_status_key_for_pin(
                product_name=PRODUCT,
                config_pin=pin,
                approved_profile_name=profile_name,
            )

            valid = (
                status_key == expected_key
                and selected_profile == profile_name
            )

            result = "PASS" if valid else "FAIL"

            print(
                f"  [{result}] Pin={pin} | "
                f"Expected={expected_key} | "
                f"Received={status_key} | "
                f"Profile={selected_profile}"
            )

            if valid:
                passed += 1
            else:
                failed += 1

    print("\n" + "=" * 65)
    print("FINAL RESULT")
    print("=" * 65)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed == 0:
        print("\n[OK] All profile mappings are correct.")
        print("Next step: validate signature/profile selection.")
    else:
        print("\n[ERROR] GPIO profile mapping failed.")


if __name__ == "__main__":
    main()
