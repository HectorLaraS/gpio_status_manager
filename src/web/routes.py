from flask import Blueprint, render_template
from src.repositories.dashboard_repository import get_alert_widgets
from src.repositories.poll_execution_dashboard_repository import (
    get_poll_executions,
)
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

from src.repositories.alert_action_repository import (
    get_alert_action_logs,
    get_alert_action_log_by_id,
)

from src.repositories.alert_action_repository import (
    create_alert_action,
    get_alert_actions,
    set_alert_action_enabled,
)

from src.repositories.alert_repository import (
    get_alert_by_id,
    update_alert_external_reference,
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

from src.repositories.poll_execution_details_repository import (
    get_poll_execution_by_execution_id,
    get_poll_logs_by_execution_id,
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

from src.repositories.auth_repository import (
    create_user,
    get_all_users,
    get_user_by_id,
    reset_user_password,
    set_user_active,
    update_user,
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

@web_bp.route("/poll-executions/<execution_id>")
@login_required
def poll_execution_details(execution_id: str):
    execution = get_poll_execution_by_execution_id(
        execution_id=execution_id,
    )

    if not execution:
        return redirect("/poll-executions")

    logs = get_poll_logs_by_execution_id(
        execution_id=execution_id,
    )

    return render_template(
        "poll_execution_details.html",
        execution=execution,
        logs=logs,
    )

@web_bp.route("/poll-executions")
@login_required
def poll_executions():
    executions = get_poll_executions()

    return render_template(
        "poll_executions.html",
        executions=executions,
    )

@web_bp.route("/alerts/<int:alert_id>/edit", methods=["GET", "POST"])
@roles_required("ENGINEER", "ADMINISTRATOR")
def edit_alert_route(alert_id: int):
    alert = get_alert_by_id(alert_id)

    if not alert:
        return redirect("/alert-dashboard")

    if request.method == "POST":
        external_system = request.form.get("external_system") or None
        external_ticket = request.form.get("external_ticket") or None
        external_url = request.form.get("external_url") or None

        update_alert_external_reference(
            alert_id=alert_id,
            external_system=external_system,
            external_ticket=external_ticket,
            external_url=external_url,
        )

        return redirect("/alert-dashboard")

    return render_template(
        "edit_alert.html",
        alert=alert,
    )

@web_bp.route("/alert-action-logs")
@roles_required("ADMINISTRATOR")
def alert_action_logs():
    logs = get_alert_action_logs()

    return render_template(
        "alert_action_logs.html",
        logs=logs,
    )

@web_bp.route("/alert-action-logs/<int:log_id>")
@roles_required("ADMINISTRATOR")
def alert_action_log_details(log_id: int):
    log = get_alert_action_log_by_id(log_id)

    if not log:
        return redirect("/alert-action-logs")

    return render_template(
        "alert_action_log_details.html",
        log=log,
    )

@web_bp.route("/alert-actions")
@roles_required("ADMINISTRATOR")
def alert_actions():
    actions = get_alert_actions()

    return render_template(
        "alert_actions.html",
        actions=actions,
    )


@web_bp.route("/alert-actions/create", methods=["GET", "POST"])
@roles_required("ADMINISTRATOR")
def create_alert_action_route():
    if request.method == "POST":
        create_alert_action(
            action_name=request.form["action_name"].strip(),
            description=request.form.get("description") or None,
            event_type=request.form["event_type"],
            webhook_url=request.form["webhook_url"].strip(),
            http_method=request.form["http_method"],
            auth_type=request.form["auth_type"],
            auth_username=request.form.get("auth_username") or None,
            auth_password=request.form.get("auth_password") or None,
            api_token=request.form.get("api_token") or None,
            api_token_header=request.form.get("api_token_header") or None,
            custom_headers_json=request.form.get("custom_headers_json") or None,
            payload_template=request.form.get("payload_template") or None,
            content_type=request.form.get("content_type") or "application/json",
            timeout_seconds=int(request.form.get("timeout_seconds") or 10),
            retry_count=int(request.form.get("retry_count") or 0),
            verify_ssl=request.form.get("verify_ssl") == "on",
            is_enabled=request.form.get("is_enabled") == "on",
        )

        return redirect("/alert-actions")

    return render_template("create_alert_action.html")


@web_bp.route("/alert-actions/<int:action_id>/disable", methods=["POST"])
@roles_required("ADMINISTRATOR")
def disable_alert_action_route(action_id: int):
    set_alert_action_enabled(
        action_id=action_id,
        is_enabled=False,
    )

    return redirect("/alert-actions")


@web_bp.route("/alert-actions/<int:action_id>/enable", methods=["POST"])
@roles_required("ADMINISTRATOR")
def enable_alert_action_route(action_id: int):
    set_alert_action_enabled(
        action_id=action_id,
        is_enabled=True,
    )

    return redirect("/alert-actions")

@web_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@roles_required("ADMINISTRATOR")
def edit_user_route(user_id: int):
    user = get_user_by_id(user_id)

    if not user:
        return redirect("/users")

    if request.method == "POST":
        display_name = request.form["display_name"].strip()
        role_name = request.form["role_name"]

        update_user(
            user_id=user_id,
            display_name=display_name,
            role_name=role_name,
        )

        return redirect("/users")

    return render_template(
        "edit_user.html",
        user=user,
    )


@web_bp.route("/users/<int:user_id>/disable", methods=["POST"])
@roles_required("ADMINISTRATOR")
def disable_user_route(user_id: int):
    set_user_active(
        user_id=user_id,
        is_active=False,
    )

    return redirect("/users")


@web_bp.route("/users/<int:user_id>/enable", methods=["POST"])
@roles_required("ADMINISTRATOR")
def enable_user_route(user_id: int):
    set_user_active(
        user_id=user_id,
        is_active=True,
    )

    return redirect("/users")


@web_bp.route("/users/<int:user_id>/reset-password", methods=["GET", "POST"])
@roles_required("ADMINISTRATOR")
def reset_password_route(user_id: int):
    user = get_user_by_id(user_id)

    if not user:
        return redirect("/users")

    if request.method == "POST":
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        if new_password != confirm_password:
            return render_template(
                "reset_password.html",
                user=user,
                error="Passwords do not match.",
            )

        reset_user_password(
            user_id=user_id,
            new_password=new_password,
        )

        return redirect("/users")

    return render_template(
        "reset_password.html",
        user=user,
        error=None,
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