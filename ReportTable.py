from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ReportTable:
    """Tabela do raportu PDF: tytuł, nagłówki, wiersze tekstu i kolumny wyrównane do prawej."""

    title: str
    header: Tuple[str, ...]
    rows: Tuple[Tuple[str, ...], ...]
    right_columns: Tuple[int, ...] = ()
    widths: Tuple[float, ...] = ()
