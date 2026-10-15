Wczytuje dochody gospodarstwa i plan budowy z pliku Excel wskazanego blokiem File content **Dochody gospodarstwa (Excel)** (arkusze Domownicy, Dochody, Wydatki, Inwestycja). Kolumny arkusza Dochody nazwane jak osoby z arkusza Domownicy są ich kwotami miesięcznymi; pozostałe kolumny (np. 800+) to dochód, którego bank nie wlicza.

Kolumna Domownicy **„Kwoty w arkuszu Dochody”** mówi, czym są te kwoty: `na rękę` — dochód netto, brany wprost; `faktury` — kwoty z faktur (netto, bez VAT), z których `B2BIncomeCalculator` odejmuje koszty, ZUS, zdrowotną i PIT wg kolumn Forma opodatkowania, Stawka ryczałtu, ZUS i Koszty działalności. Kolumny czytane są po nagłówkach — starszy plik bez nich jest traktowany jako „na rękę”.

## household_file
Ścieżka pliku z bloku File content. CatNip wpisuje ją w `__init__` jako `self.household_file = r"…"` — **nie jest parametrem konstruktora**, bo main jej nie przekazuje. Gdy ścieżka nie istnieje (np. ścieżka z Windows w Dockerze), plik o tej nazwie jest szukany w folderze `input`.

## locator
`InputFileLocator`, który rozwiązuje ścieżkę.

## reader
`ExcelSheetReader`, który czyta plik.

## b2b_income
`B2BIncomeCalculator`, który zamienia faktury na dochód na rękę.

## household
Gospodarstwo: domownicy (z rozbiciem faktur dla działalności), dochody, wydatki i nazwa pliku źródłowego.

## project
Plan budowy z arkusza Inwestycja.
