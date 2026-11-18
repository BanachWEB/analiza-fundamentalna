# Bramki stopu: CRI

Plik wygenerował silnik (2026-11-18). Nie edytuj go ręcznie.

**Decyzja: DALEJ** — brak twardej flagi.

| Etap | Bramka | Wynik | Opis | Dowody | Źródło |
|---:|---|---|---|---|---|
| 0 | B0.pokrycie | informacja | Brak danych o liczbie analityków — pokrycia nie można ocenić (dla GPW: wklejka z InvestingPro) |  | kod |
| 0 | B0.lista_alertow | brak danych | Strona GPW niedostępna: https://www.gpw.pl/lista-alertow-notowania: przerwana transmisja (RemoteDisconnected) |  | kod |
| 0 | B0.oznaczenie_ciagle | brak danych | Strona GPW niedostępna: https://www.gpw.pl/spolki-ze-szczegolnym-oznaczeniem-notowania-ciagle: przerwana transmisja (RemoteDisconnected) |  | kod |
| 0 | B0.oznaczenie_jednolite | brak danych | Strona GPW niedostępna: https://www.gpw.pl/spolki-ze-szczegolnym-oznaczeniem-notowania-jednolite: przerwana transmisja (RemoteDisconnected) |  | kod |
| 0 | B0.zawieszenia | brak danych | Strona GPW niedostępna: https://www.gpw.pl/zawieszenia-i-wykluczenia: przerwana transmisja (RemoteDisconnected) |  | kod |
| 1 | B1.nt_ksiegowe | ok | Brak w dokumentach informacji o opóźnieniu raportu z przyczyn księgowych; sprawozdanie dodatkowe dla komitetu audytu wydano 15.04.2026. | doc-134: „Niniejsza opinia jest spójna ze sprawozdaniem dodatkowym dla Komitetu Audytu” | model |
| 1 | B1.opinia_bieglego | ok | UHY ECA Audyt wydała opinię bez zastrzeżeń o SF za 2025; brak paragrafu o istotnej niepewności kontynuacji i brak objaśnień uzupełniających poza kluczową sprawą (utrata wartości prac rozwojowych). Przegląd H1 2026 (doc-135) bez zastrzeżeń. | doc-134: „Naszym zdaniem, załączone sprawozdanie” | model |
| 1 | B1.sankcja_regulatora | ok | Raport H1 2026 i sprawozdanie zarządu za 2025 nie opisują postępowań ani sankcji KNF ani innych organów. | doc-003: „Do dnia sporządzenia niniejszego sprawozdania nie toczyły” | model |
| 1 | B1.slabosc_kontroli | ok | Biegły nie stwierdza w przeglądzie H1 2026 nieprawidłowości; w badaniu 2025 brak wzmianki o istotnej słabości kontroli. | doc-135: „nie zwróciło naszej uwagi nic, co” | model |
| 2 | B2.rozwodnienie_szkodliwe | flaga | Dwie emisje w 17 mies.: seria K (475 000 akcji, I kw. 2025, 76 mln PLN) i seria M (650 000 akcji, VII 2026, 481 mln PLN, bez prawa poboru), razem ok. +47% liczby akcji (2 379 347 do 3 504 347). Emisja M skierowana do wybranych inwestorów z prawem pierwszeństwa dla akcjonariuszy >0,5% i przy dużych środkach, więc to nie jest szkodliwe seryjne rozwodnienie. Program motywacyjny: po 4 805 uprawnień dla każdego z 4 członków zarządu, warunek (Mikroglob) niespełniony. Flaga: obserwuj kolejne emisje. | doc-137: „Planowana emisja akcji serii M jest przeprowadzona z wyłączeniem prawa poboru dotychczasowych akcjonariuszy Spółki w całości.” | model |
| 2 | B2.rozwodnienie | brak danych | Brak danych o liczbie akcji |  | kod |
| 3 | B3.kontynuacja | ok | Brak istotnej niepewności kontynuacji w opinii biegłego; spółka pozyskała w lipcu 2026 481 mln PLN z emisji serii M. | doc-003: „Spółka w lipcu 2026 roku pozyskała środki” | model |
| 3 | B3.przeplywy_do_zysku | ok | Zysk netto z 3 lat ≤ 0 (patrz wskaźniki) | przeplywy_operacyjne.FY2023; przeplywy_operacyjne.FY2024; przeplywy_operacyjne.FY2025 … | kod |
| 4 | B4.insiderzy | flaga | Prezes Grzegorz Brona zbył 2.02.2026 pakiet 20 000 akcji (ok. 11% jego udziału) na rynku regulowanym; dokumenty nie mówią, czy w ramach planu. Brak innych sprzedaży w 12 mies.; wcześniejsza sprzedaż 30 000 akcji w VI 2024 jest poza oknem. Skala nie wskazuje na STOP. | doc-133: „Brona w dniu 2 lutego 2026 r. dokonał transakcji pakietowej na rynku regulowanym skutkującej zbyciem” | model |
| 4 | B4.akcjonariusz_90 | ok | Największy akcjonariusz (PTE Allianz Polska) ma 8,1161% głosów po emisji serii M (9,96% przed); jedna akcja, jeden głos (3 504 347 głosów), brak akcji uprzywilejowanych i porozumień w dokumentach. | doc-003: „PTE Allianz Polska S.A. 284 416 8,1161%” | model |
| 4 | B4.podmioty_powiazane | ok | Transakcje drobne: umowa o pracę głównej księgowej (żona członka zarządu), podwykonawstwo Creotech Geo (448 399 EUR), wynajem biura; po podziale brak istotnych transakcji z Creotech Quantum; 'na warunkach innych niż rynkowe: nie wystąpiły'. | doc-003: „Natalia Grzesiak-Misiura jest bliskim” | model |
| 5 | B5.decyzja_organu | ok | W 2025 r. nie toczyły się postępowania przed sądem, arbitrażem ani organem administracji; kar umownych z kontraktów (ESA, Agencja Uzbrojenia) dokumenty nie opisują. | doc-133: „W  2025  roku  nie  toczyły  się  żadne  postępowania  przed  sądem” | model |

## Dowody od modelu odrzucone przez silnik

Brak.
