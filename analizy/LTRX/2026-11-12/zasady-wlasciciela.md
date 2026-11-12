# Zasady właściciela dla LTRX (Lantronix, USA, NASDAQ)

Źródło: `/home/user/inwestowanie/zasady-inwestowania.md` (wersja 1.6) i `/home/user/inwestowanie/analiza/framework.md`. Sprawdzenie opiera się na `fakty.json` z tego katalogu. To nie jest rekomendacja.

| Zasada (cytat, sekcja) | Spełnia | Fakt |
|---|---|---|
| „Spółki spoza GPW tworzą koszyk „Akcje zagraniczne”.” (3. Agresywny (IKE) > Nauka — akcje i ETF tematyczne). LTRX to spółka z USA, więc trafia do tego koszyka w portfelu Agresywnym. | tak | analiza.json (rynek: USA) |
| „Kupuję spółki z GPW, z USA i z innych rynków, jeśli kraj spółki nie ma poważnych problemów (praworządność, stabilność polityczna, wojna i podobne).” (tamże) | brak danych (kraj nie jest w faktach; to ocena właściciela) | brak |
| „Pokrycie analityczne to liczba analityków, którzy wydają rekomendacje lub prognozy dla spółki. Pokrycie wystarcza, gdy spółkę śledzi ponad 3 analityków. Spółki zagranicznej z 3 analitykami lub mniej nie kupuję.” (tamże) | tak (więcej niż 3) | liczba_analitykow.2026-11-12 |
| „Skala dla USA: ponad 10 analityków to duże pokrycie, od 3 do 10 — średnie, poniżej 3 — słabe.” (tamże) | pokrycie średnie | liczba_analitykow.2026-11-12 |
| „Pauza po rajdzie: nie kupuję spółki ani ETF-u, dopóki kurs jest o ponad 25% wyższy niż 3 miesiące wcześniej.” (tamże) | tak (kurs nie jest wyższy o ponad 25%, bo spadł r/r w oknie 3 miesięcy) | zmiana_kursu_3m.2026-11-12 |
| „Najwyżej 40% IKE. Gdy Agresywny ma 40% lub więcej, nadwyżki idą do Core.” (3. Agresywny (IKE) — krypto, nauka na akcjach, ETF sektorowe) | brak danych (udział Agresywnego w IKE nie jest w faktach analizy) | brak |
| „Przed zakupem karta w pliku spółki (`spolki/<TICKER>.md`; jak ją zrobić — `analiza/framework.md`): liczba analityków z datą i źródłem (dla spółek, nie dla ETF-ów), teza w 3 zdaniach, co jest w cenie, antytezy z progami, pre-mortem, wielkość pozycji, kiedy sprzedam, data przeglądu. Kupuję w transzach.” (tamże) | nie (w `inwestowanie/spolki/` są tylko CBF, SMH, XTB; brak LTRX.md) | brak pliku |
| „zapisz ją w pliku spółki linią „**Pokrycie analityczne:** N analityków · RRRR-MM-DD · źródło” (silnik czyta tę linię)” (framework.md, Pięć kroków — przy każdej analizie). Miejsce zapisu: `spolki/LTRX.md` (spółka w portfelu) albo `analiza/kandydaci/LTRX.md` (kandydat). | do wykonania | liczba_analitykow.2026-11-12 (źródło: doc-011) |
| „Akcje zagraniczne | te same kwoty w te same dni w S&P 500” (Miary) i „Całe IKE (główna miara) | portfel-cień MSCI World” | benchmark: S&P 500 dla koszyka, MSCI World (IWDA) dla całego IKE | nie dotyczy |
| „Sprzedaję, gdy teza jest złamana, mam lepszą spółkę z kartą albo uznam „nie kupiłbym jej dziś”.” (Nauka) | nie dotyczy przed zakupem | brak |
| Nakładanie się z ETF-ami: żadna zasada nie ustala limitu nakładania się. Jedyna wzmianka to ryzyko zapisane w v1.4 dla półprzewodników („rośnie udział półprzewodników w całym IKE, bo są też w IWDA, CNDX i EIMI”, Historia zmian). Sektor LTRX w analiza.json: „ogolny”, branża Damodarana: Electronics (General). | brak danych | brak |
| Dostęp przez IKE: zasady nie mają osobnej reguły o dostępie do spółek z USA przez IKE. Agresywny jest zapisany jako „Agresywny (IKE)”, a koszyk „Akcje zagraniczne” jako część Agresywnego. Czy broker IKE oferuje LTRX, zasady nie mówią. | brak danych | brak |

Kapitalizacja ok. 210 mln USD (kapitalizacja.2026-11-12): zasady nie mają progu kapitalizacji.
