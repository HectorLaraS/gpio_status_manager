from flask import Blueprint, render_template
from src.repositories.dashboard_repository import get_alert_widgets

from src.repositories.alert_dashboard_repository import (
    get_alerts_by_type,
    get_open_alerts_summary,
    get_recently_closed_alerts,
    get_recently_opened_alerts,
    get_top_affected_routers,
    get_last_execution_by_type,
)
from src.repositories.auth_repository import (
    create_user,
    get_all_users,
)

from flask import (
    render_template,
    request,
    redirect,
    session,
)

from src.web.auth import login_required, roles_required

from flask import (
    render_template,
    request,
    redirect,
    session,
)

from src.services.auth_service import (
    authenticate_user,
)

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

from flask import request, redirect, url_for

from src.repositories.incident_rule_repository import (
    get_incident_rules,
    update_incident_rule,
)

web_bp = Blueprint("web", __name__)

@web_bp.route("/users")
@roles_required("ADMINISTRATOR")
def users():
    users_list = get_all_users()

    return render_template(
        "users.html",
        users=users_list,
    )


@web_bp.route("/users/create", methods=["GET", "POST"])
@roles_required("ADMINISTRATOR")
def create_user_route():
    if request.method == "POST":
        username = request.form["username"].strip()
        display_name = request.form["display_name"].strip()
        password = request.form["password"]
        role_name = request.form["role_name"]

        create_user(
            username=username,
            display_name=display_name,
            password=password,
            role_name=role_name,
        )

        return redirect("/users")

    return render_template("create_user.html")

@web_bp.route("/alert-dashboard")
@login_required
def alert_dashboard():
    summary = get_open_alerts_summary()
    alerts_by_type = get_alerts_by_type()
    recently_opened = get_recently_opened_alerts()
    recently_closed = get_recently_closed_alerts()
    top_routers = get_top_affected_routers()
    last_status_poll = get_last_execution_by_type("STATUS")
    last_inventory_poll = get_last_execution_by_type("INVENTORY")
    last_alert_engine = get_last_execution_by_type("ALERT_ENGINE")

    return render_template(
        "alert_dashboard.html",
        summary=summary,
        alerts_by_type=alerts_by_type,
        recently_opened=recently_opened,
        recently_closed=recently_closed,
        top_routers=top_routers,
        last_status_poll=last_status_poll,
        last_inventory_poll=last_inventory_poll,
        last_alert_engine=last_alert_engine,
        )

@web_bp.route("/incident-rules")
@roles_required("ENGINEER", "ADMINISTRATOR")
def incident_rules():

    rules = get_incident_rules()

    return render_template(
        "incident_rules.html",
        rules=rules,
    )

@web_bp.route("/incident-rules/update", methods=["POST"])
@roles_required("ENGINEER", "ADMINISTRATOR")
def update_incident_rule_route():

    rule_id = int(request.form["rule_id"])
    duration_minutes = int(request.form["duration_minutes"])
    priority = request.form["priority"]

    is_active = (
        request.form.get("is_active") == "on"
    )

    update_incident_rule(
        rule_id=rule_id,
        duration_minutes=duration_minutes,
        priority=priority,
        is_active=is_active,
    )

    return redirect(
        url_for("web.incident_rules")
    )

@web_bp.route("/")
@login_required
def home():
    return render_template("home.html")

@web_bp.route(
    "/login",
    methods=["GET", "POST"],
)
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = authenticate_user(
            username,
            password,
        )

        if not user:
            return render_template(
                "login.html",
                error="Invalid credentials",
            )

        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["display_name"] = user["display_name"]
        session["role_name"] = user["role_name"]

        next_url = request.args.get("next") or "/"
        return redirect(next_url)

    return render_template(
        "login.html",
        error=None,
    )

@web_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@web_bp.route("/dashboard")
@login_required
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
@login_required
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