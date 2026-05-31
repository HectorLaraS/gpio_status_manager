import hashlib
import json
from typing import Any


def normalize_pin_entry(config_pin: str, gpio_data: dict[str, Any]) -> dict[str, Any]:
    return {
        "config_pin": str(config_pin),
        "gpio_name": gpio_data.get("gpio_name") or "",
        "direction": gpio_data.get("direction") or "in",
        "high_state_name": gpio_data.get("high_state_name") or "",
        "low_state_name": gpio_data.get("low_state_name") or "",
    }


def build_gpio_signature(pins: dict[str, Any]) -> tuple[str, str]:
    normalized_pins = []

    for config_pin, gpio_data in pins.items():
        if not isinstance(gpio_data, dict):
            continue

        if not gpio_data.get("enabled", False):
            continue

        normalized_pins.append(
            normalize_pin_entry(
                config_pin=str(config_pin),
                gpio_data=gpio_data,
            )
        )

    normalized_pins = sorted(
        normalized_pins,
        key=lambda item: item["config_pin"],
    )

    pins_json = json.dumps(
        normalized_pins,
        ensure_ascii=False,
        sort_keys=True,
    )

    signature_hash = hashlib.sha256(
        pins_json.encode("utf-8")
    ).hexdigest()

    return signature_hash, pins_json


def build_suggested_profile_name(product_name: str | None, signature_hash: str) -> str:
    product = product_name or "UNKNOWN_PRODUCT"
    product = product.replace(" ", "_").replace("-", "_")

    short_hash = signature_hash[:8].upper()

    return f"UNKNOWN_AUTO_{product}_{short_hash}"