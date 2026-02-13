import uuid
from typing import Any, Optional

from src.database.infrastructure.connection import get_conn


def create_assignment(
    *,
    planning_id: str,
    store_id: str,
    researcher_id: str,
) -> str:
    assignment_id = str(uuid.uuid4())
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO planning_assignments (id, planning_id, store_id, researcher_id)
            VALUES (?, ?, ?, ?)
            """,
            (assignment_id, planning_id, store_id, researcher_id),
        )
    return assignment_id


def delete_assignment(assignment_id: str) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM planning_assignments WHERE id = ?", (assignment_id,))


def delete_assignment_by_keys(planning_id: str, store_id: str, researcher_id: str) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            DELETE FROM planning_assignments
            WHERE planning_id = ? AND store_id = ? AND researcher_id = ?
            """,
            (planning_id, store_id, researcher_id),
        )


def list_assignments_by_planning(planning_id: str) -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, planning_id, store_id, researcher_id
            FROM planning_assignments
            WHERE planning_id = ?
            ORDER BY store_id ASC
            """,
            (planning_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def list_assignments_by_researcher(researcher_id: str, planning_id: Optional[str] = None) -> list[dict[str, Any]]:
    where = ["researcher_id = ?"]
    params: list[Any] = [researcher_id]

    if planning_id:
        where.append("planning_id = ?")
        params.append(planning_id)

    where_sql = " AND ".join(where)

    with get_conn() as conn:
        rows = conn.execute(
            f"""
            SELECT id, planning_id, store_id, researcher_id
            FROM planning_assignments
            WHERE {where_sql}
            ORDER BY planning_id DESC
            """,
            tuple(params),
        ).fetchall()
    return [dict(r) for r in rows]


def is_assigned(planning_id: str, store_id: str, researcher_id: str) -> bool:
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT 1
            FROM planning_assignments
            WHERE planning_id = ? AND store_id = ? AND researcher_id = ?
            LIMIT 1
            """,
            (planning_id, store_id, researcher_id),
        ).fetchone()
    return bool(row)