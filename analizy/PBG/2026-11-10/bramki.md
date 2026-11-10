# Bramki stopu: PBG

Plik wygenerował silnik (2026-11-10). Nie edytuj go ręcznie.

**Decyzja: STOP** (etap 0: Identyfikacja i status) — B0.lista_alertow: Spółka jest na Liście Alertów GPW.

| Etap | Bramka | Wynik | Opis | Dowody | Źródło |
|---:|---|---|---|---|---|
| 0 | B0.lista_alertow | STOP | Spółka jest na Liście Alertów GPW | doc-023: PBG /Z /6,/7 | kod |
| 0 | B0.oznaczenie_jednolite | flaga poważna | Spółka ma szczególne oznaczenie GPW (PBG /Z /6,/7); model sprawdza przyczynę: upadłość, restrukturyzacja albo likwidacja = STOP | doc-025: PBG /Z /6,/7 | kod |
| 0 | B0.zawieszenie | flaga poważna | Spółka występuje w komunikatach GPW o zawieszeniach i wykluczeniach; model sprawdza, czy obrót jest zawieszony (wtedy STOP) | doc-026: PBG | kod |
| 0 | B0.pokrycie | informacja | Pokrycie analityczne małe albo nieznane — nie można na nim polegać (brak danych o liczbie analityków) |  | kod |
| 0 | B0.oznaczenie_ciagle | ok | Brak szczególnego oznaczenia GPW | doc-024 | kod |
| 2 | B2.rozwodnienie | brak danych | Brak danych o liczbie akcji |  | kod |
| 3 | B3.ujemny_kapital | STOP | Ujemny kapitał własny niewyjaśniony skupem akcji | kapital_wlasny.2025-12-31 | kod |
| 3 | B3.przeplywy_do_zysku | ok | Zysk netto z 3 lat ≤ 0 (patrz wskaźniki) | przeplywy_operacyjne.FY2023; przeplywy_operacyjne.FY2024; przeplywy_operacyjne.FY2025 … | kod |

## Dowody od modelu odrzucone przez silnik

Brak.
