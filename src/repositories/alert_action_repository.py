from typing import Any

from src.repositories.db import get_connection


def get_alert_actions() -> list[dict[str, Any]]:
    query = """
        SELECT
            id,
            action_name,
            description,
            event_type,
            webhook_url,
            http_method,
            auth_type,
            auth_username,
            api_token_header,
            custom_headers_json,
            payload_template,
            content_type,
            timeout_seconds,
            retry_count,
            verify_ssl,
            is_enabled,
            created_at,
            updated_at
        FROM dbo.alert_actions
        ORDER BY action_name;
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

        return [
            {
                "id": row.id,
                "action_name": row.action_name,
                "description": row.description,
                "event_type": row.event_type,
                "webhook_url": row.webhook_url,
                "http_method": row.http_method,
                "auth_type": row.auth_type,
                "auth_username": row.auth_username,
                "api_token_header": row.api_token_header,
                "custom_headers_json": row.custom_headers_json,
                "payload_template": row.payload_template,
                "content_type": row.content_type,
                "timeout_seconds": row.timeout_seconds,
                "retry_count": row.retry_count,
                "verify_ssl": bool(row.verify_ssl),
                "is_enabled": bool(row.is_enabled),
                "created_at": row.created_at,
                "updated_at": row.updated_at,
            }
            for row in rows
        ]


def get_enabled_actions_by_event(event_type: str) -> list[dict[str, Any]]:
    query = """
        SELECT
            id,
            action_name,
            description,
            event_type,
            webhook_url,
            http_method,
            auth_type,
            auth_username,
            auth_password,
            api_token,
            api_token_header,
            custom_headers_json,
            payload_template,
            content_type,
            timeout_seconds,
            retry_count,
            verify_ssl,
            is_enabled
        FROM dbo.alert_actions
        WHERE event_type = ?
          AND is_enabled = 1;
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, event_type)
        rows = cursor.fetchall()

        return [
            {
                "id": row.id,
                "action_name": row.action_name,
                "description": row.description,
                "event_type": row.event_type,
                "webhook_url": row.webhook_url,
                "http_method": row.http_method,
                "auth_type": row.auth_type,
                "auth_username": row.auth_username,
                "auth_password": row.auth_password,
                "api_token": row.api_token,
                "api_token_header": row.api_token_header,
                "custom_headers_json": row.custom_headers_json,
                "payload_template": row.payload_template,
                "content_type": row.content_type,
                "timeout_seconds": row.timeout_seconds,
                "retry_count": row.retry_count,
                "verify_ssl": bool(row.verify_ssl),
                "is_enabled": bool(row.is_enabled),
            }
            for row in rows
        ]


def create_alert_action(
    action_name: str,
    description: str | None,
    event_type: str,
    webhook_url: str,
    http_method: str,
    auth_type: str,
    auth_username: str | None,
    auth_password: str | None,
    api_token: str | None,
    api_token_header: str | None,
    custom_headers_json: str | None,
    payload_template: str | None,
    content_type: str,
    timeout_seconds: int,
    retry_count: int,
    verify_ssl: bool,
    is_enabled: bool,
) -> None:
    query = """
        INSERT INTO dbo.alert_actions (
            action_name,
            description,
            event_type,
            webhook_url,
            http_method,
            auth_type,
            auth_username,
            auth_password,
            api_token,
            api_token_header,
            custom_headers_json,
            payload_template,
            content_type,
            timeout_seconds,
            retry_count,
            verify_ssl,
            is_enabled,
            created_at,
            updated_at
        )
        VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            SYSUTCDATETIME(),
            SYSUTCDATETIME()
        );
    """

    params = (
        action_name,
        description,
        event_type,
        webhook_url,
        http_method,
        auth_type,
        auth_username,
        auth_password,
        api_token,
        api_token_header,
        custom_headers_json,
        payload_template,
        content_type,
        timeout_seconds,
        retry_count,
        int(verify_ssl),
        int(is_enabled),
    )

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()


def set_alert_action_enabled(
    action_id: int,
    is_enabled: bool,
) -> None:
    query = """
        UPDATE dbo.alert_actions
        SET
            is_enabled = ?,
            updated_at = SYSUTCDATETIME()
        WHERE id = ?;
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, int(is_enabled), action_id)
        conn.commit()


def create_alert_action_log(
    alert_id: int | None,
    alert_action_id: int,
    event_type: str,
    status: str,
    response_code: int | None = None,
    response_message: str | None = None,
    error_message: str | None = None,
    request_payload: str | None = None,
) -> None:
    query = """
        INSERT INTO dbo.alert_action_logs (
            alert_id,
            alert_action_id,
            event_type,
            status,
            response_code,
            response_message,
            error_message,
            request_payload,
            created_at
        )
        VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, SYSUTCDATETIME()
        );
    """

    params = (
        alert_id,
        alert_action_id,
        event_type,
        status,
        response_code,
        response_message,
        error_message,
        request_payload,
    )

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()