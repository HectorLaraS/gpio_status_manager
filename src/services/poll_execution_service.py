from src.repositories.poll_repository import (
    add_poll_log,
    finish_poll_execution,
    has_running_poll,
    start_poll_execution,
)
from src.services.inventory_poll_service import run_inventory_poll
from src.services.status_poll_service import run_status_poll
from src.services.alert_engine_execution_service import (
    run_alert_engine_execution,
)


def run_inventory_poll_execution() -> None:
    execution_type = "INVENTORY"

    if has_running_poll(execution_type):
        print("INVENTORY POLL SKIPPED | Existing inventory poll running.")
        return

    execution_id = start_poll_execution(execution_type)

    print("RUNNING ALERT ENGINE AFTER INVENTORY POLL")
    run_alert_engine_execution()

    print("=" * 80)
    print(f"INVENTORY POLL EXECUTION STARTED | execution_id={execution_id}")
    print("=" * 80)

    try:
        add_poll_log(
            execution_id=execution_id,
            level_name="INFO",
            source="inventory_poll",
            message="Inventory poll execution started.",
        )

        stats = run_inventory_poll()

        finish_poll_execution(
            execution_id=execution_id,
            status="success",
            groups_processed=stats.get("groups_processed", 0),
            routers_processed=stats.get("routers_processed", 0),
            routers_success=stats.get("routers_success", 0),
            routers_failed=stats.get("routers_failed", 0),
            notes=(
                f"GPIO definitions: {stats.get('gpio_definitions', 0)} | "
                f"GPIO status: {stats.get('gpio_status', 0)}"
            ),
        )

        add_poll_log(
            execution_id=execution_id,
            level_name="INFO",
            source="inventory_poll",
            message="Inventory poll execution finished successfully.",
        )

        print("=" * 80)
        print(f"INVENTORY POLL EXECUTION FINISHED | execution_id={execution_id}")
        print("=" * 80)

    except Exception as error:
        add_poll_log(
            execution_id=execution_id,
            level_name="ERROR",
            source="inventory_poll",
            message=str(error),
        )

        finish_poll_execution(
            execution_id=execution_id,
            status="failed",
            notes=str(error),
        )

        print(f"INVENTORY POLL EXECUTION FAILED | execution_id={execution_id} | error={error}")
        raise


def run_status_poll_execution() -> None:
    execution_type = "STATUS"

    if has_running_poll(execution_type):
        print("STATUS POLL SKIPPED | Existing status poll running.")
        return

    execution_id = start_poll_execution(execution_type)

    print("RUNNING ALERT ENGINE AFTER STATUS POLL")
    run_alert_engine_execution()

    print("=" * 80)
    print(f"STATUS POLL EXECUTION STARTED | execution_id={execution_id}")
    print("=" * 80)

    try:
        add_poll_log(
            execution_id=execution_id,
            level_name="INFO",
            source="status_poll",
            message="Status poll execution started.",
        )

        stats = run_status_poll()

        finish_poll_execution(
            execution_id=execution_id,
            status="success",
            groups_processed=0,
            routers_processed=stats.get("routers_processed", 0),
            routers_success=stats.get("routers_success", 0),
            routers_failed=stats.get("routers_failed", 0),
            notes=(
                f"GPIO status: {stats.get('gpio_status', 0)} | "
                f"Alerts detected: {stats.get('alerts_detected', 0)}"
            ),
        )

        add_poll_log(
            execution_id=execution_id,
            level_name="INFO",
            source="status_poll",
            message="Status poll execution finished successfully.",
        )

        print("=" * 80)
        print(f"STATUS POLL EXECUTION FINISHED | execution_id={execution_id}")
        print("=" * 80)

    except Exception as error:
        add_poll_log(
            execution_id=execution_id,
            level_name="ERROR",
            source="status_poll",
            message=str(error),
        )

        finish_poll_execution(
            execution_id=execution_id,
            status="failed",
            notes=str(error),
        )

        print(f"STATUS POLL EXECUTION FAILED | execution_id={execution_id} | error={error}")
        raise