import time
from datetime import datetime

from src.config import load_settings
from src.services.inventory_poll_service import run_inventory_poll
from src.services.status_poll_service import run_status_poll
from src.repositories.poll_repository import has_running_poll


def parse_inventory_hours(value: str) -> set[int]:
    hours = set()

    for item in value.split(","):
        item = item.strip()

        if not item:
            continue

        hours.add(int(item))

    return hours


def should_run_inventory_poll(now: datetime, inventory_hours: set[int], last_inventory_key: str | None) -> tuple[bool, str]:
    current_key = now.strftime("%Y-%m-%d-%H")

    if now.hour not in inventory_hours:
        return False, last_inventory_key or ""

    if last_inventory_key == current_key:
        return False, last_inventory_key

    return True, current_key


def main() -> None:
    settings = load_settings()

    status_interval_minutes = int(
        getattr(settings.app, "status_poll_interval_minutes", settings.app.poll_interval_minutes)
    )

    inventory_hours_value = getattr(settings.app, "inventory_poll_hours", "6,18")
    inventory_hours = parse_inventory_hours(inventory_hours_value)

    last_status_run = None
    last_inventory_key = None

    print("=" * 80)
    print("GPIO STATUS MANAGER SCHEDULER STARTED")
    print("=" * 80)
    print(f"Status poll interval: {status_interval_minutes} minutes")
    print(f"Inventory poll hours: {sorted(inventory_hours)}")
    print("=" * 80)

    while True:
        now = datetime.now()

        try:
            run_inventory, new_inventory_key = should_run_inventory_poll(
                now=now,
                inventory_hours=inventory_hours,
                last_inventory_key=last_inventory_key,
            )

            if run_inventory:
                if has_running_poll():
                    print("INVENTORY POLL SKIPPED | Existing poll running.")
                else:
                    print(f"INVENTORY POLL TRIGGERED | {now}")
                    run_inventory_poll()
                    last_inventory_key = new_inventory_key

            if (
                last_status_run is None
                or (now - last_status_run).total_seconds() >= status_interval_minutes * 60
            ):
                if has_running_poll():
                    print("STATUS POLL SKIPPED | Existing poll running.")
                else:
                    print(f"STATUS POLL TRIGGERED | {now}")
                    run_status_poll()
                    last_status_run = datetime.now()

        except Exception as error:
            print(f"SCHEDULER ERROR | {error}")

        time.sleep(30)


if __name__ == "__main__":
    main()