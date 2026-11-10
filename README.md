# analiza-fundamentalna

Skill „analiza-spolki”: wstępna analiza fundamentalna spółki z USA albo z GPW, zakończona raportem PDF albo uzasadnionym stopem. Projekt: `specyfikacja.md`. Zasady pracy: `CLAUDE.md`.

## Stan budowy

Plan ma 7 kroków (`specyfikacja.md`, część 11).

| Krok | Zakres | Stan |
|---|---|---|
| 1 | Schemat rejestru faktów, rejestr, archiwum dokumentów | gotowy |
| 2 | Pobieranie z API SEC i weryfikacja (tożsamości, drugie źródło) | gotowy |
| 3 | Odczyt ESEF i PDF dla GPW, test cytatu | gotowy |
| 4 | Obliczenia: wskaźniki, wycena odwrotna, scenariusze, karta Treli | gotowy |
| 5 | Bramki stopu | gotowy |
| 6 | Raport: szablon z miejscami na liczby, lint, PDF | gotowy |
| 7 | SKILL.md i pełne przebiegi na spółkach testowych | gotowy: skill, pełne raporty MSFT, DNP i PKO, stopy PBG i DPLS |

## Skill

Skill „analiza-spolki” jest w `.claude/skills/analiza-spolki/` (SKILL.md i pliki referencyjne). Działa w sesjach Claude Code otwartych na tym repozytorium. Polecenie dla modelu do pracy z dokumentami: `python -m silnik.dokumenty` (pobieranie do archiwum, wklejka, tekst do cytatów).

| Spółka testowa | Ścieżka | Wynik |
|---|---|---|
| Microsoft (MSFT) | USA, głębokie pokrycie | pełny raport PDF |
| PBG | GPW, Lista Alertów | STOP na etapie 0, PDF stopu |
| DarkPulse (DPLS) | USA, kontynuacja działalności | STOP na etapie 3, PDF stopu |
| PKO BP (PKO) | GPW, bank (sektor finanse) | pełny raport PDF |
| Dino (DNP) | GPW, ESEF + PDF | pełny raport PDF |

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

## Wycena, scenariusze i karta Treli (krok 4b)

**Dane rynkowe** (pobiera je przebieg danych):

| Dane | USA | GPW |
|---|---|---|
| Kurs, obroty, momentum 12–1 | Yahoo (gdy odmawia: Stock Analysis, 6 miesięcy, bez momentum) | Biznesradar, notowania historyczne |
| Indeks do momentum | S&P 500 (Yahoo) | WIG (Biznesradar) |
| Kontrola kursu (drugie źródło, ten sam dzień) | Stock Analysis | Yahoo |
| Liczba akcji | SEC (dei:EntityCommonStockSharesOutstanding) | Biznesradar, strona notowań |
| Rentowność obligacji 10-letnich | Treasury.gov | Strefa Inwestorów (tabela rentowności); `--rf` nadpisuje |
| Premia za ryzyko akcji, spread kraju | Damodaran (ctryprem) | Damodaran (ctryprem) |

**Wycena** (`silnik/obliczenia/wycena.py`, parametry w `konfiguracja/wycena.yaml`):
- koszt kapitału własnego = stopa wolna od ryzyka + beta × premia za ryzyko akcji; dla GPW stopa wolna od ryzyka = rentowność 10-letnich obligacji − spread niewypłacalności Polski (bez podwójnego liczenia ryzyka kraju); beta domyślnie 1 (założenie w rejestrze);
- mnożniki: C/Z, EV/EBIT, EV/EBITDA, C/WK, FCF yield; udział PVGO w cenie;
- wycena odwrotna w trzech wariantach: implikowany wzrost FCF przez 10 lat, implikowany okres przewagi (CAP) przy wzroście historycznym, implikowana marża FCF przy wzroście historycznym. Wzrost historyczny = niższy z CAGR przychodów 3- i 5-letniego.

**Scenariusze:** model zapisuje `analizy/<TICKER>/<data>/scenariusze.json` (2–5 scenariuszy, prawdopodobieństwa 5–85% sumujące się do 1, wzrost przychodów, marża FCF, uzasadnienie). Silnik liczy wartość na akcję w każdym scenariuszu, wartość oczekiwaną, potencjał wobec kursu, prawdopodobieństwo straty i asymetrię.

```json
{"scenariusze": [
  {"nazwa": "byk", "prawdopodobienstwo": 0.25, "wzrost_przychodow": 0.12, "marza_fcf": 0.30, "uzasadnienie": "…"},
  {"nazwa": "bazowy", "prawdopodobienstwo": 0.50, "wzrost_przychodow": 0.08, "marza_fcf": 0.25, "uzasadnienie": "…"},
  {"nazwa": "niedzwiedz", "prawdopodobienstwo": 0.25, "wzrost_przychodow": 0.03, "marza_fcf": 0.18, "uzasadnienie": "…"}]}
```

**Karta w stylu Treli** (`konfiguracja/karta-treli.yaml`): pięć filarów (wzrost 30%, jakość 25%, wycena 20%, analitycy 15%, momentum 10%), każda miara 0–10 pkt liniowo między progami, osobnymi dla USA i GPW. Filar bez danych (np. „analitycy” przy pokryciu poniżej 3 analityków) przekazuje wagę pozostałym. Karta jest informacją, nie bramką.

## Bramki stopu (krok 5)

Przebiegi `silnik.usa` i `silnik.gpw` uruchamiają bramki same. Osobno: `python -m silnik.bramki analizy/<TICKER>/<data>`. Progi i lista bramek: `konfiguracja/bramki.yaml`.

