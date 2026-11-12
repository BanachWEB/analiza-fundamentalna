# Braki silnika wykryte przy analizie MU (12.11.2026)

## Poprawione w trakcie analizy (za zgodą właściciela na decyzje techniczne)

1. **Mapowanie US GAAP: dług długoterminowy.** Micron nie używa `LongTermDebtNoncurrent`, tylko `LongTermDebtAndCapitalLeaseObligations`. Silnik widział tylko część bieżącą długu, przez co dług był zaniżony, a Piotroski F-score się nie liczył. Poprawka: `konfiguracja/mapowanie-us-gaap.yaml`, test `testy/test_braki_mu.py`.
2. **Mapowanie US GAAP: rzeczowe aktywa trwałe.** Micron od 2020 r. raportuje je razem z leasingiem finansowym (`PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization`). Beneish M-score się nie liczył. Poprawka i test jak wyżej.

## Do zrobienia (sugerowane zadania)

3. **Udziały z propozycji.** Silnik nie liczy udziału jednej pozycji w drugiej dla pozycji spoza mapowania (np. przychody z Chin ÷ przychody). Przykład: `przychody_geo_chiny.FY2026` ÷ `przychody.FY2026`. Zadanie: ogólny wskaźnik „udział” dla par pozycji wskazanych w propozycjach.
4. **Wycena odwrotna dla spółki cyklicznej.** Wycena odwrotna startuje od FCF TTM. W szczycie cyklu (MU, FY2026) daje to niski implikowany wzrost i CAP bliski zera, co myli. Zadanie: wariant z FCF znormalizowanym (średnia marża FCF z pełnego cyklu, np. 7–10 lat × przychody TTM).
5. **Dług netto a długoterminowe papiery dłużne.** `dlug_netto` odejmuje tylko gotówkę i inwestycje krótkoterminowe. Micron ma duże długoterminowe papiery dłużne dostępne do sprzedaży (`AvailableForSaleSecuritiesDebtSecuritiesNoncurrent`), więc gotówka netto jest zaniżona. Zadanie: osobna pozycja `inwestycje_dlugoterminowe_plynne` i wariant długu netto z nią.
6. **Konsensus tylko na jeden rok.** Stock Analysis dał `przychody_konsensus` tylko na FY2027, więc ścieżka przychodów w scenariuszach ma jeden rok. Zadanie: pobierać konsensus na 2–3 lata, jeśli strona go podaje.
7. **Ostrzeżenie o nieaktualnym arkuszu ceny docelowej.** Arkusz właściciela miał prognozę EPS na 12 miesięcy niższą niż raportowany EPS rozwodniony FY2026 i kurs dużo niższy od bieżącego. Silnik nie ostrzega o takiej rozbieżności. Zadanie: porównać `eps_prognoza_arkusz` z `eps_rozwodniony` TTM i z konsensusem oraz `kurs_arkusz` z `kurs` i zapisać ostrzeżenie w obliczenia.md.
8. **Data kursu.** Yahoo dał ostatni kurs z datą 11.11.2026, który różni się od kursu zamknięcia w materiale InvestingPro z tego samego dnia. Możliwe, że ostatni słupek to sesja w toku. Zadanie: sprawdzać znacznik czasu ostatniego słupka i pomijać niezamkniętą sesję.
