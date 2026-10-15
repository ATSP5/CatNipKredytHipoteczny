from dataclasses import dataclass


@dataclass(frozen=True)
class ConstructionProject:
    """Budowa domu z arkusza Inwestycja."""

    house_cost: float
    plot_value: float
    savings: float
    cash_reserve: float
    years: int
    build_months: int
    tranches: int

    @property
    def property_value(self) -> float:
        return self.house_cost + self.plot_value

    @property
    def loan_needed(self) -> float:
        return max(0.0, self.house_cost - self.savings)
