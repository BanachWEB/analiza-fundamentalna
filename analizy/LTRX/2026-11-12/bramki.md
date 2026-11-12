# Bramki stopu: LTRX

Plik wygenerował silnik (2026-11-12). Nie edytuj go ręcznie.

**Decyzja: DALEJ** — brak twardej flagi.

| Etap | Bramka | Wynik | Opis | Dowody | Źródło |
|---:|---|---|---|---|---|
| 0 | B0.pokrycie | ok | Pokrycie analityczne średnie (6 analityków) | liczba_analitykow.2026-11-12 | kod |
| 1 | B1.korekta_sprawozdan | ok | Brak 8-K z pozycją 4.02 (korekta sprawozdań) |  | kod |
| 1 | B1.opinia_bieglego | ok | Opinia bez zastrzeżeń (Baker Tilly US, LLP); jedna kluczowa sprawa badania: rezerwa na zapasy nadmiarowe i przestarzałe. | doc-017: „In our opinion, the consolidated financial statements present fairly, in” | model |
| 1 | B1.opoznione_raporty | ok | Brak zawiadomień NT 10-K/NT 10-Q |  | kod |
| 1 | B1.sankcja_regulatora | ok | Jedyne trafienia to ogólne kary za naruszenie ochrony danych w czynnikach ryzyka; brak sankcji SEC wobec spółki. | doc-017: „Failure to meet Privacy and Data Protection Law requirements could result in significant civil penalties” | model |
| 1 | B1.slabosc_kontroli | ok | Baker Tilly wydał opinię, że spółka utrzymała skuteczną kontrolę wewnętrzną; w 10-K nie ma stwierdzenia o nieusuniętej słabości. | doc-017: „Also in our opinion, the Company maintained, in all material respects, effective internal control over financial” | model |
| 1 | B1.slabosc_kontroli_wzmianka | ok | Wzorzec „material weakness” trafia w 10-K tylko w opisie zakresu badania biegłego (ryzyko, że słabość istnieje); zarząd stwierdza skuteczną kontrolę wewnętrzną na 30.06.2026. | doc-017: „management concluded that our internal control over financial reporting was effective as of June 30, 2026.” | model |
| 1 | B1.zmiana_bieglego | ok | Brak zmiany biegłego rewidenta |  | kod |
| 2 | B2.rozwodnienie_seryjne | flaga poważna | Wskaźnik z rejestru faktów potwierdza wzrost liczby akcji powyżej 10% r/r w FY2022, FY2023 i FY2026; emisja z 1.06.2026 dodała 4,17 mln akcji (oferta publiczna pod gwarancją emisji, bez prawa poboru, jak to zwykle bywa w USA), a ATM z 8.05.2026 kolejne 1,84 mln. Przyczyn FY2022-FY2023 nie sprawdzono w dokumentach. Dowód emisji nie pokazuje szkody dla mniejszości, więc to nie STOP. | doc-027: „4,166,667 shares of our Common Stock (or 4,791,667 shares if the underwriters” | model |
| 2 | B2.rozwodnienie_szkodliwe | flaga | Emisja po 7,20 USD przy ostatnim kursie 8,45 USD (dyskonto ok. 15%), na kapitał obrotowy i cele ogólne; oferta rynkowa pod gwarancją, nie emisja do wybranych podmiotów, więc brak dowodu szkody dla mniejszości, ale skala rozwodnienia wymaga obserwacji. | doc-027: „The last reported sale price of our Common Stock on May 28, 2026 was $8.45 per share.” | model |
| 3 | B3.altman | ok | Altman Z'' 1,52 (strefa zagrożenia poniżej 1,10) | altman_z2.FY2026 | kod |
| 3 | B3.beneish | ok | Beneish M-score -2,91 (próg -1,78): poniżej progu | beneish_m.FY2026 | kod |
| 3 | B3.kontynuacja | ok | Brak wzmianki o istotnej niepewności kontynuacji działalności w 10-K i w wyszukiwaniu EDGAR (0 trafień); spółka opisuje źródła płynności. | doc-017: „Our principal sources of cash and liquidity include our existing cash and” | model |
| 3 | B3.kontynuacja_wzmianka | ok | Brak wzmianki „substantial doubt” w raportach od 2026-08-26 | doc-014: 0 trafień od 2026-08-26 | kod |
| 3 | B3.przeplywy_do_zysku | ok | Zysk netto z 3 lat ≤ 0 (patrz wskaźniki) | przeplywy_operacyjne.FY2024; przeplywy_operacyjne.FY2025; przeplywy_operacyjne.FY2026 … | kod |
| 4 | B4.insiderzy | flaga | Wśród 35 przejrzanych Form 4 (doc-030..064) jedyna sprzedaż na rynku (kod S): Mathi Gurusamy sprzedał 14 467 akcji 13.03.2026 po 6,21 USD (zostało 55 569); formularz nie wskazuje planu 10b5-1. Pozostałe formularze to przyznania, potrącenia i wykonania (kody A, F, M), przekazania do trustu (G) oraz jeden zakup (P, doc-036). | doc-060: „This transaction was executed in multiple trades at prices ranging from $6.21 to $6.28.” | model |
| 4 | B4.akcjonariusz_90 | ok | Największy akcjonariusz, Needham Investment Management, ma 6,7%; zarząd i rada łącznie 2,8%. | doc-024: „Needham Investment Management L.L.C.(3)” | model |
| 4 | B4.oszustwo | ok | Żaden z przeczytanych dokumentów (10-K, DEF 14A, 8-K, Form 4) nie wskazuje oszustwa ani tunelowania; brak transakcji z podmiotami powiązanymi. | doc-024: „There were no transactions with related persons that required disclosure under applicable SEC rules during fiscal 2026 and 2025, nor are any such transactions currently proposed.” | model |
| 4 | B4.podmioty_powiazane | ok | Spółka stwierdza brak transakcji z podmiotami powiązanymi wymagających ujawnienia w FY2026 i FY2025. | doc-024: „There were no transactions with related persons that required disclosure under applicable SEC rules during fiscal 2026 and 2025, nor are any such transactions currently proposed.” | model |
| 5 | B5.decyzja_organu | ok | Brak trafień i brak wzmianki o decyzji organu odbierającej rdzeń biznesu; w sprawach sądowych spółka nie zna postępowań o istotnym wpływie. | doc-017: „ordinary course of business. We are currently not aware of any such legal proceedings or claims that we believe will have, individually” | model |

## Dowody od modelu odrzucone przez silnik

Brak.
