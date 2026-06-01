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

        stats = sync_routers_by_active_groups()

        add_poll_log(
            execution_id=execution_id,
            level_name="INFO",
            source="poll_service",
            message=(
                "Poll execution finished successfully. "
                f"groups_processed={stats['groups_processed']}, "
                f"routers_processed={stats['routers_processed']}, "
                f"routers_success={stats['routers_success']}, "
                f"routers_failed={stats['routers_failed']}, "
                f"gpio_definitions={stats['gpio_definitions']}, "
                f"gpio_status={stats['gpio_status']}"
            ),
        )

        finish_poll_execution(
            execution_id=execution_id,
            status="success",
            groups_processed=stats["groups_processed"],
            routers_processed=stats["routers_processed"],
            routers_success=stats["routers_success"],
            routers_failed=stats["routers_failed"],
            notes=(
                f"GPIO definitions: {stats['gpio_definitions']} | "
                f"GPIO status: {stats['gpio_status']}"
            ),
        )

        print("=" * 80)
        print(f"POLL FINISHED SUCCESS | execution_id={execution_id}")
        print(
            f"groups={stats['groups_processed']} | "
            f"routers={stats['routers_processed']} | "
            f"success={stats['routers_success']} | "
            f"failed={stats['routers_failed']} | "
            f"gpio_defs={stats['gpio_definitions']} | "
            f"gpio_status={stats['gpio_status']}"
        )
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