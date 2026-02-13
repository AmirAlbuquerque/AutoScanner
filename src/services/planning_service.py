from datetime import datetime, timezone, date
from typing import Any, Optional

from src.services import auth_service
from src.domain import planning_rules
from src.database.infrastructure.repositories import planning_read_db
from src.database.infrastructure.repositories import weekly_plannings_db
from src.database.infrastructure.repositories import planning_assignments_db
from src.database.infrastructure.repositories import stores_db


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

# Helper
def week_start_monday(d: date) -> str:
    monday = d.fromordinal(d.toordinal() - d.weekday())  # weekday: Mon=0
    return monday.isoformat()

# ---------------------------
# VISUALIZAÇÃO - COORDENADOR
# ---------------------------

def coordinator_list_plannings_overview(actor_payload: dict[str, Any], limit: int = 200) -> list[dict[str, Any]]:
    actor = auth_service.require_authenticated(actor_payload)
    auth_service.require_active_user(actor)
    planning_rules.ensure_coordinator(actor)

    if not actor.region:
        raise ValueError("Coordenador sem região definida.")

    return planning_read_db.list_plannings_summary_by_region(actor.region, limit=limit)


def coordinator_view_planning(actor_payload: dict[str, Any], planning_id: str) -> dict[str, Any]:
    """
    Retorna:
    - header do planejamento
    - lista detalhada de atribuições (store + researcher)
    """
    actor = auth_service.require_authenticated(actor_payload)
    auth_service.require_active_user(actor)
    planning_rules.ensure_coordinator(actor)

    header = planning_read_db.get_planning_header(planning_id)
    if not header:
        raise ValueError("Planejamento não encontrado.")

    planning_rules.ensure_same_region(actor, header["region"])

    assignments = planning_read_db.list_planning_assignments_detailed(planning_id)

    return {
        "planning": header,
        "assignments": assignments,
    }

# ---------------------------
# VISUALIZAÇÃO - PESQUISADOR
# ---------------------------

def researcher_view_current_week(actor_payload: dict[str, Any], today: Optional[date] = None) -> dict[str, Any]:
    """
    Mostra o planejamento da semana atual (por região do pesquisador) e as lojas atribuídas.
    """
    actor = auth_service.require_authenticated(actor_payload)
    auth_service.require_active_user(actor)
    if actor.role != "PESQUISADOR":
        raise PermissionError("Ação permitida apenas para PESQUISADOR.")

    if not actor.region:
        raise ValueError("Pesquisador sem região definida.")

    today = today or date.today()
    ws = week_start_monday(today)

    planning = planning_read_db.find_planning_by_region_week(actor.region, ws)
    if not planning:
        return {
            "planning": None,
            "assignments": [],
            "message": f"Não existe planejamento para {actor.region} na semana iniciando em {ws}."
        }

    tasks = planning_read_db.list_researcher_week_tasks(
        researcher_id=actor.id,
        planning_id=planning["id"],
    )

    return {
        "planning": planning,
        "assignments": tasks,
        "message": None
    }

# ---------------------------
# Weekly Planning CRUD (mínimo)
# ---------------------------

def coordinator_create_planning(actor_payload: dict[str, Any], region: str, week_start: str) -> str:
    actor = auth_service.require_authenticated(actor_payload)
    auth_service.require_active_user(actor)

    planning_rules.ensure_coordinator(actor)
    region = (region or "").strip()
    if not region:
        raise ValueError("Região é obrigatória.")
    planning_rules.ensure_same_region(actor, region)

    week_start = planning_rules.validate_week_start(week_start)

    existing = weekly_plannings_db.get_planning_by_region_week(region, week_start)
    if existing:
        return existing["id"]

    return weekly_plannings_db.create_weekly_planning(
        coordinator_id=actor.id,
        region=region,
        week_start=week_start,
        status="RASCUNHO",
        created_at=_now_iso(),
    )


def coordinator_list_plannings(actor_payload: dict[str, Any], *, status: Optional[str] = None) -> list[dict[str, Any]]:
    actor = auth_service.require_authenticated(actor_payload)
    auth_service.require_active_user(actor)

    planning_rules.ensure_coordinator(actor)

    # coordenador só enxerga a região dele
    return weekly_plannings_db.list_plannings(region=actor.region, status=status)


