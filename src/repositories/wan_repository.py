from typing import Any

from src.repositories.db import get_connection


def clear_selected_wan(router_db_id: int) -> None:
    query = """
        UPDATE dbo.router_wan_interfaces
        SET
            is_selected = 0,
            updated_at = SYSUTCDATETIME()
        WHERE router_id = ?;
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, router_db_id)
        conn.commit()


def upsert_wan_interface(
    router_db_id: int,
    net_device: dict[str, Any],
    is_selected: bool = False,
) -> int:
    query = """
        MERGE dbo.router_wan_interfaces AS target
        USING (
            SELECT
                ? AS router_id,
                ? AS uid,
                ? AS name,
                ? AS interface_type,
                ? AS connection_state,
                ? AS summary,
                ? AS ipv4_address,
                ? AS gateway,
                ? AS netmask,
                ? AS dns_primary,
                ? AS dns_secondary,
                ? AS is_selected
        ) AS source
        ON target.router_id = source.router_id
           AND ISNULL(target.uid, '') = ISNULL(source.uid, '')
           AND ISNULL(target.name, '') = ISNULL(source.name, '')

        WHEN MATCHED THEN
            UPDATE SET
                target.interface_type = source.interface_type,
                target.connection_state = source.connection_state,
                target.summary = source.summary,
                target.ipv4_address = source.ipv4_address,
                target.gateway = source.gateway,
                target.netmask = source.netmask,
                target.dns_primary = source.dns_primary,
                target.dns_secondary = source.dns_secondary,
                target.is_selected = source.is_selected,
                target.last_successful_connection =
                    CASE
                        WHEN source.connection_state = 'connected'
                        THEN SYSUTCDATETIME()
                        ELSE target.last_successful_connection
                    END,
                target.checked_at = SYSUTCDATETIME(),
                target.updated_at = SYSUTCDATETIME()

        WHEN NOT MATCHED THEN
            INSERT (
                router_id,
                uid,
                name,
                interface_type,
                connection_state,
                summary,
                ipv4_address,
                gateway,
                netmask,
                dns_primary,
                dns_secondary,
                is_selected,
                last_successful_connection,
                checked_at,
                created_at,
                updated_at
            )
            VALUES (
                source.router_id,
                source.uid,
                source.name,
                source.interface_type,
                source.connection_state,
                source.summary,
                source.ipv4_address,
                source.gateway,
                source.netmask,
                source.dns_primary,
                source.dns_secondary,
                source.is_selected,
                CASE
                    WHEN source.connection_state = 'connected'
                    THEN SYSUTCDATETIME()
                    ELSE NULL
                END,
                SYSUTCDATETIME(),
                SYSUTCDATETIME(),
                SYSUTCDATETIME()
            )

        OUTPUT inserted.id;
    """

    params = (
        router_db_id,
        net_device.get("uid"),
        net_device.get("name"),
        net_device.get("type"),
        net_device.get("connection_state"),
        net_device.get("summary"),
        net_device.get("ipv4_address"),
        net_device.get("gateway"),
        net_device.get("netmask"),
        net_device.get("dns0"),
        net_device.get("dns1"),
        1 if is_selected else 0,
    )

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        conn.commit()

        return row[0]