from src.services.auth_service import Actor

def ensure_manager(actor: Actor) -> None:
    if actor.role != "GERENTE":
        raise PermissionError("Ação permitida apenas para GERENTE.")
