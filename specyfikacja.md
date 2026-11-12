# Specyfikacja: skill „analiza-spolki” (repo `analiza-fundamentalna`)

Wersja 1.1 · 12.11.2026 (wersja 1 zaakceptowana 10.11.2026). Podstawa: raport „Analiza fundamentalna i wycena spółek” (9.11.2026) i twoje decyzje z 10–12.11.2026. Zmiany wersji 1.1: punkt 13.

## 1. Cel

Podajesz ticker. Skill robi wstępną analizę fundamentalną i oddaje PDF, z którego decydujesz, czy spółka jest warta twojej własnej, pogłębionej analizy. Skill przerywa pracę, gdy znajdzie twardą czerwoną flagę, i pisze dlaczego. Skill nie daje rekomendacji kup/sprzedaj. To, co wynika z twoich zasad, podaje jako „wg twoich zasad: …”.

Najważniejsza zasada architektury: **model nie wpisuje liczb.** Model szuka danych w dokumentach i pisze tekst. Liczby trafiają do rejestru faktów, kod je weryfikuje i liczy, a potem wstawia do raportu.

## 2. Zakres i twoje decyzje

| Sprawa | Decyzja |
|---|---|
| Rynki | USA (rynek główny, także ADR) i GPW (tylko rynek główny) |
| Poza zakresem | inne rynki rozwinięte, Korea jako rynek, NewConnect |
| Benchmark | USA: S&P 500; GPW: WIG |
| Pokrycie analityczne poniżej 3 analityków | Flaga informacyjna na każdym rynku, nie stop: „Pokrycie analityczne małe, nie można na nim polegać” |
| Akcjonariusz z ponad 90% głosów albo ryzyko przymusowego wykupu | STOP |
| Progi bramek z raportu (np. rozwodnienie 10% rocznie, przepływy operacyjne poniżej 70% zysku netto) | Przyjęte jako wersja 1; kalibrujemy na testach |
| Karta punktowa w stylu Treli | Tak; wagi i progi w punkcie 9 |
| Dane z InvestingPro, Scrab i TipRanks | Wklejka na start analizy: tropy, nie źródło prawdy (punkt 3.3, „Materiały od właściciela”) |
| Twoje wstępne zdanie przed raportem | Domyślnie skill o nie nie pyta |
| Długość PDF | Bez limitu; na początku sekcja TL;DR |
| Zasada „Tylko spółki z GPW” w `inwestowanie` | Zmienisz ją osobno; skill czyta aktualne zasady przy każdym uruchomieniu |
| Dostępność w XTB i IKE (12.11.2026) | Skill tego nie sprawdza; XTB ma w ofercie spółki z USA i GPW, a koszty IKE sprawdzasz sam |
| Zakres skilla (12.11.2026) | Tylko analiza fundamentalna; skład portfela, wielkość pozycji i punkty wejścia robi inny segment |

## 3. Architektura: cztery warstwy

```
ticker
  │
  ▼
[1] Archiwum dokumentów ──► [2] Rejestr faktów ──► [3] Weryfikacja i obliczenia ──► [4] Raport
    (pliki źródłowe,           (fakty.json:              (testy, tożsamości,             (tekst modelu z
     adres, data, hash)         każda liczba +            drugie źródło, wskaźniki,       miejscami na liczby,
                                źródło + cytat)           wycena, scenariusze)            kod wstawia liczby,
                                                                                          lint, PDF)
```

### 3.1. Archiwum dokumentów

- Skill zapisuje każdy pobrany plik: JSON z API SEC, raport 10-K/10-Q, PDF raportu kwartalnego, plik ESEF, zrzut tabeli z Biznesradaru, twoją wklejkę.
- Każdy dokument dostaje wpis w `dokumenty.json`: id, adres, data pobrania, typ, suma SHA-256.
- Nikt nie zmienia plików w archiwum. Do repozytorium trafia tylko `dokumenty.json`; same pliki zostają w katalogu roboczym, bo są ciężkie, a adres i suma kontrolna pozwalają je odtworzyć.

### 3.2. Rejestr faktów (`fakty.json`) — źródło prawdy analizy

Każda liczba w raporcie ma wpis w rejestrze. Rejestr ma cztery rodzaje wpisów:

