from dataclasses import dataclass, replace
from typing import Mapping, Tuple

from ExpenseItem import ExpenseItem


@dataclass(frozen=True)
class HouseholdBudget:
    """Miesięczny budżet rodziny, którym liczy się zdolność: dochody uznane przez bank i wydatki."""

    adults: int
    children: int
    incomes: Tuple[Tuple[str, float], ...]      # (osoba, dochód netto uznany przez bank)
    other_income: float                         # dochód, którego bank nie wlicza (np. 800+)
    expenses: Tuple[ExpenseItem, ...]

    @property
    def total_income(self) -> float:
        return sum(amount for _, amount in self.incomes)

    @property
    def living_costs(self) -> float:
        return self._sum(ExpenseItem.LIVING)

    @property
    def obligations(self) -> float:
        return self._sum(ExpenseItem.OBLIGATION)

    @property
    def other_costs(self) -> float:
        return self._sum(ExpenseItem.OTHER)

    def with_amounts(self, incomes: Mapping[str, float], expenses: Mapping[str, float]) -> "HouseholdBudget":
        """Ten sam budżet z kwotami poprawionymi ręcznie (po nazwie osoby i wydatku)."""
        return replace(
            self,
            incomes=tuple((name, float(incomes.get(name, amount))) for name, amount in self.incomes),
            expenses=tuple(replace(item, monthly=float(expenses.get(item.name, item.monthly)))
                           for item in self.expenses),
        )

    def _sum(self, kind: str) -> float:
        return sum(item.monthly for item in self.expenses if item.kind == kind)
