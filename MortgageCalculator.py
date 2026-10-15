from dataclasses import replace
from typing import List, Optional, Tuple

from BankOffer import BankOffer
from ConstructionProject import ConstructionProject
from CreditAssessment import CreditAssessment
from CreditAssessor import CreditAssessor
from Household import Household
from HouseholdBudget import HouseholdBudget
from MarketRates import MarketRates
from MortgageParameters import MortgageParameters
from MortgageSchedule import MortgageSchedule
from NbpRate import NbpRate
from ScheduleBuilder import ScheduleBuilder


class MortgageCalculator:
    """Łączy dane rodziny, plan budowy, oferty banków i stawki rynkowe w jedno narzędzie dla raportu."""

    def __init__(self, household: Household, project: ConstructionProject, offers: List[BankOffer],
                 market: MarketRates, reference_rate: Optional[NbpRate], builder: ScheduleBuilder,
                 assessor: CreditAssessor):
        self.household = household
        self.project = project
        self.offers = list(offers)
        self.rates = market.updated_with(reference_rate)
        self.builder = builder
        self.assessor = assessor

    def calculator(self) -> "MortgageCalculator":
        return self

    def base_budget(self) -> HouseholdBudget:
        return self.household.budget()

    def project_parameters(self) -> MortgageParameters:
        p = self.project
        return MortgageParameters(house_cost=p.house_cost, plot_value=p.plot_value, savings=p.savings,
                                  years=p.years, build_months=p.build_months, tranches=p.tranches)

    def parameters_for(self, offer: BankOffer, base: MortgageParameters) -> MortgageParameters:
        """Parametry base z oprocentowaniem, prowizją i opłatami banku offer (stopa zmienna)."""
        return replace(base, bank=offer.bank, rate_type=MortgageParameters.VARIABLE, index_name=offer.index_name,
                       index_rate_pct=self.rates.index_rate(offer.index_name), margin_pct=offer.margin_pct,
                       commission_pct=offer.commission_pct, bridge_margin_pp=offer.bridge_margin_pp,
                       property_insurance_pct=offer.property_insurance_pct,
                       low_contribution_pp=(offer.margin_high_ltv_pct - offer.margin_pct
                                            if offer.margin_high_ltv_pct is not None
                                            else self.rates.low_contribution_pp),
                       max_ltv_basic_pct=self.rates.max_ltv_basic_pct)

    def compare(self, base: MortgageParameters) -> List[Tuple[BankOffer, MortgageSchedule]]:
        """Każda oferta policzona dla tej samej budowy i okresu, od najtańszej (całkowity koszt)."""
        results = [(offer, self.schedule(self.parameters_for(offer, base))) for offer in self.offers]
        return sorted(results, key=lambda pair: pair[1].total_cost)

    def best_offer(self) -> BankOffer:
        return self.compare(self.project_parameters())[0][0]

    def default_parameters(self) -> MortgageParameters:
        return self.parameters_for(self.best_offer(), self.project_parameters())

    def offer(self, bank: str) -> Optional[BankOffer]:
        return next((o for o in self.offers if o.bank == bank), None)

    def schedule(self, parameters: MortgageParameters) -> MortgageSchedule:
        return self.builder.build(parameters)

    def assess(self, parameters: MortgageParameters, budget: HouseholdBudget,
               schedule: MortgageSchedule) -> CreditAssessment:
        offer = self.offer(parameters.bank)
        return self.assessor.assess(parameters, budget, schedule, self.rates, offer.max_ltv_pct if offer else 90.0)
