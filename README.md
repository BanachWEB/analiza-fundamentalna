# analiza-fundamentalna

Skill „analiza-spolki”: wstępna analiza fundamentalna spółki z USA albo z GPW, zakończona raportem PDF albo uzasadnionym stopem. Projekt: `specyfikacja.md`. Zasady pracy: `CLAUDE.md`.

## Stan budowy

Plan ma 7 kroków (`specyfikacja.md`, część 11).

| Krok | Zakres | Stan |
|---|---|---|
| 1 | Schemat rejestru faktów, rejestr, archiwum dokumentów | gotowy |
| 2 | Pobieranie z API SEC i weryfikacja (tożsamości, drugie źródło) | gotowy |
| 3 | Odczyt ESEF i PDF dla GPW, test cytatu | — |
| 4 | Obliczenia: wskaźniki, wycena odwrotna, scenariusze, karta Treli | — |
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

## Jak działa rejestr faktów

- `silnik/pobieranie/archiwum.py` zapisuje każdy pobrany dokument poza repozytorium i dopisuje go do `analizy/<TICKER>/<data>/dokumenty.json` (id, adres, data pobrania, SHA-256).
- `silnik/fakty/rejestr.py` przyjmuje tylko fakty zgodne ze schematem: fakt raportowany musi wskazywać istniejący dokument, fakt z tekstu musi mieć cytat dosłowny, kwota musi mieć walutę, założenie musi mieć uzasadnienie, a prognoza — dostawcę, datę i liczbę analityków.
- Fakty wyliczone tworzy tylko kod (`RejestrFaktow.wylicz`). Wpis zapamiętuje wzór i dane wejściowe, a status dziedziczy po najsłabszym wejściu. Z faktów odrzuconych kod niczego nie liczy.
