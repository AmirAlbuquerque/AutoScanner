from datetime import datetime, timezone
from typing import Any, Optional
import uuid
from src.database.infrastructure.connection import get_conn

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def insert_public_query_log(
    *,
    region: str,
    brand_id: str,
    model_id: str,
    version_id: Optional[str],
    year_model: Optional[int],
    actor_user_id: Optional[str],
) -> str:
    """
    Registra um log simples em public_queries.
    Retorna o id inserido.
    """
    qid = str(uuid.uuid4())
    v = version_id if version_id else "__ALL__"
    y = year_model if year_model is not None else -1

    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO public_queries
            (id, brand_id, model_id, version_id, year_model, region, created_at, actor_user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                qid,
                brand_id,
                model_id,
                v,
                y,
                region,
                _now_iso(),
                actor_user_id,
            ),
        )

    return qid

def compute_monthly_avg_and_samples(
    *,
    region: str,
    capture_month: str,
    brand_id: str,
    model_id: str,
    version_id: Optional[str],
    year_fabrication: Optional[int],
) -> tuple[int, Optional[float]]:
    """
    Retorna (samples, avg_price) para o filtro informado.
    """
    params: list[Any] = [region, capture_month, brand_id, model_id]

    where_version = ""
    if version_id:
        where_version = "AND vc.version_id = ?"
        params.append(version_id)

    where_year = ""
    if year_fabrication is not None:
        where_year = "AND vc.year_fabrication = ?"
        params.append(int(year_fabrication))

    with get_conn() as conn:
        row = conn.execute(
            f"""
            SELECT
              COUNT(1) AS samples,
              AVG(vc.price) AS avg_price
            FROM vehicle_captures vc
            JOIN captures c ON c.id = vc.capture_id
            JOIN stores s ON s.id = c.store_id
            WHERE s.region = ?
              AND c.capture_month = ?
              AND vc.brand_id = ?
              AND vc.model_id = ?
              {where_version}
              {where_year}
            """,
            params,
        ).fetchone()

    samples = int(row["samples"] or 0) if row else 0
    avg_price = float(row["avg_price"]) if row and row["avg_price"] is not None else None
    return samples, avg_price


def list_store_prices_last_capture_in_month(
    *,
    region: str,
    capture_month: str,
    brand_id: str,
    model_id: str,
    version_id: Optional[str],
    year_fabrication: Optional[int],
) -> list[dict[str, Any]]:
    """
    Lista preços por loja pegando a ÚLTIMA capture do mês por loja.
    """
    params: list[Any] = [region, capture_month, brand_id, model_id]

    where_version = ""
    if version_id:
        where_version = "AND vc.version_id = ?"
        params.append(version_id)

    where_year = ""
    if year_fabrication is not None:
        where_year = "AND vc.year_fabrication = ?"
        params.append(int(year_fabrication))

    with get_conn() as conn:
        rows = conn.execute(
            f"""
            WITH last_capture AS (
              SELECT
                c.store_id,
                MAX(c.capture_date) AS last_capture_date
              FROM captures c
              JOIN stores s ON s.id = c.store_id
              WHERE s.region = ?
                AND c.capture_month = ?
              GROUP BY c.store_id
            )
            SELECT
              s.id AS store_id,
              s.name AS store_name,
              s.region AS store_region,
              c.capture_date,
              vc.price
            FROM last_capture lc
            JOIN captures c
              ON c.store_id = lc.store_id
             AND c.capture_date = lc.last_capture_date
            JOIN stores s ON s.id = c.store_id
            JOIN vehicle_captures vc ON vc.capture_id = c.id
            WHERE vc.brand_id = ?
              AND vc.model_id = ?
              {where_version}
              {where_year}
            ORDER BY vc.price ASC
            """,
            params,
        ).fetchall()

    return [dict(r) for r in rows] if rows else []