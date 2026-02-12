from __future__ import annotations
from typing import Optional
from src.services.auth_service import Actor

def ensure_researcher(actor: Actor) -> None:
    if actor.role != "PESQUISADOR":
        raise PermissionError("Ação permitida apenas para PESQUISADOR.")

def ensure_can_capture(
    actor: Actor,
    store_status: str,
    assigned_to_researcher: Optional[bool] = None,
) -> None:
    ensure_researcher(actor)

    if store_status != "APROVADA":
        raise PermissionError("Captura permitida apenas em loja APROVADA.")

    if assigned_to_researcher is not None and assigned_to_researcher is False:
        raise PermissionError("Loja não atribuída a você no planejamento da semana.")