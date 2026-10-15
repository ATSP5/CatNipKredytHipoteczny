Wczytuje oferty banków i reguły rynkowe z `input/oferty_bankow.xlsx` (arkusze Oferty i Rynek). Kolumny arkusza Oferty są rozpoznawane po nagłówkach, więc ich kolejność można zmieniać.

## locator
`InputFileLocator`, który znajduje plik w folderze `input`.

## reader
`ExcelSheetReader`, który czyta plik.

## file_name
Nazwa pliku w folderze `input` — ustawiana w sekcji INITIALISER.

## offers
Lista ofert banków.

## market
Wskaźniki (WIBOR, POLSTR) z datami notowań, stopa NBP w dniu notowań, bufory KNF, limity DSTI, minimalne koszty życia i LTV.
