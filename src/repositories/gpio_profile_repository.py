from typing import Any

from src.repositories.db import get_connection


def upsert_profile_candidate(
    signature_hash: str,
    suggested_profile_name: str,
    product_name: str | None,
    sample_router_id: int,
    sample_router_name: str | None,
    sample_group_id: int | None,
    sample_group_name: str | None,
    pins_json: str,
) -> int:
    query = """
        MERGE dbo.gpio_profile_candidates AS target
        USING (
            SELECT
                ? AS signature_hash,
                ? AS suggested_profile_name,
                ? AS product_name,
                ? AS sample_router_id,
                ? AS sample_router_name,
                ? AS sample_group_id,
                ? AS sample_group_name,
                ? AS pins_json
        ) AS source
        ON target.signature_hash = source.signature_hash

        WHEN MATCHED THEN
            UPDATE SET
                target.routers_detected = target.routers_detected + 1,
                target.updated_at = SYSUTCDATETIME()

        WHEN NOT MATCHED THEN
            INSERT (
                signature_hash,
                suggested_profile_name,
                product_name,
                sample_router_id,
                sample_router_name,
                sample_group_id,
                sample_group_name,
                pins_json,
                routers_detected,
                created_at,
                updated_at
            )
            VALUES (
                source.signature_hash,
                source.suggested_profile_name,
                source.product_name,
                source.sample_router_id,
                source.sample_router_name,
                source.sample_group_id,
                source.sample_group_name,
                source.pins_json,
                1,
                SYSUTCDATETIME(),
                SYSUTCDATETIME()
            )

        OUTPUT inserted.id;
    """

    params = (
        signature_hash,
        suggested_profile_name,
        product_name,
        sample_router_id,
        sample_router_name,
        sample_group_id,
        sample_group_name,
        pins_json,
    )

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        conn.commit()

        return row[0]


def link_candidate_router(candidate_id: int, router_id: int) -> None:
    query = """
        IF NOT EXISTS (
            SELECT 1
            FROM dbo.gpio_profile_candidate_routers
            WHERE candidate_id = ?
              AND router_id = ?
        )
        BEGIN
            INSERT INTO dbo.gpio_profile_candidate_routers (
                candidate_id,
                router_id,
                created_at
            )
            VALUES (?, ?, SYSUTCDATETIME());
        END
    """

    params = (
        candidate_id,
        router_id,
        candidate_id,
        router_id,
    )

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()