| Rodzaj | Co to jest | Kto tworzy |
|---|---|---|
| `raportowany` | liczba z dokumentu | parser (API, XBRL, tabela PDF, wklejka) albo model z testem cytatu |
| `wyliczony` | liczba policzona z innych faktów | tylko kod; wpis ma wzór i id danych wejściowych |
| `zalozenie` | koszt kapitału, wzrost w scenariuszu, prawdopodobieństwo | model albo ty; wpis ma uzasadnienie |
| `prognoza` | konsensus analityków | parser; wpis ma dostawcę, datę i liczbę analityków |

Przykładowy wpis:

```json
{
  "id": "przychody.FY2025",
  "rodzaj": "raportowany",
  "pozycja": "przychody",
  "okres": {"typ": "FY", "koniec": "2025-06-30"},
  "wartosc": 245122,
  "skala": "mln",
  "waluta": "USD",
  "dokument": "doc-003",
  "miejsce": {"xbrl": "us-gaap:Revenues"},
  "cytat": null,
  "metoda": "xbrl",
  "status": "zweryfikowany",
  "kontrole": ["drugie_zrodlo:doc-007:0.0%", "suma_kwartalow:ok"]
}
```

Wpis wyliczony:

```json
{
  "id": "marza_operacyjna.FY2025",
  "rodzaj": "wyliczony",
  "wzor": "ebit / przychody",
  "wejscia": ["ebit.FY2025", "przychody.FY2025"],
  "wartosc": 0.456,
  "status": "zweryfikowany"
}
```

Status wpisu: `zweryfikowany` (dwa źródła albo dane maszynowe z tożsamościami w porządku), `jedno_zrodlo`, `konflikt`, `odrzucony`. Fakt odrzucony nie wchodzi do obliczeń. Fakt wyliczony dziedziczy najsłabszy status swoich danych wejściowych.

### 3.3. Pozyskanie danych: najpierw dane maszynowe

| Kolejność | USA | GPW |
|---|---|---|
| 1. Dane maszynowe (bez udziału modelu) | API SEC: companyconcept, companyfacts, frames | Raport roczny ESEF (iXBRL) ze strony spółki |
| 2. Tabele z dokumentów | 10-Q/8-K (Ex. 99.1), gdy brak XBRL | PDF raportów kwartalnych przez pdfplumber |
| 3. Drugie źródło | Stock Analysis, Yahoo, Finviz | Biznesradar |
| 4. Wklejka od ciebie | InvestingPro, Scrab | InvestingPro, Scrab |

Model wchodzi do gry dopiero w kroku 2: przypisuje wiersz tabeli do pozycji z tabeli mapowania i podaje dosłowny cytat. ADR (raporty 20-F i 6-K) często nie mają kwartalnych danych XBRL, więc skill traktuje je jako ścieżkę „USA z ograniczonymi danymi”.

**Materiały od właściciela: tropy, nie źródło prawdy.** Właściciel wybiera spółki screenerem (Scrab, TipRanks) i może na początku analizy dołączyć materiał: raport InvestingPro, zrzut ekranu, liczby ze Scrab, własne notatki. Skill traktuje taki materiał tak (decyzja właściciela z 11.11.2026):

1. Materiał to lista tematów i poszlak do dalszej analizy. Skill zapisuje go w archiwum (`wklejka`), a tropy spisuje w `D/tropy.md`: jeden trop w wierszu, z miejscem w materiale.
2. Analiza nie służy potwierdzeniu ani obaleniu tezy z materiału. Skill prowadzi analizę według własnych etapów, a tropy ma na uwadze: sprawdza je w dokumentach pierwotnych przy etapie, którego dotyczą.
3. Przy każdym tropie skill zapisuje wynik: potwierdzony dokumentem (numer dokumentu), sprzeczny z dokumentem, niepotwierdzony albo niesprawdzony. Wynik trafia do części 14 raportu.
4. Liczby ze Scrab skill traktuje jako dobre dane wyjściowe, a liczby z InvestingPro i TipRanks jako dane pomocnicze. Żadne z nich nie zastępują danych z SEC, ESEF ani raportów spółki (krok 4 w tabeli wyżej). Liczba z materiału trafia do rejestru tylko z testem cytatu i statusem `jedno_zrodlo`, a do raportu tylko wtedy, gdy lepszego źródła brak. Rozbieżność między materiałem a silnikiem to trop do sprawdzenia, bo często ujawnia błąd danych po jednej ze stron.
5. Oceny bez jawnej metody (fair value, oceny kondycji finansowej, teksty pisane przez AI dostawcy) nie wchodzą do raportu jako fakty. Mogą być tylko tropem.
6. Aktualność (decyzja z 12.11.2026): silnik ostrzega, gdy materiał odbiega od danych silnika: kurs w arkuszu ceny docelowej albo we wklejce różni się od dzisiejszego kursu o więcej niż próg, EPS w arkuszu od EPS TTM albo konsensusu o więcej niż próg, a data danych we wklejce jest starsza niż próg. Progi są w `konfiguracja/wycena.yaml`. Ostrzeżenia trafiają do `obliczenia.md` i do części „Jakość danych”.

