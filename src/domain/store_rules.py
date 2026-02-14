from src.services.auth_service import Actor

def ensure_store_submitter(actor: Actor) -> None:
    if actor.role not in ("LOJISTA", "PESQUISADOR"):
        raise PermissionError("Ação permitida apenas para LOJISTA ou PESQUISADOR.")

def ensure_coordinator(actor: Actor) -> None:
    if actor.role != "COORDENADOR":
        raise PermissionError("Ação permitida apenas para COORDENADOR.")

def ensure_same_region(actor: Actor, target_region: str) -> None:
    if not actor.region:
        raise PermissionError("Usuário sem região definida.")
    if actor.region != target_region:
        raise PermissionError("Ação não permitida fora da sua região.")

def ensure_can_approve_store(actor: Actor, store_region: str) -> None:
    ensure_coordinator(actor)
    ensure_same_region(actor, store_region)

def ensure_can_manage_own_store(actor: Actor, store_owner_id: str) -> None:
    if actor.role != "LOJISTA":
        raise PermissionError("Ação permitida apenas para LOJISTA.")
    if actor.id != store_owner_id:
        raise PermissionError("Você só pode gerenciar suas próprias lojas.")