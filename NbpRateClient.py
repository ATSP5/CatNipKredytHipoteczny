import urllib.request
import xml.etree.ElementTree as ElementTree
from typing import Optional

from NbpRate import NbpRate


class NbpRateClient:
    """Pobiera bieżącą stopę referencyjną z darmowego pliku XML NBP; bez sieci zwraca None."""

    URL = "https://static.nbp.pl/dane/stopy/stopy_procentowe.xml"

    def __init__(self, url: str = URL, timeout_s: float = 10.0):
        self.url = url
        self.timeout_s = timeout_s

    def reference_rate(self) -> Optional[NbpRate]:
        try:
            request = urllib.request.Request(self.url, headers={"User-Agent": "KredytHipoteczny/1.0"})
            with urllib.request.urlopen(request, timeout=self.timeout_s) as response:
                root = ElementTree.fromstring(response.read())
            position = next(p for p in root.iter("pozycja") if p.get("id") == "ref")
            rate = NbpRate(rate_pct=float(position.get("oprocentowanie").replace(",", ".")),
                           valid_from=position.get("obowiazuje_od", ""),
                           published=root.get("data_publikacji", ""))
            print("[NBP] stopa referencyjna %.2f%% od %s" % (rate.rate_pct, rate.valid_from), flush=True)
            return rate
        except Exception as error:  # brak sieci, zmiana formatu — analiza działa dalej na danych z pliku
            print("[NBP] nie udało się pobrać stopy (%s: %s) — używam danych z pliku."
                  % (type(error).__name__, error), flush=True)
            return None