### 3.4. Weryfikacja

1. **Test cytatu.** Dla faktu z PDF albo ze strony skrypt szuka liczby w zapisanym dokumencie, we wskazanym miejscu, po normalizacji zapisu (spacje, przecinki, minus, nawias). Brak liczby oznacza status `odrzucony`.
2. **Tożsamości księgowe.** Aktywa = pasywa; cztery kwartały = rok; suma segmentów ≈ przychody; zmiana gotówki = suma przepływów.
3. **Drugie źródło.** Przychody, zysk operacyjny, zysk netto, przepływy operacyjne, kapitał własny, dług netto i liczba akcji z dwóch niezależnych źródeł. Różnica powyżej 0,5% oznacza `konflikt`.
4. **Jednostki i ciągłość.** Tysiące a miliony, znak, skoki r/r powyżej progu, zmiana definicji pozycji (np. IFRS 18 od 2027 r.).
5. **Daty.** Każdy fakt ma koniec okresu; raport pokazuje, z jakiego dnia są ostatnie dane.

Konflikty i fakty z jednego źródła trafiają do ramki „Jakość danych” w PDF.

### 3.5. Raport bez liczb od modelu

- Model pisze tekst z miejscami na liczby, np. `Przychody wzrosły do {{przychody.FY2025}}, a marża operacyjna wyniosła {{marza_operacyjna.FY2025}}.`
- Renderer wstawia liczbę w formacie „245,1 mld USD | FY do 30.06.2025 | SEC 10-K” i przypis do dokumentu.
- Lint przegląda tekst modelu. Każda cyfra spoza miejsca na liczbę jest błędem, z wyjątkiem lat, dat i numerów etapów. Lint pilnuje też reguły „każda liczba ma walutę, okres i źródło”.
- Recenzent (osobny przebieg modelu) czyta szkic na tle dokumentów i sprawdza twierdzenia jakościowe, których rejestr nie obejmuje: opis biznesu, przewagę konkurencyjną, zarząd.

### 3.6. Czego architektura nie załatwia

- Model może przypisać zły wiersz do pozycji (np. przychody segmentu zamiast przychodów). Część takich błędów łapią tożsamości księgowe; resztę ograniczają tabele mapowania i drugie źródło.
- Oceny jakościowe weryfikuje tylko recenzent, a nie kod.
- Skany PDF bez warstwy tekstowej skill oznacza jako „brak danych”, a nie odczytuje na siłę.

### 3.7. Podział pracy między modele

Wątek główny skilla działa na najlepszym modelu, a pracę, która wymaga czytania wielu dokumentów, zleca subagentom na tańszych modelach. Subagenci są w `.claude/agents/`. Model, effort i narzędzia każdego z nich ustala nagłówek jego pliku i ten nagłówek jest źródłem prawdy; tabela niżej opisuje decyzję z 11.11.2026.

| Kto | Model / effort | Zadanie |
|---|---|---|
| Wątek główny | Opus 5.5 / medium | etap 0, decyzje bramek (w tym każdy STOP), teza, prawdopodobieństwa, scenariusze, raport, zapis |
| `fakty-z-pdf` | Sonnet 5.5 / low | propozycje faktów z raportów PDF (GPW) |
| `dowody-bramek` | Sonnet 5.5 / medium | dowody z cytatami do bramek modelu |
| `badacz-biznesu` | Sonnet 5.5 / medium | fakty o biznesie, konkurencji i zarządzie z cytatami |
| `zasady-wlasciciela` | Sonnet 5.5 / low | wyciąg z zasad właściciela dotyczących spółki |
| `recenzent` | Sonnet 5.5 / medium | recenzja raportu na tle archiwum (punkt 3.5) |
| `wiadomosci` | Haiku 5.5 / low | przyczyny ruchów kursu z linkami, bez liczb |

