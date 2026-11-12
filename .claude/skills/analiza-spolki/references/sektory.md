# Sektory z osobnymi miarami

Ustaw w `D/analiza.json` pole `"sektor": "finanse"` dla banków, ubezpieczycieli, brokerów i firm windykacyjnych. Silnik wtedy:
- nie liczy F-score, M-score i Z'' i pomija bramki przepływów, M-score i Z'';
- w karcie Treli mierzy jakość przez ROE, a wycenę przez C/Z i C/WK.

Miary sektorowe dodajesz jako propozycje z raportu (PDF albo prezentacja) z nowymi pozycjami.

## Typ spółki w `analiza.json` (wybiera metodę wyceny w silniku)

| `sektor` | Kiedy | Co robi silnik |
|---|---|---|
| `ogolny` | pozostałe spółki | wycena odwrotna i scenariusze z FCF TTM |
| `cykliczny` | wynik zależy od cyklu: surowce, chemia, stal, półprzewodniki, pamięci, przewoźnicy, motoryzacja | dodaje wariant z FCF znormalizowanym (marża FCF z pełnego cyklu × przychody); karta Treli bierze ten wariant |
| `finanse` | bank, ubezpieczyciel, broker, windykacja | zysk netto zamiast FCF, uzasadnione C/WK, ROE implikowane, scenariusze z polem `roe`; wyłącza F/M/Z''/O |
| `deweloper` | deweloper mieszkaniowy i komercyjny | jak `finanse`, ale z F/M/Z''; zadłużenie jako dług netto ÷ kapitał własny |

Gdy nie masz pewności między `ogolny` a `cykliczny`, wybierz `ogolny`: silnik ostrzeże w `obliczenia.md`, jeśli spółka ma głęboki spadek przychodów r/r albo dużą zmienność marży FCF. Wtedy zmień typ i uruchom obliczenia jeszcze raz.

## Miary sektorowe

| Typ spółki | Miary główne (pozycje propozycji) | Czego nie używać |
|---|---|---|
| Bank | `nim` (marża odsetkowa netto), `koszty_do_dochodow`, `koszt_ryzyka`, `npl`, `cet1`, `wymog_cet1`, ROE (silnik) wobec kosztu kapitału | EBITDA, dług netto, Z'', M-score, FCF |
| Ubezpieczyciel | `wskaznik_mieszany` (combined ratio), `wskaznik_wyplacalnosci` (Solvency II), ROE | EBITDA, dług netto |
| Broker | `liczba_klientow`, `aktywa_klientow`, `przychod_na_klienta`, koszt pozyskania klienta | dług netto ÷ EBITDA (gotówka klientów) |
| Windykacja | `ebitda_gotowkowa`, `erc` (szacowane wpływy), dług netto ÷ EBITDA gotówkowa | zwykła EBITDA, Z'' |
| Deweloper | `sprzedaz_przedwstepna`, `przekazania`, `bank_ziemi`, marża brutto, dług netto ÷ kapitał | dług netto ÷ EBITDA (przychody skaczą przy przekazaniach) |
| Studio gier | udział największego tytułu, sprzedaż katalogu, aktywowane nakłady wobec gotówki, odpisy, terminy premier | marża z jednego roku |
| Handel | `sprzedaz_lfl`, `powierzchnia`, sprzedaż na m², dług z leasingiem (silnik: dług netto z leasingiem ÷ EBITDA) | EBITDA z MSSF 16 obok długu bez leasingu |
| SaaS/IT | `arr`, `retencja_netto`, SBC ÷ przychody (silnik odejmuje SBC w FCF), portfel zamówień | sam LTV/CAC |
| Cykliczne (surowce, chemia, półprzewodniki) | marża przez pełny cykl, pozycja w cyklu | C/Z ze szczytu cyklu |

Bank: bramka `B3.bank_kapital` (STOP) — CET1 poniżej wymogu, z cytatem z raportu. Adekwatność kapitałową oceniasz zawsze.
