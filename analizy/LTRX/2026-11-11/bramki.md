# Bramki stopu: LTRX

Plik wygenerował silnik (2026-11-11). Nie edytuj go ręcznie.

**Decyzja: DALEJ** — brak twardej flagi.

| Etap | Bramka | Wynik | Opis | Dowody | Źródło |
|---:|---|---|---|---|---|
| 0 | B0.pokrycie | ok | Pokrycie analityczne średnie (6 analityków) | liczba_analitykow.2026-11-11 | kod |
| 1 | B1.korekta_sprawozdan | ok | Brak 8-K z pozycją 4.02 (korekta sprawozdań) |  | kod |
| 1 | B1.opinia_bieglego | ok | Opinia bez zastrzeżeń (Baker Tilly US, LLP); jedna kluczowa sprawa badania (critical audit matter): rezerwa na zapasy nadmiarowe i przestarzałe (zapasy ok. 25,8 mln USD). | doc-015: „In our opinion, the consolidated financial statements present fairly, in” | model |
| 1 | B1.opoznione_raporty | ok | Brak zawiadomień NT 10-K/NT 10-Q |  | kod |
| 1 | B1.sankcja_regulatora | ok | Jedyne trafienia to ogólne kary za naruszenie ochrony danych w czynnikach ryzyka; brak sankcji SEC wobec spółki. | doc-015: „Failure to meet Privacy and Data Protection Law requirements could result in significant civil penalties” | model |
| 1 | B1.slabosc_kontroli | ok | Baker Tilly wydał opinię o skutecznej kontroli wewnętrznej; w 10-K nie ma wzmianki o nieusuniętej słabości. | doc-015: „Also in our opinion, the Company maintained, in all material respects, effective internal control over financial” | model |
| 1 | B1.slabosc_kontroli_wzmianka | ok | „Material weakness” pada tylko w opisie zakresu badania biegłego; zarząd i biegły stwierdzają skuteczną kontrolę wewnętrzną na 30.06.2026. | doc-015: „management concluded that our internal control over financial reporting was effective as of June 30, 2026.” | model |
| 1 | B1.zmiana_bieglego | ok | Brak zmiany biegłego rewidenta |  | kod |
| 2 | B2.rozwodnienie_seryjne | flaga poważna | Liczba akcji rosła o ponad 10% r/r w 3 z 5 ostatnich lat; miara: na koniec okresu, średnia ważona; sprawdź, czy emisje szły bez prawa poboru (wtedy STOP wymaga dowodu) | zmiana_liczby_akcji.FY2022; zmiana_liczby_akcji_koniec.FY2022; zmiana_liczby_akcji.FY2023 … | kod |
| 2 | B2.rozwodnienie_szkodliwe | flaga | Dwie emisje w ciągu miesiąca (ATM od 8.05 i oferta pod gwarancją 1.06 po 7,20 USD przy kursie 8,45 USD, czyli z dyskontem ok. 15%), bez warrantów, za zgodą rynku i na kapitał obrotowy; nie jest to seryjne rozwodnienie na szkodę mniejszości, ale skala ok. 15% akcji wymaga obserwacji. | doc-025: „The last reported sale price of our Common Stock on May 28, 2026 was $8.45 per share.” | model |
| 3 | B3.altman | ok | Altman Z'' 1,52 (strefa zagrożenia poniżej 1,10) | altman_z2.FY2026 | kod |
| 3 | B3.beneish | ok | Beneish M-score -2,91 (próg -1,78): poniżej progu | beneish_m.FY2026 | kod |
| 3 | B3.kontynuacja | ok | Brak wzmianki o istotnej niepewności kontynuacji w 10-K; spółka podała rozbudowaną płynność i bieżącą emisję akcji. | doc-015: „Our principal sources of cash and liquidity include our existing cash and” | model |
| 3 | B3.kontynuacja_wzmianka | ok | Brak wzmianki „substantial doubt” w raportach od 2026-08-26 | doc-068: 0 trafień od 2026-08-26 | kod |
| 3 | B3.przeplywy_do_zysku | ok | Zysk netto z 3 lat ≤ 0 (patrz wskaźniki) | przeplywy_operacyjne.FY2024; przeplywy_operacyjne.FY2025; przeplywy_operacyjne.FY2026 … | kod |
| 4 | B4.insiderzy | flaga | Jedyna sprzedaż na rynku w 2026 r. (kod S): Mathi Gurusamy sprzedał 14 467 akcji 13.03.2026 po ok. 6,21 USD (ok. 21% jego udziału); formularz nie wskazuje planu 10b5-1. Form 4 prezesa z 2.11.2026 (doc-035) pokazuje tylko kody A, F, M, bez sprzedaży; prezes kupił 15 000 akcji 9.09.2026 (doc-036). | doc-060: „This transaction was executed in multiple trades at prices ranging from $6.21 to $6.28.” | model |
| 4 | B4.akcjonariusz_90 | ok | Największy akcjonariusz to Needham Investment Management z 6,7%; zarząd i rada łącznie 2,8%. | doc-022: „Needham Investment Management L.L.C.(3)” | model |
| 4 | B4.oszustwo | ok | Żaden z przeczytanych dokumentów nie wskazuje oszustwa ani tunelowania; brak transakcji z podmiotami powiązanymi. | doc-022: „There were no transactions with related persons that required disclosure under applicable SEC rules during fiscal 2026 and 2025, nor are any such transactions currently proposed.” | model |
| 4 | B4.podmioty_powiazane | ok | Spółka stwierdza brak transakcji z podmiotami powiązanymi wymagających ujawnienia w FY2026 i FY2025. | doc-022: „There were no transactions with related persons that required disclosure under applicable SEC rules during fiscal 2026 and 2025, nor are any such transactions currently proposed.” | model |
| 5 | B5.decyzja_organu | ok | Brak trafień i brak wzmianki o decyzji organu odbierającej rdzeń biznesu w fragmentach i 10-K. | doc-015: „We do not own or operate a manufacturing facility.” | model |

## Dowody od modelu odrzucone przez silnik

- B2.rozwodnienie: nieznana bramka
