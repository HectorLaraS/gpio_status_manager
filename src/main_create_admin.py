from getpass import getpass

from werkzeug.security import generate_password_hash

from src.repositories.db import get_connection


def main() -> None:
    username = input("Username: ").strip()
    display_name = input("Display name: ").strip()
    password = getpass("Password: ")

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
            'ADMINISTRATOR',
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
        )
        conn.commit()

    print("Admin user created.")


if __name__ == "__main__":
    main()