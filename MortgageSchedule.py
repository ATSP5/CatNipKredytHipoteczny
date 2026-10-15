from dataclasses import dataclass
from typing import List, Tuple

from Installment import Installment
from MortgageParameters import MortgageParameters


@dataclass(frozen=True)
class MortgageSchedule:
    """Harmonogram kredytu: transze w czasie budowy, potem spłata, plus RRSO."""

    BUILD = "budowa"
    REPAYMENT = "spłata"

    parameters: MortgageParameters
    installments: List[Installment]
    rrso_pct: float

    @property
    def total_interest(self) -> float:
        return sum(i.interest for i in self.installments)

    @property
    def total_insurance(self) -> float:
        return sum(i.insurance for i in self.installments)

    @property
    def total_cost(self) -> float:
        return self.total_interest + self.total_insurance + self.parameters.commission

    @property
    def total_to_pay(self) -> float:
        return self.parameters.amount + self.total_cost

    @property
    def first_full_payment(self) -> float:
        """Pierwsza rata po zakończeniu budowy — ta, którą rodzina płaci na co dzień."""
        return next((i.total for i in self.installments if i.phase == self.REPAYMENT), 0.0)

    @property
    def max_payment(self) -> float:
        return max((i.total for i in self.installments), default=0.0)

    @property
    def max_build_payment(self) -> float:
        return max((i.total for i in self.installments if i.phase == self.BUILD), default=0.0)

    def yearly(self) -> List[Tuple[int, float, float, float, float]]:
        """(rok, kapitał, odsetki, ubezpieczenie, saldo na koniec roku) — do wykresów i podsumowań."""
        years = []
        for start in range(0, len(self.installments), 12):
            chunk = self.installments[start:start + 12]
            years.append((start // 12 + 1, sum(i.principal for i in chunk), sum(i.interest for i in chunk),
                          sum(i.insurance for i in chunk), chunk[-1].balance_after))
        return years
