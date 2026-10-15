from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class CreditAssessment:
    """Ocena zdolności kredytowej po regułach Rekomendacji S: DSTI przy stopie z buforem i LTV."""

    income: float
    living_costs: float
    obligations: float
    dsti_limit_pct: float
    stress_rate_pct: float
    stress_payment: float
    dsti_pct: float
    max_payment: float
    max_amount: float
    ltv_pct: float
    max_ltv_pct: float
    free_cash_build: float      # wolne środki w czasie budowy (z najmem, najwyższa rata budowy)
    free_cash: float            # wolne środki po przeprowadzce (pierwsza pełna rata)
    problems: List[str]         # to, przez co bank odmówi
    warnings: List[str]         # to, co zagraża budżetowi rodziny

    @property
    def passes(self) -> bool:
        return not self.problems
