from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class BankOffer:
    """Oferta kredytu hipotecznego jednego banku z arkusza Oferty."""

    bank: str
    index_name: str
    margin_pct: float
    margin_high_ltv_pct: Optional[float]     # marża przy LTV > 80%; None — dopłata z arkusza Rynek
    commission_pct: float
    bridge_margin_pp: float
    property_insurance_pct: float
    max_ltv_pct: float
    notes: str
    source: str
    as_of: str
