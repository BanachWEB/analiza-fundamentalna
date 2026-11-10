# Bramki stopu: STX

Plik wygenerował silnik (2026-11-10). Nie edytuj go ręcznie.

**Decyzja: DALEJ** — brak twardej flagi.

| Etap | Bramka | Wynik | Opis | Dowody | Źródło |
|---:|---|---|---|---|---|
| 0 | B0.pokrycie | ok | Pokrycie analityczne duże (26 analityków) | liczba_analitykow.2026-11-10 | kod |
| 1 | B1.sankcja_regulatora | flaga | Ugoda z BIS (Departament Handlu USA) za sprzedaż dysków do Huawei w latach 2020–2021, płatna w ratach do 2028 r. Sankcja dotyczy kontroli eksportu, nie raportów finansowych, więc to flaga, nie stop. Osobno spółka zawarła ugodę w pozwie zbiorowym akcjonariuszy za okres 2020–2023 (ostateczne zatwierdzenie 17.11.2026). | doc-014: „entered into a settlement agreement (the “Settlement Agreement”) with the U.S. Department of Commerce’s Bureau of Industry and Security (“BIS”) that resolves BIS’ allegations regarding Seagate’s sales” | model |
| 1 | B1.korekta_sprawozdan | ok | Brak 8-K z pozycją 4.02 (korekta sprawozdań) |  | kod |
| 1 | B1.opinia_bieglego | ok | Ernst & Young: opinia bez zastrzeżeń o sprawozdaniach za rok obrotowy do 3.07.2026 | doc-014: „In our opinion, the consolidated financial statements present fairly, in all material respects, the financial position of the Company at July 3, 2026 and June 27, 2025” | model |
| 1 | B1.opoznione_raporty | ok | Brak zawiadomień NT 10-K/NT 10-Q |  | kod |
| 1 | B1.slabosc_kontroli_wzmianka | ok | Zarząd uznał kontrolę wewnętrzną za skuteczną, a Ernst & Young wydał o niej opinię bez zastrzeżeń; „material weakness” pada tylko w opisie procedury badania | doc-014: „our management has concluded that our internal control over financial reporting was effective as of July 3, 2026” | model |
| 1 | B1.zmiana_bieglego | ok | Brak zmiany biegłego rewidenta |  | kod |
| 2 | B2.rozwodnienie_szkodliwe | flaga | Spółka wydaje akcje przy wymianie obligacji wymiennych z terminem 2028; to rozwodnienie wynika z warunków długu, a nie z emisji na szkodę mniejszości | doc-017: „delivered 1,647,862 ordinary shares of Seagate, par value $0.00001 per share (the “Ordinary Shares”) to settle exchanges of $150.51 million aggregate principal amount of the Issuer’s outstanding 3.50%” | model |
| 2 | B2.rozwodnienie | ok | Brak rozwodnienia powyżej progu | zmiana_liczby_akcji.FY2026 | kod |
| 3 | B3.altman | ok | Altman Z'' 2,50 (strefa zagrożenia poniżej 1,10) | altman_z2.FY2026 | kod |
| 3 | B3.beneish | ok | Beneish M-score -2,27 (próg -1,78): poniżej progu | beneish_m.FY2026 | kod |
| 3 | B3.kontynuacja_wzmianka | ok | Brak wzmianki „substantial doubt” w raportach od 2026-08-03 | doc-012: 0 trafień od 2026-08-03 | kod |
| 3 | B3.przeplywy_do_zysku | ok | Przepływy operacyjne pokrywają zysk netto | przeplywy_operacyjne.FY2024; przeplywy_operacyjne.FY2025; przeplywy_operacyjne.FY2026 … | kod |
| 4 | B4.akcjonariusz_90 | ok | Akcjonariat rozproszony; największy akcjonariusz (Vanguard) ma kilka procent akcji | doc-016: „Vanguard Capital Management(b)” | model |
| 4 | B4.insiderzy | ok | Sprzedaż akcji przez prezesa (W. Mosley) i drugiego członka kierownictwa z początku listopada 2026 odbyła się według planów 10b5-1 przyjętych wcześniej; to szum, nie sygnał | doc-021: „All transactions reported in this Form 4 were effected pursuant to a Rule 10b5-1 trading plan adopted by the Reporting Person on February 18, 2026.” | model |
| 4 | B4.podmioty_powiazane | ok | DEF 14A opisuje tylko politykę zatwierdzania transakcji z podmiotami powiązanymi i nie wymienia żadnej takiej transakcji | doc-016: „Our Board has adopted a written policy for approval of transactions with our directors, director nominees, executive officers, shareholders that beneficially own more than 5% of our ordinary shares” | model |

## Dowody od modelu odrzucone przez silnik

Brak.
