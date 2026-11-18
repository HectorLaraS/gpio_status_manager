import argparse
import logging
from collections import Counter
from datetime import datetime
from pathlib import Path

from src.clients.netcloud_client import NetCloudClient
from src.repositories.db import get_connection
from src.repositories.gpio_profile_repository import (
    get_approved_profile_name_by_signature,
)
from src.services.gpio_service import (
    extract_gpio_pins_from_configuration,
    sync_gpio_definitions_for_router,
)
from src.utils.gpio_mapper import get_status_key_for_pin
from src.utils.gpio_signature import build_gpio_signature


EXPECTED_STATUS_KEY = "CONNECTOR_INPUT"

ALLOWED_PROFILES = (
    "PTC_WAYSIDE_LINE_POWER",
    "PTC_WAYSIDE_SOLAR",
)

LOG_DIR = Path(__file__).resolve().parents[1] / "logs"


def setup_logging():
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    filename = (
        "gpio_wayside_sync_"
        + datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        + ".log"
    )

    log_path = LOG_DIR / filename

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(),
        ],
        force=True,
    )

    return log_path


def fetch_pending_routers():
    query = """
        SELECT
            gd.id,
            gd.router_id,
            r.netcloud_id,
            r.name,
            r.full_product_name,
            gd.config_pin,
            gd.profile_name
        FROM dbo.gpio_definitions gd
        INNER JOIN dbo.routers r
            ON r.id = gd.router_id
        WHERE gd.enabled = 1
          AND gd.status_key IS NULL
          AND gd.config_pin = '1'
          AND gd.profile_name IN (?, ?)
        ORDER BY gd.router_id
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, ALLOWED_PROFILES)
        return cursor.fetchall()


def fetch_current_definition(definition_id):
    query = """
        SELECT status_key, profile_name
        FROM dbo.gpio_definitions
        WHERE id = ?
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (definition_id,))
        return cursor.fetchone()


def validate_router(client, router):
    (
        definition_id,
        router_db_id,
        netcloud_id,
        router_name,
        product_name,
        config_pin,
        expected_profile,
    ) = router

    if not netcloud_id or not product_name:
        return False, "Missing NetCloud ID or product", None

    config = client.get_configuration_manager_by_router(
        int(netcloud_id)
    )

    pins = extract_gpio_pins_from_configuration(config)

    if not pins:
        return False, "No GPIO pins found", None

    gpio_data = pins.get(str(config_pin))

    if not isinstance(gpio_data, dict):
        return False, "GPIO pin not found", None

    if not gpio_data.get("enabled", False):
        return False, "GPIO pin is disabled", None

    signature_hash, _ = build_gpio_signature(pins)

    approved_profile = get_approved_profile_name_by_signature(
        signature_hash
    )

    if approved_profile != expected_profile:
        return (
            False,
            f"Profile mismatch: expected={expected_profile}, "
            f"approved={approved_profile}, "
            f"signature={signature_hash}",
            None,
        )

    status_key, selected_profile = get_status_key_for_pin(
        product_name=product_name,
        config_pin=str(config_pin),
        approved_profile_name=approved_profile,
    )

    if (
        status_key != EXPECTED_STATUS_KEY
        or selected_profile != expected_profile
    ):
        return (
            False,
            f"Mapping mismatch: key={status_key}, "
            f"profile={selected_profile}",
            None,
        )

    return True, "Validated", signature_hash


def main():
    parser = argparse.ArgumentParser(
        description="Synchronize pending Wayside GPIO mappings"
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--execute", action="store_true")

    parser.add_argument("--limit", type=int, default=None)

    args = parser.parse_args()

    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be greater than zero")

    log_path = setup_logging()

    logging.info("=" * 65)
    logging.info("GPIO STATUS MANAGER - WAYSIDE SYNC")
    logging.info("=" * 65)
    logging.info(
        "Mode: %s",
        "EXECUTE" if args.execute else "DRY RUN",
    )

    routers = fetch_pending_routers()

    if args.limit is not None:
        routers = routers[:args.limit]

    logging.info("Pending GPIO selected: %s", len(routers))

    counters = Counter()
    client = NetCloudClient()

    for index, router in enumerate(routers, start=1):
        (
            definition_id,
            router_db_id,
            netcloud_id,
            router_name,
            product_name,
            config_pin,
            expected_profile,
        ) = router

        logging.info(
            "[%s/%s] Router=%s | NetCloud=%s | %s",
            index,
            len(routers),
            router_db_id,
            netcloud_id,
            router_name,
        )

        try:
            valid, reason, signature = validate_router(
                client, router
            )

            if not valid:
                counters["validation_failed"] += 1
                logging.warning(
                    "SKIPPED | Router=%s | %s",
                    router_db_id,
                    reason,
                )
                continue

            counters["validated"] += 1

            logging.info(
                "VALIDATED | Router=%s | Profile=%s | "
                "Signature=%s",
                router_db_id,
                expected_profile,
                signature,
            )

            if args.dry_run:
                counters["dry_run_passed"] += 1
                continue

            # Verify the record is still pending.
            current = fetch_current_definition(definition_id)

            if current is None:
                counters["skipped"] += 1
                logging.warning(
                    "SKIPPED | Definition %s disappeared",
                    definition_id,
                )
                continue

            if current[0] is not None or current[1] != expected_profile:
                counters["skipped"] += 1
                logging.warning(
                    "SKIPPED | Definition %s changed before update",
                    definition_id,
                )
                continue

            updated_count = sync_gpio_definitions_for_router(
                router_db_id=int(router_db_id),
                router_netcloud_id=int(netcloud_id),
                product_name=product_name,
                router_name=router_name,
            )

            result = fetch_current_definition(definition_id)

            if (
                result is not None
                and result[0] == EXPECTED_STATUS_KEY
                and result[1] == expected_profile
            ):
                counters["updated"] += 1
                logging.info(
                    "UPDATED | Router=%s | Definition=%s | "
                    "StatusKey=%s | SyncedGPIO=%s",
                    router_db_id,
                    definition_id,
                    result[0],
                    updated_count,
                )
            else:
                counters["verification_failed"] += 1
                logging.error(
                    "VERIFY FAILED | Router=%s | Definition=%s | "
                    "DatabaseValue=%s",
                    router_db_id,
                    definition_id,
                    result,
                )

        except Exception:
            counters["errors"] += 1
            logging.exception(
                "ERROR | Router=%s | NetCloud=%s",
                router_db_id,
                netcloud_id,
            )

    logging.info("=" * 65)
    logging.info("FINAL SUMMARY")
    logging.info("=" * 65)
    logging.info("Selected: %s", len(routers))
    logging.info("Validated: %s", counters["validated"])
    logging.info(
        "Dry-run passed: %s", counters["dry_run_passed"]
    )
    logging.info("Updated: %s", counters["updated"])
    logging.info(
        "Validation failed: %s",
        counters["validation_failed"],
    )
    logging.info("Skipped: %s", counters["skipped"])
    logging.info(
        "Verification failed: %s",
        counters["verification_failed"],
    )
    logging.info("Errors: %s", counters["errors"])
    logging.info("Log file: %s", log_path)


if __name__ == "__main__":
    main()