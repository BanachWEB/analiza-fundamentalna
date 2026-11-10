# analiza-fundamentalna

Skill „analiza-spolki”: wstępna analiza fundamentalna spółki z USA albo z GPW, zakończona raportem PDF albo uzasadnionym stopem. Projekt: `specyfikacja.md`. Zasady pracy: `CLAUDE.md`.

## Stan budowy

Plan ma 7 kroków (`specyfikacja.md`, część 11).

| Krok | Zakres | Stan |
|---|---|---|
| 1 | Schemat rejestru faktów, rejestr, archiwum dokumentów | gotowy |
| 2 | Pobieranie z API SEC i weryfikacja (tożsamości, drugie źródło) | gotowy |
| 3 | Odczyt ESEF i PDF dla GPW, test cytatu | gotowy |
| 4 | Obliczenia: wskaźniki, wycena odwrotna, scenariusze, karta Treli | 4a gotowy (okresy, wskaźniki, jakość); 4b w budowie |
| 5 | Bramki stopu | — |
| 6 | Raport: szablon z miejscami na liczby, lint, PDF | — |
| 7 | SKILL.md i pełne przebiegi na 6 spółkach testowych | — |

## Uruchomienie

```bash
pip install -r requirements.txt
```

```bash
python -m pytest
```

Po zmianie `silnik/fakty/schemat.py` wygeneruj schemat JSON od nowa:

```bash
python -m silnik.fakty.eksport_schematu
```

## Dane spółki z USA (krok 2)

```bash
python -m silnik.usa MSFT
```

- CIK spółki silnik bierze z `konfiguracja/sec-cik.yaml`. Gdy go tam nie ma, a zmienna `ANALIZA_USER_AGENT` zawiera adres e-mail, pobiera listę SEC i sam dopisuje CIK do tego pliku.
- Silnik pobiera z SEC dane XBRL (companyfacts) i listę raportów, a ze Stock Analysis trzy strony ze sprawozdaniami. Wszystkie pliki trafiają do archiwum.
- Fakty z SEC trafiają do rejestru bez udziału modelu: 10 lat obrotowych, 12 kwartałów i stany na koniec okresów.
- Weryfikacja sprawdza cztery tożsamości księgowe (aktywa = pasywa; zobowiązania + kapitał = pasywa; przychody − koszt sprzedaży = zysk brutto; przepływy = zmiana gotówki) i porównuje 12 pozycji rocznych ze Stock Analysis, z progiem 0,5%.
- Wynik: `analizy/<TICKER>/<data>/` z plikami `dokumenty.json`, `fakty.json` i `weryfikacja.md`.

Znane ograniczenia: kwartał Q4 i przepływy kwartalne (raporty 10-Q podają je narastająco) policzy dopiero krok 4. Stock Analysis za darmo daje tylko dane roczne, więc fakty kwartalne mają zwykle status „jedno_zrodlo”. Spółki zagraniczne z raportami 20-F (taksonomia IFRS) wymagają osobnego mapowania.

## Dane spółki z GPW (krok 3)

```bash
python -m silnik.gpw DNP --esef URL_ESEF_2025 --esef URL_ESEF_2024 --pdf URL_RAPORTU_KWARTALNEGO
```

- **ESEF (raport roczny):** silnik czyta liczby z pakietu ZIP (także ZIP w ZIP i `.xbri`) bez udziału modelu, według `konfiguracja/mapowanie-mssf.yaml`. Każdy raport daje rok bieżący i rok porównawczy; nowszy raport nadpisuje dane porównawcze i zostawia ślad „zmiana_wersji”. Adresy pakietów są na stronie relacji inwestorskich spółki. Darmowe repozytorium filings.xbrl.org ma polskie raporty tylko do 2024 r.
- **PDF (raporty kwartalne i półroczne):** model czyta tekst strony i zapisuje propozycje faktów w `analizy/<TICKER>/<data>/propozycje.json`, z dosłownym cytatem i numerem strony. Potem uruchamia to samo polecenie jeszcze raz.
- **Test cytatu:** silnik przyjmuje propozycję tylko wtedy, gdy cytat jest na wskazanej stronie, a wartość jest całą liczbą z kolumny tego wiersza (silnik składa liczby z pozycji słów w PDF). Propozycja, która nie przejdzie testu, zostaje w rejestrze ze statusem „odrzucony” i powodem.
- **Drugie źródło:** Biznesradar (dane roczne i kwartalne w tys. PLN). Z kwartałów silnik liczy sumy narastające (H1, M9), żeby porównać je z raportami kwartalnymi.
- **Uzupełnienie historii:** lata obrotowe i stany na koniec roku, których nie pokrywa żaden raport spółki w archiwum, silnik bierze z Biznesradaru (do 10 lat). Takie fakty mają metodę `parser_strony`, status „jedno_zrodlo” i ślad „uzupelnienie:biznesradar”; `weryfikacja.md` wymienia te lata. Fakt nie może potwierdzić sam siebie: porównanie z drugim źródłem pomija fakty z tego samego dokumentu.