def coordinator_get_planning(actor_payload: dict[str, Any], planning_id: str) -> dict[str, Any]:
    actor = auth_service.require_authenticated(actor_payload)
    auth_service.require_active_user(actor)

    planning_rules.ensure_coordinator(actor)

    planning = weekly_plannings_db.get_planning(planning_id)
    if not planning:
        raise ValueError("Planejamento não encontrado.")

    planning_rules.ensure_same_region(actor, planning["region"])
    return planning


def coordinator_publish_planning(actor_payload: dict[str, Any], planning_id: str) -> None:
    actor = auth_service.require_authenticated(actor_payload)
    auth_service.require_active_user(actor)

    planning_rules.ensure_coordinator(actor)

    planning = weekly_plannings_db.get_planning(planning_id)
    if not planning:
        raise ValueError("Planejamento não encontrado.")

    planning_rules.ensure_same_region(actor, planning["region"])
    planning_rules.ensure_planning_status_allows_publish(planning["status"])

    assignments = planning_assignments_db.list_assignments_by_planning(planning_id)
    if len(assignments) == 0:
        raise ValueError("Não é possível publicar: planejamento sem atribuições.")

    weekly_plannings_db.set_planning_status(planning_id, "PUBLICADO")


# ---------------------------
# Assignments (Store x Researcher) dentro do planejamento
# ---------------------------

def coordinator_add_assignment(
    actor_payload: dict[str, Any],
    planning_id: str,
    store_id: str,
    researcher_id: str,
) -> str:
    actor = auth_service.require_authenticated(actor_payload)
    auth_service.require_active_user(actor)

    planning_rules.ensure_coordinator(actor)

    planning = weekly_plannings_db.get_planning(planning_id)
    if not planning:
        raise ValueError("Planejamento não encontrado.")
    planning_rules.ensure_same_region(actor, planning["region"])
    planning_rules.ensure_planning_status_allows_edit(planning["status"])

    store = stores_db.get_store_region_and_status(store_id)
    if not store:
        raise ValueError("Loja não encontrada.")

    # Regras de domínio: atribuição só faz sentido se loja é da mesma região do planning
    if store["region"] != planning["region"]:
        raise PermissionError("Loja pertence a outra região. Não pode ser atribuída neste planejamento.")

    # Só atribuir loja aprovada
    if store["status"] != "APROVADA":
        raise ValueError("Só é possível atribuir lojas com status APROVADA.")

    from src.database.infrastructure.repositories import user_db
    u = user_db.get_user_by_id(researcher_id)
    if not u:
        raise ValueError("Pesquisador não encontrado.")
    if u["role"] != "PESQUISADOR":
        raise ValueError("researcher_id não pertence a um usuário PESQUISADOR.")
    if u.get("region") != planning["region"]:
        raise ValueError("Pesquisador não pertence à mesma região do planejamento.")

    if planning_assignments_db.is_assigned(planning_id, store_id, researcher_id):
        raise ValueError("Atribuição já existe.")

    return planning_assignments_db.create_assignment(
        planning_id=planning_id,
        store_id=store_id,
        researcher_id=researcher_id,
    )


def coordinator_remove_assignment(
    actor_payload: dict[str, Any],
    planning_id: str,
    store_id: str,
    researcher_id: str,
) -> None:
    actor = auth_service.require_authenticated(actor_payload)
    auth_service.require_active_user(actor)

    planning_rules.ensure_coordinator(actor)

    planning = weekly_plannings_db.get_planning(planning_id)
    if not planning:
        raise ValueError("Planejamento não encontrado.")
    planning_rules.ensure_same_region(actor, planning["region"])
    planning_rules.ensure_planning_status_allows_edit(planning["status"])

    planning_assignments_db.delete_assignment_by_keys(planning_id, store_id, researcher_id)


def coordinator_list_assignments(actor_payload: dict[str, Any], planning_id: str) -> list[dict[str, Any]]:
    actor = auth_service.require_authenticated(actor_payload)
    auth_service.require_active_user(actor)

    planning_rules.ensure_coordinator(actor)

    planning = weekly_plannings_db.get_planning(planning_id)
    if not planning:
        raise ValueError("Planejamento não encontrado.")
    planning_rules.ensure_same_region(actor, planning["region"])

    return planning_assignments_db.list_assignments_by_planning(planning_id)