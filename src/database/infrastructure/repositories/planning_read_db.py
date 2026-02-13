from typing import Any, Optional
from src.database.infrastructure.connection import get_conn

def list_plannings_summary_by_region(region: str, limit: int = 200) -> list[dict[str, Any]]:
    """
    Lista planejamentos da região + contagem de atribuições.
    Bom para tabela de overview do coordenador.
    """
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT
              wp.id,
              wp.region,
              wp.week_start,
              wp.status,
              wp.created_at,
              wp.coordinator_id,
              u.name AS coordinator_name,
              u.email AS coordinator_email,
              COUNT(pa.id) AS assignments_count
            FROM weekly_plannings wp
            JOIN users u ON u.id = wp.coordinator_id
            LEFT JOIN planning_assignments pa ON pa.planning_id = wp.id
            WHERE wp.region = ?
            GROUP BY wp.id
            ORDER BY wp.week_start DESC
            LIMIT ?
            """,
            (region, int(limit)),
        ).fetchall()

    return [dict(r) for r in rows]


def get_planning_header(planning_id: str) -> Optional[dict[str, Any]]:
    """
    Header do planejamento (sem assignments).
    """
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT
              wp.id,
              wp.region,
              wp.week_start,
              wp.status,
              wp.created_at,
              wp.coordinator_id,
              u.name AS coordinator_name,
              u.email AS coordinator_email
            FROM weekly_plannings wp
            JOIN users u ON u.id = wp.coordinator_id
            WHERE wp.id = ?
            """,
            (planning_id,),
        ).fetchone()

    return dict(row) if row else None


def list_planning_assignments_detailed(planning_id: str) -> list[dict[str, Any]]:
    """
    Traz o “miolo” do planejamento: loja + pesquisador.
    """
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT
              pa.id AS assignment_id,
              pa.planning_id,

              s.id AS store_id,
              s.name AS store_name,
              s.region AS store_region,
              s.status AS store_status,

              r.id AS researcher_id,
              r.name AS researcher_name,
              r.email AS researcher_email,
              r.region AS researcher_region

            FROM planning_assignments pa
            JOIN stores s ON s.id = pa.store_id
            JOIN users r ON r.id = pa.researcher_id
            WHERE pa.planning_id = ?
            ORDER BY s.name ASC, r.name ASC
            """,
            (planning_id,),
        ).fetchall()

    return [dict(r) for r in rows]


def list_researcher_week_tasks(*, researcher_id: str, planning_id: str) -> list[dict[str, Any]]:
    """
    Para o pesquisador: quais lojas ele deve visitar naquele planejamento.
    """
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT
              pa.id AS assignment_id,
              pa.planning_id,

              s.id AS store_id,
              s.name AS store_name,
              s.region AS store_region,
              s.status AS store_status,

              wp.week_start,
              wp.status AS planning_status
            FROM planning_assignments pa
            JOIN stores s ON s.id = pa.store_id
            JOIN weekly_plannings wp ON wp.id = pa.planning_id
            WHERE pa.researcher_id = ? AND pa.planning_id = ?
            ORDER BY s.name ASC
            """,
            (researcher_id, planning_id),
        ).fetchall()

    return [dict(r) for r in rows]


def find_planning_by_region_week(region: str, week_start: str) -> Optional[dict[str, Any]]:
    """
    Helper para achar o planning da semana/região
    """
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT id, region, week_start, status, coordinator_id, created_at
            FROM weekly_plannings
            WHERE region = ? AND week_start = ?
            """,
            (region, week_start),
        ).fetchone()
    return dict(row) if row else None