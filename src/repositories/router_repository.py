from typing import Any

from src.repositories.db import get_connection


def upsert_router(router: dict[str, Any], group_db_id: int) -> int:
    """
    Inserta o actualiza un router usando netcloud_id como llave natural.
    Regresa el id interno de dbo.routers.
    """

    query = """
        MERGE dbo.routers AS target
        USING (
            SELECT
                ? AS netcloud_id,
                ? AS group_id,
                ? AS name,
                ? AS description,
                ? AS state,
                ? AS config_status,
                ? AS full_product_name,
                ? AS mac,
                ? AS serial_number,
                ? AS asset_id
        ) AS source
        ON target.netcloud_id = source.netcloud_id

        WHEN MATCHED THEN
            UPDATE SET
                target.group_id = source.group_id,
                target.name = source.name,
                target.description = source.description,
                target.state = source.state,
                target.config_status = source.config_status,
                target.full_product_name = source.full_product_name,
                target.mac = source.mac,
                target.serial_number = source.serial_number,
                target.asset_id = source.asset_id,
                target.is_active = 1,
                target.last_seen_at = SYSUTCDATETIME(),
                target.updated_at = SYSUTCDATETIME()

        WHEN NOT MATCHED THEN
            INSERT (
                netcloud_id,
                group_id,
                name,
                description,
                state,
                config_status,
                full_product_name,
                mac,
                serial_number,
                asset_id,
                is_active,
                last_seen_at,
                created_at,
                updated_at
            )
            VALUES (
                source.netcloud_id,
                source.group_id,
                source.name,
                source.description,
                source.state,
                source.config_status,
                source.full_product_name,
                source.mac,
                source.serial_number,
                source.asset_id,
                1,
                SYSUTCDATETIME(),
                SYSUTCDATETIME(),
                SYSUTCDATETIME()
            )

        OUTPUT inserted.id;
    """

    params = (
        int(router.get("id")),
        group_db_id,
        router.get("name"),
        router.get("description"),
        router.get("state"),
        router.get("config_status"),
        router.get("full_product_name"),
        router.get("mac"),
        router.get("serial_number"),
        router.get("asset_id"),
    )

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        conn.commit()

        return row[0]


def count_routers() -> int:
    query = """
        SELECT COUNT(*)
        FROM dbo.routers;
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        return cursor.fetchone()[0]


def get_router_by_netcloud_id(netcloud_id: int) -> dict[str, Any] | None:
    query = """
        SELECT
            id,
            netcloud_id,
            group_id,
            name,
            description,
            state,
            config_status,
            full_product_name,
            mac,
            serial_number,
            asset_id,
            is_active,
            last_seen_at
        FROM dbo.routers
        WHERE netcloud_id = ?;
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, netcloud_id)
        row = cursor.fetchone()

        if not row:
            return None

        return {
            "id": row.id,
            "netcloud_id": row.netcloud_id,
            "group_id": row.group_id,
            "name": row.name,
            "description": row.description,
            "state": row.state,
            "config_status": row.config_status,
            "full_product_name": row.full_product_name,
            "mac": row.mac,
            "serial_number": row.serial_number,
            "asset_id": row.asset_id,
            "is_active": bool(row.is_active),
            "last_seen_at": row.last_seen_at,
        }