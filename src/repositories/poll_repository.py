from src.repositories.db import get_connection


def start_poll_execution(execution_type: str = "GENERAL") -> str:
    query = """
        INSERT INTO dbo.poll_executions (
            execution_type,
            status,
            started_at
        )
        OUTPUT inserted.execution_id
        VALUES (
            ?,
            'running',
            SYSUTCDATETIME()
        );
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, execution_type)
        row = cursor.fetchone()
        conn.commit()

        return str(row[0])


def finish_poll_execution(
    execution_id: str,
    status: str,
    groups_processed: int = 0,
    routers_processed: int = 0,
    routers_success: int = 0,
    routers_failed: int = 0,
    notes: str | None = None,
) -> None:
    query = """
        UPDATE dbo.poll_executions
        SET
            status = ?,
            finished_at = SYSUTCDATETIME(),
            groups_processed = ?,
            routers_processed = ?,
            routers_success = ?,
            routers_failed = ?,
            notes = ?            
        WHERE execution_id = ?;
    """

    params = (
        status,
        groups_processed,
        routers_processed,
        routers_success,
        routers_failed,
        notes,
        execution_id,
    )

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()

def has_running_poll(execution_type: str | None = None) -> bool:
    if execution_type:
        query = """
            SELECT COUNT(*)
            FROM dbo.poll_executions
            WHERE status = 'running'
              AND execution_type = ?;
        """

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, execution_type)
            return cursor.fetchone()[0] > 0

    query = """
        SELECT COUNT(*)
        FROM dbo.poll_executions
        WHERE status = 'running';
    """

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        return cursor.fetchone()[0] > 0

def add_poll_log(
    execution_id: str,
    level_name: str,
    message: str,
    router_id: int | None = None,
    source: str | None = None,
) -> None:
    query = """
        INSERT INTO dbo.poll_logs (
            execution_id,
            router_id,
            level_name,
            source,
            message,
            created_at
        )
        VALUES (
            ?,
            ?,
            ?,
            ?,
            ?,
            SYSUTCDATETIME()
        );
    """

    params = (
        execution_id,
        router_id,
        level_name,
        source,
        message,
    )

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()