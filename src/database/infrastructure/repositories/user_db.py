from src.database.infrastructure.connection import get_conn
from typing import Any, Optional

def create_user (
    *,
    user_id: str,
    name: str,
    email: str,
    role: str,
    region: Optional[str],
    hash_password: str,
    active: int,
    created_at: str,) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO users (id, name, email, role, region, password_hash, active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, name.strip(), email, role, region, hash_password, int(active), created_at)
        )

def list_users () -> list[dict[str, Any]]: 
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, name, email, role, region, active, created_at FROM users ORDER BY created_at DESC"
        ).fetchall()
    return [dict(r) for r in rows]

def get_user(user_id: str) -> Optional [dict[str, Any]] :
     with get_conn() as conn:
        row = conn.execute(
            "SELECT id, name, email, role, region, active, created_at FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
        return dict(row) if row else None
    
def get_user_by_email(email: str) -> Optional [dict[str, Any]] :
     with get_conn() as conn:
        row = conn.execute(
            "SELECT id, name, email, role, region, active, created_at FROM users WHERE email = ?",
            (email.strip().lower(),)
        ).fetchone()
        return dict(row) if row else None

def update_user(
    *,
    user_id: str,
    name: str,
    email: str,
    role: str,
    region: Optional[str],
    active: int) -> None:
     with get_conn() as conn:
        conn.execute(
            """
            UPDATE users
            SET name = ?, email = ?, role = ?, region = ?, active = ?
            WHERE id = ?
            """,
            (name.strip(), email.strip().lower(), role, region, int(active), user_id)
        )

def set_password (*, user_id: str, new_hash_password: str) -> None:
        with get_conn() as conn:
            conn.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (new_hash_password, user_id)
            )

def delete_user (user_id: str) -> None:
     with get_conn() as conn:
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))