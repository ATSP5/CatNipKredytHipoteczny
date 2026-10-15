import re
from typing import Callable, List, Sequence

from BankOffer import BankOffer
from ExcelSheetReader import ExcelSheetReader
from ExcelWorkbook import ExcelWorkbook
from InputFileLocator import InputFileLocator
from MarketRates import MarketRates


class BankOfferLoader:
    """Wczytuje oferty banków i reguły rynkowe z input/oferty_bankow.xlsx."""

    INDEX_PREFIXES = ("WIBOR", "POLSTR", "WIRON")

    def __init__(self, locator: InputFileLocator, reader: ExcelSheetReader, file_name: str = "oferty_bankow.xlsx"):
        path = locator.find(file_name)
        self.workbook = reader.read(path)
        print("[Dane] oferty banków: %s" % path, flush=True)

    def offers(self) -> List[BankOffer]:
        column = self._columns("Oferty")
        offers = []
        for row in self.workbook.records("Oferty", min_filled=3):
            cell = lambda prefix: row[column(prefix)] if column(prefix) < len(row) else None
            high_ltv = cell("Marża przy LTV")
            offers.append(BankOffer(
                bank=str(cell("Bank")).strip(), index_name=str(cell("Wskaźnik") or "WIBOR 3M").strip().upper(),
                margin_pct=float(cell("Marża [") or 0),
                margin_high_ltv_pct=float(high_ltv) if isinstance(high_ltv, (int, float)) else None,
                commission_pct=float(cell("Prowizja") or 0), bridge_margin_pp=float(cell("Podwyżka marży") or 0),
                property_insurance_pct=float(cell("Ubezpieczenie nieruchomości") or 0),
                max_ltv_pct=float(cell("Maks. LTV") or 80), notes=str(cell("Uwagi") or ""),
                source=str(cell("Źródło") or ""), as_of=str(cell("Stan na") or "")))
        if not offers:
            raise ValueError("Arkusz Oferty nie zawiera żadnego banku.")
        return offers

    def market(self) -> MarketRates:
        p = self.workbook.parameters("Rynek")
        value = lambda prefix: float(ExcelWorkbook.lookup(p, prefix))
        indices, dates = {}, {}
        for row in self.workbook.records("Rynek"):
            label = str(row[0]).strip()
            if label.upper().startswith(self.INDEX_PREFIXES) and isinstance(row[1], (int, float)):
                name = re.sub(r"\s*\[.*$", "", label).strip().upper()
                indices[name] = float(row[1])
                dates[name] = str(row[2] or "") if len(row) > 2 else ""
        if not indices:
            raise ValueError("Arkusz Rynek nie zawiera żadnego wskaźnika (wiersze WIBOR… albo POLSTR…).")
        nbp_at_quotes = value("Stopa referencyjna NBP")
        return MarketRates(
            indices=indices, index_dates=dates,
            nbp_ref_at_quotes=nbp_at_quotes, nbp_ref_now=nbp_at_quotes, nbp_date="", nbp_live=False,
            buffer_variable_pp=value("Bufor KNF — stopa zmienna"),
            buffer_fixed_pp=value("Bufor KNF — stopa okresowo"),
            dsti_low_pct=value("DSTI — dochód do"), dsti_high_pct=value("DSTI — dochód powyżej"),
            dsti_threshold=value("Próg dochodu"),
            min_cost_adult=value("Minimalne koszty utrzymania — dorosły"),
            min_cost_child=value("Minimalne koszty utrzymania — dziecko"),
            max_ltv_basic_pct=value("Maks. LTV"), low_contribution_pp=value("Ubezpieczenie niskiego"))

    def _columns(self, sheet: str) -> Callable[[str], int]:
        """Numer kolumny po początku jej nagłówka — kolejność kolumn w arkuszu nie ma znaczenia."""
        header: Sequence[str] = self.workbook.header(sheet)

        def column(prefix: str) -> int:
            for index, name in enumerate(header):
                if name.lower().startswith(prefix.lower()):
                    return index
            raise KeyError("W arkuszu %s brakuje kolumny '%s…'." % (sheet, prefix))
        return column
