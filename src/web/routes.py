from flask import Blueprint, render_template

from src.repositories.dashboard_repository import (
    get_dashboard_routers,
    get_dashboard_summary,
)

web_bp = Blueprint("web", __name__)


@web_bp.route("/")
def dashboard():
    summary = get_dashboard_summary()
    routers = get_dashboard_routers()

    return render_template(
        "dashboard.html",
        summary=summary,
        routers=routers,
    )