# Bramki stopu: LTRX

Plik wygenerował silnik (2026-11-12). Nie edytuj go ręcznie.

**Decyzja: DALEJ** — brak twardej flagi.

| Etap | Bramka | Wynik | Opis | Dowody | Źródło |
|---:|---|---|---|---|---|
| 0 | B0.pokrycie | ok | Pokrycie analityczne średnie (6 analityków) | liczba_analitykow.2026-11-12 | kod |
| 1 | B1.slabosc_kontroli_wzmianka | flaga | Raport roczny wspomina o istotnej słabości kontroli wewnętrznej („material weakness”); często to ogólny opis ryzyka — model sprawdza; STOP, jeśli słabość jest nieusunięta | doc-015: 1 trafień od 2026-08-26 | kod |
| 1 | B1.korekta_sprawozdan | ok | Brak 8-K z pozycją 4.02 (korekta sprawozdań) |  | kod |
| 1 | B1.opoznione_raporty | ok | Brak zawiadomień NT 10-K/NT 10-Q |  | kod |
| 1 | B1.zmiana_bieglego | ok | Brak zmiany biegłego rewidenta |  | kod |
| 2 | B2.rozwodnienie_seryjne | flaga poważna | Liczba akcji rosła o ponad 10% r/r w 3 z 5 ostatnich lat; miara: na koniec okresu, średnia ważona; sprawdź, czy emisje szły bez prawa poboru (wtedy STOP wymaga dowodu) | zmiana_liczby_akcji.FY2022; zmiana_liczby_akcji_koniec.FY2022; zmiana_liczby_akcji.FY2023 … | kod |
| 3 | B3.altman | ok | Altman Z'' 1,52 (strefa zagrożenia poniżej 1,10) | altman_z2.FY2026 | kod |
| 3 | B3.beneish | ok | Beneish M-score -2,91 (próg -1,78): poniżej progu | beneish_m.FY2026 | kod |
| 3 | B3.kontynuacja_wzmianka | ok | Brak wzmianki „substantial doubt” w raportach od 2026-08-26 | doc-014: 0 trafień od 2026-08-26 | kod |
| 3 | B3.przeplywy_do_zysku | ok | Zysk netto z 3 lat ≤ 0 (patrz wskaźniki) | przeplywy_operacyjne.FY2024; przeplywy_operacyjne.FY2025; przeplywy_operacyjne.FY2026 … | kod |

## Dowody od modelu odrzucone przez silnik

Brak.
