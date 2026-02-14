import uuid
from src.database.infrastructure.connection import get_conn
from typing import Any, Optional

def list_models_by_brand(brand_id: str) -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, brand_id, name FROM models WHERE brand_id = ? ORDER BY name ASC",
            (brand_id,)
        ).fetchall()
    return [dict(r) for r in rows]

def get_model(model_id: str) -> Optional[dict[str, Any]]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, brand_id, name FROM models WHERE id = ?",
            (model_id,)
        ).fetchone()
    return dict(row) if row else None

def create_model(brand_id: str, name: str) -> str:
    model_id = str(uuid.uuid4())
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO models (id, brand_id, name) VALUES (?, ?, ?)",
            (model_id, brand_id, name)
        )
    return model_id

def update_model(model_id: str, name: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE models SET name = ? WHERE id = ?",
            (name, model_id)
        )

def delete_model(model_id: str) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM models WHERE id = ?", (model_id,))