from typing import Dict, List, Optional, Sequence, Tuple

from B2BIncomeCalculator import B2BIncomeCalculator
from BusinessTaxProfile import BusinessTaxProfile
from ConstructionProject import ConstructionProject
from ExcelSheetReader import ExcelSheetReader
from ExcelWorkbook import ExcelWorkbook
from ExpenseItem import ExpenseItem
from Household import Household
from HouseholdMember import HouseholdMember
from InputFileLocator import InputFileLocator


class HouseholdLoader:
    """Wczytuje dochody gospodarstwa i plan budowy z pliku Excel wskazanego blokiem File content."""

    def __init__(self, locator: InputFileLocator, reader: ExcelSheetReader, b2b_income: B2BIncomeCalculator):
        # Ścieżka z bloku File content „Dochody gospodarstwa (Excel)” — CatNip wpisuje ją tutaj
        # i aktualizuje po wyborze innego pliku; main jej nie przekazuje.
        self.household_file = r"input/dochody_singiel_b2b.xlsx"
        path = locator.resolve(self.household_file)
        self.workbook = reader.read(path)
        self.b2b_income = b2b_income
        print("[Dane] dochody gospodarstwa: %s" % path, flush=True)

    def household(self) -> Household:
        incomes = self._monthly_incomes()
        columns = self._columns("Domownicy")
        members = tuple(self._member(row, columns, incomes) for row in self.workbook.records("Domownicy"))
        names = {m.name for m in members}
        other = tuple((source, sum(values) / len(values)) for source, values in incomes.items()
                      if source not in names and values)
        return Household(source=self.workbook.name, members=members, other_income=other,
                         expenses=self._expenses())

    def project(self) -> ConstructionProject:
        p = self.workbook.parameters("Inwestycja")
        value = lambda prefix: float(ExcelWorkbook.lookup(p, prefix) or 0)
        return ConstructionProject(
            house_cost=value("Koszt budowy"), plot_value=value("Wartość działki"), savings=value("Oszczędności"),
            cash_reserve=value("Rezerwa"), years=int(value("Okres kredytu")),
            build_months=int(value("Czas budowy")), tranches=int(value("Liczba transz")))

    def _monthly_incomes(self) -> Dict[str, List[float]]:
        header = self.workbook.header("Dochody")
        incomes: Dict[str, List[float]] = {name: [] for name in header[1:] if name}
        for row in self.workbook.records("Dochody"):
            for column, value in zip(header[1:], row[1:]):
                if column and isinstance(value, (int, float)):
                    incomes[column].append(float(value))
        return incomes

    def _member(self, row, column, incomes: Dict[str, List[float]]) -> HouseholdMember:
        cell = lambda prefix, default=None: (row[column(prefix)] if column(prefix) is not None
                                             and column(prefix) < len(row) and row[column(prefix)] not in (None, "")
                                             else default)
        name = str(cell("Osoba")).strip()
        amounts = tuple(incomes.get(name, ()))
        profile = self._tax_profile(cell)
        if profile is None:                       # kwoty w arkuszu Dochody są już na rękę
            return HouseholdMember(name=name, role=str(cell("Rola", "dorosły")),
                                   income_type=str(cell("Rodzaj dochodu", "brak")),
                                   seniority_months=int(cell("Staż", 0)), monthly_net=amounts)
        business = tuple(self.b2b_income.months(amounts, profile))
        return HouseholdMember(name=name, role=str(cell("Rola", "dorosły")),
                               income_type=str(cell("Rodzaj dochodu", "brak")),
                               seniority_months=int(cell("Staż", 0)),
                               monthly_net=tuple(round(m.net, 2) for m in business),
                               tax_profile=profile, business=business)

    @staticmethod
    def _tax_profile(cell) -> Optional[BusinessTaxProfile]:
        """Profil podatkowy, gdy arkusz Dochody podaje kwoty z faktur; None, gdy kwoty są na rękę."""
        if not str(cell("Kwoty w arkuszu", "na rękę")).strip().lower().startswith("faktur"):
            return None
        form = str(cell("Forma opodatkowania", BusinessTaxProfile.LUMP_SUM)).strip().lower()
        form = next((f for f in (BusinessTaxProfile.LUMP_SUM, BusinessTaxProfile.LINEAR, BusinessTaxProfile.SCALE)
                     if form.startswith(f[:4])), BusinessTaxProfile.LUMP_SUM)
        zus = str(cell("ZUS", BusinessTaxProfile.FULL_ZUS)).strip().lower()
        zus = next((z for z in (BusinessTaxProfile.FULL_ZUS, BusinessTaxProfile.PREFERENTIAL_ZUS,
                                BusinessTaxProfile.START_RELIEF) if zus.startswith(z[:4])), BusinessTaxProfile.FULL_ZUS)
        return BusinessTaxProfile(tax_form=form, lump_sum_rate=float(cell("Stawka ryczałtu", 12)) / 100, zus=zus,
                                  monthly_costs=float(cell("Koszty działalności", 0)))

    def _columns(self, sheet: str):
        """Numer kolumny po początku nagłówka (None, gdy jej nie ma) — starsze pliki mają mniej kolumn."""
        header: Sequence[str] = self.workbook.header(sheet)
        return lambda prefix: next((i for i, name in enumerate(header) if name.lower().startswith(prefix.lower())), None)

    def _expenses(self) -> Tuple[ExpenseItem, ...]:
        kinds = (ExpenseItem.LIVING, ExpenseItem.OBLIGATION, ExpenseItem.OTHER)
        items = []
        for row in self.workbook.records("Wydatki"):
            kind = str(row[2] or ExpenseItem.LIVING).strip().lower()
            items.append(ExpenseItem(str(row[0]).strip(), float(row[1] or 0),
                                     next((k for k in kinds if kind.startswith(k[:5])), ExpenseItem.OTHER)))
        return tuple(items)
