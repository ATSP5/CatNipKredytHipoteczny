from dataclasses import dataclass
from datetime import datetime
from typing import Tuple

from MortgageSchedule import MortgageSchedule
from ReportTable import ReportTable


@dataclass(frozen=True)
class MortgageReportSnapshot:
    """Stan analizy w chwili kliknięcia „Zapisz PDF”."""

    title: str
    created_at: datetime
    kpis: Tuple[Tuple[str, str, str, bool], ...]     # (etykieta, wartość, opis, czy ostrzeżenie)
    messages: Tuple[Tuple[str, str], ...]            # (tekst, "ok" | "warning" | "error")
    tables: Tuple[ReportTable, ...]
    schedule: MortgageSchedule
    notes: Tuple[str, ...]
