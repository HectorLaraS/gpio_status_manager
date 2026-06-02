from flask import Blueprint, render_template

from src.repositories.dashboard_repository import (
    format_duration,
    get_dashboard_routers,
    get_dashboard_summary,
    get_last_poll_by_type,
)

web_bp = Blueprint("web", __name__)


@web_bp.route("/")
def dashboard():
    summary = get_dashboard_summary()
    routers = get_dashboard_routers()
    last_inventory_poll = get_last_poll_by_type("INVENTORY")
    last_status_poll = get_last_poll_by_type("STATUS")

    if last_inventory_poll:
        last_inventory_poll["duration"] = format_duration(
            last_inventory_poll["duration_seconds"]
        )

    if last_status_poll:
        last_status_poll["duration"] = format_duration(
            last_status_poll["duration_seconds"]
        )

    return render_template(
        "dashboard.html",
        summary=summary,
        routers=routers,
    )