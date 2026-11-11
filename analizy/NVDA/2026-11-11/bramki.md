# Bramki stopu: NVDA

Plik wygenerował silnik (2026-11-11). Nie edytuj go ręcznie.

**Decyzja: DALEJ** — brak twardej flagi.

| Etap | Bramka | Wynik | Opis | Dowody | Źródło |
|---:|---|---|---|---|---|
| 0 | B0.pokrycie | ok | Pokrycie analityczne duże (62 analityków) | liczba_analitykow.2026-11-11 | kod |
| 1 | B1.korekta_sprawozdan | ok | Brak 8-K z pozycją 4.02 (korekta sprawozdań) |  | kod |
| 1 | B1.nt_ksiegowe | ok | Brak NT 10-K i NT 10-Q na liście raportów SEC (doc-002) w 2026; 10-K złożony 25.02.2026, 10-Q 26.08.2026, terminowo. | doc-002: „” | model |
| 1 | B1.opinia_bieglego | ok | Opinia bez zastrzeżeń (unqualified) o sprawozdaniu FY2026 i o skuteczności kontroli wewnętrznej. Jedna krytyczna sprawa badania dotyczy rezerw na zapasy i nadmiarowe zobowiązania zakupowe. | doc-019: „present fairly, in all material respects, the financial position of the Company” | model |
| 1 | B1.opoznione_raporty | ok | Brak zawiadomień NT 10-K/NT 10-Q |  | kod |
| 1 | B1.sankcja_regulatora | ok | Brak trafień o sankcji SEC za raporty; 10-K i 10-Q opisują zwykłe postępowania, bez sankcji za sprawozdawczość. | doc-020: „We are engaged in legal actions not described above arising in the ordinary course of business, as well as regulatory and government inquiries and investigations” | model |
| 1 | B1.slabosc_kontroli | ok | Brak nieusuniętej istotnej słabości: zarząd stwierdza skuteczną kontrolę, biegły potwierdza. Zmiana głównego księgowego w maju 2026 (doc-027) jest planową emeryturą z następcą z Intela, bez wzmianki o problemach kontroli. | doc-019: „our management concluded that our internal control over financial reporting was effective” | model |
| 1 | B1.slabosc_kontroli_wzmianka | ok | „Material weakness” pada w 10-K tylko w czynniku ryzyka o ewentualnej słabości. Zarząd stwierdza skuteczną kontrolę wewnętrzną na 25.01.2026, a biegły wydaje opinię bez zastrzeżeń także o kontroli wewnętrznej. | doc-019: „our management concluded that our internal control over financial reporting was effective” | model |
| 1 | B1.zmiana_bieglego | ok | Brak zmiany biegłego rewidenta |  | kod |
| 2 | B2.rozwodnienie | ok | Brak rozwodnienia powyżej progu | zmiana_liczby_akcji.FY2026; zmiana_liczby_akcji_koniec.FY2026 | kod |
| 2 | B2.rozwodnienie_szkodliwe | ok | Spółka skupuje akcje, nie emituje ich bez prawa poboru; brak trafień o seryjnych emisjach na szkodę mniejszości. | doc-020: „we repurchased 94 million and 203 million shares of our common stock” | model |
| 3 | B3.beneish | flaga | Wzrost należności 10-Q tłumaczy spółka wydłużonymi terminami płatności w dużych umowach wieloletnich z klientami o ratingu inwestycyjnym; jednocześnie zapasy i zobowiązania zakupowe rosną pod popyt (Vera Rubin). To diagnostyka jakości zysków, nie stop; bez dowodu manipulacji zostaje flaga. | doc-020: „partially offset by an increase in accounts receivable due to extended payment terms on large multi-quarter agreements with certain investment-grade customers.” | model |
| 3 | B3.altman | ok | Altman Z'' 12,85 (strefa zagrożenia poniżej 1,10) | altman_z2.FY2026 | kod |
| 3 | B3.kontynuacja_wzmianka | ok | Brak wzmianki „substantial doubt” w raportach od 2026-02-24 | doc-014: 0 trafień od 2026-02-24 | kod |
| 3 | B3.przeplywy_do_zysku | ok | Przepływy operacyjne pokrywają zysk netto | przeplywy_operacyjne.FY2024; przeplywy_operacyjne.FY2025; przeplywy_operacyjne.FY2026 … | kod |
| 4 | B4.oszustwo | flaga | Spółka ogłosiła 8.11.2026 niezależne dochodzenie rady (kancelaria Wachtell, doc-043); rada pisze, że nie ma podstaw sądzić, że bezpieczeństwo narodowe lub tajemnice zostały naruszone. Brak dowodu oszustwa lub tunelowania, więc nie stop; ryzyko ładu do obserwacji do wyniku dochodzenia. Brak 8-K w EDGAR; źródło to komunikaty na nvidianews.nvidia.com (doc-043..045). | doc-045: „The NVIDIA Board is initiating an independent investigation in light of recent reporting that founder and CEO Jensen Huang has been the target of a foreign intelligence effort.” | model |
| 4 | B4.insiderzy | informacja | Sprzedaże Teter (doc-032), Coxe (doc-034, doc-037), Kress (doc-041) idą w planach 10b5-1; prezes Huang we wrześniu 2026 ma tylko potrącenie podatku i darowizny (doc-042). Wyjątek: dyrektor Stevens 18.09.2026 sprzedał w otwartym oknie akcje bez wzmianki o planie 10b5-1 (doc-033), to legalne, więc informacja, nie flaga. | doc-033: „Represents weighted average sales price. The shares were sold at prices ranging from $219.40 to $220.35.” | model |
| 4 | B4.kontrahenci | informacja | Klienci bezpośredni to znane firmy (należności: pięciu klientów 22%, 14%, 13%, 11%, 10%), brak niesprawdzalnych kontrahentów. Informacja: gwarancje wartości rezydualnej do $105 mld dla dzierżawy z najemcą OpenAI to ekspozycja na jednego klienta, poza bilansem. | doc-023: „NVIDIA will pay an amount generally equal to any shortfall between the guaranteed minimum value of a lease” | model |
| 4 | B4.akcjonariusz_90 | ok | Zarząd i rada razem mają 3,94% akcji, najwięksi akcjonariusze to BlackRock 7,43% i Vanguard 7,31%. Brak akcjonariusza z 90% głosów. | doc-022: „Directors and executive officers as a group (14 persons)” | model |
| 4 | B4.podmioty_powiazane | ok | Jedyne ujawnione transakcje z osobami powiązanymi to zatrudnienie dzieci prezesa (ok. 1,2 i 1,3 mln USD) i syna dyrektora, wynagrodzenie wg standardowych zasad, zatwierdza komitet NCGC. Brak dużych transakcji. | doc-022: „The daughter and son of Jen-Hsun Huang, our President and CEO and a member of our Board, are employed by the Company.” | model |
| 5 | B5.decyzja_organu | flaga | Spółka sama pisze o faktycznym wyłączeniu z chińskiego rynku centrów danych i odpisach H20/H200, ale sprzedaż H200 to poniżej 1% przychodów Data Center, a Chiny są poza prognozą (doc-031). Rdzeń biznesu nie jest odebrany, więc flaga. | doc-020: „we were effectively foreclosed from competing in China’s data center computing/compute market” | model |

## Dowody od modelu odrzucone przez silnik

Brak.
