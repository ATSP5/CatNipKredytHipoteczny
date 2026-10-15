from dataclasses import dataclass
from typing import List, Mapping


@dataclass(frozen=True)
class MortgageParameters:
    """Parametry kredytu na budowę domu, tak jak ustawia je strona raportu."""

    VARIABLE = "zmienna"
    FIXED = "stała"
    ANNUITY = "równe"
    DECREASING = "malejące"

    bank: str = ""
    house_cost: float = 780_000.0
    plot_value: float = 220_000.0
    savings: float = 60_000.0
    years: int = 30
    build_months: int = 18
    tranches: int = 4
    rate_type: str = "zmienna"
    index_name: str = "WIBOR 3M"
    index_rate_pct: float = 3.82
    margin_pct: float = 1.40
    fixed_rate_pct: float = 6.0
    commission_pct: float = 0.0
    bridge_margin_pp: float = 1.0
    bridge_months: int = 4
    low_contribution_pp: float = 0.25
    max_ltv_basic_pct: float = 80.0
    property_insurance_pct: float = 0.08
    installment_type: str = "równe"

    @property
    def amount(self) -> float:
        return max(0.0, self.house_cost - self.savings)

    @property
    def property_value(self) -> float:
        return self.house_cost + self.plot_value

    @property
    def ltv_pct(self) -> float:
        return self.amount / self.property_value * 100 if self.property_value > 0 else float("inf")

    @property
    def months(self) -> int:
        return self.years * 12

    @property
    def nominal_rate_pct(self) -> float:
        return self.fixed_rate_pct if self.rate_type == self.FIXED else self.index_rate_pct + self.margin_pct

    @property
    def commission(self) -> float:
        return self.amount * self.commission_pct / 100

    @property
    def own_contribution(self) -> float:
        return self.plot_value + self.savings

    def validate(self) -> List[str]:
        errors = []
        if self.house_cost <= 0:
            errors.append("Koszt budowy musi być większy od zera.")
        if self.savings < 0 or self.plot_value < 0:
            errors.append("Wartość działki i oszczędności nie mogą być ujemne.")
        if self.house_cost > 0 and self.amount <= 0:
            errors.append("Oszczędności pokrywają całą budowę — kredyt nie jest potrzebny.")
        if not 5 <= self.years <= 35:
            errors.append("Okres kredytu musi mieścić się w 5–35 latach.")
        if not 1 <= self.build_months < self.months:
            errors.append("Czas budowy musi być krótszy niż okres kredytu.")
        if not 1 <= self.tranches <= self.build_months:
            errors.append("Liczba transz musi mieścić się między 1 a liczbą miesięcy budowy.")
        if self.nominal_rate_pct <= 0:
            errors.append("Oprocentowanie musi być dodatnie.")
        return errors

    @classmethod
    def from_state(cls, state: Mapping[str, object]) -> "MortgageParameters":
        defaults = cls()

        def number(name: str, kind=float):
            value = state.get(name, getattr(defaults, name))
            try:
                return kind(float(value)) if kind is int else kind(value)
            except (TypeError, ValueError):
                return getattr(defaults, name)

        def text(name: str) -> str:
            value = state.get(name)
            return str(value) if value not in (None, "") else getattr(defaults, name)

        return cls(
            bank=text("bank"),
            house_cost=number("house_cost"), plot_value=number("plot_value"), savings=number("savings"),
            years=number("years", int), build_months=number("build_months", int), tranches=number("tranches", int),
            rate_type=text("rate_type"), index_name=text("index_name"),
            index_rate_pct=number("index_rate_pct"), margin_pct=number("margin_pct"),
            fixed_rate_pct=number("fixed_rate_pct"), commission_pct=number("commission_pct"),
            bridge_margin_pp=number("bridge_margin_pp"), bridge_months=number("bridge_months", int),
            low_contribution_pp=number("low_contribution_pp"), max_ltv_basic_pct=number("max_ltv_basic_pct"),
            property_insurance_pct=number("property_insurance_pct"),
            installment_type=text("installment_type"),
        )
