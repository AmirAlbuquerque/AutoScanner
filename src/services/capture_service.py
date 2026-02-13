from __future__ import annotations

from datetime import datetime, timezone, date
from typing import Any

from src.services import auth_service
from src.domain import capture_rules
from src.database.infrastructure.repositories import stores_db, weekly_plannings_db, planning_assignments_db, captures_db, vehicle_captures_db


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def week_start_monday(d: date) -> str:
    monday = d.fromordinal(d.toordinal() - d.weekday())  # Monday=0
    return monday.isoformat()

def create_capture_with_vehicles(
    actor_payload: dict[str, Any],
    *,
    store_id: str,
    capture_month: str,
    vehicles: list[dict[str, Any]],
    capture_date_iso: str | None = None,
) -> dict[str, Any]:
    """
    Cria 1 'capture' (visita) e N 'vehicle_captures' associados.

    - capture_month: 'YYYY-MM' (competência)
    - capture_date_iso: timestamp ISO; se None usa now()
    - vehicles: lista de itens com brand_id, model_id, version_id, year_fabrication, price
    """
    actor = auth_service.require_authenticated(actor_payload)
    auth_service.require_active_user(actor)
    capture_rules.ensure_researcher(actor)

    capture_month = capture_rules.validate_capture_month(capture_month)
    vehicles = capture_rules.validate_vehicle_items(vehicles)

    store = stores_db.get_store_region_and_status(store_id)
    if not store:
        raise ValueError("Loja não encontrada.")

    # data da captura
    capture_dt_iso = capture_date_iso or _now_iso()

    # calcula week_start pela data da captura
    # (usa a data local do timestamp ISO — suficiente para seu caso)
    d = datetime.fromisoformat(capture_dt_iso.replace("Z", "+00:00")).date()
    ws = week_start_monday(d)

    # encontra o planejamento da semana para a região da loja
    planning = weekly_plannings_db.get_planning_by_region_week(store["region"], ws)

    # valida atribuição
    assigned = planning_assignments_db.is_assigned(planning["id"], store_id, actor.id)

    capture_rules.ensure_can_capture(
        actor=actor,
        store_status=store["status"],
        assigned_to_researcher=assigned,
        planning_status=planning["status"],
    )

    # persiste
    created_at = _now_iso()
    capture_id = captures_db.create_capture(
        store_id=store_id,
        researcher_id=actor.id,
        capture_date=capture_dt_iso,
        capture_month=capture_month,
        created_at=created_at,
    )

    n = vehicle_captures_db.bulk_create_vehicle_captures(
        capture_id=capture_id,
        items=vehicles,
        created_at=created_at,
    )

    return {
        "capture_id": capture_id,
        "planning_id": planning["id"],
        "week_start": ws,
        "store_id": store_id,
        "capture_month": capture_month,
        "vehicles_inserted": n,
    }