Pobiera bieżącą stopę referencyjną NBP z darmowego pliku XML `https://static.nbp.pl/dane/stopy/stopy_procentowe.xml`. To jedyna stawka dostępna za darmo w formacie danych; WIBOR (GPW Benchmark) i marże banków takiego źródła nie mają. Bez sieci zwraca `None`, a analiza liczy dalej na danych z pliku.

## timeout_s
Ile sekund czekać na serwer NBP — ustawiane w sekcji INITIALISER.

## reference_rate
Stopa referencyjna NBP albo `None`.
