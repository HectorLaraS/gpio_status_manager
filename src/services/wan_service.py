from typing import Any

from src.clients.netcloud_client import NetCloudClient
from src.repositories.wan_repository import clear_selected_wan, upsert_wan_interface


def select_primary_wan(net_devices: list[dict[str, Any]]) -> dict[str, Any] | None:
    """
    Selecciona la WAN principal para usar su ipv4_address.
    Regla inicial:
    1. Debe tener connection_state = connected.
    2. Debe tener ipv4_address.
    3. Si hay varias, toma la primera que regrese NetCloud.
    """

    for device in net_devices:
        if (
            device.get("connection_state") == "connected"
            and device.get("ipv4_address")
        ):
            return device

    return None


def sync_wan_interfaces_for_router(router_db_id: int, router_netcloud_id: int) -> str | None:
    client = NetCloudClient()

    net_devices = client.get_wan_net_devices_by_router(router_netcloud_id)
    primary_wan = select_primary_wan(net_devices)

    clear_selected_wan(router_db_id)

    for device in net_devices:
        is_selected = False

        if primary_wan:
            is_selected = device is primary_wan

        upsert_wan_interface(
            router_db_id=router_db_id,
            net_device=device,
            is_selected=is_selected,
        )

    if primary_wan:
        return primary_wan.get("ipv4_address")

    return None