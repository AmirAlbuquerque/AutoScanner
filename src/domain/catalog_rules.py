from src.services.auth_service import Actor
from typing import Optional

def ensure_manager(actor: Actor) -> None:
    if actor.role != "GERENTE":
        raise PermissionError("Ação permitida apenas para GERENTE.")

def validate_brand_name(name: str) -> str:
    name = (name or "").strip()
    if len(name) < 1:
        raise ValueError("Nome da marca inválido.")
    return name

def validate_model_name(name: str) -> str:
    name = (name or "").strip()
    if len(name) < 1:
        raise ValueError("Nome do modelo inválido.")
    return name

def validate_version_name(name: str) -> str:
    name = (name or "").strip()
    if len(name) < 1:
        raise ValueError("Nome da versão inválido.")
    return name

def normalize_image_url(image_url: Optional[str]) -> Optional[str]:
    if not image_url:
        return None
    image_url = image_url.strip()
    return image_url or None