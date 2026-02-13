import uuid
from src.database.infrastructure.connection import get_conn
from typing import Any, Optional

def list_versions_by_model(model_id: str) -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, model_id, name, image_url FROM versions WHERE model_id = ? ORDER BY name ASC",
            (model_id,)
        ).fetchall()
    return [dict(r) for r in rows]

def get_version(version_id: str) -> Optional[dict[str, Any]]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, model_id, name, image_url FROM versions WHERE id = ?",
            (version_id,)
        ).fetchone()
    return dict(row) if row else None

def create_version(model_id: str, name: str, image_url: Optional[str]) -> str:
    version_id = str(uuid.uuid4())
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO versions (id, model_id, name, image_url) VALUES (?, ?, ?, ?)",
            (version_id, model_id, name, image_url)
        )
    return version_id

def update_version(version_id: str, name: str, image_url: Optional[str]) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE versions SET name = ?, image_url = ? WHERE id = ?",
            (name, image_url, version_id)
        )

def delete_version(version_id: str) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM versions WHERE id = ?", (version_id,))