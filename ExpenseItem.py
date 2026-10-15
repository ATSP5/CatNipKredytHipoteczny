from dataclasses import dataclass


@dataclass(frozen=True)
class ExpenseItem:
    """Miesięczny wydatek rodziny. kind: koszty życia, zobowiązanie (rata, limit karty) albo inne."""

    LIVING = "koszty życia"
    OBLIGATION = "zobowiązanie"
    OTHER = "inne"

    name: str
    monthly: float
    kind: str
