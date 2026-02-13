import re
from datetime import date
from typing import Iterable, Any
from src.services.auth_service import Actor

_MONTH_RE = re.compile(r"^\d{4}-\d{2}$")

def ensure_researcher(actor: Actor) -> None:
    if actor.role != "PESQUISADOR":
        raise PermissionError("Ação permitida apenas para PESQUISADOR.")
    
def validate_capture_month(capture_month: str) -> str:
    cm = (capture_month or "").strip()
    if not _MONTH_RE.match(cm):
        raise ValueError("capture_month deve estar no formato YYYY-MM.")
    # valida mês 01-12
    year = int(cm[0:4])
    month = int(cm[5:7])
    if month < 1 or month > 12:
        raise ValueError("Mês inválido em capture_month.")
    if year < 1990 or year > date.today().year + 1:
        raise ValueError("Ano inválido em capture_month.")
    return cm

def validate_vehicle_item(item: dict[str, Any]) -> dict[str, Any]:
    """
    Espera chaves:
      brand_id, model_id, version_id, year_fabrication, price
    """
    required = ["brand_id", "model_id", "version_id", "year_fabrication", "price"]
    for k in required:
        if k not in item:
            raise ValueError(f"Campo obrigatório ausente: {k}")

    year = int(item["year_fabrication"])
    current_year = date.today().year
    if year < 1960 or year > current_year + 1:
        raise ValueError("year_fabrication fora do intervalo esperado.")

    price = float(item["price"])
    if price < 0:
        raise ValueError("price não pode ser negativo.")

    # normaliza
    item = dict(item)
    item["year_fabrication"] = year
    item["price"] = price
    item["brand_id"] = str(item["brand_id"]).strip()
    item["model_id"] = str(item["model_id"]).strip()
    item["version_id"] = str(item["version_id"]).strip()
    return item

def validate_vehicle_items(items: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    items = list(items or [])
    if not items:
        raise ValueError("A captura deve conter ao menos 1 veículo.")
    return [validate_vehicle_item(i) for i in items]

def ensure_can_capture(
    actor: Actor,
    store_status: str,
    assigned_to_researcher: bool,
    planning_status: str,
) -> None:
    ensure_researcher(actor)

    if store_status != "APROVADA":
        raise PermissionError("Captura permitida apenas em loja APROVADA.")

    if planning_status != "PUBLICADO":
        raise PermissionError("Captura permitida apenas quando o planejamento estiver PUBLICADO.")

    if assigned_to_researcher is not None and assigned_to_researcher is False:
        raise PermissionError("Loja não atribuída a você no planejamento da semana.")