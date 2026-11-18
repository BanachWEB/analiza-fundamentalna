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
