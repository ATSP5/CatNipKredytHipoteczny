from dataclasses import dataclass


@dataclass(frozen=True)
class BusinessIncomeMonth:
    """Jeden miesiąc działalności: kwota z faktur i to, co z niej zostaje po ZUS, zdrowotnej i PIT."""

    invoiced: float          # faktury netto (bez VAT)
    costs: float             # koszty działalności
    social: float            # ZUS społeczny
    health: float            # składka zdrowotna
    tax: float               # PIT (ryczałt, liniowy albo skala)

    @property
    def net(self) -> float:
        return self.invoiced - self.costs - self.social - self.health - self.tax
