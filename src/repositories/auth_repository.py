from typing import Any

from src.repositories.db import get_connection

from werkzeug.security import generate_password_hash

def get_user_by_id(user_id: int) -> dict | None:
    query = """
        SELECT
            id,
            username,
            display_name,
            role_name,
            is_active,
            created_at,
            last_login_at
        FROM dbo.app_users
        WHERE id = ?;
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, user_id)
        row = cursor.fetchone()

        if not row:
            return None

        return {
            "id": row.id,
            "username": row.username,
            "display_name": row.display_name,
            "role_name": row.role_name,
            "is_active": bool(row.is_active),
            "created_at": row.created_at,
            "last_login_at": row.last_login_at,
        }


def update_user(
    user_id: int,
    display_name: str,
    role_name: str,
) -> None:
    query = """
        UPDATE dbo.app_users
        SET
            display_name = ?,
            role_name = ?,
            updated_at = SYSUTCDATETIME()
        WHERE id = ?;
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, display_name, role_name, user_id)
        conn.commit()


def set_user_active(
    user_id: int,
    is_active: bool,
) -> None:
    query = """
        UPDATE dbo.app_users
        SET
            is_active = ?,
            updated_at = SYSUTCDATETIME()
        WHERE id = ?;
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, int(is_active), user_id)
        conn.commit()


def reset_user_password(
    user_id: int,
    new_password: str,
) -> None:
    password_hash = generate_password_hash(new_password)

    query = """
        UPDATE dbo.app_users
        SET
            password_hash = ?,
            updated_at = SYSUTCDATETIME()
        WHERE id = ?;
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, password_hash, user_id)
        conn.commit()

def get_all_users() -> list[dict]:
    query = """
        SELECT
            id,
            username,
            display_name,
            role_name,
            is_active,
            created_at,
            last_login_at
        FROM dbo.app_users
        ORDER BY username;
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

        return [
            {
                "id": row.id,
                "username": row.username,
                "display_name": row.display_name,
                "role_name": row.role_name,
                "is_active": bool(row.is_active),
                "created_at": row.created_at,
                "last_login_at": row.last_login_at,
            }
            for row in rows
        ]


def create_user(
    username: str,
    display_name: str,
    password: str,
    role_name: str,
) -> None:
    password_hash = generate_password_hash(password)

    query = """
        INSERT INTO dbo.app_users (
            username,
            password_hash,
            display_name,
            role_name,
            is_active,
            created_at,
            updated_at
        )
        VALUES (
            ?,
            ?,
            ?,
            ?,
            1,
            SYSUTCDATETIME(),
            SYSUTCDATETIME()
        );
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            query,
            username,
            password_hash,
            display_name,
            role_name,
        )
        conn.commit()

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