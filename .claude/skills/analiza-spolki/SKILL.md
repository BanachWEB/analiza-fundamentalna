---
name: analiza-spolki
description: Wstępna analiza fundamentalna spółki z USA albo z GPW (rynek główny) zakończona raportem PDF albo uzasadnionym stopem. Używaj, gdy właściciel podaje ticker i prosi o analizę, ocenę, kartę albo „czy warto się tym zająć”. Skill przechodzi etapy z bramkami czerwonych flag, buduje rejestr faktów z dokumentów (SEC, ESEF, raporty PDF), liczy wskaźniki, wycenę odwrotną i scenariusze w kodzie i pisze raport, w którym każdą liczbę wstawia silnik, a nie model.
---

# Analiza spółki

Właściciel podaje ticker. Skill robi wstępną analizę fundamentalną i oddaje PDF, z którego właściciel decyduje, czy spółka jest warta jego własnej, pogłębionej analizy. Pełny projekt: `specyfikacja.md`. Zasady pisania: `CLAUDE.md`, sekcja „Język i styl”.

## Zasady, których nie łamiesz

1. **Nie wpisujesz liczb.** Każda liczba trafia do raportu przez miejsce `{{id_faktu}}`, a fakt musi być w `fakty.json`. Liczby z pamięci są zakazane. Liczbę z dokumentu dodajesz tylko jako propozycję z dosłownym cytatem (`references/dane-i-dowody.md`). Lint odrzuci raport z jakąkolwiek cyfrą poza wyjątkami.
2. **Nie liczysz.** Wskaźniki, wycenę, scenariusze i kartę Treli liczy silnik. Brakuje wskaźnika — dopisz kod w `silnik/` (z testem), nie licz w tekście.
3. **Stop wymaga dokumentu.** Czerwona flaga z oceną (oszustwo, decyzja organu, akcjonariusz > 90% …) wchodzi tylko jako dowód z cytatem z dokumentu w archiwum. Wskaźniki statystyczne (M-score, Z'') nigdy same nie zatrzymują analizy.
4. **Bez rekomendacji kup/sprzedaj.** To, co wynika z zasad właściciela, piszesz jako „wg twoich zasad: …”, czytając aktualne `inwestowanie/zasady-inwestowania.md` (jeśli repozytorium jest w sesji; inaczej piszesz, że zasady były niedostępne).
5. **Fakty oddzielasz od ocen.** Ocena zaczyna się od „Moim zdaniem” albo „Zakładam, że”. Czego nie wiesz — piszesz wprost.

## Przebieg

Pracujesz w katalogu repozytorium. `D` = `analizy/<TICKER>/<RRRR-MM-DD>` (data analizy = dziś).

### Etap 0. Identyfikacja (minuty)

- Ustal rynek (USA albo GPW), pełną nazwę, walutę, typ instrumentu, sektor i ticker w XTB (`<TICKER>.US` albo `<TICKER>.PL`). Właściciel nie podaje instrumentów spoza XTB; jeśli instrument może być niedostępny, dodaj adnotację, nie stop.
- Zapisz `D/analiza.json`: `{"ticker": "…", "rynek": "USA|GPW", "nazwa": "…", "sektor": "ogolny|finanse", "xtb": "…"}`. Sektor „finanse” (bank, ubezpieczyciel, broker, windykacja) wyłącza miary, które tam nie działają (`references/sektory.md`).
- USA: sprawdź CIK w `konfiguracja/sec-cik.yaml` (silnik dopisze go sam, gdy ma adres kontaktowy w `ANALIZA_USER_AGENT`).

### Etap 1. Dane (kod)

- **USA:** `python -m silnik.usa <TICKER>`
- **GPW:** znajdź na stronie relacji inwestorskich (WebSearch/WebFetch tylko do znalezienia adresów) pakiety ESEF z 2–3 ostatnich lat i ostatni raport okresowy PDF, potem:
  `python -m silnik.gpw <TICKER> --esef URL --esef URL --pdf URL`
- Przebieg pobiera dokumenty do archiwum, buduje `fakty.json`, weryfikuje (tożsamości księgowe, drugie źródło), liczy (`obliczenia.md`) i uruchamia bramki (`bramki.md`). Przeczytaj `weryfikacja.md`, `obliczenia.md` i `bramki.md`.
- GPW: dodaj propozycje faktów z raportu PDF (bieżący okres narastający, bilans na koniec okresu, liczba akcji) i uruchom przebieg jeszcze raz. Jeśli właściciel wkleił dane z InvestingPro (konsensus, liczba analityków), zapisz je przez `python -m silnik.dokumenty wklejka` i dodaj jako propozycje typu `prognoza`.

