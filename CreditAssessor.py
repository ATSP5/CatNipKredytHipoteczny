from CreditAssessment import CreditAssessment
from HouseholdBudget import HouseholdBudget
from MarketRates import MarketRates
from MortgageParameters import MortgageParameters
from MortgageSchedule import MortgageSchedule
from PlnFormat import PlnFormat


class CreditAssessor:
    """Ocenia zdolność jak bank: rata przy stopie z buforem KNF, limit DSTI, minimalne koszty życia, LTV."""

    def __init__(self, formatter: PlnFormat):
        self.formatter = formatter

    def assessor(self) -> "CreditAssessor":
        return self

    def assess(self, p: MortgageParameters, budget: HouseholdBudget, schedule: MortgageSchedule,
               rates: MarketRates, max_ltv_pct: float = 90.0) -> CreditAssessment:
        r = rates
        f = self.formatter
        income = budget.total_income
        living = max(budget.living_costs, budget.adults * r.min_cost_adult + budget.children * r.min_cost_child)
        obligations = budget.obligations
        buffer = r.buffer_fixed_pp if p.rate_type == MortgageParameters.FIXED else r.buffer_variable_pp
        stress_rate = p.nominal_rate_pct + buffer
        months = p.months - p.build_months
        stress_payment = self.payment(p.amount, stress_rate, months, p.installment_type)
        dsti_limit = r.dsti_high_pct if income / max(budget.adults, 1) > r.dsti_threshold else r.dsti_low_pct
        dsti = (stress_payment + obligations) / income * 100 if income > 0 else float("inf")
        max_payment = max(0.0, min(income * dsti_limit / 100 - obligations, income - living - obligations))
        max_amount = self.amount_for(max_payment, stress_rate, months, p.installment_type)
        free_cash_build = (income + budget.other_income - living - obligations - budget.other_costs
                           - schedule.max_build_payment)
        free_cash = income + budget.other_income - living - obligations - schedule.first_full_payment

        problems = []
        if p.amount > max_amount:
            problems.append("Kwota kredytu %s przekracza zdolność kredytową %s (rata przy stopie %s z buforem %s pp "
                            "to %s, DSTI %s przy limicie %s)." % (
                                f.zl(p.amount), f.zl(max_amount), f.pct(stress_rate),
                                f.num(buffer, 1), f.zl(stress_payment), f.pct(dsti, 1),
                                f.pct(dsti_limit, 0)))
        if p.ltv_pct > max_ltv_pct:
            problems.append("LTV %s przekracza maksimum banku %s — potrzeba %s więcej wkładu własnego." % (
                f.pct(p.ltv_pct, 1), f.pct(max_ltv_pct, 0),
                f.zl(p.amount - p.property_value * max_ltv_pct / 100)))
        warnings = []
        if p.ltv_pct > p.max_ltv_basic_pct:
            warnings.append("LTV powyżej %s — bank doliczy %s pp marży za niski wkład, dopóki saldo nie spadnie "
                            "poniżej %s wartości domu." % (f.pct(p.max_ltv_basic_pct, 0),
                                                           f.num(p.low_contribution_pp, 2),
                                                           f.pct(p.max_ltv_basic_pct, 0)))
        if free_cash_build < 0:
            warnings.append("W czasie budowy (z najmem) budżet rodziny jest na minusie o %s miesięcznie."
                            % f.zl(-free_cash_build))
        if free_cash < 0:
            warnings.append("Po przeprowadzce rata nie mieści się w budżecie — brakuje %s miesięcznie."
                            % f.zl(-free_cash))
        return CreditAssessment(
            income=income, living_costs=living, obligations=obligations, dsti_limit_pct=dsti_limit,
            stress_rate_pct=stress_rate, stress_payment=stress_payment, dsti_pct=dsti, max_payment=max_payment,
            max_amount=max_amount, ltv_pct=p.ltv_pct, max_ltv_pct=max_ltv_pct, free_cash_build=free_cash_build,
            free_cash=free_cash, problems=problems, warnings=warnings)

    @staticmethod
    def payment(amount: float, rate_pct: float, months: int, installment_type: str) -> float:
        r = rate_pct / 100 / 12
        if installment_type == MortgageParameters.DECREASING:
            return amount / months + amount * r
        return amount * r / (1 - (1 + r) ** -months) if r > 0 else amount / months

    @staticmethod
    def amount_for(payment: float, rate_pct: float, months: int, installment_type: str) -> float:
        """Największa kwota, której rata przy danej stopie nie przekracza payment."""
        r = rate_pct / 100 / 12
        if installment_type == MortgageParameters.DECREASING:
            return payment / (1 / months + r)
        return payment * (1 - (1 + r) ** -months) / r if r > 0 else payment * months
