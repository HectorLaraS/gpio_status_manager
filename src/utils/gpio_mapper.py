import json
from pathlib import Path
from typing import Any


PROFILE_PATH = Path("config/gpio_profiles.json")


def load_gpio_profiles() -> dict[str, Any]:
    if not PROFILE_PATH.exists():
        return {}

    with open(PROFILE_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def find_profile_for_product(product_name: str | None) -> tuple[str | None, dict[str, Any] | None]:
    profiles = load_gpio_profiles()

    if not product_name:
        return None, None

    for profile_name, profile_data in profiles.items():
        product_match = profile_data.get("product_match")

        if product_match and product_match in product_name:
            return profile_name, profile_data

    return None, None


def get_status_key_for_pin(product_name: str | None, config_pin: str) -> tuple[str | None, str | None]:
    profile_name, profile_data = find_profile_for_product(product_name)

    if not profile_data:
        return None, None

    pin_to_status_key = profile_data.get("pin_to_status_key", {})
    status_key = pin_to_status_key.get(str(config_pin))

    return status_key, profile_name