Zasady podziału:
- Tańszy model dostaje tylko zadania, których wynik sprawdza kod (test cytatu, tożsamości księgowe, drugie źródło) albo wątek główny (każdy STOP i każda flaga poważna). Oceny i tekst raportu zostają na najlepszym modelu.
- Subagent zapisuje wynik w pliku w katalogu analizy i oddaje krótkie streszczenie, więc dokumenty źródłowe nie trafiają do kontekstu wątku głównego.
- Kod wyręcza model w pracy mechanicznej: `python -m silnik.dokumenty fragmenty-bramek` wyciąga fragmenty do bramek, a `python -m silnik.raport D --miejsca` wypisuje miejsca na liczby.
- Analiza nie rozwija silnika. Braki trafiają do `D/braki-silnika.md` i do osobnej sesji. Wyjątek stanowi błąd, który uniemożliwia decyzję bramki.

Podstawa decyzji (pomiar z 10.11.2026, analiza Seagate na jednym modelu Opus 5.5 / medium): 86 zapytań, 14,75 mln tokenów odczytu z cache, 0,20 mln zapisu do cache i 55,9 tys. tokenów wyjścia, razem 5,67 USD. Każde zapytanie czyta cały kontekst rozmowy od nowa, więc koszt rośnie z liczbą zapytań w wątku głównym. Rozwijanie silnika w trakcie analizy kosztowało około 1,0 USD. Szacunek po podziale pracy: 2,1–2,6 USD za podobną analizę. Szacunek sprawdzimy na pierwszej analizie nowej spółki.

## 4. Etapy i bramki stopu

Skill pracuje w kolejności „najtańsze rozstrzygające sprawdzenia najpierw”. Stop zawsze wskazuje fakt albo dokument z archiwum.

| Etap | Co robi | STOP, gdy | Flaga poważna (praca trwa, flaga na TL;DR) |
|---|---|---|---|
| 0. Identyfikacja | rynek, waluta, typ instrumentu, sektor, pokrycie analityczne | upadłość, restrukturyzacja, likwidacja; Lista Alertów; zawieszenie obrotu; brak wiarygodnych sprawozdań | pokrycie poniżej 3 analityków |
| 1. Biegły i regulator | opinia biegłego, zmiany biegłego, terminowość, korekty, sankcje KNF/SEC, NT 10-K/10-Q | opinia negatywna albo odmowa; korekta przyznająca błąd; sankcja za raporty przy tym samym zarządzie; NT z przyczyn księgowych; nieusunięta material weakness | zmiana biegłego bez wyjaśnienia; kluczowe sprawy badania dotyczące przychodów |
| 2. Kapitał | liczba akcji z 5–10 lat, emisje, prawo poboru, zamienne, warranty, skup | seryjne rozwodnienie na szkodę mniejszości | liczba akcji rośnie o ponad 10% rocznie |
| 3. Wypłacalność i jakość zysków | przepływy ÷ zysk netto, memoriały, DSO/DIO, F-score, M-score, Z'', zapadalność długu, kowenanty | istotna niepewność co do kontynuacji + ujemne przepływy + dług do spłaty w 12 mies. bez finansowania; ujemny kapitał własny niewyjaśniony skupem; bank z CET1 poniżej wymogu | przepływy operacyjne poniżej 70% zysku netto przez 3–5 lat; M-score powyżej −1,78; Z'' poniżej 1,10 |
| 4. Ład korporacyjny | akcjonariat, podmioty powiązane, wezwania, insiderzy, raporty krótkich sprzedawców | dowody oszustwa lub tunelowania; większość zysku przez niesprawdzalnych kontrahentów; akcjonariusz z ponad 90% głosów albo ryzyko przymusowego wykupu | duże transakcje z podmiotami powiązanymi; sprzedaż przez insiderów poza planem |
| 5. Biznes i przewaga | jak działa, jak zarabia, branża, konkurenci, przewaga konkurencyjna, test AI, alokacja kapitału | decyzja organu, która odbiera rdzeń biznesu | przewaga „brak” przy wycenie zakładającej długi okres przewagi |
| 6. Sprawozdania | panel dwunastu liczb, korekty (SBC, IFRS 16, prace rozwojowe), miary sektorowe | — | flagi trafiają na TL;DR |
| 7. Co jest w cenie | wycena odwrotna (wzrost, marża, okres przewagi), PVGO, mnożniki, konsensus | — | — |
| 8. Teza i scenariusze | teza, prawdopodobieństwo, scenariusze z wiadomości, pre-mortem, karta Treli, „wg twoich zasad”, projekt karty | — | — |
| 9. Weryfikacja i PDF | walidator, recenzent, lint, PDF | — | — |

