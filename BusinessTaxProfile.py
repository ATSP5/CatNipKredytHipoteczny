from dataclasses import dataclass


@dataclass(frozen=True)
class BusinessTaxProfile:
    """Jak rozlicza się działalność domownika: forma opodatkowania, wariant ZUS, koszty firmy."""

    LUMP_SUM = "ryczałt"
    LINEAR = "liniowy"
    SCALE = "skala"

    FULL_ZUS = "pełny"
    PREFERENTIAL_ZUS = "preferencyjny"
    START_RELIEF = "ulga na start"

    tax_form: str = "ryczałt"
    lump_sum_rate: float = 0.12             # stawka ryczałtu, np. 12% dla usług IT
    zus: str = "pełny"
    monthly_costs: float = 0.0              # koszty działalności (liniowy i skala; ryczałt ich nie odlicza)

    @property
    def label(self) -> str:
        form = ("ryczałt %g%%" % (self.lump_sum_rate * 100) if self.tax_form == self.LUMP_SUM
                else "podatek liniowy 19%" if self.tax_form == self.LINEAR else "skala podatkowa")
        return "%s, ZUS %s" % (form, self.zus)
