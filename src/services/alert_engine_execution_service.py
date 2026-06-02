from src.repositories.poll_repository import (
    add_poll_log,
    finish_poll_execution,
    has_running_poll,
    start_poll_execution,
)

from src.services.alert_engine import run_alert_engine


def run_alert_engine_execution() -> None:

    execution_type = "ALERT_ENGINE"

    if has_running_poll(execution_type):
        print(
            "ALERT ENGINE SKIPPED | "
            "Existing alert engine execution running."
        )
        return

    execution_id = start_poll_execution(
        execution_type
    )

    try:

        add_poll_log(
            execution_id=execution_id,
            level_name="INFO",
            source="alert_engine",
            message="Alert engine execution started.",
        )

        stats = run_alert_engine()

        finish_poll_execution(
            execution_id=execution_id,
            status="success",
            routers_processed=stats.get(
                "conditions_processed",
                0,
            ),
            routers_success=stats.get(
                "alerts_evaluated",
                0,
            ),
            routers_failed=0,
            notes=(
                f"Alerts closed: "
                f"{stats.get('alerts_closed', 0)}"
            ),
        )

        add_poll_log(
            execution_id=execution_id,
            level_name="INFO",
            source="alert_engine",
            message="Alert engine execution finished.",
        )

    except Exception as error:

        add_poll_log(
            execution_id=execution_id,
            level_name="ERROR",
            source="alert_engine",
            message=str(error),
        )

        finish_poll_execution(
            execution_id=execution_id,
            status="failed",
            notes=str(error),
        )

        raise