Zapisuje analizę jako nowy plik PDF `kredyt_hipoteczny_<rrrr-mm-dd_ggmmss>.pdf` w folderze `output` projektu — każde kliknięcie tworzy nowy plik. Raport: komunikaty i wskaźniki, parametry kredytu, ocena zdolności, budżet rodziny, porównanie banków, wykres spłat i struktura kosztu, pełny harmonogram (dzielony na strony). PDF powstaje w matplotlib bez pyplot, więc działa w wątku obsługującym kliknięcia.

## snapshot
`MortgageReportSnapshot` z `on_zapisz` strony. Przy błędnych parametrach przychodzi sam stan strony — wtedy blok niczego nie zapisuje.

## formatter
`PlnFormat` do liczb w raporcie.

## output_dir
Folder raportów, ustawiany w sekcji INITIALISER; ścieżka względna liczona od folderu z plikiem `.catnip`.

## pdf_path
Ścieżka zapisanego pliku (pusty tekst, gdy nie było czego zapisać); trafia też do konsoli jako `[Zapis PDF] zapisano …`.
