import uuid
from src.database.infrastructure.connection import get_conn
from typing import Any, Optional

def list_brands() -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, name FROM brands ORDER BY name ASC"
        ).fetchall()
    return [dict(r) for r in rows]

def get_brand(brand_id: str) -> Optional[dict[str, Any]]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, name FROM brands WHERE id = ?",
            (brand_id,)
        ).fetchone()
    return dict(row) if row else None

def create_brand(name: str) -> str:
    brand_id = str(uuid.uuid4())
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO brands (id, name) VALUES (?, ?)",
            (brand_id, name)
        )
    return brand_id

def update_brand(brand_id: str, name: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE brands SET name = ? WHERE id = ?",
            (name, brand_id)
        )

def delete_brand(brand_id: str) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM brands WHERE id = ?", (brand_id,))