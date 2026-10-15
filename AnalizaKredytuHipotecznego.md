Interaktywna analiza kredytu hipotecznego na budowę domu.

Na starcie strona bierze plan budowy i budżet rodziny z Excela oraz ofertę najkorzystniejszego banku (najniższy całkowity koszt). Wszystko można zmienić ręcznie: koszt budowy, działkę, oszczędności, czas budowy i transze, bank, okres, rodzaj rat i oprocentowania, marżę, prowizję, dochody każdej osoby i wydatki. Przyciski „Przywróć…” wracają do danych z plików, a kliknięcie wiersza porównania banków przełącza na ofertę tego banku.

Wejścia: `calculator` (MortgageCalculator), `formatter` (PlnFormat) i `b2b_income` (B2BIncomeCalculator).

Strona pokazuje: wskaźniki (kwota, rata, RRSO, koszt, zdolność, DSTI, wolne środki, wkład własny), ocenę zdolności według reguł KNF, porównanie banków, budżet rodziny w czasie budowy i po przeprowadzce, strukturę kosztu, spłaty w kolejnych latach i pełny harmonogram.

Dla osoby rozliczającej działalność z faktur karta **Budżet rodziny** ma dwa pola: **faktury netto (bez VAT)** i **na rękę**. Wpisanie kwoty z faktury przelicza dochód na rękę (ZUS, zdrowotna, PIT wg profilu z Excela), tabelę „Dochód z działalności (B2B)”, zdolność i całą analizę; pole „na rękę” można też nadpisać ręcznie.

## b2b_income
`B2BIncomeCalculator` — przelicza kwotę z faktury wpisaną na stronie.

## on_change
Reaguje na zmianę pola `invoice_<n>`: przelicza dochód na rękę tej osoby i wpisuje go w `income_<n>`.

## zapisz
Akcja **Zapisz PDF** (tryb Live). `on_zapisz` zbiera bieżący stan w `MortgageReportSnapshot`; wygenerowany main przekazuje ją przy każdym kliknięciu do `MortgageReportPdf`. Przy błędnych parametrach strona pokazuje błąd i nic nie zapisuje.
