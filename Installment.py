from dataclasses import dataclass


@dataclass(frozen=True)
class Installment:
    """Jeden miesiąc kredytu: wypłacona transza, rata i saldo po niej."""

    number: int
    phase: str              # "budowa" albo "spłata"
    disbursed: float
    principal: float
    interest: float
    insurance: float
    rate_pct: float
    balance_after: float

    @property
    def payment(self) -> float:
        return self.principal + self.interest

    @property
    def total(self) -> float:
        return self.payment + self.insurance
