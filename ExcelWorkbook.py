from dataclasses import dataclass
from typing import Dict, List, Sequence


@dataclass(frozen=True)
class ExcelWorkbook:
    """Zawartość pliku .xlsx: nazwa arkusza → wiersze wartości, z nagłówkiem w pierwszym wierszu."""

    name: str
    sheets: Dict[str, List[tuple]]

    def header(self, sheet: str) -> List[str]:
        rows = self._rows(sheet)
        return [str(value).strip() if value is not None else "" for value in rows[0]] if rows else []

    def records(self, sheet: str, min_filled: int = 2) -> List[Sequence[object]]:
        """Wiersze danych pod nagłówkiem; bez pustych wierszy i notatek (tylko pierwsza komórka)."""
        rows = self._rows(sheet)[1:]
        return [row for row in rows if sum(value not in (None, "") for value in row) >= min_filled]

    def parameters(self, sheet: str) -> Dict[str, object]:
        """Arkusz w układzie Parametr | Wartość jako słownik."""
        return {str(row[0]).strip(): row[1] for row in self.records(sheet) if row[0] is not None}

    def _rows(self, sheet: str) -> List[tuple]:
        if sheet not in self.sheets:
            raise KeyError("W pliku %s brakuje arkusza '%s' (są: %s)." % (self.name, sheet, ", ".join(self.sheets)))
        return self.sheets[sheet]

    @staticmethod
    def lookup(parameters: Dict[str, object], prefix: str) -> object:
        """Wartość parametru, którego nazwa zaczyna się od prefix (bez względu na wielkość liter)."""
        for name, value in parameters.items():
            if name.lower().startswith(prefix.lower()):
                return value
        raise KeyError("Brakuje parametru '%s…'." % prefix)
