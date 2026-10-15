from dataclasses import dataclass, replace
from typing import Dict, Optional

from NbpRate import NbpRate


@dataclass(frozen=True)
class MarketRates:
    """Wskaźniki (WIBOR, POLSTR) i reguły oceny zdolności z arkusza Rynek, uaktualnione stopą NBP z internetu."""

    indices: Dict[str, float]           # nazwa wskaźnika → wartość [%] z dnia notowania
    index_dates: Dict[str, str]         # nazwa wskaźnika → data / opis notowania
    nbp_ref_at_quotes: float
    nbp_ref_now: float
    nbp_date: str
    nbp_live: bool
    buffer_variable_pp: float
    buffer_fixed_pp: float
    dsti_low_pct: float
    dsti_high_pct: float
    dsti_threshold: float
    min_cost_adult: float
    min_cost_child: float
    max_ltv_basic_pct: float
    low_contribution_pp: float

    @property
    def nbp_shift_pp(self) -> float:
        return self.nbp_ref_now - self.nbp_ref_at_quotes

    def index_rate(self, index_name: str) -> float:
        """Wskaźnik z pliku przesunięty o zmianę stopy NBP od dnia notowania."""
        key = index_name.strip().upper()
        base = self.indices.get(key, next(iter(self.indices.values()), 0.0))
        return round(base + self.nbp_shift_pp, 2)

    def updated_with(self, nbp: Optional[NbpRate]) -> "MarketRates":
        if nbp is None:
            return replace(self, nbp_live=False)
        return replace(self, nbp_ref_now=nbp.rate_pct, nbp_date=nbp.valid_from, nbp_live=True)