### Etap 2. Bramki (decyzja)

- **STOP** w `bramki.md` → nie piszesz pełnego raportu. Uzupełnij w `D/bramki_dowody.json` cztery testy i warunek powrotu dla bramki stopu (z cytatem), uruchom `python -m silnik.bramki D`, potem `python -m silnik.raport D` (krótki PDF). Koniec.
- **PAUZA** (flagi poważne w ≥ 3 kategoriach) → zatrzymaj się i zapytaj właściciela, czy kontynuować. Pokaż mu listę flag.
- **DALEJ** → sprawdź każdą flagę poważną i flagę wymagającą oceny (np. przyczyna NT 10-K, „material weakness”, szczególne oznaczenie GPW, zawieszenie, rozwodnienie seryjne). Przeczytaj dokument (`python -m silnik.dokumenty url …`, potem `tekst`) i zapisz wynik w `bramki_dowody.json` (poziom `ok`, `flaga`, `flaga_powazna` albo `stop` z cytatem). Sprawdź też bramki modelu z etapów 1, 4 i 5 (`konfiguracja/bramki.yaml`, `bramki_modelu`): opinię biegłego z ostatniego raportu rocznego, akcjonariat (> 90% głosów = STOP), transakcje z podmiotami powiązanymi. Uruchom `python -m silnik.bramki D` po każdej zmianie. Nowy STOP → jak wyżej.

### Etap 3. Biznes, branża, przewaga, zarząd (godzina)

Według `references/biznes-i-przewaga.md`. Źródła: raport roczny (10-K Item 1 i 7; w Polsce sprawozdanie zarządu), prezentacje wynikowe, strony spółki. Każde zdanie z faktem musi dać się wskazać w dokumencie; liczby z tych dokumentów (segmenty, udziały, liczba sklepów) dodajesz jako propozycje z cytatem.

### Etap 4. Co jest w cenie, teza, scenariusze

Według `references/teza-i-scenariusze.md`:
- przeczytaj wycenę odwrotną z `obliczenia.md` (implikowany wzrost FCF, CAP, implikowana marża FCF, PVGO, konsensus);
- napisz tezę z prawdopodobieństwem (procedura w 7 krokach) i antytezy z progami;
- zapisz `D/scenariusze.json` (2–5 scenariuszy, prawdopodobieństwa 5–85% sumujące się do 1, uzasadnienie ze stopą bazową); silnik policzy wartości.

### Etap 5. Raport i PDF

- Napisz `D/raport.md` według `references/szablon-raportu.md` (TL;DR na początku, potem 14 części).
- `python -m silnik.raport D` — lint, renderowanie, PDF. Lint odrzucił → popraw tekst (zamień liczbę na miejsce `{{…}}` albo na słowa bez liczb) i uruchom ponownie.
- Obejrzyj PDF (`pdftoppm -r 60 -png D/raport.pdf /tmp/strona`), sprawdź, czy tabele i wykresy są czytelne.
- Przeczytaj raport jako recenzent: czy każde twierdzenie jakościowe ma źródło w dokumentach, czy oceny zaczynają się od „Moim zdaniem”, czy nie ma rekomendacji.

### Etap 6. Zapis

- `git add D konfiguracja/sec-cik.yaml && git commit` (opis po polsku), `git pull --rebase`, `git push` na `main`.
- Wyślij właścicielowi PDF i streszczenie w 3–5 zdaniach: decyzja bramek, teza z prawdopodobieństwem, co jest w cenie, największe ryzyka, czego nie sprawdziłeś.
- Projekt karty (część 13 raportu) trafia do `inwestowanie/spolki/<TICKER>.md` dopiero po „tak” właściciela.

## Pliki referencyjne

| Plik | Kiedy czytać |
|---|---|
| `references/dane-i-dowody.md` | etap 1–2: źródła, propozycje z PDF i wklejki, dowody do bramek, polecenia `silnik.dokumenty` |
| `references/biznes-i-przewaga.md` | etap 3: jak działa firma, branża, przewaga konkurencyjna, test AI, zarząd |
| `references/teza-i-scenariusze.md` | etap 4: teza, prawdopodobieństwo, scenariusze, konsensus, wiadomości |
| `references/sektory.md` | etap 0 i 3: banki i inne branże z osobnymi miarami |
| `references/trela.md` | etap 4–5: styl Treli, karta punktowa, podział pracy ze Scrab |
| `references/szablon-raportu.md` | etap 5: układ raportu i dostępne miejsca na liczby |
