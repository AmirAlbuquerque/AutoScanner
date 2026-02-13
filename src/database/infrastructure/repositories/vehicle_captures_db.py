import uuid
from typing import Any, Iterable
from src.database.infrastructure.connection import get_conn

def create_vehicle_capture(
    *,
    capture_id: str,
    brand_id: str,
    model_id: str,
    version_id: str,
    year_fabrication: int,
    price: float,
    created_at: str,
) -> str:
    vc_id = str(uuid.uuid4())
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO vehicle_captures (
              id, capture_id, brand_id, model_id, version_id, year_fabrication, price, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (vc_id, capture_id, brand_id, model_id, version_id, int(year_fabrication), float(price), created_at),
        )
    return vc_id

def bulk_create_vehicle_captures(
    *,
    capture_id: str,
    items: Iterable[dict[str, Any]],
    created_at: str,
) -> int:
    """
    items: dicts com brand_id, model_id, version_id, year_fabrication, price
    Retorna quantidade inserida.
    """
    rows = []
    for it in items:
        rows.append((
            str(uuid.uuid4()),
            capture_id,
            it["brand_id"],
            it["model_id"],
            it["version_id"],
            int(it["year_fabrication"]),
            float(it["price"]),
            created_at,
        ))

    with get_conn() as conn:
        conn.executemany(
            """
            INSERT INTO vehicle_captures (
              id, capture_id, brand_id, model_id, version_id, year_fabrication, price, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
    return len(rows)

def list_vehicle_captures(capture_id: str) -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, capture_id, brand_id, model_id, version_id, year_fabrication, price, created_at
            FROM vehicle_captures
            WHERE capture_id = ?
            ORDER BY created_at ASC
            """,
            (capture_id,),
        ).fetchall()
    return [dict(r) for r in rows]