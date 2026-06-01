from src.repositories.poll_repository import (
    add_poll_log,
    finish_poll_execution,
    start_poll_execution,
)
from src.services.router_service import sync_routers_by_active_groups


def run_poll() -> None:
    execution_id = start_poll_execution()

    print("=" * 80)
    print(f"POLL STARTED | execution_id={execution_id}")
    print("=" * 80)

    try:
        add_poll_log(
            execution_id=execution_id,
            level_name="INFO",
            source="poll_service",
            message="Poll execution started.",
        )

        sync_routers_by_active_groups()

        add_poll_log(
            execution_id=execution_id,
            level_name="INFO",
            source="poll_service",
            message="Poll execution finished successfully.",
        )

        finish_poll_execution(
            execution_id=execution_id,
            status="success",
            notes="Poll finished successfully.",
        )

        print("=" * 80)
        print(f"POLL FINISHED SUCCESS | execution_id={execution_id}")
        print("=" * 80)

    except Exception as error:
        add_poll_log(
            execution_id=execution_id,
            level_name="ERROR",
            source="poll_service",
            message=str(error),
        )

        finish_poll_execution(
            execution_id=execution_id,
            status="failed",
            notes=str(error),
        )

        print("=" * 80)
        print(f"POLL FAILED | execution_id={execution_id}")
        print(f"ERROR: {error}")
        print("=" * 80)

        raise