from flask import Blueprint, render_template
from src.repositories.dashboard_repository import get_alert_widgets

from src.repositories.dashboard_repository import (
    format_duration,
    get_dashboard_routers,
    get_dashboard_summary,
    get_last_poll_by_type,
)

from src.repositories.dashboard_repository import (
    get_alert_widgets,
    get_config_pending_routers,
    get_offline_routers,
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
        last_inventory_poll=last_inventory_poll,
        last_status_poll=last_status_poll,
    )

@web_bp.route("/alerts")
def alerts():
    alert_widgets = get_alert_widgets()
    offline_routers = get_offline_routers()
    config_pending_routers = get_config_pending_routers()

    return render_template(
        "alerts.html",
        alert_widgets=alert_widgets,
        offline_routers=offline_routers,
        config_pending_routers=config_pending_routers,
    )