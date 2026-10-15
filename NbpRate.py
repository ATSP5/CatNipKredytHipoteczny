from dataclasses import dataclass


@dataclass(frozen=True)
class NbpRate:
    """Stopa referencyjna NBP pobrana z serwisu NBP."""

    rate_pct: float
    valid_from: str
    published: str
