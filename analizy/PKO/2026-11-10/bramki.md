# Bramki stopu: PKO

Plik wygenerował silnik (2026-11-10). Nie edytuj go ręcznie.

**Decyzja: DALEJ** — brak twardej flagi.

| Etap | Bramka | Wynik | Opis | Dowody | Źródło |
|---:|---|---|---|---|---|
| 0 | B0.pokrycie | informacja | Brak danych o liczbie analityków — pokrycia nie można ocenić (dla GPW: wklejka z InvestingPro) |  | kod |
| 0 | B0.lista_alertow | brak danych | Strona GPW niedostępna: https://www.gpw.pl/lista-alertow-notowania: przerwana transmisja (RemoteDisconnected) |  | kod |
| 0 | B0.oznaczenie_ciagle | brak danych | Strona GPW niedostępna: https://www.gpw.pl/spolki-ze-szczegolnym-oznaczeniem-notowania-ciagle: przerwana transmisja (RemoteDisconnected) |  | kod |
| 0 | B0.oznaczenie_jednolite | brak danych | Strona GPW niedostępna: https://www.gpw.pl/spolki-ze-szczegolnym-oznaczeniem-notowania-jednolite: przerwana transmisja (RemoteDisconnected) |  | kod |
| 0 | B0.zawieszenia | brak danych | Strona GPW niedostępna: https://www.gpw.pl/zawieszenia-i-wykluczenia: przerwana transmisja (RemoteDisconnected) |  | kod |
| 1 | B1.sankcja_regulatora | flaga | Rezerwa na karę KNF dotyczącą lokat strukturyzowanych (sprawa produktowa, nie sprawozdawcza) i rezerwy na ochronę konsumentów | doc-051: „rezerw na karę KNF dotyczącą lokat strukturyzowanych” | model |
| 2 | B2.rozwodnienie | brak danych | Brak danych o liczbie akcji |  | kod |
| 3 | B3.finanse | informacja | Spółka finansowa: przepływy ÷ zysk, M-score i Z'' pominięte; adekwatność kapitałową (CET1) ocenia model |  | kod |
| 3 | B3.bank_kapital | ok | Współczynniki kapitałowe powyżej wymogów regulacyjnych (raport za III kw. 2026) | doc-051: „Współczynniki pozostawały powyżej wymogów regulacyjnych.” | model |

## Dowody od modelu odrzucone przez silnik

Brak.