**Decyzja:** STOP (pierwsza twarda flaga według etapu), PAUZA (flagi poważne w co najmniej 3 kategoriach — skill pyta, czy kontynuować) albo DALEJ. Wynik: `bramki.md`, `bramki.json` i przy stopie `stop.md` (powód, dowód, cztery testy, warunek powrotu).

**Sprawdzenia automatyczne:**

| Etap | USA | GPW | Oba rynki (z rejestru) |
|---:|---|---|---|
| 0 | pokrycie analityczne: 3 analityków lub mniej = STOP (zasady właściciela) | Lista Alertów (STOP), szczególne oznaczenie, zawieszenia obrotu; pokrycie: 3 lub mniej = flaga | brak danych o pokryciu = informacja |
| 1 | 8-K 4.02 — korekta sprawozdań (STOP), NT 10-K/NT 10-Q, 8-K 4.01 — zmiana biegłego, wzmianka „material weakness” | — | — |
| 2 | — | — | rozwodnienie > 10% r/r; seryjne (3 z 5 lat) = flaga poważna |
| 3 | wzmianka „substantial doubt”; razem z ujemnymi przepływami i zobowiązaniami krótkoterminowymi > aktywa obrotowe = STOP | — | przepływy ÷ zysk netto (3 lata) < 70%, M-score > −1,78, Z'' < 1,10, ujemny kapitał niewyjaśniony skupem (STOP) |

**Dowody od modelu** (`bramki_dowody.json`): bramki wymagające oceny (opinia biegłego, sankcje, oszustwo, akcjonariusz > 90%, decyzja organu, brak przewagi itd.). Silnik przyjmuje dowód tylko z cytatem obecnym w dokumencie z archiwum; STOP wymaga też czterech testów i warunku powrotu. Dowód modelu zastępuje automatyczny wynik tej samej bramki (np. model ocenia, czy NT miało przyczyny księgowe).

```json
{"dowody": [{"bramka": "B4.akcjonariusz_90", "poziom": "stop", "dokument": "doc-012", "strona": 5,
  "cytat": "…dosłowny fragment…", "opis": "…",
  "testy": {"strukturalny": "…", "uczciwosc_liczb": "…", "zarzad_rozwiazuje": "…", "termin": "…"},
  "warunek_powrotu": "…"}]}
```

Przypadki testowe w `analizy/`: PBG (Lista Alertów → STOP na etapie 0) i DarkPulse, DPLS (istotna niepewność kontynuacji + ujemne przepływy + brak pokrycia zobowiązań → STOP na etapie 3).

## Raport PDF (krok 6)

```bash
python -m silnik.raport analizy/<TICKER>/<data>
```

- **STOP z bramek:** krótki PDF ze `stop.md` i tabelą wszystkich bramek.
- **Inaczej:** model pisze `raport.md` z miejscami na liczby; silnik sprawdza tekst (lint), wstawia wartości z rejestru z przypisami źródeł, dokłada tabele i wykresy generowane przez kod i buduje `raport.pdf` (oraz `raport_wyrenderowany.md` do wglądu).

Miejsca w `raport.md`:

| Miejsce | Co wstawia silnik |
|---|---|
| `{{id_faktu}}`, np. `{{marza_operacyjna.TTM2026-09-30}}` | wartość po polsku (np. „47,1%”, „331,8 mld USD”) i przypis: okres, źródło albo wzór, status weryfikacji |
| `{{tabela:panel}}`, `{{tabela:wycena}}`, `{{tabela:scenariusze}}`, `{{tabela:karta}}`, `{{tabela:bramki}}`, `{{tabela:jakosc_danych}}` | tabele z obliczeń, bramek i weryfikacji |
| `{{wykres:przychody}}`, `{{wykres:marze}}`, `{{wykres:fcf_zysk}}`, `{{wykres:roic}}` | wykresy z faktów rejestru |

**Lint** odrzuca raport, gdy w tekście modelu jest jakakolwiek cyfra albo znak % poza miejscami na liczby. Wyjątki: lata (1990–2049; starsze tylko z „r.”/„roku”), daty, etykiety okresów (FY2025, Q3, H1, M9, TTM), numeracja nagłówków i list, nazwy typu S&P 500, MSSF 16, 10-K. Lint odrzuca też miejsce wskazujące nieistniejący albo odrzucony fakt.

PDF: ReportLab z czcionką DejaVu (polskie znaki), wykresy matplotlib (paleta i zasady z wytycznych dataviz: jedna oś, legenda przy 2+ seriach, etykiety na końcach linii).

## Jak działa rejestr faktów

- `silnik/pobieranie/archiwum.py` zapisuje każdy pobrany dokument poza repozytorium i dopisuje go do `analizy/<TICKER>/<data>/dokumenty.json` (id, adres, data pobrania, SHA-256).
- `silnik/fakty/rejestr.py` przyjmuje tylko fakty zgodne ze schematem: fakt raportowany musi wskazywać istniejący dokument, fakt z tekstu musi mieć cytat dosłowny, kwota musi mieć walutę, założenie musi mieć uzasadnienie, a prognoza — dostawcę, datę i liczbę analityków.
- Fakty wyliczone tworzy tylko kod (`RejestrFaktow.wylicz`). Wpis zapamiętuje wzór i dane wejściowe, a status dziedziczy po najsłabszym wejściu. Z faktów odrzuconych kod niczego nie liczy.
