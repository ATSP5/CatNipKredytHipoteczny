Wybiera plik Excel z dochodami gospodarstwa i planem budowy — przekazuje **ścieżkę** do wejścia `household_file` bloku `HouseholdLoader` (sam plik czyta loader). Aby przeliczyć analizę dla innego gospodarstwa, wskaż tu inny plik z folderu `input`:

- `input/dochody_rodziny.xlsx` — rodzina: dwoje dorosłych (umowa o pracę i B2B) i dwoje dzieci,
- `input/dochody_singiel_b2b.xlsx` — jedna osoba bez dzieci, B2B, 74 zł/h netto, ok. 160 h miesięcznie.

Nowy plik musi mieć te same arkusze: Domownicy, Dochody, Wydatki, Inwestycja. Ścieżka względna (`input/…`) działa lokalnie i w Dockerze; gdy wskazany plik nie istnieje (np. ścieżka z Windows w kontenerze), loader szuka pliku o tej nazwie w folderze `input` projektu.

## household_file
Ścieżka wybranego pliku Excel.
