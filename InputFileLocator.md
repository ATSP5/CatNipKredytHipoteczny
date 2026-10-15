Znajduje plik wejściowy w folderze `input` projektu. Szuka najpierw w folderach z plikiem `.catnip` (lokalnie i w Dockerze, gdzie projekt leży w `/app`), potem w bieżącym folderze i folderze modułu; na końcu przyjmuje też plik położony bezpośrednio obok projektu.

## locator
Wyjście bloku — ten lokalizator, podawany do `HouseholdLoader` i `BankOfferLoader`.

## resolve
Ścieżka wskazana wprost (np. przez blok File content), a gdy nie istnieje — plik o tej samej nazwie w folderze `input`. Rozumie ukośniki z Windows także w Dockerze.

## find
Ścieżka pliku o podanej nazwie albo czytelny błąd z listą sprawdzonych folderów.
