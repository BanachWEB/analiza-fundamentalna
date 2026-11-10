# Bramki stopu: DNP

Plik wygenerował silnik (2026-11-10). Nie edytuj go ręcznie.

**Decyzja: DALEJ** — brak twardej flagi.

| Etap | Bramka | Wynik | Opis | Dowody | Źródło |
|---:|---|---|---|---|---|
| 0 | B0.pokrycie | informacja | Pokrycie analityczne małe albo nieznane — nie można na nim polegać (brak danych o liczbie analityków) |  | kod |
| 0 | B0.lista_alertow | ok | Spółki nie ma na Liście Alertów GPW | doc-064 | kod |
| 0 | B0.oznaczenie_ciagle | ok | Brak szczególnego oznaczenia GPW | doc-065 | kod |
| 0 | B0.oznaczenie_jednolite | ok | Brak szczególnego oznaczenia GPW | doc-066 | kod |
| 0 | B0.zawieszenie | ok | Brak spółki w komunikatach o zawieszeniach | doc-067 | kod |
| 2 | B2.rozwodnienie | brak danych | Brak danych o liczbie akcji |  | kod |
| 3 | B3.altman | ok | Altman Z'' 2,06 (strefa zagrożenia poniżej 1,10) | altman_z2.FY2025 | kod |
| 3 | B3.beneish | ok | Beneish M-score -2,85 (próg -1,78): poniżej progu | beneish_m.FY2025 | kod |
| 3 | B3.przeplywy_do_zysku | ok | Przepływy operacyjne pokrywają zysk netto | przeplywy_operacyjne.FY2023; przeplywy_operacyjne.FY2024; przeplywy_operacyjne.FY2025 … | kod |

## Dowody od modelu odrzucone przez silnik

Brak.