Format propozycji (wartość tak, jak stoi w raporcie, razem ze skalą z nagłówka tabeli):

```json
{"fakty": [{"id": "przychody.FY2026M9", "pozycja": "przychody",
  "okres": {"typ": "M9", "poczatek": "2026-01-01", "koniec": "2026-09-30"},
  "wartosc": 27679127, "skala": "tys", "jednostka": "pieniadz", "waluta": "PLN",
  "dokument": "doc-003", "miejsce": {"strona": 4, "kolumna": 0},
  "cytat": "Przychody ze sprzedaży .... 27 679 127 24 738 104 6 467 086 5 839 279"}]}
```

Znane ograniczenie: test cytatu nie wykryje wartości z niewłaściwej kolumny (np. rok poprzedni zamiast bieżącego). Taki błąd łapie drugie źródło.

## Obliczenia (krok 4a)

Przebiegi `silnik.usa` i `silnik.gpw` uruchamiają obliczenia same. Osobno: `python -m silnik.obliczenia analizy/<TICKER>/<data>`.

- **Okresy pochodne:** Q2, Q3 i Q4 z danych narastających (np. Q4 = rok − 9 miesięcy) oraz TTM = ostatni rok + bieżący okres narastający − ten sam okres rok wcześniej.
- **Uzupełnienia ze składników** (z jawnym wzorem): amortyzacja z części (Microsoft), zobowiązania = pasywa − kapitał (Walmart), dług z kredytów i obligacji (spółki z GPW).
- **Panel:** marże, EBITDA, FCF dla właścicieli (po capeksie, SBC i spłacie leasingu, jeśli spółka je podaje), konwersja FCF, capex ÷ amortyzacja, ROE, ROIC (NOPAT przy stawce ustawowej: 21% USA, 19% Polska — założenie zapisane w rejestrze), dług netto ÷ EBITDA (z leasingiem i bez), pokrycie odsetek, dynamika r/r i CAGR 3/5 lat, zmiana liczby akcji.
- **Jakość:** Piotroski F-score, Beneish M-score (próg −1,78), Altman Z'' (strefy 1,10 / 2,60). To diagnostyka, nie stop.
- **Podział akcji:** gdy liczba akcji zmienia się o całkowitą krotność (np. 3:1), silnik nie liczy dynamiki liczby akcji ani EPS przez tę granicę.
- Wskaźnik bez danych albo bez sensu (np. dynamika od ujemnej bazy) nie powstaje; powód trafia do sekcji „Braki danych” w `obliczenia.md`.

## Jak działa rejestr faktów

- `silnik/pobieranie/archiwum.py` zapisuje każdy pobrany dokument poza repozytorium i dopisuje go do `analizy/<TICKER>/<data>/dokumenty.json` (id, adres, data pobrania, SHA-256).
- `silnik/fakty/rejestr.py` przyjmuje tylko fakty zgodne ze schematem: fakt raportowany musi wskazywać istniejący dokument, fakt z tekstu musi mieć cytat dosłowny, kwota musi mieć walutę, założenie musi mieć uzasadnienie, a prognoza — dostawcę, datę i liczbę analityków.
- Fakty wyliczone tworzy tylko kod (`RejestrFaktow.wylicz`). Wpis zapamiętuje wzór i dane wejściowe, a status dziedziczy po najsłabszym wejściu. Z faktów odrzuconych kod niczego nie liczy.
