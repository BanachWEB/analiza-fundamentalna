# Bramki stopu: AAPL

Plik wygenerował silnik (2026-11-10). Nie edytuj go ręcznie.

**Decyzja: DALEJ** — brak twardej flagi.

| Etap | Bramka | Wynik | Opis | Dowody | Źródło |
|---:|---|---|---|---|---|
| 0 | B0.pokrycie | informacja | Brak danych o liczbie analityków — pokrycia nie można ocenić |  | kod |
| 1 | B1.slabosc_kontroli_wzmianka | flaga | Raport roczny wspomina o istotnej słabości kontroli wewnętrznej („material weakness”); często to ogólny opis ryzyka — model sprawdza; STOP, jeśli słabość jest nieusunięta | doc-012: 1 trafień od 2026-11-02 | kod |
| 1 | B1.korekta_sprawozdan | ok | Brak 8-K z pozycją 4.02 (korekta sprawozdań) |  | kod |
| 1 | B1.opoznione_raporty | ok | Brak zawiadomień NT 10-K/NT 10-Q |  | kod |
| 1 | B1.zmiana_bieglego | ok | Brak zmiany biegłego rewidenta |  | kod |
| 2 | B2.rozwodnienie | ok | Brak rozwodnienia powyżej progu | zmiana_liczby_akcji.FY2026 | kod |
| 3 | B3.altman | ok | Altman Z'' 3,20 (strefa zagrożenia poniżej 1,10) | altman_z2.FY2026 | kod |
| 3 | B3.beneish | ok | Beneish M-score -2,52 (próg -1,78): poniżej progu | beneish_m.FY2026 | kod |
| 3 | B3.kontynuacja_wzmianka | ok | Brak wzmianki „substantial doubt” w raportach od 2026-11-02 | doc-011: 0 trafień od 2026-11-02 | kod |
| 3 | B3.przeplywy_do_zysku | ok | Przepływy operacyjne pokrywają zysk netto | przeplywy_operacyjne.FY2024; przeplywy_operacyjne.FY2025; przeplywy_operacyjne.FY2026 … | kod |

## Dowody od modelu odrzucone przez silnik

Brak.
