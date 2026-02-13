import re
from datetime import date
from typing import Optional

from src.services.auth_service import Actor

_WEEK_START_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

def ensure_coordinator(actor: Actor) -> None:
    if actor.role != "COORDENADOR":
        raise PermissionError("Ação permitida apenas para COORDENADOR.")

def ensure_same_region(actor: Actor, region: str) -> None:
    if not actor.region:
        raise PermissionError("Usuário sem região definida.")
    if actor.region != region:
        raise PermissionError("Ação não permitida fora da sua região.")

def validate_week_start(week_start: str) -> str:
    """
    Regra recomendada: week_start no formato YYYY-MM-DD.
    Exigir segunda-feira (weekday == 0).
    """
    week_start = (week_start or "").strip()
    if not _WEEK_START_RE.match(week_start):
        raise ValueError("week_start deve estar no formato YYYY-MM-DD.")

    y, m, d = map(int, week_start.split("-"))
    dt = date(y, m, d)

    if dt.weekday() != 0:
        raise ValueError("week_start deve ser uma segunda-feira.")

    return week_start

def ensure_planning_status_allows_edit(status: str) -> None:
    """
    Regra: enquanto RASCUNHO pode editar assignments.
    Depois que PUBLICADO, não permite mudanças.
    """
    if status != "RASCUNHO":
        raise PermissionError("Planejamento já publicado; não é permitido alterar atribuições.")

def ensure_planning_status_allows_publish(status: str) -> None:
    if status != "RASCUNHO":
        raise PermissionError("Apenas planejamentos em RASCUNHO podem ser publicados.")