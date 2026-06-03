import json
import time
from typing import Any

import requests

from src.repositories.alert_action_repository import (
    create_alert_action_log,
    get_enabled_actions_by_event,
)


def build_alert_context(
    event_type: str,
    alert: dict[str, Any],
) -> dict[str, Any]:
    return {
        "event_type": event_type,
        "alert_id": alert.get("id"),
        "alert_number": alert.get("alert_number"),
        "status": alert.get("status"),
        "priority": alert.get("priority"),
        "title": alert.get("title"),
        "description": alert.get("description"),
        "router_id": alert.get("router_id"),
        "router_name": alert.get("router_name"),
        "router_description": alert.get("router_description"),
        "rule_name": alert.get("rule_name"),
        "opened_at": str(alert.get("opened_at")) if alert.get("opened_at") else None,
        "closed_at": str(alert.get("closed_at")) if alert.get("closed_at") else None,
        "last_detected_at": str(alert.get("last_detected_at")) if alert.get("last_detected_at") else None,
        "occurrence_count": alert.get("occurrence_count"),
    }


def render_payload_template(
    payload_template: str | None,
    context: dict[str, Any],
) -> str:
    if not payload_template:
        payload_template = """
{
  "event_type": "{{ event_type }}",
  "alert_number": "{{ alert_number }}",
  "status": "{{ status }}",
  "priority": "{{ priority }}",
  "title": "{{ title }}",
  "description": "{{ description }}",
  "router_id": "{{ router_id }}",
  "router_name": "{{ router_name }}",
  "router_description": "{{ router_description }}",
  "rule_name": "{{ rule_name }}",
  "opened_at": "{{ opened_at }}",
  "closed_at": "{{ closed_at }}",
  "last_detected_at": "{{ last_detected_at }}",
  "occurrence_count": "{{ occurrence_count }}"
}
""".strip()

    rendered = payload_template

    for key, value in context.items():
        rendered = rendered.replace(
            "{{ " + key + " }}",
            "" if value is None else str(value),
        )

    json.loads(rendered)

    return rendered


def build_headers(
    action: dict[str, Any],
) -> dict[str, str]:
    headers = {
        "Content-Type": action.get("content_type") or "application/json",
    }

    auth_type = action.get("auth_type") or "NONE"

    if auth_type == "API_TOKEN":
        token_header = action.get("api_token_header") or "Authorization"
        token = action.get("api_token") or ""

        if token_header.lower() == "authorization":
            headers[token_header] = f"Bearer {token}"
        else:
            headers[token_header] = token

    if auth_type == "CUSTOM_HEADERS":
        raw_headers = action.get("custom_headers_json")

        if raw_headers:
            custom_headers = json.loads(raw_headers)

            for key, value in custom_headers.items():
                headers[str(key)] = str(value)

    return headers


def build_basic_auth(
    action: dict[str, Any],
):
    if action.get("auth_type") != "BASIC_AUTH":
        return None

    username = action.get("auth_username")
    password = action.get("auth_password")

    if not username or not password:
        return None

    return (username, password)


def send_webhook_request(
    action: dict[str, Any],
    payload: str,
) -> tuple[str, int | None, str | None, str | None]:
    method = action.get("http_method") or "POST"
    url = action["webhook_url"]
    timeout = action.get("timeout_seconds") or 10
    verify_ssl = bool(action.get("verify_ssl"))

    headers = build_headers(action)
    auth = build_basic_auth(action)

    try:
        response = requests.request(
            method=method,
            url=url,
            data=payload.encode("utf-8"),
            headers=headers,
            auth=auth,
            timeout=timeout,
            verify=verify_ssl,
        )

        status = "SUCCESS" if 200 <= response.status_code < 300 else "FAILED"

        return (
            status,
            response.status_code,
            response.text[:4000],
            None,
        )

    except Exception as error:
        return (
            "FAILED",
            None,
            None,
            str(error),
        )


def execute_alert_action(
    action: dict[str, Any],
    event_type: str,
    alert: dict[str, Any],
) -> None:
    alert_id = alert.get("id")

    try:
        context = build_alert_context(
            event_type=event_type,
            alert=alert,
        )

        payload = render_payload_template(
            payload_template=action.get("payload_template"),
            context=context,
        )

        retry_count = action.get("retry_count") or 0

        last_status = "FAILED"
        last_response_code = None
        last_response_message = None
        last_error_message = None

        for attempt in range(retry_count + 1):
            status, response_code, response_message, error_message = send_webhook_request(
                action=action,
                payload=payload,
            )

            last_status = status
            last_response_code = response_code
            last_response_message = response_message
            last_error_message = error_message

            if status == "SUCCESS":
                break

            if attempt < retry_count:
                time.sleep(1)

        create_alert_action_log(
            alert_id=alert_id,
            alert_action_id=action["id"],
            event_type=event_type,
            status=last_status,
            response_code=last_response_code,
            response_message=last_response_message,
            error_message=last_error_message,
            request_payload=payload,
        )

    except Exception as error:
        create_alert_action_log(
            alert_id=alert_id,
            alert_action_id=action["id"],
            event_type=event_type,
            status="FAILED",
            error_message=str(error),
            request_payload=None,
        )


def execute_alert_actions(
    event_type: str,
    alert: dict[str, Any],
) -> None:
    actions = get_enabled_actions_by_event(event_type)

    for action in actions:
        execute_alert_action(
            action=action,
            event_type=event_type,
            alert=alert,
        )