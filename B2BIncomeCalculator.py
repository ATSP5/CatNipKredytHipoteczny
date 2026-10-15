from typing import List, Sequence

from BusinessIncomeMonth import BusinessIncomeMonth
from BusinessTaxProfile import BusinessTaxProfile
from TaxRules import TaxRules


class B2BIncomeCalculator:
    """Zamienia kwoty z faktur (netto bez VAT) na dochód na rękę: koszty, ZUS, zdrowotna i PIT."""

    def __init__(self, rules: TaxRules = TaxRules()):
        self.rules = rules

    def b2b_income(self) -> "B2BIncomeCalculator":
        return self

    def months(self, invoiced: Sequence[float], profile: BusinessTaxProfile) -> List[BusinessIncomeMonth]:
        """Miesiąc po miesiącu; roczne progi (ryczałt, skala) liczone z rocznej sumy faktur."""
        social = self._social(profile)
        annual_revenue = sum(invoiced) * 12 / max(len(invoiced), 1)
        if profile.tax_form == BusinessTaxProfile.LUMP_SUM:
            return [self._lump_sum(amount, social, annual_revenue, profile) for amount in invoiced]
        if profile.tax_form == BusinessTaxProfile.LINEAR:
            return [self._linear(amount, social, profile) for amount in invoiced]
        return self._scale(invoiced, social, profile)

    def _social(self, profile: BusinessTaxProfile) -> float:
        r = self.rules
        return {BusinessTaxProfile.PREFERENTIAL_ZUS: r.social_preferential,
                BusinessTaxProfile.START_RELIEF: r.social_start_relief}.get(profile.zus, r.social_full)

    def _lump_sum(self, amount: float, social: float, annual_revenue: float,
                  profile: BusinessTaxProfile) -> BusinessIncomeMonth:
        r = self.rules
        health = (r.health_lump_low if annual_revenue <= r.lump_low_limit
                  else r.health_lump_mid if annual_revenue <= r.lump_high_limit else r.health_lump_high)
        # Ryczałt: od przychodu odlicza się składki społeczne i połowę zapłaconej zdrowotnej.
        tax = max(0.0, amount - social - 0.5 * health) * profile.lump_sum_rate
        return BusinessIncomeMonth(amount, 0.0, social, health, round(tax))

    def _linear(self, amount: float, social: float, profile: BusinessTaxProfile) -> BusinessIncomeMonth:
        r = self.rules
        income = max(0.0, amount - profile.monthly_costs - social)
        health = max(r.health_min, income * r.health_rate_linear)
        deductible = min(health, r.health_linear_deduction_cap / 12)
        tax = max(0.0, income - deductible) * r.linear_rate
        return BusinessIncomeMonth(amount, profile.monthly_costs, social, health, round(tax))

    def _scale(self, invoiced: Sequence[float], social: float,
               profile: BusinessTaxProfile) -> List[BusinessIncomeMonth]:
        """Skala jest progresywna rocznie: podatek roczny rozłożony na miesiące proporcjonalnie do dochodu."""
        r = self.rules
        incomes = [max(0.0, amount - profile.monthly_costs - social) for amount in invoiced]
        annual_income = sum(incomes) * 12 / max(len(incomes), 1)
        if annual_income <= r.scale_threshold:
            annual_tax = max(0.0, annual_income * r.scale_low_rate - r.scale_tax_reduction)
        else:
            annual_tax = (r.scale_threshold * r.scale_low_rate - r.scale_tax_reduction
                          + (annual_income - r.scale_threshold) * r.scale_high_rate)
        share = annual_tax / annual_income if annual_income > 0 else 0.0
        return [BusinessIncomeMonth(amount, profile.monthly_costs, social,
                                    max(r.health_min, income * r.health_rate_scale), round(income * share))
                for amount, income in zip(invoiced, incomes)]
