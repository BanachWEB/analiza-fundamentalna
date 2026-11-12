# Dane i dowody

## Spis treści
1. Źródła według rynku
2. Polecenia do pracy z dokumentami
3. Propozycje faktów (PDF, strona, wklejka)
4. Dowody do bramek
5. Czego nie robić

## 1. Źródła według rynku

| Dane | USA | GPW |
|---|---|---|
| Sprawozdania | SEC XBRL (automatycznie) | ESEF z relacji inwestorskich (automatycznie z adresu), raporty PDF (propozycje) |
| Drugie źródło | Stock Analysis (automatycznie) | Biznesradar (automatycznie) |
| Kurs, momentum, obroty | Yahoo, awaryjnie Stock Analysis | Biznesradar |
| Konsensus, liczba analityków | Stock Analysis (S&P Global, automatycznie) | wklejka z InvestingPro od właściciela |
| Treść raportów (biznes, ryzyka, opinia biegłego) | 10-K, 10-Q, 8-K, DEF 14A z EDGAR | raport roczny i sprawozdanie zarządu (PDF), raporty ESPI na stronie spółki |
| Flagi | EDGAR: NT, 8-K 4.01/4.02, wyszukiwanie pełnotekstowe (automatycznie) | GPW: Lista Alertów, oznaczenie szczególne, zawieszenia (automatycznie) |

Strony, które odmawiają (403): Bankier, Macrotrends, Morningstar, Seeking Alpha. Nie obchodź blokad. WebSearch i WebFetch służą do znajdowania adresów i kontekstu, nigdy do przepisywania liczb: WebFetch przepuszcza stronę przez model streszczający.

## 2. Polecenia

```
python -m silnik.dokumenty url     D URL --opis "raport roczny 2025" --typ raport_pdf --zrodlo spółka
python -m silnik.dokumenty tekst   D doc-012 --strona 47
python -m silnik.dokumenty tekst   D doc-012 --szukaj "Przychody ze sprzedaży"
python -m silnik.dokumenty wklejka D wklejka.txt --zrodlo InvestingPro --opis "konsensus"
python -m silnik.dokumenty lista   D
python -m silnik.dokumenty fragmenty-bramek D
```

`fragmenty-bramek` zapisuje `D/fragmenty_bramek.md`: fragmenty wszystkich dokumentów archiwum, które pasują do wzorców bramek modelu (`konfiguracja/fragmenty-bramek.yaml`). Z fragmentów wolno cytować, bo pochodzą z tego samego tekstu co polecenie `tekst`.

Typy dokumentów: `10-K`, `10-Q`, `8-K`, `raport_pdf`, `espi`, `strona`, `wklejka`, `inny`. Dla stron SEC w HTML (10-K) użyj `--typ 10-K`. Cytuj wyłącznie z wyjścia polecenia `tekst`: to ten sam tekst, w którym silnik szuka cytatu.

## 3. Propozycje faktów

Plik `D/propozycje.json`. Silnik dołącza propozycje przy każdym przebiegu (`silnik.gpw`, `silnik.obliczenia`, `silnik.raport`), tylko te, których id jeszcze nie ma w rejestrze.

```json
{"fakty": [
  {"id": "przychody.FY2026M9", "pozycja": "przychody",
   "okres": {"typ": "M9", "poczatek": "2026-01-01", "koniec": "2026-09-30"},
   "wartosc": 27679127, "skala": "tys", "jednostka": "pieniadz", "waluta": "PLN",
   "dokument": "doc-003", "miejsce": {"strona": 4, "kolumna": 0},
   "cytat": "Przychody ze sprzedaży .... 27 679 127 24 738 104"}
]}
```

- **Wartość** wpisujesz tak, jak stoi w dokumencie, a skalę bierzesz z nagłówka tabeli (`tys`, `mln`, `mld`, `jedn`). Wartość ujemna ma minus, nawet gdy dokument pisze ją w nawiasie.
- **Id:** `pozycja.okres`. Okresy: `FY2025` (rok), `FY2026Q3` (kwartał), `FY2026H1`, `FY2026M9` (narastająco), `2026-09-30` (stan na dzień).
- **Pozycje:** używaj nazw z `konfiguracja/mapowanie-mssf.yaml` (przychody, zysk_operacyjny, zysk_netto, zysk_netto_razem, przeplywy_operacyjne, aktywa, kapital_wlasny …). Nowe pozycje (np. `liczba_sklepow`, `nim`, `cet1`) są dozwolone; jednostka musi pasować (`liczba`, `ulamek`, `akcje`).
- **Liczba akcji** dla GPW: `akcje_w_obrocie.<data>`, jednostka `akcje`.
- **Test cytatu:** cytat musi być na wskazanej stronie, a wartość musi być całą liczbą z kolumny tego wiersza. Test nie łapie złej kolumny (np. rok poprzedni) — sprawdzaj nagłówki kolumn.
- **Wklejka z InvestingPro** (konsensus): najpierw `silnik.dokumenty wklejka`, potem propozycje typu prognoza:

