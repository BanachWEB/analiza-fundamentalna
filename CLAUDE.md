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
| Jak uruchomić i stan budowy | `README.md` |
| Schemat rejestru faktów i dokumentów | `silnik/fakty/schemat.py` (plik `schemat/*.schema.json` jest z niego generowany) |
| Rejestr faktów: dodawanie, wyliczanie, zapis | `silnik/fakty/rejestr.py` |
| Archiwum dokumentów źródłowych | `silnik/pobieranie/archiwum.py` |
| Wyniki analiz | `analizy/<TICKER>/<RRRR-MM-DD>/` |
| Zasady inwestowania właściciela (limity, pauza po rajdzie, benchmarki) | repozytorium `inwestowanie`, plik `zasady-inwestowania.md` |
| Zasady pisania | repozytorium `inwestowanie`, plik `CLAUDE.md`, sekcja „Język i styl” |

## Język

Pisz po polsku, na „ty”, pełnymi zdaniami, stroną czynną. Każda liczba ma walutę, okres i źródło. Oddzielaj fakty od ocen: ocenę zaczynaj od „Moim zdaniem” albo „Zakładam, że”. Pełne zasady: `inwestowanie/CLAUDE.md`, sekcja „Język i styl”.

## Środowisko

- `pip install -r requirements.txt`, potem `python -m pytest`.
- Internet tylko przez narzędzia WebSearch i WebFetch; sieć powłoki jest ograniczona.
- Pliki źródłowe z archiwum trzymaj poza repozytorium (domyślnie `~/.cache/analiza-fundamentalna/archiwum`, zmienna `ANALIZA_ARCHIWUM`). Do repozytorium trafia tylko `dokumenty.json` z adresem i sumą SHA-256 każdego pliku.
