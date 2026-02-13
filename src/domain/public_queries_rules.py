from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass(frozen=True)
class PublicQueryFilters:
    region: str
    capture_month: str  # "YYYY-MM"
    brand_id: str
    model_id: str
    version_id: Optional[str]
    year_fabrication: Optional[int]


def normalize_capture_month(capture_month: str) -> str:
    """
    Normaliza:
      - '2026-2'  -> '2026-02'
      - ' 2026-02 ' -> '2026-02'
    """
    cm = (capture_month or "").strip()
    if len(cm) == 6 and len(cm) >= 6 and cm[4] == "-":
        # YYYY-M -> YYYY-0M
        cm = cm[:5] + "0" + cm[5:]
    return cm


def validate_public_query_filters(
    *,
    region: str,
    capture_month: str,
    brand_id: str,
    model_id: str,
    version_id: Optional[str],
    year_fabrication: Optional[int],
) -> PublicQueryFilters:
    cm = normalize_capture_month(capture_month)

    if not cm or len(cm) != 7 or cm[4] != "-":
        raise ValueError("capture_month inválido. Use YYYY-MM (ex.: 2026-02).")

    reg = (region or "").strip()
    if not reg:
        raise ValueError("Região é obrigatória.")

    if not (brand_id or "").strip():
        raise ValueError("Marca é obrigatória.")
    if not (model_id or "").strip():
        raise ValueError("Modelo é obrigatório.")

    vid = (version_id or "").strip() or None

    yf = None
    if year_fabrication is not None:
        yf = int(year_fabrication)

        current_year = datetime.now().year

        if yf < 1900:
            raise ValueError("Ano de fabricação inválido (mínimo 1900).")

        if yf > current_year:
            raise ValueError(
                f"Ano de fabricação não pode ser maior que o ano atual ({current_year})."
            )

    return PublicQueryFilters(
        region=reg,
        capture_month=cm,
        brand_id=brand_id.strip(),
        model_id=model_id.strip(),
        version_id=vid,
        year_fabrication=yf,
    )