from src.clients.netcloud_client import NetCloudClient
from src.repositories.group_repository import get_active_groups


def preview_routers_by_active_groups() -> None:
    client = NetCloudClient()
    groups = get_active_groups()

    print(f"Consultando routers de {len(groups)} grupos activos...")
    print("=" * 80)

    total_routers = 0

    for group in groups:
        group_netcloud_id = group["netcloud_id"]
        group_name = group["name"]

        print(f"Grupo: {group_name} ({group_netcloud_id})")

        routers = client.get_routers_by_group(group_netcloud_id)
        total_routers += len(routers)

        print(f"Routers encontrados: {len(routers)}")

        for router in routers[:5]:
            print(
                f"  - ID: {router.get('id')} | "
                f"Name: {router.get('name')} | "
                f"Description: {router.get('description')} | "
                f"State: {router.get('state')} | "
                f"Config: {router.get('config_status')}"
            )

        if len(routers) > 5:
            print(f"  ... y {len(routers) - 5} routers más")

        print("-" * 80)

    print(f"Total routers encontrados: {total_routers}")