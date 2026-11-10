# Bramki stopu: DNP

Plik wygenerował silnik (2026-11-10). Nie edytuj go ręcznie.

**Decyzja: DALEJ** — brak twardej flagi.

| Etap | Bramka | Wynik | Opis | Dowody | Źródło |
|---:|---|---|---|---|---|
| 0 | B0.pokrycie | informacja | Brak danych o liczbie analityków — pokrycia nie można ocenić (dla GPW: wklejka z InvestingPro) |  | kod |
| 0 | B0.lista_alertow | brak danych | Strona GPW niedostępna: https://www.gpw.pl/lista-alertow-notowania: przerwana transmisja (RemoteDisconnected) |  | kod |
| 0 | B0.oznaczenie_ciagle | brak danych | Strona GPW niedostępna: https://www.gpw.pl/spolki-ze-szczegolnym-oznaczeniem-notowania-ciagle: przerwana transmisja (RemoteDisconnected) |  | kod |
| 0 | B0.oznaczenie_jednolite | brak danych | Strona GPW niedostępna: https://www.gpw.pl/spolki-ze-szczegolnym-oznaczeniem-notowania-jednolite: przerwana transmisja (RemoteDisconnected) |  | kod |
| 0 | B0.zawieszenia | brak danych | Strona GPW niedostępna: https://www.gpw.pl/zawieszenia-i-wykluczenia: przerwana transmisja (RemoteDisconnected) |  | kod |
| 1 | B1.opinia_bieglego | ok | Opinia biegłego o skonsolidowanym sprawozdaniu za 2025 bez zastrzeżeń; kluczowa sprawa badania: nakłady inwestycyjne i aktywowanie kosztów w rzeczowych aktywach trwałych | doc-087: „Naszym zdaniem, załączone skonsolidowane sprawozdanie finansowe Grupy Kapitałowej:” | model |
| 2 | B2.rozwodnienie | brak danych | Brak danych o liczbie akcji |  | kod |
| 3 | B3.altman | ok | Altman Z'' 2,06 (strefa zagrożenia poniżej 1,10) | altman_z2.FY2025 | kod |
| 3 | B3.beneish | ok | Beneish M-score -2,85 (próg -1,78): poniżej progu | beneish_m.FY2025 | kod |
| 3 | B3.przeplywy_do_zysku | ok | Przepływy operacyjne pokrywają zysk netto | przeplywy_operacyjne.FY2023; przeplywy_operacyjne.FY2024; przeplywy_operacyjne.FY2025 … | kod |
| 4 | B4.akcjonariusz_90 | ok | Akcjonariusz kontrolujący (założyciel) ma ok. połowę głosów, daleko poniżej progu przymusowego wykupu | doc-003: „Tomasz Biernacki wraz z podmiotem zależnym3 ...... 501 600 000 51,16%” | model |

## Dowody od modelu odrzucone przez silnik

Brak.