Trzy flagi poważne z różnych kategorii naraz: skill robi pauzę i pyta cię, czy kontynuować.

Komunikat stopu (krótki PDF albo wiadomość):
1. Spółka, ticker, etap, data.
2. Powód w jednym zdaniu i dokument, który go potwierdza.
3. Cztery testy: czy problem jest strukturalny, czy dotyczy uczciwości liczb, czy zarząd go rozwiązuje, czy ma termin.
4. Warunek powrotu: co musiałoby się zmienić, żeby wrócić do spółki.

## 5. Ścieżki rynkowe

| Parametr | USA | GPW |
|---|---|---|
| Źródło pierwotne | API SEC, 10-K, 10-Q, 8-K | ESEF, PDF raportów okresowych, ESPI ze strony spółki |
| Drugie źródło | Stock Analysis, Yahoo, Finviz | Biznesradar |
| Konsensus | Stock Analysis, Yahoo, TipRanks, MarketScreener; wklejka z InvestingPro | wklejka z InvestingPro; rekomendacje domów maklerskich z oznaczeniem, czy sponsorowane |
| Koszt kapitału | rentowność 10-letnich obligacji USA z dnia analizy + β × premia Damodarana | rentowność 10-letnich obligacji PL − spread niewypłacalności + β × premia dla Polski |
| Beta (decyzja z 12.11.2026) | beta skorygowana Blume'a z regresji tygodniowej z 5 lat wobec S&P 500 | beta skorygowana Blume'a z regresji tygodniowej z 5 lat wobec WIG |
| Flagi specyficzne | NT, Item 4.01/4.02, material weakness, listy komentarzy SEC, SPAC, VIE, raporty krótkich sprzedawców | Lista Alertów, oznaczenie szczególne, KNF, emisje bez prawa poboru, przymusowy wykup, Skarb Państwa |
| Benchmark | S&P 500 | WIG |

## 6. Sektory z osobnymi miarami

Banki, ubezpieczyciele, brokerzy, windykacja, deweloperzy, studia gier, handel detaliczny, SaaS/IT, energetyka, surowce. Dla każdego sektora plik konfiguracji określa miary zamiast marży i długu netto (np. bank: NIM, koszt ryzyka, C/I, CET1, P/BV wobec ROE).

Typ spółki w `analiza.json` (pole `sektor`) wybiera metodę wyceny w silniku (decyzja z 12.11.2026):

| Typ | Kiedy | Wycena w silniku |
|---|---|---|
| `ogolny` | pozostałe spółki | wycena odwrotna i scenariusze z FCF TTM |
| `cykliczny` | surowce, chemia, stal, półprzewodniki, przewoźnicy i inne spółki z wynikiem zależnym od cyklu | jak `ogolny`, a obok wariant z FCF znormalizowanym (średnia marża FCF z pełnego cyklu × przychody TTM); karta Treli bierze wariant znormalizowany |
| `finanse` | bank, ubezpieczyciel, broker, windykacja | uzasadnione C/WK = (ROE − g) ÷ (koszt kapitału − g), ROE implikowane przez kurs, scenariusze opisane przez ROE |
| `deweloper` | deweloper mieszkaniowy i komercyjny | jak `finanse`, a zadłużenie jako dług netto ÷ kapitał własny |

Silnik ostrzega, gdy spółka oznaczona jako `ogolny` ma zmienność marży FCF i spadki przychodów typowe dla spółki cyklicznej.

## 7. „Co jest w cenie” i prawdopodobieństwa

