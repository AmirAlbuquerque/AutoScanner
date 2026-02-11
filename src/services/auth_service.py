import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from src.common.config import SECRET_KEY, ALGORITHM, ISSUER, TOKEN_TTL_HOURS
from src.common.logging import get_logger
from src.database.infrastructure.connection import get_conn
from src.database.infrastructure.repositories import user_db

logger = get_logger("auth_service")

def _now_utc() -> datetime:
    return datetime.now(timezone.utc)

def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def _verify_password(password: str, hashed: str) -> bool:
    '''
    Essa função verifica se a senha em texto simples corresponde à
    senha hasheada.

    Argumentos:
    password -- A senha em texto simples a ser verificada.
    hashed -- A senha hasheada para comparação.
    Retorna:
    True se a senha corresponder, False caso contrário.
    '''
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            hashed.encode("utf-8")
        )
    except Exception:
        return False

def create_token(user: dict[str, Any]) -> str:
    """JWT com claims essenciais para RBAC."""
    now = _now_utc()
    payload = {
        "sub": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "region": user.get("region"),
        "iss": ISSUER,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=TOKEN_TTL_HOURS)).timestamp()),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> Optional[dict[str, Any]]:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            issuer=ISSUER,
            options={"require": ["exp", "iat", "iss", "sub"]},
        )
        return payload
    except Exception as e:
        logger.info(f"Token inválido/expirado: {e}")
        return None

def login(email: str, password: str) -> tuple[bool, str, Optional[dict[str, Any]]]:
    """Retorna (ok, message, token_payload)."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email.strip().lower(),)
        ).fetchone()

    if not row:
        return False, "Usuário ou senha inválidos.", None
    if int(row["active"]) != 1:
        return False, "Usuário inativo.", None
    if not _verify_password(password, row["password_hash"]):
        return False, "Usuário ou senha inválidos.", None

    user = dict(row)
    token = create_token(user)
    payload = decode_token(token)
    return True, token, payload

# ---------------------------
# RBAC guard (service-level)
# ---------------------------
def _require_admin(actor_payload: dict[str, Any]) -> None:
    if not actor_payload or actor_payload.get("role") != "ADMIN":
        raise PermissionError("Ação permitida apenas para ADMIN.")