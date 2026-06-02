from werkzeug.security import check_password_hash

from src.repositories.auth_repository import (
    get_user_by_username,
    update_last_login,
)


def authenticate_user(
    username: str,
    password: str,
):
    user = get_user_by_username(username)

    if not user:
        return None

    if not user["is_active"]:
        return None

    if not check_password_hash(
        user["password_hash"],
        password,
    ):
        return None

    update_last_login(user["id"])

    return user