- Wycena odwrotna w trzech wariantach: jaki wzrost przychodów, jaka marża operacyjna i jaki okres przewagi uzasadniają dzisiejszą cenę.
- Trzy liczby obok siebie: co zakłada cena, co zakłada konsensus (gdy pokrycie wynosi co najmniej 3 analityków) i scenariusz bazowy skilla.
- Scenariusze byka, bazowy i niedźwiedzia z prawdopodobieństwami, które sumują się do 100%; wartość oczekiwana i stosunek zysku do straty.
- Teza bez prawdopodobieństwa (decyzja z 12.11.2026): skill wypisuje 3–5 warunków koniecznych tezy, a przy każdym status: potwierdzony dokumentem (numer dokumentu), sprzeczny z dokumentem albo do sprawdzenia (z miejscem do sprawdzenia). Ocena prawdopodobieństwa tezy należy do twojej analizy miękkiej.
- Skill zapisuje prawdopodobieństwa scenariuszy z datą rozstrzygnięcia, żeby można było później liczyć Brier score.
- Historyczne pasma wyceny: percentyle C/Z, EV/EBIT, EV/EBITDA, C/WK i FCF yield z 5–10 lat obok dzisiejszych mnożników. Skill nie przelicza pasm na kursy, bo punkty wejścia ustala inny segment.
- Tabela wrażliwości: wartość na akcję przy krokach wzrostu i marży FCF (dla `finanse` i `deweloper`: ROE) wokół scenariusza bazowego oraz przy krokach kosztu kapitału i wzrostu rezydualnego. Silnik wskazuje założenie, które najmocniej zmienia wartość.
- Profil ryzyka kursu wobec benchmarku (S&P 500 albo WIG), z 5 lat notowań: beta skorygowana Blume'a, beta sektorowa Damodarana przeliczona na zadłużenie spółki (kontrola), zmienność roczna, maksymalne obsunięcie kursu, czas powrotu do szczytu i korelacja. Skill nie porównuje spółki z portfelem.
- Prawdopodobieństwo upadłości w ciągu roku z modelu Ohlsona raport podaje jedną liczbą w procentach, bez wartości O-score i bez składników.

### 7.1. Cena docelowa wg arkusza właściciela

Właściciel liczy cenę docelową w swoim arkuszu „Cena-docelowa.xlsx” (metoda Tomasza Treli, tradingforaliving.pl; dane ze Scrab). Decyzje właściciela z 11.11.2026: skill nie liczy tej wyceny sam, tylko przepisuje wyniki arkusza i traktuje je jako wycenę właściciela według jego założeń; plik dołącza właściciel do rozmowy; miejsce w części 8 raportu; potencjał konserwatywny jest miarą karty Treli; jedno wyliczenie na datę analizy, bez dziennika rewizji.

- Plik jest opcjonalny. Skill kopiuje go do `D/cena-docelowa.xlsx`. Bez pliku raport i karta pomijają tę część bez wpisu w brakach danych.
- Silnik odczytuje z zakładki „Cena docelowa” wartości policzone przez arkusz (dane wejściowe, ceny docelowe z P/E i P/S, średnią, potencjały) i zapisuje plik w archiwum jako `wklejka`. Każda liczba trafia do rejestru ze statusem `jedno_zrodlo` i z adresem komórki (punkt 3.3).
- Ticker w arkuszu musi zgadzać się z analizowaną spółką; inaczej silnik nie wstawia żadnej liczby.
- Datą wyceny jest zawsze data analizy (decyzja właściciela z 11.11.2026), bo zakładka „Cena docelowa” nie ma własnej daty.
- Progi miary w karcie Treli: potencjał konserwatywny −40% daje 0 pkt, a +40% daje 10 pkt (`konfiguracja/karta-treli.yaml`; zgoda właściciela z 11.11.2026).
- Raport podaje wynik jako „wg twojego arkusza”, z założeniami arkusza. To wycena przy założeniach właściciela, a nie prognoza kursu ani rekomendacja.

## 8. Strona TL;DR i układ PDF

**TL;DR (strona 1):** jedno zdanie o spółce; werdykt etapu bramek (przeszła / flagi poważne); trzy najważniejsze flagi; przewaga konkurencyjna (brak / wąska / szeroka, trend); co jest w cenie w jednym zdaniu; teza w 3 zdaniach z warunkami koniecznymi; tabela scenariuszy; karta Treli; „wg twoich zasad”; pokrycie analityczne; data danych.

**Dalsze części:** 1. Jak działa firma · 2. Jak zarabia · 3. Najważniejsze fakty (akcjonariat, zarząd, płynność, kalendarz) · 4. Branża, konkurencja (tabela 4–6 konkurentów z danymi z SEC albo Biznesradaru), przewaga · 5. Zarząd i alokacja kapitału · 6. Sprawozdania i wykresy · 7. Jakość zysków i flagi · 8. Co jest w cenie · 9. Teza, antytezy z progami, pre-mortem · 10. Wiadomości i scenariusze, byki mówią / niedźwiedzie mówią · 11. Karta Treli · 12. Do dalszej analizy: otwarte pytania ze źródłem do sprawdzenia, najważniejsze założenie wyceny, kalendarz zdarzeń, progi zmiany tezy · 13. Projekt karty w formacie `spolki/<TICKER>.md` · 14. Jakość danych · Aneksy i słowniczek.

