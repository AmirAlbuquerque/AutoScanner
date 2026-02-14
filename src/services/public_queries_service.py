from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from src.database.infrastructure.repositories import public_queries_db
from src.domain.public_queries_rules import validate_public_query_filters


@dataclass(frozen=True)
class PublicQueryResult:
    monthly_avg: Optional[float]
    monthly_samples: int
    fipe_price: Optional[float]          # stub (por enquanto None)
    fipe_ref: Optional[str]              # ex: "2026-02"
    store_prices: list[dict[str, Any]]   # lista de lojas com preço


def public_query_prices(
    *,
    region: str,
    capture_month: str,
    brand_id: str,
    model_id: str,
    version_id: Optional[str],
    year_fabrication: Optional[int],
    actor_user_id: Optional[str] = None,
) -> PublicQueryResult:
    """
    Consulta pública:
      - Média mensal (AVG) com base em vehicle_captures no mês selecionado
      - Lista de preços por loja (última capture do mês por loja)
      - FIPE: stub (retorna None até integrar)
    """

    f = validate_public_query_filters(
        region=region,
        capture_month=capture_month,
        brand_id=brand_id,
        model_id=model_id,
        version_id=version_id,
        year_fabrication=year_fabrication,
    )

    public_queries_db.insert_public_query_log(
        brand_id=f.brand_id,
        model_id=f.model_id,
        version_id=f.version_id,
        year_model=f.year_fabrication,
        region=f.region,
        actor_user_id=actor_user_id,
    )

    samples, avg_price = public_queries_db.compute_monthly_avg_and_samples(
        region=f.region,
        capture_month=f.capture_month,
        brand_id=f.brand_id,
        model_id=f.model_id,
        version_id=f.version_id,
        year_fabrication=f.year_fabrication,
    )

    store_prices = public_queries_db.list_store_prices_last_capture_in_month(
        region=f.region,
        capture_month=f.capture_month,
        brand_id=f.brand_id,
        model_id=f.model_id,
        version_id=f.version_id,
        year_fabrication=f.year_fabrication,
    )

    # FIPE (stub) — integra depois
    fipe_price = None
    fipe_ref = None

    return PublicQueryResult(
        monthly_avg=avg_price,
        monthly_samples=samples,
        fipe_price=fipe_price,
        fipe_ref=fipe_ref,
        store_prices=store_prices,
    )