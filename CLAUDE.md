# Analiza fundamentalna — skill „analiza-spolki”

Repozytorium buduje skill, który robi wstępną analizę fundamentalną spółki z USA albo z GPW i oddaje PDF. Pełny projekt jest w `specyfikacja.md`. Ten plik czytasz na początku każdej sesji: mówi, gdzie co jest i jakich zasad pilnować.

## Zasada nadrzędna: model nie wpisuje liczb

- Każda liczba w analizie ma wpis w rejestrze faktów (`fakty.json`) z dokumentem źródłowym, miejscem w dokumencie i statusem weryfikacji.
- Model szuka danych w dokumentach i pisze tekst. Liczby liczy i wstawia kod (`silnik/`).
- Nigdy nie używaj liczb z pamięci. Liczba bez pobranego źródła dostaje „brak danych”.
- Gdy kod nie umie czegoś policzyć, dopisz kod. Nie licz „w głowie”.

## Reguły porządku

1. **Jedna informacja — jeden plik.** Tabela „Gdzie co jest” wskazuje źródło prawdy. Inne pliki tylko do niego odsyłają.
2. **Zapisuj na gałęzi `main`** (commit i push). Przed zapisem zrób `git pull`.
3. Każdy commit ma krótki opis po polsku: co i dlaczego.
4. Zmiany w specyfikacji, progach bramek i wagach karty Treli wprowadzasz tylko po zgodzie właściciela repozytorium.
5. Bez rekomendacji kup/sprzedaj. To, co wynika z zasad właściciela, podawaj jako „wg twoich zasad: …”.

## Gdzie co jest

| Co | Źródło prawdy |
|---|---|
| Projekt skilla: architektura, etapy, bramki, układ PDF, plan budowy | `specyfikacja.md` |
| Badanie metody (stan na 9.11.2026; podstawa specyfikacji i plików referencyjnych skilla) | `badanie/analiza-fundamentalna-i-wycena-spolek.md` |
| Jak uruchomić i stan budowy | `README.md` |
| Schemat rejestru faktów i dokumentów | `silnik/fakty/schemat.py` (plik `schemat/*.schema.json` jest z niego generowany) |
| Rejestr faktów: dodawanie, wyliczanie, zapis | `silnik/fakty/rejestr.py` |
| Archiwum dokumentów źródłowych | `silnik/pobieranie/archiwum.py` |
| Dane z SEC i kalendarz fiskalny | `silnik/pobieranie/sec.py` |
| Mapowanie znaczników XBRL na pozycje | `konfiguracja/mapowanie-us-gaap.yaml` |
| Ticker → CIK | `konfiguracja/sec-cik.yaml` |
| Drugie źródło dla USA | `silnik/pobieranie/stockanalysis.py` |
| Tożsamości księgowe i porównanie z drugim źródłem | `silnik/fakty/weryfikacja.py` |
| Przebieg danych dla spółki z USA | `silnik/usa.py` |
| Raporty ESEF (GPW) i mapowanie MSSF | `silnik/pobieranie/esef.py`, `konfiguracja/mapowanie-mssf.yaml` |
| Drugie źródło dla GPW | `silnik/pobieranie/biznesradar.py` |
| Test cytatu dla liczb z PDF i tekstu | `silnik/fakty/cytat.py` |
| Przebieg danych dla spółki z GPW | `silnik/gpw.py` |
| Obliczenia: okresy pochodne, wskaźniki, F/M/Z'', wycena, scenariusze, karta Treli | `silnik/obliczenia/` |
| Dane rynkowe: kursy, stopy, premie za ryzyko | `silnik/pobieranie/rynek.py` |
| Parametry wyceny odwrotnej | `konfiguracja/wycena.yaml` |
| Wagi i progi karty Treli | `konfiguracja/karta-treli.yaml` |
| Bramki stopu: lista, progi, decyzja | `konfiguracja/bramki.yaml`, `silnik/bramki/` |
| Raport: miejsca na liczby, lint, wykresy, PDF | `silnik/raport/` |
| Wyniki analiz | `analizy/<TICKER>/<RRRR-MM-DD>/` |
| Zasady inwestowania właściciela (limity, pauza po rajdzie, benchmarki) | repozytorium `inwestowanie`, plik `zasady-inwestowania.md` |
| Zasady pisania (rozmowa, pliki, raporty) | ten plik, sekcja „Język i styl” |

## Język i styl

Dotyczy wszystkiego, co piszesz: odpowiedzi w rozmowie, plików w repozytorium i raportów PDF.

### Język
- Pisz po polsku, na „ty”. Zostaw angielskie skróty miar finansowych: EBITDA, FCF, EV, TTM, CAGR.
- Pisz pełnymi zdaniami. Każde zdanie ma podmiot i orzeczenie. Nie pisz telegraficznie.

### Nazwy
- Jedna rzecz, jedna nazwa. Wybierz jeden termin dla pojęcia i używaj go w całej odpowiedzi. Nie używaj synonimów.
- Jedno słowo, jedno znaczenie. Nie używaj tego samego słowa dla dwóch różnych pojęć.
- Zawsze dookreślaj miary: „zysk netto”, nie „zysk”; „marża operacyjna”, nie „marża”; „wzrost r/r”, nie „wzrost”.

### Zdania i akapity
- Jedna myśl w zdaniu.
- Używaj strony czynnej. Pisz, kto co robi: „Spółka obniżyła koszty”, nie „Koszty zostały obniżone”.
- Używaj czasowników, nie rzeczowników odczasownikowych: „spółka zwiększyła sprzedaż”, nie „nastąpiło zwiększenie sprzedaży”.
- Najwyżej 3 rzeczowniki pod rząd.
- Jeden akapit, jeden temat.

### Liczby
- Każda liczba ma walutę, okres i źródło. Przykład: „Zysk netto: 1,2 mld PLN | TTM do 30.09.2026 | InvestingPro”.
- Oznacz wyniki skorygowane słowem „skorygowany”.

### Fakty i oceny
- Oddzielaj fakty od ocen i założeń. Ocenę zaczynaj od „Moim zdaniem” albo „Zakładam, że”.
- Gdy czegoś nie wiesz, napisz to wprost. Nie zgaduj.

## Środowisko

- `pip install -r requirements.txt`, potem `python -m pytest`.
- Powłoka i Python mają dostęp do data.sec.gov, stockanalysis.com, biznesradar.pl i stron relacji inwestorskich spółek oraz query1.finance.yahoo.com, home.treasury.gov, pages.stern.nyu.edu i strefainwestorow.pl, efts.sec.gov i gpw.pl (strony notowań i komunikatów) (sprawdzone 10.11.2026; bankier.pl odmawia, 403; Yahoo ogranicza liczbę zapytań, 429). Pobieraj dane kodem (`silnik/pobieranie/`), bo WebFetch przepuszcza strony przez model streszczający. WebFetch i WebSearch służą tylko do szukania informacji, nigdy do przepisywania liczb.
- Zmienna `ANALIZA_USER_AGENT`: SEC prosi o nazwę narzędzia i adres kontaktowy w nagłówku. Silnik nie podmienia nagłówków i nie omija blokad.
- Pliki źródłowe z archiwum trzymaj poza repozytorium (domyślnie `~/.cache/analiza-fundamentalna/archiwum`, zmienna `ANALIZA_ARCHIWUM`). Do repozytorium trafia tylko `dokumenty.json` z adresem i sumą SHA-256 każdego pliku.
