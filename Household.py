from dataclasses import dataclass
from typing import Tuple

from ExpenseItem import ExpenseItem
from HouseholdBudget import HouseholdBudget
from HouseholdMember import HouseholdMember


@dataclass(frozen=True)
class Household:
    """Gospodarstwo domowe z pliku Excel: domownicy, ich dochody i wydatki."""

    source: str                                    # nazwa pliku, z którego wczytano dane
    members: Tuple[HouseholdMember, ...]
    other_income: Tuple[Tuple[str, float], ...]    # (źródło, średnio miesięcznie) — bank tego nie wlicza
    expenses: Tuple[ExpenseItem, ...]

    def budget(self) -> HouseholdBudget:
        adults = [m for m in self.members if m.is_adult]
        return HouseholdBudget(
            adults=len(adults),
            children=len(self.members) - len(adults),
            incomes=tuple((m.name, round(m.bank_income, 2)) for m in adults),
            other_income=sum(amount for _, amount in self.other_income),
            expenses=self.expenses,
        )