## 9. Karta punktowa w stylu Treli

Każda miara dostaje 0–10 punktów na liniowej skali między dwoma progami. Wynik filaru to średnia jego miar; wynik karty to suma ważona.

| Filar | Waga | Miary |
|---|---|---|
| Wzrost | 30% | przychody i EPS: CAGR z 3 lat oraz prognoza na 2 lata |
| Jakość i stabilność | 25% | ROIC, FCF po SBC ÷ zysk netto, dług netto/EBITDA, Z'' |
| Wycena | 20% | EV/EBIT i FCF yield wobec własnej historii z 5 lat i sektora; wzrost implikowany z wyceny odwrotnej; potencjał do ceny docelowej z arkusza właściciela, wariant konserwatywny (punkt 7.1) |
| Analitycy | 15% | kierunek rewizji EPS z 90 dni, potencjał do średniej ceny docelowej |
| Momentum | 10% | stopa zwrotu z 12 mies. bez ostatniego miesiąca, wobec benchmarku |

- Przy pokryciu poniżej 3 analityków filar „Analitycy” dostaje „brak danych”, a jego waga przechodzi proporcjonalnie na pozostałe filary. Karta pokazuje adnotację „karta z czterech filarów”.
- Progi skal są osobne dla USA i GPW (plik `konfiguracja/karta-treli.yaml`).
- Wagi i progi to moja propozycja, a nie publikowana metoda Treli. Karta jest informacją, a nie bramką.
- Gdy we wklejce jest wynik Scrab, silnik porównuje go z wynikiem karty po sprowadzeniu obu do skali 0–100 i oznacza rozbieżność powyżej progu z `konfiguracja/karta-treli.yaml`. Raport komentuje kartę tylko przy takim oznaczeniu (decyzja z 12.11.2026).

## 10. Struktura repozytorium

```
analiza-fundamentalna/
├── CLAUDE.md                     # zasady projektu, gdzie co jest, styl
├── README.md                     # jak uruchomić analizę
├── .claude/skills/analiza-spolki/
│   ├── SKILL.md                  # etapy, bramki, lista kontrolna (< 500 linii)
│   └── references/               # etapy-i-flagi.md, rynki.md, wycena.md, sektory.md, trela.md, pdf.md
├── .claude/agents/               # subagenci skilla na tańszych modelach (punkt 3.7)
├── silnik/                       # pakiet Python
│   ├── pobieranie/               # sec.py, esef.py, pdf.py, wklejka.py, archiwum.py
│   ├── fakty/                    # schemat.py, rejestr.py, weryfikacja.py
│   ├── obliczenia/               # wskazniki.py, wycena.py, scenariusze.py, karta_treli.py
│   └── raport/                   # szablony, render.py, lint.py, wykresy.py, pdf.py
├── konfiguracja/                 # mapowanie-us-gaap.yaml, mapowanie-mssf.yaml, progi.yaml, sektory.yaml, karta-treli.yaml
├── testy/                        # testy jednostkowe + spółki testowe
└── analizy/<TICKER>/<RRRR-MM-DD>/
    ├── dokumenty.json
    ├── fakty.json
    ├── raport.md
    └── raport.pdf (albo stop.md)
```

- Progi bramek i karty Treli są parametrami metody, więc żyją w tym repozytorium (`konfiguracja/`).
- Twoje zasady (limit Agresywnego, pauza po rajdzie, benchmarki) zostają w `inwestowanie/zasady-inwestowania.md`. Skill czyta je przy każdym uruchomieniu; sesja potrzebuje wtedy obu repozytoriów. Bez dostępu do `inwestowanie` sekcja „wg twoich zasad” dostaje adnotację „zasady niedostępne”.
- Po każdej pełnej analizie skill zapisuje projekt karty w `inwestowanie`: spółka z portfela w `spolki/<TICKER>.md`, kandydat w `analiza/kandydaci/<TICKER>.md`. Po każdej analizie wysyła ci mail z PDF w załączniku. Szczegóły: `SKILL.md`, etap 6.
- Skill działa w sesjach Claude Code (w chmurze albo lokalnie) otwartych na tym repozytorium, bo potrzebuje Pythona i plików.

## 11. Plan budowy

