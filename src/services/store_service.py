from typing import Any
from src.services import auth_service
from src.domain.store_rules import (
    ensure_store_submitter,
    ensure_can_approve_store,
)
from src.database.infrastructure.repositories import stores_db

def create_store(actor_payload: dict[str, Any], store_in: dict[str, Any]) -> str:
    actor = auth_service.require_authenticated(actor_payload)
    auth_service.require_active_user(actor)
    ensure_store_submitter(actor)
    return stores_db.create_store(created_by=actor.id, **store_in)  # status=PENDENTE

def approve_store(actor_payload: dict[str, Any], store_id: str) -> None:
    actor = auth_service.require_authenticated(actor_payload)
    auth_service.require_active_user(actor)

    store = stores_db.get_store(store_id)  # precisa de region
    ensure_can_approve_store(actor, store["region"])

    stores_db.approve_store(store_id, approved_by=actor.id)