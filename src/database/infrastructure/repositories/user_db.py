from src.database.infrastructure.connection import get_conn
from typing import Any, Optional

def create_user (
    user_id: str,
    name: str,
    email: str,
    role: str,
    region: str,
    hash_password: str,
    active: int, date) :
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO users (id, name, email, role, region, password_hash, active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, name.strip(), email, role, region, hash_password, int(active), date)
        )

def list_users () -> list[dict[str, Any]]: 
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, name, email, role, region, active, created_at FROM users ORDER BY created_at DESC"
        ).fetchall()
    return [dict(r) for r in rows]

def get_user(user_id) -> Optional [dict[str, Any]] :
     with get_conn() as conn:
        row = conn.execute(
            "SELECT id, name, email, role, region, active, created_at FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
        return dict(row) if row else None

def update_user(name, email, role, region, active, user_id) -> None:
     with get_conn() as conn:
        conn.execute(
            """
            UPDATE users
            SET name = ?, email = ?, role = ?, region = ?, active = ?
            WHERE id = ?
            """,
            (name.strip(), email, role, region, int(active), user_id)
        )

def set_password (new_hash_password, user_id) -> None:
        with get_conn() as conn:
            conn.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (new_hash_password, user_id)
            )

def delete_user (user_id) -> None:
     with get_conn() as conn:
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))

def get_user_by_id(user_id: str) -> Optional[dict[str, Any]]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, name, email, role, region, active, created_at FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
    return dict(row) if row else None