| Krok | Co powstaje | Jak sprawdzamy |
|---|---|---|
| 1 | CLAUDE.md, README, schemat `fakty.json`, archiwum dokumentów | testy schematu |
| 2 | Pobieranie z API SEC + weryfikacja (tożsamości, drugie źródło) | rejestr dla 2 spółek z USA bez konfliktów |
| 3 | Odczyt ESEF i PDF dla GPW + test cytatu | rejestr dla 2 spółek z GPW |
| 4 | Obliczenia: panel dwunastu liczb, F/M/Z'', wycena odwrotna, scenariusze, karta Treli | testy na liczbach policzonych ręcznie |
| 5 | Bramki stopu | spółka z Listy Alertów i spółka z „going concern” zatrzymują się na właściwym etapie |
| 6 | Raport: szablon z miejscami na liczby, lint, PDF z polskimi znakami | lint bez błędów, PDF czytelny |
| 7 | SKILL.md i pliki referencyjne | pełne przebiegi na 6 spółkach testowych |
| 8 | Podział pracy między modele (punkt 3.7) | pierwszy przebieg na nowej spółce |
| 9 | Wersja 1.1 (punkt 13): wycena według typu spółki, profil ryzyka, beta sektorowa, pasma wyceny, wrażliwość, konkurenci, dywidendy, aktualność materiałów, nowy układ raportu | testy jednostkowe; parsery stron Damodarana i moduł konkurentów sprawdzi pierwszy przebieg z dostępem do sieci |

Spółki testowe (propozycja): duża spółka z USA z głębokim pokryciem (np. MSFT), ADR (np. SK Hynix, SKHY), bank z WIG20, średnia spółka przemysłowa z GPW, spółka z Listy Alertów, spółka z USA z zastrzeżeniem o kontynuacji działalności. Przy każdej oceniasz, czy stop był uzasadniony i czy raport odpowiada na twoje punkty.

## 12. Sposób pracy w repozytorium

- Zapis na gałęzi `main` (commit i push, przed zapisem `git pull`).
- Całe analizy trafiają do repozytorium: `analizy/<TICKER>/<RRRR-MM-DD>/` z plikami `dokumenty.json`, `fakty.json`, `raport.md` i `raport.pdf` (albo `stop.md`). Pliki źródłowe z archiwum zostają poza repozytorium.

## 13. Zmiany w wersji 1.1 (decyzje z 12.11.2026)

Zasada: wynik skilla to punkt wyjścia do twojej analizy miękkiej. Skład portfela, wielkość pozycji i punkty wejścia robi inny segment, więc skill ich nie liczy.

| Nr | Zmiana | Gdzie |
|---|---|---|
| 1 | Warunki konieczne tezy zamiast prawdopodobieństwa tezy; prawdopodobieństwa scenariuszy zostają | punkt 7, 8 |
| 2 | Wycena według typu spółki: `cykliczny` (FCF znormalizowany), `finanse` i `deweloper` (C/WK wobec ROE) | punkt 6 |
| 3 | Ostrzeżenia o nieaktualnym materiale od właściciela: kurs i EPS w arkuszu ceny docelowej, wiek wklejki, konsensus z wklejki wobec konsensusu silnika | punkt 3.3, 7.1 |
| 4 | Ohlson: w raporcie tylko prawdopodobieństwo upadłości w ciągu roku w procentach | punkt 7 |
| 5 | Bez sprawdzania dostępności w XTB i bez części o IKE | punkt 2, 4, 5, 8 |
| 6 | Komentarz do karty Treli tylko przy dużej rozbieżności z wynikiem Scrab | punkt 9 |
| 7 | Nowa część 12 „Do dalszej analizy” i tabela wrażliwości | punkt 7, 8 |
| 8 | Historyczne pasma wyceny bez przeliczania na kursy | punkt 7 |
| 9 | Profil ryzyka kursu wobec benchmarku i beta sektorowa Damodarana jako kontrola | punkt 7 |
| 10 | Dywidendy: stopa dywidendy, wypłata z zysku netto i z FCF, stopa zwrotu dla akcjonariuszy | część 5 raportu |
| 11 | Tabela konkurentów w części 4 | punkt 8 |
| 12 | Beta skorygowana Blume'a w koszcie kapitału (zbudowana wcześniej tego dnia) | punkt 5 |
| 13 | Projekt karty zapisywany w `inwestowanie` po każdej pełnej analizie (bez czekania na „tak”) i mail z PDF po każdej analizie | punkt 10, `SKILL.md` etap 6 |
