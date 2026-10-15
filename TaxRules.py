from dataclasses import dataclass


@dataclass(frozen=True)
class TaxRules:
    """Stawki ZUS, składki zdrowotnej i PIT dla działalności gospodarczej — wartości na 2026 r."""

    social_full: float = 1926.76            # pełny ZUS: emerytalna, rentowa, chorobowa, wypadkowa, Fundusz Pracy (podstawa 5 652 zł)
    social_preferential: float = 456.18     # preferencyjny ZUS (podstawa 1 441,80 zł), bez Funduszu Pracy
    social_start_relief: float = 0.0        # ulga na start: pierwsze 6 miesięcy bez składek społecznych
    health_min: float = 432.54              # minimalna składka zdrowotna (skala, liniowy) — 9% płacy minimalnej 4 806 zł
    health_rate_scale: float = 0.09         # skala podatkowa: 9% dochodu
    health_rate_linear: float = 0.049       # podatek liniowy: 4,9% dochodu
    health_linear_deduction_cap: float = 14100.0   # roczny limit odliczenia zdrowotnej od dochodu (liniowy)
    health_lump_low: float = 498.35         # ryczałt, przychód roczny do 60 000 zł
    health_lump_mid: float = 830.58         # ryczałt, przychód 60 000–300 000 zł
    health_lump_high: float = 1495.04       # ryczałt, przychód powyżej 300 000 zł
    lump_low_limit: float = 60000.0
    lump_high_limit: float = 300000.0
    linear_rate: float = 0.19
    scale_low_rate: float = 0.12
    scale_high_rate: float = 0.32
    scale_threshold: float = 120000.0
    scale_tax_reduction: float = 3600.0     # kwota zmniejszająca podatek (kwota wolna 30 000 zł)
    source: str = "ZUS 2026: podstawa 5 652 zł (60% prognozowanego wynagrodzenia 9 420 zł); zdrowotna 2026: infakt.pl"
