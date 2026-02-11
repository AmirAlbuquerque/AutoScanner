from src.services.auth_service import Actor

def ensure_admin(actor: Actor) -> None:
    if actor.role != "ADMIN":
        raise PermissionError("Ação permitida apenas para ADMIN.")
