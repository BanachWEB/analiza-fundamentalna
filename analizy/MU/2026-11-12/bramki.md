# Bramki stopu: MU

Plik wygenerował silnik (2026-11-12). Nie edytuj go ręcznie.

**Decyzja: DALEJ** — brak twardej flagi.

| Etap | Bramka | Wynik | Opis | Dowody | Źródło |
|---:|---|---|---|---|---|
| 0 | B0.pokrycie | ok | Pokrycie analityczne duże (49 analityków) | liczba_analitykow.2026-11-12 | kod |
| 1 | B1.korekta_sprawozdan | ok | Brak 8-K z pozycją 4.02 (korekta sprawozdań) |  | kod |
| 1 | B1.opinia_bieglego | ok | PricewaterhouseCoopers LLP (San Jose), opinia bez zastrzeżeń (unqualified) o sprawozdaniach i kontroli wewnętrznej, z datą 9.10.2026; biegły od 1984 r.; jedna kluczowa sprawa badania (ujmowanie przychodów). | doc-017: „the consolidated financial statements referred to above present fairly, in all material respects, the financial position of the Company as of September 3, 2026” | model |
| 1 | B1.opoznione_raporty | ok | Brak zawiadomień NT 10-K/NT 10-Q |  | kod |
| 1 | B1.sankcja_regulatora | ok | Item 3 odsyła do noty 11; w opisie postępowań brak sankcji SEC ani zawiadomień o dochodzeniu w sprawie raportowania (brak trafień na subpoena, Wells, SEC investigation). Pozostałe sprawy to spory patentowe i antymonopolowe. | doc-017: „For a discussion of legal proceedings, see Part II, Item 8. Financial Statements and Supplementary Data, Notes to Consolidated Financial Statements, Note 11. Contingencies” | model |
| 1 | B1.slabosc_kontroli | ok | Item 9A: zarząd uznał kontrolę za skuteczną, a PwC zbadał ją i wydał opinię bez zastrzeżeń; brak wskazanych istotnych słabości. | doc-017: „our internal control over financial reporting was effective as of September 3, 2026” | model |
| 1 | B1.slabosc_kontroli_wzmianka | ok | Zarząd i biegły stwierdzają skuteczną kontrolę wewnętrzną na 3.09.2026; „material weakness” pada tylko w opisie procedur biegłego (ocena ryzyka), nie jako stwierdzona słabość. | doc-017: „Also in our opinion, the Company maintained, in all material respects, effective internal control over financial reporting as of September 3, 2026” | model |
| 1 | B1.zmiana_bieglego | ok | Brak zmiany biegłego rewidenta |  | kod |
| 2 | B2.rozwodnienie | ok | Brak rozwodnienia powyżej progu | zmiana_liczby_akcji.FY2026; zmiana_liczby_akcji_koniec.FY2026 | kod |
| 3 | B3.beneish | flaga | Beneish M-score 0,48 (próg -1,78): sprawdź należności i memoriały | beneish_m.FY2026 | kod |
| 3 | B3.altman | ok | Altman Z'' 10,26 (strefa zagrożenia poniżej 1,10) | altman_z2.FY2026 | kod |
| 3 | B3.kontynuacja | ok | W 10-K FY2026 brak wzmianki „substantial doubt” i „going concern” (0 trafień w całym tekście); automatyczna bramka kontynuacji też bez trafień w doc-014. | doc-017: „” | model |
| 3 | B3.kontynuacja_wzmianka | ok | Brak wzmianki „substantial doubt” w raportach od 2026-10-08 | doc-014: 0 trafień od 2026-10-08 | kod |
| 3 | B3.przeplywy_do_zysku | ok | Przepływy operacyjne pokrywają zysk netto | przeplywy_operacyjne.FY2024; przeplywy_operacyjne.FY2025; przeplywy_operacyjne.FY2026 … | kod |
| 4 | B4.akcjonariusz_90 | ok | Największy akcjonariusz to Vanguard z 8,4% akcji, potem BlackRock 7,6% i Capital World Investors 6,3%. Dane z DEF 14A 2025 (stan na 31.10.2025), udziały z zawiadomień 13G z lutego 2024 - niezbyt świeże, ale rząd wielkości wyklucza próg 90%. | doc-018: „The Vanguard Group, Inc.(4) 94,984,500 — 94,984,500 8.4 %” | model |
| 4 | B4.insiderzy | ok | 10-K Item 9B: w IV kwartale FY2026 jedyny nowy plan 10b5-1 przyjął Scott DeBoer (do 85 632 akcji, od 16.10.2026); inni członkowie zarządu nie przyjęli ani nie zakończyli planów. Nie sprawdzono formularzy 4, więc brak dowodu o sprzedaży poza planem, ale też brak pełnej weryfikacji. Powiązane: 8-K z 5.11.2026 (doc-019, pozycja 5.02) dotyczy tylko rezygnacji dyrektorki Linnie Haynesworth, która nie będzie kandydować w ponownym wyborze na walnym zgromadzeniu FY2026; nie jest to odejście z powodu sporu. | doc-017: „On July 17, 2026, Scott DeBoer, our President and Chief Technology and Products Officer, adopted a Rule 10b5-1 trading arrangement providing for the sale of an aggregate of up to 85,632 shares of our ” | model |
| 4 | B4.oszustwo | ok | Nota 11: jest tylko domniemany pozew zbiorowy o zmowę cenową na DRAM (z 25.06.2026, także Samsung i SK hynix); to zarzuty powodów, nie wiarygodny dowód oszustwa przez zarząd. Warto obserwować rozstrzygnięcie. | doc-017: „alleging that the defendants conspired to restrict the supply of, and fix prices for, DRAM products in violation of the Sherman Act” | model |
| 4 | B4.podmioty_powiazane | ok | DEF 14A: brak transakcji z podmiotami powiązanymi od początku roku obrotowego 2025; polityka wymaga zatwierdzenia przez komitet audytu. Nie sprawdzono transakcji za FY2026 (nowszy proxy jeszcze nie opublikowany). | doc-018: „There were no actual or proposed related person transactions in which a related person had a direct or indirect material interest since the beginning of Fiscal 2025.” | model |
| 5 | B5.decyzja_organu | flaga | Decyzja CAC z maja 2023 r.: operatorzy krytycznej infrastruktury w Chinach nie mogą kupować produktów Micron; to ograniczenie dostępu do części rynku, nie utrata rdzenia biznesu (spółka działa i rośnie poza tym rynkiem). Dalsze działania chińskiego rządu mogą pogorszyć sytuację. | doc-017: „the CAC determined that critical information infrastructure operators in China may not purchase Micron products, impacting our revenue with companies headquartered in mainland China and Hong Kong” | model |

## Dowody od modelu odrzucone przez silnik

Brak.
