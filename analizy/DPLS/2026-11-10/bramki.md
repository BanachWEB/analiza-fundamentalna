# Bramki stopu: DPLS

Plik wygenerował silnik (2026-11-10). Nie edytuj go ręcznie.

**Decyzja: STOP** (etap 3: Wypłacalność i jakość zysków) — B3.kontynuacja: Istotna niepewność kontynuacji działalności w raporcie, ujemne przepływy operacyjne i zobowiązania krótkoterminowe wyższe niż aktywa obrotowe.

| Etap | Bramka | Wynik | Opis | Dowody | Źródło |
|---:|---|---|---|---|---|
| 0 | B0.pokrycie | informacja | Pokrycie analityczne małe albo nieznane — nie można na nim polegać (brak danych o liczbie analityków) |  | kod |
| 1 | B1.opoznione_raporty | flaga poważna | 9 zawiadomień o opóźnieniu raportu (NT) w 3 latach; przyczynę sprawdza model (przyczyny księgowe = STOP) | doc-002: NT 10-Q 2026-08-14 0001683168-26-006462; doc-002: NT 10-Q 2026-05-15 0001683168-26-003993; doc-002: NT 10-K 2026-03-31 0001683168-26-002553 … | kod |
| 1 | B1.zmiana_bieglego | flaga | Zmiana biegłego rewidenta (8-K, pozycja 4.01); model sprawdza, czy były spory | doc-002: 8-K 4.01 2026-09-24 0001683168-26-007352; doc-002: 8-K 4.01 2026-09-17 0001683168-26-007212; doc-002: 8-K 4.01 2024-07-03 0001683168-24-004669 … | kod |
| 1 | B1.korekta_sprawozdan | ok | Brak 8-K z pozycją 4.02 (korekta sprawozdań) |  | kod |
| 1 | B1.slabosc_kontroli_wzmianka | ok | Brak wzmianki „material weakness” w raportach od 2026-05-04 | doc-008: 0 trafień od 2026-05-04 | kod |
| 2 | B2.rozwodnienie_seryjne | flaga poważna | Liczba akcji rosła o ponad 10% r/r w 4 z 5 ostatnich lat; sprawdź, czy emisje szły bez prawa poboru (wtedy STOP wymaga dowodu) | zmiana_liczby_akcji.FY2021; zmiana_liczby_akcji.FY2022; zmiana_liczby_akcji.FY2023 … | kod |
| 3 | B3.kontynuacja | STOP | Istotna niepewność kontynuacji działalności w raporcie, ujemne przepływy operacyjne i zobowiązania krótkoterminowe wyższe niż aktywa obrotowe | doc-007: 4 trafień od 2026-05-04; przeplywy_operacyjne.FY2025; aktywa_obrotowe.2026-06-30 … | kod |
| 3 | B3.ujemny_kapital | STOP | Ujemny kapitał własny na 2026-06-30, niewyjaśniony skupem akcji | kapital_wlasny_z_udzialami_niekontrolujacymi.2026-06-30 | kod |
| 3 | B3.altman | flaga poważna | Altman Z'' -284,43 (strefa zagrożenia poniżej 1,10) | altman_z2.FY2025 | kod |
| 3 | B3.kontynuacja_wzmianka | flaga poważna | Raport okresowy wspomina o istotnej niepewności kontynuacji działalności („substantial doubt”); STOP, jeśli do tego ujemne przepływy i dług do spłaty bez finansowania | doc-007: 4 trafień od 2026-05-04 | kod |
| 3 | B3.przeplywy_do_zysku | ok | Zysk netto z 3 lat ≤ 0 (patrz wskaźniki) | przeplywy_operacyjne.FY2023; przeplywy_operacyjne.FY2024; przeplywy_operacyjne.FY2025 … | kod |

## Dowody od modelu odrzucone przez silnik

Brak.
