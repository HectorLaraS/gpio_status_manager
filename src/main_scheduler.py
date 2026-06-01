import time
from datetime import datetime, timedelta

from src.config import load_settings
from src.repositories.poll_repository import has_running_poll
from src.services.poll_execution_service import (
    run_inventory_poll_execution,
    run_status_poll_execution,
)


def parse_inventory_hours(value: str) -> set[int]:
    hours = set()

    for item in value.split(","):
        item = item.strip()

        if not item:
            continue

        hours.add(int(item))

    return hours


def should_run_status_poll(
    now: datetime,
    last_status_run: datetime | None,
    interval_minutes: int,
) -> bool:
    if last_status_run is None:
        return True

    next_run = last_status_run + timedelta(minutes=interval_minutes)
    return now >= next_run


def should_run_inventory_poll(
    now: datetime,
    inventory_hours: set[int],
    last_inventory_key: str | None,
) -> tuple[bool, str | None]:
    if now.hour not in inventory_hours:
        return False, last_inventory_key

    current_key = now.strftime("%Y-%m-%d-%H")

    if last_inventory_key == current_key:
        return False, last_inventory_key

    return True, current_key


def main() -> None:
    settings = load_settings()

    status_interval_minutes = settings.app.status_poll_interval_minutes
    inventory_hours = parse_inventory_hours(settings.app.inventory_poll_hours)

    last_status_run: datetime | None = None
    last_inventory_key: str | None = None

    print("=" * 80)
    print("GPIO STATUS MANAGER SCHEDULER STARTED")
    print("=" * 80)
    print(f"Status poll interval: {status_interval_minutes} minutes")
    print(f"Inventory poll hours: {sorted(inventory_hours)}")
    print("=" * 80)

    while True:
        now = datetime.now()

        try:
            run_inventory, inventory_key = should_run_inventory_poll(
                now=now,
                inventory_hours=inventory_hours,
                last_inventory_key=last_inventory_key,
            )

            if run_inventory:
                if has_running_poll("INVENTORY"):
                    print("INVENTORY POLL SKIPPED | Existing inventory poll running.")
                else:
                    print(f"INVENTORY POLL TRIGGERED | {now}")
                    run_inventory_poll_execution()
                    last_inventory_key = inventory_key

            if should_run_status_poll(
                now=now,
                last_status_run=last_status_run,
                interval_minutes=status_interval_minutes,
            ):
                if has_running_poll("STATUS"):
                    print("STATUS POLL SKIPPED | Existing status poll running.")
                else:
                    print(f"STATUS POLL TRIGGERED | {now}")
                    run_status_poll_execution()
                    last_status_run = datetime.now()

        except Exception as error:
            print(f"SCHEDULER ERROR | {error}")

        time.sleep(30)


if __name__ == "__main__":
    main()