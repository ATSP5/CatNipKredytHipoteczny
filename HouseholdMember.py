from dataclasses import dataclass
from typing import Optional, Tuple

from BusinessIncomeMonth import BusinessIncomeMonth
from BusinessTaxProfile import BusinessTaxProfile


@dataclass(frozen=True)
class HouseholdMember:
    """Domownik z arkusza Domownicy i jego dochody netto z arkusza Dochody (od najstarszego miesiąca)."""

    name: str
    role: str
    income_type: str
    seniority_months: int
    monthly_net: Tuple[float, ...]
    tax_profile: Optional[BusinessTaxProfile] = None      # gdy dochód policzono z faktur
    business: Tuple[BusinessIncomeMonth, ...] = ()        # rozbicie faktur na ZUS, zdrowotną, PIT

    @property
    def is_adult(self) -> bool:
        return self.role.strip().lower().startswith("doros")

    @property
    def months_counted_by_bank(self) -> int:
        kind = self.income_type.lower()
        if not self.monthly_net or kind.startswith("brak"):
            return 0
        return 12 if ("działalność" in kind or "b2b" in kind) else 6

    @property
    def bank_income(self) -> float:
        """Średni dochód netto z okresu, który bierze bank: 6 miesięcy z umowy, 12 z działalności."""
        months = self.months_counted_by_bank
        recent = self.monthly_net[-months:] if months else ()
        return sum(recent) / len(recent) if recent else 0.0
