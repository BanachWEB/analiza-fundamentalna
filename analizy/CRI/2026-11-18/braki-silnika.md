# Braki silnika: CRI (18.11.2026)

## 1. ESEF bez znaczników XBRL (sprawozdania jednostkowe)

- **Co:** `silnik/pobieranie/esef.py` (`wyciagnij_fakty`) przerywa przebieg błędem `BladESEF: w raporcie nie ma okresów rocznych`, gdy pakiet ESEF zawiera sam XHTML bez znaczników `ix:nonFraction` i kontekstów `xbrli:context`.
- **Dlaczego:** spółki, które sporządzają tylko jednostkowe sprawozdanie finansowe, publikują raport roczny w formacie XHTML bez obowiązku znakowania XBRL. Creotech Instruments jest taką spółką: oba pakiety (SF za 2024 i 2025) mają 0 znaczników `ix:nonFraction`.
- **Przykład:** `https://cdn.sanity.io/files/lbgrp8oj/production/112780a4810f9cb7ba14ab6e34d5305f31bb331a.zip` (SF 2025) i `…/921ca6737ab067361aeb3de8c0b701ea23636198.zip` (SF 2024).
- **Obejście w tej analizie:** przebieg bez `--esef`; dane roczne z Biznesradaru (jedno źródło), dokumenty ESEF w archiwum jako doc-001 i doc-002, a liczby ze sprawozdań jako propozycje z cytatem (test cytatu czyta XHTML z ZIP).
- **Sugerowane zadanie:** gdy pakiet nie ma znaczników XBRL, `silnik.gpw` powinien dodać dokument do archiwum, wypisać ostrzeżenie „ESEF bez XBRL: dane z propozycji” i kontynuować, zamiast przerywać przebieg. Opcjonalnie: parser tabel XHTML (rachunek, bilans, przepływy) z testem na pakiecie Creotech.

## 2. Strony GPW a nagłówek przeglądarkowy

- **Co:** bramki B0 (lista alertów, oznaczenia szczególne, zawieszenia) dostały „brak danych”: `RemoteDisconnected` przy pobieraniu stron www.gpw.pl.
- **Przykład:** 18.11.2026 `curl` z domyślnym nagłówkiem dostał 200, a z nagłówkiem `Mozilla/5.0` pustą odpowiedź serwera. Do sprawdzenia, jakiego nagłówka używa `silnik/pobieranie/http.py` dla gpw.pl.

## 3. Jednorazowy zysk z podziału spółki w TTM

- **Co:** silnik bierze do TTM `zysk_netto` razem z wynikiem na rozliczeniu dystrybucji aktywów niepieniężnych (KIMSF 17). Dla CRI zysk netto TTM do 30.06.2026 zawiera niegotówkowy zysk z wydania akcji Creotech Quantum akcjonariuszom (`wynik_na_dystrybucji_aktywow.FY2026H1`), więc C/Z, ROE i marża netto TTM nie mają sensu ekonomicznego.
- **Sugerowane zadanie:** pozycja `zysk_netto_kontynuowana` (albo pozycje jednorazowe odejmowane od zysku) jako podstawa C/Z, ROE i marży netto, gdy rejestr ją ma; ostrzeżenie w `obliczenia.md`, gdy zysk netto różni się od zysku z działalności kontynuowanej o więcej niż np. 50%.

## 4. Emisja po dniu bilansowym a EV i wycena

- **Co:** kapitalizacja liczy się z liczbą akcji po emisji serii M (3 504 347), a dług netto i gotówka pochodzą z bilansu na 30.06.2026, czyli sprzed wpływu z emisji (`wplywy_z_emisji_serii_m.2026-07-31`). EV jest więc zawyżone o wpływy z emisji, a wartości scenariuszy na akcję są zaniżone o gotówkę z emisji przypadającą na akcję.
- **Sugerowane zadanie:** pozycja „zdarzenia po dniu bilansowym” (emisja, wypłata, przejęcie), którą silnik dolicza do gotówki netto, gdy liczba akcji pochodzi z daty po bilansie.

## 5. Przekształcenie danych porównawczych (działalność zaniechana)

- **Co:** Biznesradar podaje FY2024 i H1 2025 sprzed wydzielenia segmentu kwantowego, a raporty spółki po przekształceniu. Kontrola drugiego źródła daje 8 konfliktów, które wynikają z definicji, a nie z błędu. FY2023 (doc-002) nie jest przekształcony, więc dynamika FY2024/FY2023 porównuje różne zakresy działalności.
- **Sugerowane zadanie:** oznaczanie faktów jako „przekształcone” i wyłączanie porównania z drugim źródłem dla okresów przekształconych.