```json
{"id": "cena_docelowa_srednia.2026-11-10", "rodzaj": "prognoza", "metoda": "wklejka",
 "pozycja": "cena_docelowa_srednia", "okres": {"typ": "dzien", "koniec": "2026-11-10"},
 "wartosc": 45.2, "jednostka": "pieniadz_na_akcje", "waluta": "PLN", "dokument": "doc-031",
 "dostawca": "InvestingPro", "data_prognozy": "2026-11-10", "liczba_analitykow": 7,
 "miejsce": {}, "cytat": "…dosłowny fragment wklejki…"}
```

  oraz `liczba_analitykow.<data>` (rodzaj `raportowany`, metoda `wklejka`, jednostka `liczba`). Pozycje filaru „analitycy”: `cena_docelowa_srednia`, `wzrost_eps_konsensus`, `rewizje_eps_90d`.

- **Wynik Scrab** (gdy jest we wklejce): dwie propozycje z tym samym cytatem, `wynik_scrab.<data>` (np. 72) i `wynik_scrab_max.<data>` (np. 100), rodzaj `raportowany`, metoda `wklejka`, jednostka `liczba`. Silnik porówna je z kartą Treli na skali 0–100.
- **Data danych we wklejce:** w propozycjach z wklejki ustaw `data_prognozy` (prognozy) albo `okres.koniec` na datę danych z materiału, a nie na datę analizy. Silnik ostrzega o materiale starszym niż próg.

Propozycja odrzucona zostaje w rejestrze ze statusem „odrzucony”; `python -m silnik.gpw` wypisuje powód. Popraw cytat albo wartość.

## 4. Dowody do bramek

Plik `D/bramki_dowody.json`; lista bramek modelu w `konfiguracja/bramki.yaml` (`bramki_modelu`). Dowód modelu zastępuje automatyczny wynik tej samej bramki — tak oceniasz flagi automatyczne (np. `B1.opoznione_raporty`, `B1.slabosc_kontroli_wzmianka`, `B0.zawieszenie`).

```json
{"dowody": [
  {"bramka": "B1.slabosc_kontroli_wzmianka", "poziom": "ok", "opis": "Zarząd i biegły stwierdzają skuteczną kontrolę; „material weakness” pada tylko w opisie ryzyk",
   "dokument": "doc-020", "cytat": "…"},
  {"bramka": "B4.akcjonariusz_90", "poziom": "stop", "dokument": "doc-021", "strona": 5,
   "cytat": "…posiada 93,5% głosów…", "opis": "…",
   "testy": {"strukturalny": "…", "uczciwosc_liczb": "…", "zarzad_rozwiazuje": "…", "termin": "…"},
   "warunek_powrotu": "…"}
]}
```

- Poziom inny niż `ok` wymaga cytatu obecnego w dokumencie (`strona` dla PDF).
- STOP wymaga czterech testów i warunku powrotu. Cztery testy: czy problem jest strukturalny, czy dotyczy uczciwości liczb, czy zarząd go rozwiązuje, czy rozwiązanie ma termin.
- Odróżniaj flagę twardą od przejściowego problemu: jeden słaby kwartał, dołek cyklu albo zapowiedziana restrukturyzacja z finansowaniem to flaga, nie stop.

## 5. Czego nie robić

- Nie wpisuj liczb do `fakty.json` ręcznie i nie edytuj plików generowanych przez silnik (`fakty.json`, `weryfikacja.md`, `obliczenia.md`, `bramki.md`).
- Nie bierz liczb z WebFetch, z pamięci ani z artykułów bez dokumentu w archiwum.
- Nie zmieniaj progów w `konfiguracja/` bez zgody właściciela.
