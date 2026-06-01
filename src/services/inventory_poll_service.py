from src.services.router_service import sync_routers_by_active_groups


def run_inventory_poll() -> dict:
    print("=" * 80)
    print("INVENTORY POLL STARTED")
    print("=" * 80)

    stats = sync_routers_by_active_groups()

    print("=" * 80)
    print("INVENTORY POLL FINISHED")
    print("=" * 80)

    return stats