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
6. **Nie rozwijasz silnika w trakcie analizy.** Brak w silniku zapisujesz w `D/braki-silnika.md` (co, dlaczego, przykład z tej spółki), dodajesz sugerowane zadanie i w raporcie piszesz „brak danych”. Wyjątek: błąd, który uniemożliwia decyzję bramki. Taki błąd poprawiasz od razu, z testem.

## Podział pracy między modele

Ty (wątek główny) prowadzisz analizę, rozstrzygasz bramki, piszesz tezę, scenariusze i raport. Pracę, która wymaga czytania wielu dokumentów, zlecasz subagentom z `.claude/agents/` (narzędzie Agent, parametr `subagent_type`). Subagent zapisuje wynik w pliku w `D`, a tobie oddaje krótkie streszczenie. Wynik subagenta czytasz z pliku, a nie z pamięci rozmowy. Uzasadnienie i oszacowanie kosztów: `specyfikacja.md`, punkt 3.7.

| Subagent | Etap | Wynik |
|---|---|---|
| `fakty-z-pdf` | 1 (GPW) | propozycje faktów z raportu PDF w `D/propozycje.json` |
| `dowody-bramek` | 2 | `D/bramki_dowody.json` z cytatami |
| `badacz-biznesu` | 3 | `D/notatki-biznes.md` i propozycje liczb |
| `zasady-wlasciciela` | 4 | wyciąg z zasad właściciela w odpowiedzi |
| `wiadomosci` | 4 | przyczyny ruchu kursu z linkami w odpowiedzi |
| `recenzent` | 5 | lista poprawek raportu w odpowiedzi |

Subagentów niezależnych od siebie uruchamiasz w jednej wiadomości, np. `badacz-biznesu`, `zasady-wlasciciela` i `wiadomosci` po decyzji DALEJ. Każde twoje zapytanie czyta cały kontekst rozmowy od nowa, dlatego łączysz odczyty w jedno polecenie powłoki i nie czytasz plików, których etap nie potrzebuje (także przykładowych raportów innych spółek).

## Przebieg

Pracujesz w katalogu repozytorium. `D` = `analizy/<TICKER>/<RRRR-MM-DD>` (data analizy = dziś).

### Etap 0. Identyfikacja (minuty)

- Ustal rynek (USA albo GPW), pełną nazwę, walutę, typ instrumentu, sektor i ticker w XTB (`<TICKER>.US` albo `<TICKER>.PL`). Właściciel nie podaje instrumentów spoza XTB; jeśli instrument może być niedostępny, dodaj adnotację, nie stop.
- Zapisz `D/analiza.json`: `{"ticker": "…", "rynek": "USA|GPW", "nazwa": "…", "sektor": "ogolny|finanse", "xtb": "…"}`. Sektor „finanse” (bank, ubezpieczyciel, broker, windykacja) wyłącza miary, które tam nie działają (`references/sektory.md`).
- USA: sprawdź CIK w `konfiguracja/sec-cik.yaml` (silnik dopisze go sam, gdy ma adres kontaktowy w `ANALIZA_USER_AGENT`).
- Jeśli właściciel dołączył materiał (InvestingPro, Scrab, TipRanks, zrzut ekranu, notatki), zapisz go w archiwum (`python -m silnik.dokumenty wklejka`; PDF najpierw zamień na tekst `pdftotext -layout`) i spisz tropy w `D/tropy.md`. Materiał to lista tematów i poszlak, a nie źródło prawdy ani teza do potwierdzenia: zasady w `specyfikacja.md`, punkt 3.3, „Materiały od właściciela”.
- Cena docelowa z arkusza właściciela: jeśli właściciel dołączył plik `Cena-docelowa.xlsx`, skopiuj go bez zmian do `D/cena-docelowa.xlsx`. Silnik sam zapisze go w archiwum i odczyta wyniki (`specyfikacja.md`, punkt 7.1). Nie licz tej wyceny sam i nie przepisuj liczb ze zrzutu ekranu. Bez pliku pomiń tę część.

### Etap 1. Dane (kod)

- **USA:** `python -m silnik.usa <TICKER>`
- **GPW:** znajdź na stronie relacji inwestorskich (WebSearch/WebFetch tylko do znalezienia adresów) pakiety ESEF z 2–3 ostatnich lat i ostatni raport okresowy PDF, potem:
  `python -m silnik.gpw <TICKER> --esef URL --esef URL --pdf URL`
- Przebieg pobiera dokumenty do archiwum, buduje `fakty.json`, weryfikuje (tożsamości księgowe, drugie źródło), liczy (`obliczenia.md`) i uruchamia bramki (`bramki.md`). Przeczytaj `weryfikacja.md`, `obliczenia.md` i `bramki.md` jednym poleceniem.
- GPW: zleć subagentowi `fakty-z-pdf` propozycje faktów z raportu PDF (bieżący okres narastający, bilans na koniec okresu, liczba akcji); podaj mu `D`, numer dokumentu i polecenie przebiegu GPW. Jeśli właściciel wkleił dane z InvestingPro (konsensus, liczba analityków), zapisz je przez `python -m silnik.dokumenty wklejka` i dodaj jako propozycje typu `prognoza`.

