from typing import Dict, List

from Installment import Installment
from MortgageParameters import MortgageParameters
from MortgageSchedule import MortgageSchedule


class ScheduleBuilder:
    """Liczy harmonogram kredytu na budowę: transze i same odsetki w czasie budowy, potem spłata."""

    RRSO_ITERATIONS = 60

    def builder(self) -> "ScheduleBuilder":
        return self

    def build(self, p: MortgageParameters) -> MortgageSchedule:
        tranches = self.tranche_plan(p)
        insurance = p.property_value * p.property_insurance_pct / 100 / 12
        repayment_months = p.months - p.build_months
        level_principal = p.amount / repayment_months
        balance = 0.0
        installments: List[Installment] = []
        for month in range(1, p.months + 1):
            disbursed = tranches.get(month, 0.0)
            balance += disbursed
            rate_pct = self.rate_pct(p, month, balance)
            monthly_rate = rate_pct / 100 / 12
            interest = balance * monthly_rate
            if month <= p.build_months:
                principal, phase = 0.0, MortgageSchedule.BUILD
            else:
                phase = MortgageSchedule.REPAYMENT
                if month == p.months:
                    principal = balance
                elif p.installment_type == MortgageParameters.DECREASING:
                    principal = min(level_principal, balance)
                else:
                    principal = self.annuity(balance, monthly_rate, p.months - month + 1) - interest
            balance -= principal
            installments.append(Installment(month, phase, disbursed, principal, interest, insurance, rate_pct,
                                            max(balance, 0.0)))
        return MortgageSchedule(p, installments, self.rrso_pct(p, installments))

    @staticmethod
    def tranche_plan(p: MortgageParameters) -> Dict[int, float]:
        """Miesiąc wypłaty → kwota: transze w równych odstępach w czasie budowy, pierwsza w 1. miesiącu."""
        count = max(1, min(p.tranches, p.build_months))
        plan: Dict[int, float] = {}
        for k in range(count):
            month = 1 + (k * p.build_months) // count
            plan[month] = plan.get(month, 0.0) + p.amount / count
        return plan

    @staticmethod
    def rate_pct(p: MortgageParameters, month: int, balance: float) -> float:
        """Oprocentowanie w danym miesiącu: bazowe + marża pomostowa do wpisu hipoteki + niski wkład."""
        rate = p.nominal_rate_pct
        if month <= p.bridge_months:
            rate += p.bridge_margin_pp
        if p.property_value > 0 and balance > p.property_value * p.max_ltv_basic_pct / 100:
            rate += p.low_contribution_pp
        return rate

    @staticmethod
    def annuity(principal: float, monthly_rate: float, months: int) -> float:
        if months <= 0:
            return principal
        if monthly_rate == 0:
            return principal / months
        return principal * monthly_rate / (1 - (1 + monthly_rate) ** -months)

    def rrso_pct(self, p: MortgageParameters, installments: List[Installment]) -> float:
        """RRSO: roczna stopa, przy której wypłacone transze równoważą prowizję i wszystkie raty."""
        flows = [(0.0, -p.commission)]
        flows += [((i.number - 1) / 12, i.disbursed) for i in installments if i.disbursed]
        flows += [(i.number / 12, -i.total) for i in installments]

        def present_value(rate: float) -> float:
            return sum(amount * (1 + rate) ** -t for t, amount in flows)

        low, high = 0.0, 1.0
        if present_value(low) > 0 or present_value(high) < 0:
            return float("nan")
        for _ in range(self.RRSO_ITERATIONS):
            middle = (low + high) / 2
            if present_value(middle) < 0:
                low = middle
            else:
                high = middle
        return (low + high) / 2 * 100
