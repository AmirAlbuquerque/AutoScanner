import uuid
from datetime import datetime, timezone
from typing import Any, Optional
from src.database.infrastructure.repositories import user_db
from src.services import auth_service
from src.domain import user_rules
from src.common.logging import get_logger

logger = get_logger("user_service")
ROLES = {"ADMIN", "GERENTE", "COORDENADOR", "PESQUISADOR", "LOJISTA"}

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _get_actor(payload):
    actor = auth_service.require_authenticated(payload)
    return auth_service.require_active_user(actor)
# ---------------------------
# CRUD de usuários (ADMIN)
# ---------------------------
def admin_create_user(
    actor_payload: dict[str, Any],
    name: str,
    email: str,
    role: str,
    region: Optional[str],
    password: str,
    active: int = 1,
) -> str:
    actor = _get_actor(actor_payload)
    user_rules.ensure_admin(actor)

    role = role.strip().upper()
    if role not in ROLES:
        raise ValueError("Role inválido.")
    if len(password) < 6:
        raise ValueError("Senha deve ter pelo menos 6 caracteres.")

    user_id = str(uuid.uuid4())
    email_norm = email.strip().lower()
    pw_hash = auth_service._hash_password(password)

    user_db.create_user(user_id, name.strip(), email_norm, role, region, pw_hash, int(active), _now())

    logger.info(f"[ADMIN_CREATE_USER] actor={actor_payload.get('email')} created={email_norm} role={role}")
    return user_id

def admin_list_users(actor_payload: dict[str, Any]) -> list[dict[str, Any]]:
    actor = _get_actor(actor_payload)
    user_rules.ensure_admin(actor)
    return user_db.list_users()

def admin_get_user(actor_payload: dict[str, Any], user_id: str) -> Optional[dict[str, Any]]:
    actor = _get_actor(actor_payload)
    user_rules.ensure_admin(actor)
    return user_db.get_user(user_id)

def admin_update_user(
    actor_payload: dict[str, Any],
    user_id: str,
    name: str,
    email: str,
    role: str,
    region: Optional[str],
    active: int,
) -> None:
    actor = _get_actor(actor_payload)
    user_rules.ensure_admin(actor)

    role = role.strip().upper()
    if role not in ROLES:
        raise ValueError("Role inválida.")

    email_norm = email.strip().lower()

    user_db.update_user(name, email_norm, role, region, active, user_id)

    logger.info(f"[ADMIN_UPDATE_USER] actor={actor_payload.get('email')} updated={email_norm} role={role} active={active}")

def admin_set_password(
    actor_payload: dict[str, Any],
    user_id: str,
    new_password: str,
) -> None:
    actor = _get_actor(actor_payload)
    user_rules.ensure_admin(actor)
    if len(new_password) < 6:
        raise ValueError("Senha deve ter pelo menos 6 caracteres.")

    pw_hash = auth_service._hash_password(new_password)
    user_db.set_password(pw_hash,user_id)

    logger.info(f"[ADMIN_SET_PASSWORD] actor={actor_payload.get('email')} user_id={user_id}")

def admin_delete_user(actor_payload: dict[str, Any], user_id: str) -> None:
    actor = _get_actor(actor_payload)
    user_rules.ensure_admin(actor)
    user_db.delete_user(user_id)
    logger.info(f"[ADMIN_DELETE_USER] actor={actor_payload.get('email')} user_id={user_id}")