### Etap 2. Bramki (decyzja)

- **STOP** w `bramki.md` → nie piszesz pełnego raportu. Uzupełnij w `D/bramki_dowody.json` cztery testy i warunek powrotu dla bramki stopu (z cytatem), uruchom `python -m silnik.bramki D`, potem `python -m silnik.raport D` (krótki PDF). Koniec.
- **PAUZA** (flagi poważne w ≥ 3 kategoriach) → zatrzymaj się i zapytaj właściciela, czy kontynuować. Pokaż mu listę flag.
- **DALEJ** → uruchom `python -m silnik.dokumenty fragmenty-bramek D` i zleć subagentowi `dowody-bramek` ocenę. Podaj mu `D` i listę: każda flaga poważna i flaga wymagająca oceny z `bramki.md` (np. przyczyna NT 10-K, „material weakness”, szczególne oznaczenie GPW, zawieszenie, rozwodnienie seryjne) oraz bramki modelu z etapów 1, 4 i 5 (`konfiguracja/bramki.yaml`, `bramki_modelu`): opinia biegłego z ostatniego raportu rocznego, akcjonariat (> 90% głosów = STOP), transakcje z podmiotami powiązanymi, sprzedaż przez insiderów. Subagent zapisuje `bramki_dowody.json` i uruchamia `python -m silnik.bramki D`.
- Każdy wpis `stop` i `flaga_powazna` sprawdzasz sam: czytasz cytat w `bramki_dowody.json` i fragment dokumentu wokół niego (`python -m silnik.dokumenty tekst D doc-… --szukaj …`). Decyzję o STOP podejmujesz ty, a nie subagent. Nowy STOP → jak wyżej.

### Etap 3. Biznes, branża, przewaga, zarząd (godzina)

Zleć subagentowi `badacz-biznesu` zebranie faktów (podaj `D`; jeśli jest `D/tropy.md`, subagent sprawdzi tropy dotyczące biznesu). Wynik przeczytaj z `D/notatki-biznes.md` i uruchom przebieg danych jeszcze raz, jeśli subagent dodał propozycje. Oceny według `references/biznes-i-przewaga.md` wydajesz ty: werdykt o przewadze konkurencyjnej, test AI, ocenę zarządu. Każde zdanie z faktem musi dać się wskazać w dokumencie. Fakt, którego nie ma w notatkach ani w archiwum, nie trafia do raportu.

### Etap 4. Co jest w cenie, teza, scenariusze

Według `references/teza-i-scenariusze.md`:
- przeczytaj wycenę odwrotną z `obliczenia.md` (implikowany wzrost FCF, CAP, implikowana marża FCF, PVGO, konsensus) i cenę docelową z arkusza właściciela (gdy jest `D/cena-docelowa.xlsx`);
- przyczyny ostatnich ruchów kursu zleć subagentowi `wiadomosci`, a wyciąg z zasad właściciela subagentowi `zasady-wlasciciela` (podaj mu `D` i ścieżkę do repozytorium `inwestowanie`);
- napisz tezę z prawdopodobieństwem (procedura w 7 krokach) i antytezy z progami;
- zapisz `D/scenariusze.json` (2–5 scenariuszy, prawdopodobieństwa 5–85% sumujące się do 1, uzasadnienie ze stopą bazową); silnik policzy wartości.

### Etap 5. Raport i PDF

- Listę dostępnych miejsc na liczby wypisze `python -m silnik.raport D --miejsca`. Nie przeglądaj `fakty.json` skryptami i nie czytaj raportów innych spółek jako przykładu.
- Napisz `D/raport.md` według `references/szablon-raportu.md` (TL;DR na początku, potem 14 części).
- `python -m silnik.raport D` — lint, renderowanie, PDF. Lint odrzucił → popraw tekst (zamień liczbę na miejsce `{{…}}` albo na słowa bez liczb) i uruchom ponownie.
- Obejrzyj PDF (`pdftoppm -r 60 -png D/raport.pdf /tmp/strona`), sprawdź, czy tabele i wykresy są czytelne.
- Zleć subagentowi `recenzent` sprawdzenie raportu (podaj `D`). Recenzent sprawdza każde zdanie z faktem (także jakościowym, np. „spółka posiada nieruchomości”) w archiwum, oddzielenie ocen od faktów i brak rekomendacji. Zdanie oznaczone „brak w archiwum” usuwasz albo oznaczasz jako niesprawdzone, potem budujesz PDF jeszcze raz. (Przebieg Dino z 10.11.2026: model wpisał z pamięci fakt o nieruchomościach, którego nie było w dokumentach.)

### Etap 6. Zapis

- `git add D konfiguracja/sec-cik.yaml && git commit` (opis po polsku), `git pull --rebase`, `git push` na `main`.
- Jeśli powstał `D/braki-silnika.md`, wymień braki w streszczeniu dla właściciela.
- Wyślij właścicielowi PDF i streszczenie w 3–5 zdaniach: decyzja bramek, teza z prawdopodobieństwem, co jest w cenie, największe ryzyka, czego nie sprawdziłeś. Jeśli był materiał od właściciela, dodaj jedno zdanie o tropach, które coś zmieniły w analizie.
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
