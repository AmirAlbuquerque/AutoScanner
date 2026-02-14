import uuid
from typing import Any, Optional

from src.database.infrastructure.connection import get_conn


def create_weekly_planning(
    *,
    coordinator_id: str,
    region: str,
    week_start: str,
    status: str,
    created_at: str,
) -> str:
    planning_id = str(uuid.uuid4())
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO weekly_plannings (id, coordinator_id, region, week_start, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (planning_id, coordinator_id, region, week_start, status, created_at),
        )
    return planning_id


def get_planning(planning_id: str) -> Optional[dict[str, Any]]:
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT id, coordinator_id, region, week_start, status, created_at
            FROM weekly_plannings
            WHERE id = ?
            """,
            (planning_id,),
        ).fetchone()
    return dict(row) if row else None


def get_planning_by_region_week(region: str, week_start: str) -> Optional[dict[str, Any]]:
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT id, coordinator_id, region, week_start, status, created_at
            FROM weekly_plannings
            WHERE region = ? AND week_start = ?
            """,
            (region, week_start),
        ).fetchone()
    return dict(row) if row else None


def list_plannings(
    *,
    region: Optional[str] = None,
    coordinator_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 200,
    offset: int = 0,
) -> list[dict[str, Any]]:
    where = []
    params: list[Any] = []

    if region:
        where.append("region = ?")
        params.append(region)
    if coordinator_id:
        where.append("coordinator_id = ?")
        params.append(coordinator_id)
    if status:
        where.append("status = ?")
        params.append(status)

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    with get_conn() as conn:
        rows = conn.execute(
            f"""
            SELECT id, coordinator_id, region, week_start, status, created_at
            FROM weekly_plannings
            {where_sql}
            ORDER BY week_start DESC
            LIMIT ? OFFSET ?
            """,
            (*params, int(limit), int(offset)),
        ).fetchall()
    return [dict(r) for r in rows]


def set_planning_status(planning_id: str, status: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE weekly_plannings SET status = ? WHERE id = ?",
            (status, planning_id),
        )