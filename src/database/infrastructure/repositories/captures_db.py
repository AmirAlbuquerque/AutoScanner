import uuid
from typing import Any, Optional

from src.database.infrastructure.connection import get_conn


def create_capture(
    *,
    store_id: str,
    researcher_id: str,
    capture_date: str,   # ISO timestamp
    capture_month: str,  # YYYY-MM
    created_at: str,     # ISO timestamp
) -> str:
    capture_id = str(uuid.uuid4())
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO captures (id, store_id, researcher_id, capture_date, capture_month, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (capture_id, store_id, researcher_id, capture_date, capture_month, created_at),
        )
    return capture_id


def get_capture(capture_id: str) -> Optional[dict[str, Any]]:
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT id, store_id, researcher_id, capture_date, capture_month, created_at
            FROM captures
            WHERE id = ?
            """,
            (capture_id,),
        ).fetchone()
    return dict(row) if row else None


def list_captures(
    *,
    store_id: Optional[str] = None,
    researcher_id: Optional[str] = None,
    capture_month: Optional[str] = None,
    limit: int = 200,
    offset: int = 0,
) -> list[dict[str, Any]]:
    where = []
    params: list[Any] = []

    if store_id:
        where.append("store_id = ?")
        params.append(store_id)
    if researcher_id:
        where.append("researcher_id = ?")
        params.append(researcher_id)
    if capture_month:
        where.append("capture_month = ?")
        params.append(capture_month)

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    with get_conn() as conn:
        rows = conn.execute(
            f"""
            SELECT id, store_id, researcher_id, capture_date, capture_month, created_at
            FROM captures
            {where_sql}
            ORDER BY capture_date DESC
            LIMIT ? OFFSET ?
            """,
            (*params, int(limit), int(offset)),
        ).fetchall()

    return [dict(r) for r in rows]


def delete_capture(capture_id: str) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM captures WHERE id = ?", (capture_id,))