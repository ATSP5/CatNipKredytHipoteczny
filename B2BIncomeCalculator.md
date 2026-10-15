Zamienia kwoty z faktur (netto, bez VAT) na dochód na rękę dla domownika z działalnością gospodarczą: odejmuje koszty działalności, ZUS społeczny, składkę zdrowotną i PIT wg jego formy opodatkowania. Stawki na 2026 r. bierze z rekordu `TaxRules`.

- **ryczałt** — podatek = stawka × (przychód − ZUS społeczny − ½ zdrowotnej); zdrowotna stała, zależna od rocznego przychodu (do 60 tys., do 300 tys., powyżej); kosztów się nie odlicza,
- **liniowy** — 19% od dochodu po kosztach i ZUS, minus odliczona zdrowotna (do 14 100 zł rocznie); zdrowotna 4,9% dochodu, nie mniej niż 432,54 zł,
- **skala** — 12% / 32% (próg 120 tys., kwota zmniejszająca 3 600 zł) liczone rocznie i rozłożone na miesiące; zdrowotna 9% dochodu, nie mniej niż 432,54 zł.

## rules
Stawki ZUS, zdrowotnej i PIT (`TaxRules`, domyślnie 2026 r.).

## b2b_income
Wyjście bloku — ten kalkulator, podawany do `HouseholdLoader`.

## months
Kolejne miesiące działalności (`BusinessIncomeMonth`) dla kwot z faktur i profilu podatkowego domownika.
