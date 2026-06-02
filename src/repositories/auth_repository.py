from typing import Any

from src.repositories.db import get_connection


def get_user_by_username(
    username: str,
) -> dict[str, Any] | None:

    query = """
        SELECT
            id,
            username,
            password_hash,
            display_name,
            role_name,
            is_active,
            last_login_at
        FROM dbo.app_users
        WHERE username = ?;
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, username)

        row = cursor.fetchone()

        if not row:
            return None

        return {
            "id": row.id,
            "username": row.username,
            "password_hash": row.password_hash,
            "display_name": row.display_name,
            "role_name": row.role_name,
            "is_active": bool(row.is_active),
            "last_login_at": row.last_login_at,
        }


def update_last_login(
    user_id: int,
) -> None:

    query = """
        UPDATE dbo.app_users
        SET
            last_login_at = SYSUTCDATETIME(),
            updated_at = SYSUTCDATETIME()
        WHERE id = ?;
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, user_id)
        conn.commit()