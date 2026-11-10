# analiza-fundamentalna

Skill „analiza-spolki”: wstępna analiza fundamentalna spółki z USA albo z GPW, zakończona raportem PDF albo uzasadnionym stopem. Projekt: `specyfikacja.md`. Zasady pracy: `CLAUDE.md`.

## Stan budowy

Plan ma 7 kroków (`specyfikacja.md`, część 11).

| Krok | Zakres | Stan |
|---|---|---|
| 1 | Schemat rejestru faktów, rejestr, archiwum dokumentów | gotowy |
| 2 | Pobieranie z API SEC i weryfikacja (tożsamości, drugie źródło) | — |
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

## Jak działa rejestr faktów

- `silnik/pobieranie/archiwum.py` zapisuje każdy pobrany dokument poza repozytorium i dopisuje go do `analizy/<TICKER>/<data>/dokumenty.json` (id, adres, data pobrania, SHA-256).
- `silnik/fakty/rejestr.py` przyjmuje tylko fakty zgodne ze schematem: fakt raportowany musi wskazywać istniejący dokument, fakt z tekstu musi mieć cytat dosłowny, kwota musi mieć walutę, założenie musi mieć uzasadnienie, a prognoza — dostawcę, datę i liczbę analityków.
- Fakty wyliczone tworzy tylko kod (`RejestrFaktow.wylicz`). Wpis zapamiętuje wzór i dane wejściowe, a status dziedziczy po najsłabszym wejściu. Z faktów odrzuconych kod niczego nie liczy.
