Domownik z arkusza Domownicy i jego miesięczne dochody na rękę (od najstarszego miesiąca). Przy działalności rozliczanej z faktur dochody na rękę są wyliczone, a `business` zawiera rozbicie każdego miesiąca.

## bank_income
Średni dochód na rękę z okresu, który bierze bank: 6 miesięcy z umowy o pracę lub zlecenia, 12 z działalności gospodarczej. Osoba z rodzajem dochodu „brak” ma 0.

## tax_profile
Forma opodatkowania, ZUS i koszty (`BusinessTaxProfile`), gdy kwoty pochodzą z faktur; inaczej `None`.

## business
Miesiące działalności (`BusinessIncomeMonth`): faktury, koszty, ZUS, zdrowotna, PIT, na rękę.

## is_adult
Czy osoba jest dorosła (rola zaczyna się od „doros…”). Dzieci liczą się tylko do minimalnych kosztów utrzymania.
