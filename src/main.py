from src.config import load_settings
from src.repositories.db import get_connection
from src.repositories.group_repository import (
    count_active_groups,
    count_groups,
    get_active_groups,
)
from src.services.router_service import preview_routers_by_active_groups
from src.services.router_service import sync_routers_by_active_groups
from src.clients.ncos_client import NcosClient


def test_database_connection() -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DB_NAME()")
        db_name = cursor.fetchone()[0]

        print(f"Conexión exitosa a MS SQL. Database actual: {db_name}")


def test_groups_repository() -> None:
    total_groups = count_groups()
    active_groups = count_active_groups()
    groups = get_active_groups()

    print(f"Groups registrados: {total_groups}")
    print(f"Groups activos: {active_groups}")
    print("-" * 40)

    for group in groups[:10]:
        print(f"{group['netcloud_id']} | {group['name']} | active={group['is_active']}")

    if len(groups) > 10:
        print(f"... y {len(groups) - 10} grupos activos más")


def main() -> None:
    settings = load_settings()

    print("Cradlepoint GPIO Monitor")
    print("=" * 40)
    print(f"NetCloud URL: {settings.netcloud.base_url}")
    print(f"Database: {settings.database.database}")
    print(f"DB Server: {settings.database.server}")
    print(f"Poll interval: {settings.app.poll_interval_minutes} minutes")
    print("=" * 40)

    test_database_connection()
    print("=" * 40)

    test_groups_repository()
    print("=" * 40)

    #preview_routers_by_active_groups()
    sync_routers_by_active_groups()


if __name__ == "__main__":
    main()