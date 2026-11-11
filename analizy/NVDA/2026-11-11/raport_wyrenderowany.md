# NVIDIA Corporation (NVDA) — wstępna analiza fundamentalna

Data analizy: 11.11.2026. Rynek: USA. Instrument w XTB: NVDA.US. Decyzja bramek: DALEJ, z flagami do śledzenia (dochodzenie rady wobec prezesa, Chiny, jakość zysków wg Beneisha).

## TL;DR

> NVIDIA sprzedaje platformy obliczeniowe dla centrów danych AI: układy GPU, procesory, sieć i oprogramowanie. Spółka nie ma własnych fabryk. W Q2 FY2027 centra danych dały 89,0 mld USD[^1] z 96,2 mld USD[^2] przychodów. Kurs 168,89 USD[^3] zakłada, że FCF dla właścicieli będzie rósł o 13,7%[^4] rocznie przez dziesięć lat. Moim zdaniem to oczekiwanie leży powyżej stopy bazowej dla spółek tej wielkości, więc szansę, że spółka pobije oczekiwania zawarte w cenie, oceniam na około jedną trzecią. Największe ryzyka to cykl nakładów na centra danych, koncentracja klientów i ograniczenia eksportowe. Do tego dochodzi świeże dochodzenie rady w sprawie prezesa. Wg twoich zasad: spółka ma duże pokrycie analityczne, pauza po rajdzie jej nie dotyczy, a przed zakupem potrzebujesz karty w `spolki/NVDA.md`.

- Przewaga konkurencyjna: wąska, trend niepewny (uzasadnienie w części czwartej).
- Wycena: kapitalizacja 4,07 bln USD[^5], C/Z 21,1×[^6], FCF yield 2,9%[^7].
- Wartość oczekiwana ze scenariuszy: 104,87 USD[^8] przy kursie 168,89 USD[^3]; prawdopodobieństwo straty 75,0%[^9]. Model scenariuszy przyjmuje stały wzrost przez dziesięć lat, więc nie oddaje prognozy zarządu na najbliższe dwa lata (część dziesiąta).
- Karta w stylu Treli: wynik wysoki; wycenę i momentum karta ocenia słabiej niż wzrost i jakość (część jedenasta).
- Pokrycie analityczne: duże, 62[^10] analityków.

## 1. Jak działa firma

NVIDIA opisuje się w raporcie rocznym jako spółka infrastruktury AI w skali centrum danych (`doc-019`). Klient kupuje od niej nie sam układ, lecz platformę: procesory graficzne, procesory centralne, układy sieciowe, systemy i oprogramowanie (`doc-031`). Podstawą platformy jest środowisko programistyczne CUDA. Spółka podaje, że z CUDA i innych narzędzi korzysta ponad siedem i pół miliona programistów (`doc-019`).

Spółka nie produkuje układów sama. Płytki krzemowe wytwarzają TSMC i Samsung, pamięć dostarczają SK Hynix, Micron i Samsung, a montaż wykonują firmy kontraktowe (`doc-019`). Produkcja i montaż koncentrują się na Tajwanie (`doc-019`).

Bezpośrednimi klientami są producenci kart, dystrybutorzy, producenci serwerów, dostawcy chmury, twórcy modeli AI i integratorzy (`doc-020`). Użytkownik końcowy często kupuje pośrednio, na przykład wynajmuje moc obliczeniową w chmurze. W raporcie rocznym spółka szacuje, że jedna firma badawcza AI wniosła znaczącą część przychodów przez zakupy usług chmurowych u klientów NVIDII (`doc-019`).

W 2026 roku spółka dodała nowy element modelu. Pomaga wybranym chmurom AI zdobyć grunt, energię i budynki pod centra danych, bo ci klienci rosną szybciej niż ich bilanse (`doc-031`). W zamian sprzedaje im infrastrukturę i przy spełnieniu warunków dostaje udział w ich przychodach (`doc-031`).

Jedno zdanie: dostawcy chmury, twórcy modeli i przedsiębiorstwa płacą NVIDII za kompletną infrastrukturę do trenowania i uruchamiania modeli AI. Wybierają ją, bo prawie całe oprogramowanie AI powstaje na jej platformie, a konkurencyjne układy nie mają tak szerokiego ekosystemu.

Czynniki wartości do śledzenia co kwartał:
1. przychody centrów danych i ich podział na hiperskalerów oraz grupę ACIE (chmury AI, przemysł, przedsiębiorstwa);
2. marża brutto wobec prognozy zarządu;
3. zobowiązania zakupowe i zapasy wobec przychodów;
4. należności i terminy płatności;
5. udział największych klientów.

Test `3P` (Damodaran), moja ocena:
- Prawdopodobne: przychody w najbliższych kwartałach rosną, bo zarząd ma zamówienia i zabezpieczone dostawy.
- Wiarygodne: NVIDIA utrzymuje wysoką marżę brutto przy kolejnych generacjach układów.
- Tylko możliwe: dzisiejsza skala przychodów utrzyma się i będzie rosła przez dekadę mimo własnych układów klientów.

## 2. Na czym zarabia

Spółka raportuje dwa segmenty: Compute & Networking oraz Graphics (`doc-019`). W Q2 FY2027 segment Compute & Networking dał 88,3 mld USD[^11] przychodów i 62,7 mld USD[^12] zysku operacyjnego. Segment Graphics dał 7,9 mld USD[^13] przychodów i 3,9 mld USD[^14] zysku operacyjnego (`doc-031`, `doc-020`). Zysk pochodzi więc prawie w całości z segmentu, o którym mówią nagłówki.

Od Q1 FY2027 spółka pokazuje też przychody według platform rynkowych (`doc-020`). W Q2 FY2027 centra danych dały 89,0 mld USD[^1], w tym hiperskalerzy 48,7 mld USD[^15] i grupa ACIE 40,3 mld USD[^16]. Edge Computing dał 7,2 mld USD[^17] (`doc-031`). W Q2 FY2027 spółka przeniosła jednego klienta z ACIE do hiperskalerów i przeliczyła okres porównawczy, więc podział na te dwie grupy nie jest ciągły (`doc-031`).

Przychody są skoncentrowane. W Q2 FY2027 jeden klient bezpośredni dał 16,0%[^18] przychodów (`doc-020`). W Q1 FY2027 trzech klientów bezpośrednich dało 21,0%[^19], 17,0%[^20] i 16,0%[^21] przychodów (`doc-021`). W FY2026 dwóch klientów dało 22,0%[^22] i 14,0%[^23] przychodów (`doc-019`).

Według siedziby klienta bezpośredniego USA dały w Q2 FY2027 60,1 mld USD[^24], Tajwan 27,0 mld USD[^25], a Chiny z Hongkongiem 7,9 mld USD[^26] (`doc-020`). Spółka zastrzega, że siedziba klienta nie musi być miejscem wysyłki ani użytkowania (`doc-020`).

Zarząd prognozuje na Q3 FY2027 przychody 108,0 mld USD[^27] i marżę brutto 74,0%[^28]. W Q2 FY2027 marża brutto wyniosła 75,0%[^29] (`doc-030`, `doc-031`). Prognoza nie zakłada żadnych przychodów z centrów danych w Chinach (`doc-031`).

## 3. Najważniejsze fakty (akcjonariat, zarząd, płynność, kalendarz)

- Akcjonariat: zarząd i rada mają razem 3,9%[^30] akcji, prezes Jensen Huang 3,6%[^31], BlackRock 7,4%[^32], a Vanguard 7,3%[^33] (`doc-022`). Nikt nie kontroluje spółki.
- Prezes: Jensen Huang założył spółkę w 1993 roku i od początku kieruje nią jako prezes (`doc-022`). `DEF 14A` nie opisuje planu sukcesji. W raporcie rocznym spółka pisze, że w dużym stopniu zależy od wieloletniego zespołu kierowniczego (`doc-019`).
- Dochodzenie rady: 8.11.2026 rada ogłosiła niezależne dochodzenie po doniesieniach, że prezes był celem działań obcego wywiadu (`doc-045`). Rada pisze, że nie ma powodu sądzić, by naruszono bezpieczeństwo narodowe albo tajemnice spółki, i deklaruje zaufanie do prezesa (`doc-045`). 10.11.2026 niezależni członkowie rady zatrudnili do dochodzenia kancelarię Wachtell, Lipton, Rosen & Katz (`doc-043`). Spółka nie złożyła w tej sprawie raportu 8-K.
- Płynność: średnie obroty dzienne z sześćdziesięciu sesji wynoszą 27,7 mld USD[^34].
- Kurs: 168,89 USD[^3], zmiana w trzy miesiące -22,3%[^35], RSI czternastodniowy 23,95[^36].
- Kalendarz: spółka poda wyniki za Q3 FY2027 17.11.2026 (komunikat spółki z 28.10.2026, według przeglądu wiadomości). Przejęcie Hugging Face za 11,9 mld USD[^37] ma się zamknąć w pierwszej połowie 2027 roku, po zgodach regulatorów (`doc-024`).

## 4. Branża, konkurencja i przewaga konkurencyjna

Spółka wymienia jako konkurentów w akceleratorach AMD, Huawei i Intel (`doc-019`). Własne układy AI projektują duzi dostawcy chmury: Alibaba, Alphabet, Amazon, Baidu, Huawei i Microsoft (`doc-019`). Czterech z nich to jednocześnie klienci NVIDII. W sieciach spółka konkuruje między innymi z Aristą, Broadcomem, Cisco i Marvellem (`doc-019`). Spółka oczekuje silniejszej konkurencji, w tym tańszych produktów nowych graczy (`doc-019`).

Chiny są dla spółki praktycznie zamknięte. W 10-Q za Q2 FY2027 spółka pisze, że ograniczenia eksportowe wykluczyły ją z chińskiego rynku centrów danych, a to pomogło konkurentom zbudować większe ekosystemy (`doc-020`). Rząd Chin zachęca klientów do zakupów u chińskich producentów (`doc-020`). Organy ochrony konkurencji w UE, USA, Wielkiej Brytanii, Chinach i Korei Południowej wysyłają spółce zapytania o sprzedaż i przydział dostaw (`doc-020`).

Branża jest w fazie gwałtownej budowy mocy. Nie mam w archiwum danych o udziałach rynkowych, więc nie liczę stabilności udziałów ani HHI. Branża półprzewodników jest cykliczna: w panelu widać, że w FY2023 przychody stały w miejscu, a marża operacyjna spadła do 15,7%‼[^38].

Kandydaci na źródło przewagi:
- **Efekt sieciowy i koszty zmiany dostawcy (CUDA).** Korzyść: klient płaci wyższą cenę, bo oprogramowanie AI działa na NVIDII od razu. Bariera: miliony programistów i setki bibliotek, których konkurent nie skopiuje szybko (`doc-019`).
- **Pełna platforma.** Korzyść: spółka sprzedaje cały system, a nie pojedynczy układ. Bariera: integracja procesorów, sieci i oprogramowania w skali szafy serwerowej (`doc-019`).
- **Skala i zabezpieczone dostawy.** Spółka zabezpieczyła komponenty na kilka lat; zobowiązania na dostawy i moce wzrosły do 279,0 mld USD[^39] (`doc-020`, `doc-031`). To przewaga w okresie niedoboru, ale też ryzyko, gdy popyt spadnie.

Liczby: ROIC wynosi 65,1%[^40], a w FY2023, roku spadku, wyniósł 16,9%‼[^41]. Koszt kapitału własnego to 9,4%[^42]. Marża brutto spadła w FY2023 do 56,9%[^43], a potem wróciła do 74,7%[^44].

Moim zdaniem przewaga jest wąska, a trend niepewny. Zwroty powyżej kosztu kapitału przez dziesięć lat są bardziej prawdopodobne niż nie, bo ekosystem CUDA działa jak efekt sieciowy. Nie uznaję jej za szeroką z trzech powodów. Po pierwsze, najwięksi klienci budują własne układy i mają skalę, by przenieść część pracy. Po drugie, rząd USA już odebrał spółce chiński rynek centrów danych, a dalsze ograniczenia są możliwe. Po trzecie, dzisiejsze zwroty powstały w okresie niedoboru, a nie w pełnym cyklu. Stopa bazowa: nawet spółka z najwyższego kwintyla ROIC ma około połowy szans, że zostanie w nim po dekadzie.

Test AI (moja ocena):
1. Przychody nie zależą od godzin pracy ludzi; AI to źródło popytu.
2. Koszt zmiany dostawcy wynika z integracji oprogramowania i infrastruktury, więc jest silniejszy niż przyzwyczajenie.
3. Spółka ma własne biblioteki i modele, ale nie dane klientów.
4. AI może obniżyć koszt przenoszenia oprogramowania na inne układy, a to osłabia barierę CUDA. Spółka sama pisze, że modele otwarte uruchamiane na platformach konkurentów mogą zmniejszyć popyt na jej produkty (`doc-020`).
5. Oszczędności z AI w samej spółce nie decydują o wyniku.

## 5. Zarząd i alokacja kapitału

Jensen Huang kieruje spółką od założenia (`doc-022`). Jego łączne wynagrodzenie w FY2026 wyniosło 36,3 mln USD[^45], a w FY2025 49,9 mln USD[^46] (`doc-022`). Wieloletnie akcje za wyniki zależą od zwrotu dla akcjonariuszy względem S&P 500 (`doc-022`). Rada ma niezależnego dyrektora wiodącego, a wszyscy jej członkowie poza prezesem są niezależni (`doc-022`). Trzech niezależnych dyrektorów zasiada w radzie od lat dziewięćdziesiątych: Tench Coxe i Harvey Jones od 1993 roku, Brooke Seawell od 1997 roku (`doc-022`). Moim zdaniem tak długi staż osłabia niezależność rady akurat w dochodzeniu wobec prezesa, z którym ci dyrektorzy pracują od dekad.

W 2026 roku spółka wymieniła głównego księgowego: od 4.05.2026 jest nim Scott Gawel, wcześniej w Intelu (`doc-027`). Szef sprzedaży światowej Ajay Puri przechodzi na emeryturę, a jego następca Nicholas Parker przychodzi z Microsoftu (`doc-025`).

Zwrot kapitału: w Q2 FY2027 spółka zwróciła akcjonariuszom około 26,0 mld USD[^47] przez odkup i dywidendy (`doc-030`). W pierwszym półroczu FY2027 odkupiła 203,0 mln akcji[^48] akcji za 39,8 mld USD[^49] (`doc-020`). Rada podniosła dywidendę kwartalną z 0,01 USD[^50] do 0,25 USD[^51] na akcję (`doc-020`). Liczba akcji na koniec roku spadła w FY2026 o -0,7%[^52].

Nowe zastosowania kapitału zmieniają profil ryzyka:
- Spółka kupiła w półroczu papiery kapitałowe za -42,4 mld USD[^53]; papiery nienotowane wzrosły od początku roku z 22,3 mld USD[^54] do 51,2 mld USD[^55] (`doc-020`). Spółka zobowiązała się do dalszych inwestycji w twórców modeli AI i firmy finansujące infrastrukturę za 25,0 mld USD[^56] (`doc-020`).
- W sierpniu 2026 spółka udzieliła gwarancji wartości rezydualnej dzierżaw kampusu SB Energy, którego najemcą jest spółka powiązana z OpenAI, z limitem 105,0 mld USD[^57] (`doc-023`). Łączna maksymalna ekspozycja z gwarancji wynosi 108,5 mld USD[^58] (`doc-031`). OpenAI zobowiązał się zwrócić NVIDII wypłaty, a gwarancje zaczną działać etapami od FY2029 (`doc-023`, `doc-031`).
- W Q2 FY2027 spółka wyemitowała obligacje za 25,0 mld USD[^59] (`doc-031`). Dług wynosi 33,4 mld USD[^60], a gotówka z papierami dłużnymi 56,6 mld USD[^61] (`doc-020`, `doc-031`).

Moim zdaniem spółka finansuje dziś własnych klientów: inwestuje w nich, gwarantuje ich dzierżawy i wydłuża im terminy płatności. To wspiera sprzedaż, ale wiąże wynik NVIDII z kondycją kilku klientów bez ratingu inwestycyjnego. Spółka sama pisze, że te zobowiązania zależą od wyników klientów i partnerów (`doc-020`).

## 6. Sprawozdania finansowe


| Wskaźnik | FY2022 | FY2023 | FY2024 | FY2025 | FY2026 | TTM 07.2026 |
|---|---:|---:|---:|---:|---:|---:|
| Przychody | 26 914 | 26 974 | 60 922 | 130 497 | 215 938 | 302 970 |
| Wzrost przychodów r/r | 61,4% | 0,2% | 125,9% | 114,2% | 65,5% | — |
| Marża brutto | 64,9% | 56,9% | 72,7% | 75,0% | 71,1% | 74,7% |
| Marża operacyjna | 37,3% | 15,7%‼ | 54,1% | 62,4% | 60,4% | 65,2%¹ |
| Marża netto | 36,2% | 16,2% | 48,8% | 55,8% | 55,6% | 63,7%¹ |
| Zysk netto | 9 752 | 4 368 | 29 760 | 72 880 | 120 067 | 192 880¹ |
| EBITDA | 11 215¹ | 5 768‼ | 34 480¹ | 83 317¹ | 133 230¹ | 201 266¹ |
| FCF dla właścicieli | 6 128 | 1 099 | 23 472 | 56 116 | 90 290 | 119 765¹ |
| FCF dla właścicieli ÷ zysk netto | 62,8% | 25,2% | 78,9% | 77,0% | 75,2% | 62,1%¹ |
| Marża FCF | 22,8% | 4,1% | 38,5% | 43,0% | 41,8% | 39,5%¹ |
| Capex ÷ amortyzacja | 0,83¹ | 1,19¹ | 0,71¹ | 1,74¹ | 2,13¹ | 1,99¹ |
| ROE | 44,8% | 17,9% | 91,5% | 119,2% | 101,5% | 117,2%¹ |
| ROIC | 48,5%¹ | 16,9%‼ | 97,5%¹ | 144,3%¹ | 66,4%¹ | 65,1%¹ |
| Dług netto ÷ EBITDA | gotówka netto¹ | gotówka netto¹ | gotówka netto¹ | gotówka netto¹ | gotówka netto¹ | 0,05¹ |
| Dług netto z leasingiem ÷ EBITDA | — | — | — | — | — | — |
| Pokrycie odsetek (EBIT ÷ odsetki) | 42,55¹ | 16,12‼ | 128,30¹ | 329,77¹ | 503,42¹ | 425,82¹ |
| Zmiana liczby akcji r/r (średnia ważona) | 1,0%‼ | — | -0,5% | -0,5% | -1,2% | — |
| Zmiana liczby akcji r/r (koniec okresu) | 1,1%¹ | -1,6%¹ | — | -0,7%¹ | -0,7%¹ | — |
| Piotroski F-score (0–9) | 5,00‼ | 4,00‼ | 8,00¹ | 8,00¹ | 4,00¹ | — |
| Beneish M-score (próg −1,78) | -1,74¹ | -2,69¹ | -1,12¹ | -0,95¹ | -1,15¹ | — |
| Altman Z'' (strefy 1,10 / 2,60) | 7,95¹ | 5,34‼ | 10,20¹ | 13,12¹ | 12,85¹ | — |
| Ohlson: prawdopodobieństwo upadłości w roku (próg 3,8%) | 0,0%¹ | 0,1%¹ | 0,0%¹ | 0,0%¹ | 0,0%¹ | — |

Kwoty w mln USD. ¹ = co najmniej jedno wejście z jednego źródła; ‼ = konflikt źródeł; — = brak danych. TTM = ostatnie 12 miesięcy.


![przychody](wykres_przychody.png)

![marze](wykres_marze.png)

![fcf_zysk](wykres_fcf_zysk.png)

![roic](wykres_roic.png)

Wzrost: przychody wzrosły w FY2026 o 65,5%[^62] do 215,9 mld USD[^63]. Za cztery kwartały do 26.07.2026 przychody wyniosły 303,0 mld USD[^64]. CAGR przychodów z pięciu lat to 66,9%[^65].

Marże: marża brutto wynosi 74,7%[^44], marża operacyjna 65,2%[^66], a marża netto 63,7%[^67]. Zysk netto Q2 FY2027 zawiera zyski z papierów kapitałowych w wysokości 7,8 mld USD[^68] (`doc-031`), więc marża netto TTM jest zawyżona przez wynik spoza działalności podstawowej.

Jakość zysków: FCF dla właścicieli za cztery kwartały wyniósł 119,8 mld USD[^69], czyli 62,1%[^70] zysku netto. W FY2026 konwersja wyniosła 75,2%[^71]. Capex rośnie szybciej niż amortyzacja: relacja wynosi 2,0×[^72].

Kapitał obrotowy: zapasy wzrosły do 31,6 mld USD[^73] z 25,8 mld USD[^74] kwartał wcześniej; spółka tłumaczy to przygotowaniem do premiery Vera Rubin (`doc-031`). Należności handlowe wynoszą 63,1 mld USD[^75], a DSO wzrosło do 60 dni[^76] z 45 dni[^77] (`doc-031`). Spółka podaje jako przyczynę dłuższe terminy płatności, do roku, w dużych umowach z klientami o ratingu inwestycyjnym (`doc-020`).

Zadłużenie: dług netto do EBITDA wynosi 0,1×[^78], a pokrycie odsetek 425,8×[^79]. Spółka ma bilans bez napięcia mimo emisji obligacji.

Rozwodnienie: spółka skupuje więcej akcji, niż wydaje w programach motywacyjnych; liczba akcji (średnia ważona) spadła w FY2026 o -1,2%[^80]. Wynagrodzenia akcyjne w Q2 FY2027 wyniosły 2,0 mld USD[^81].

## 7. Jakość zysków i czerwone flagi


**Decyzja bramek: DALEJ** — brak twardej flagi.

| Etap | Bramka | Wynik | Opis |
|---:|---|---|---|
| 3 | B3.beneish | flaga | Wzrost należności 10-Q tłumaczy spółka wydłużonymi terminami płatności w dużych umowach wieloletnich z klientami o ratingu inwestycyjnym; jednocześnie zapasy i zobowiązania zakupowe rosną pod popyt (Vera Rubin). To diagnostyka jakości zysków, nie stop; bez dowodu manipulacji zostaje flaga. |
| 4 | B4.oszustwo | flaga | Spółka ogłosiła 8.11.2026 niezależne dochodzenie rady (kancelaria Wachtell, doc-043); rada pisze, że nie ma podstaw sądzić, że bezpieczeństwo narodowe lub tajemnice zostały naruszone. Brak dowodu oszustwa lub tunelowania, więc nie stop; ryzyko ładu do obserwacji do wyniku dochodzenia. Brak 8-K w EDGAR; źródło to komunikaty na nvidianews.nvidia.com (doc-043..045). |
| 4 | B4.insiderzy | informacja | Sprzedaże Teter (doc-032), Coxe (doc-034, doc-037), Kress (doc-041) idą w planach 10b5-1; prezes Huang we wrześniu 2026 ma tylko potrącenie podatku i darowizny (doc-042). Wyjątek: dyrektor Stevens 18.09.2026 sprzedał w otwartym oknie akcje bez wzmianki o planie 10b5-1 (doc-033), to legalne, więc informacja, nie flaga. |
| 4 | B4.kontrahenci | informacja | Klienci bezpośredni to znane firmy (należności: pięciu klientów 22%, 14%, 13%, 11%, 10%), brak niesprawdzalnych kontrahentów. Informacja: gwarancje wartości rezydualnej do $105 mld dla dzierżawy z najemcą OpenAI to ekspozycja na jednego klienta, poza bilansem. |
| 5 | B5.decyzja_organu | flaga | Spółka sama pisze o faktycznym wyłączeniu z chińskiego rynku centrów danych i odpisach H20/H200, ale sprzedaż H200 to poniżej 1% przychodów Data Center, a Chiny są poza prognozą (doc-031). Rdzeń biznesu nie jest odebrany, więc flaga. |


Opis flag:
- **Dochodzenie rady wobec prezesa (flaga).** Rada bada, czy prezes był celem obcego wywiadu, i deklaruje zaufanie do niego (`doc-045`). Nie ma dowodu oszustwa, więc to flaga, a nie stop. Z materiału InvestingPro nie potwierdziłem dokumentem spółki zarzutów o ułatwianie wysyłek układów do Chin ani udziału FBI.
- **Chiny (flaga).** Spółka pisze, że jest praktycznie wykluczona z chińskiego rynku centrów danych (`doc-020`). Poniosła odpis na zapasy i zobowiązania związane z układami `H200` w wysokości 400,0 mln USD[^82] (`doc-020`). Rdzeń biznesu działa jednak bez Chin, więc to flaga, a nie stop.
- **Beneish M-score (flaga diagnostyczna).** M-score za FY2026 wynosi -1,15[^83], powyżej progu. Wskaźnik reaguje na szybki wzrost należności. Spółka tłumaczy ten wzrost dłuższymi terminami płatności (`doc-020`). Moim zdaniem to nie dowód manipulacji, ale realne ryzyko kredytowe, które warto śledzić.
- **„Material weakness”.** Zwrot występuje w raporcie rocznym tylko w opisie ryzyk. Zarząd i biegły stwierdzają skuteczną kontrolę wewnętrzną, a opinia biegłego jest bez zastrzeżeń (`doc-019`).
- **Insiderzy.** Sprzedaże dyrektorów i członków zarządu w ostatnich miesiącach idą głównie w planach `10b5-1`. Prezes we wrześniu 2026 przekazał akcje na podatek i w darowiznach (`doc-042`). Jeden dyrektor sprzedał akcje we wrześniu bez wzmianki o planie, w otwartym oknie transakcyjnym (`doc-033`).

Wskaźniki statystyczne: Altman Z'' wynosi 12,85[^84] (strefa bezpieczna), Piotroski F-score 4,00[^85], a prawdopodobieństwo upadłości wg Ohlsona 0,0%[^86]. Żaden z nich nie zatrzymuje analizy.

## 8. Co jest w cenie


| Miara | Wartość | Uwagi |
|---|---:|---|
| Kurs | 168,89 USD |  |
| Kapitalizacja | 4 070 249 mln USD¹ |  |
| EV | 4 081 172 mln USD¹ |  |
| Koszt kapitału własnego | 9,4%¹ | stopa wolna od ryzyka + beta × premia (Damodaran) |
| C/Z | 21,10¹ |  |
| EV/EBIT | 20,66¹ |  |
| EV/EBITDA | 20,28¹ |  |
| C/WK | 17,78¹ |  |
| C/S na rok naprzód | 9,88¹ | informacja; kapitalizacja ÷ konsensus przychodów na rok obrotowy do 2027-01-31 |
| FCF yield | 2,9%¹ | FCF dla właścicieli ÷ kapitalizacja |
| Udział PVGO w cenie | 49,8%¹ | część ceny za przyszły wzrost |
| Implikowany wzrost FCF (10 lat) | 13,7%¹ | wariant 1 |
| Implikowany okres przewagi (CAP) | 1,7 lat¹ | wariant 2, wzrost w tempie historycznym |
| Implikowana marża FCF | 1,1%¹ | wariant 3, wzrost w tempie historycznym |
| Wzrost historyczny (CAGR przychodów) | 66,9% |  |
| RSI 14-dniowy | 23,95¹ | informacja, nie bramka; umowne progi 70 i 30 |


Kurs 168,89 USD[^3] zakłada, że FCF dla właścicieli będzie rósł o 13,7%[^4] rocznie przez dziesięć lat przy koszcie kapitału 9,4%[^42]. Udział PVGO, czyli część ceny płacona za przyszły wzrost, wynosi 49,8%[^87]. Przy wzroście w tempie historycznym (66,9%[^65]) cenę uzasadnia już 1,7 lat[^88] wzrostu. Moim zdaniem ta liczba myli, bo tempa z okresu boomu nie da się powtórzyć przy dzisiejszej skali.

Trzy liczby obok siebie:
- wzrost zakładany przez cenę: 13,7%[^4] rocznie przez dziesięć lat;
- konsensus wzrostu EPS: 95,3%[^89] na najbliższy rok, a konsensus przychodów na rok obrotowy do 31.01.2027 to 411,9 mld USD[^90];
- mój scenariusz bazowy: wzrost przychodów 9,0%[^91] rocznie przez dziesięć lat.

Moim zdaniem spółka cykliczna na szczycie wzrostu nie powinna być wyceniana od zysku z jednego roku. Cena zakłada, że FCF za dekadę będzie kilka razy wyższy niż dziś, a dzisiejszy FCF i tak powstaje w warunkach niedoboru i przy marży bliskiej rekordu.

Konsensus: średnia cena docelowa analityków to 325,25 USD[^92], czyli 92,6%[^93] powyżej kursu. Cena docelowa to kontekst, a nie wartość godziwa. Analitycy historycznie zawyżają długoterminowy wzrost.


Wycena właściciela z arkusza „Cena docelowa” (metoda Tomasza Treli, dane ze Scrab; doc-013, ticker w arkuszu: NVDA). Silnik przepisuje wyniki arkusza i niczego nie przelicza.

| Dane wejściowe z arkusza | P/E 1-Year Forward | P/S 1-Year Forward |
|---|---:|---:|
| Prognoza na akcję na 12 miesięcy | EPS 15,81 USD¹ | sprzedaż 28,57 USD¹ |
| Mediana mnożnika (wariant konserwatywny) | 28,92×¹ | 14,86×¹ |
| Maksimum mnożnika (wariant optymistyczny) | 65,20×¹ | 18,00×¹ |

| Cena docelowa na 12 miesięcy | Konserwatywna | Optymistyczna | Potencjał kons. | Potencjał optym. |
|---|---:|---:|---:|---:|
| Z P/E (mediana albo maksimum P/E × prognoza EPS) | 457,23 USD¹ | 1 030,81 USD¹ | +170,7%¹ | +510,3%¹ |
| Z P/S (mediana albo maksimum P/S × prognoza sprzedaży na akcję) | 424,55 USD¹ | 514,26 USD¹ | +151,4%¹ | +204,5%¹ |
| **Cena docelowa** (średnia z P/E i P/S) | 440,89 USD¹ | 772,54 USD¹ | +161,1%¹ | +357,4%¹ |

Potencjał liczy arkusz od kursu z arkusza: 168,89 USD¹. Kurs pobrany przez silnik z 10.11.2026: 168,89 USD.

Założenia arkusza (ustawia je właściciel):

- Wariant konserwatywny: mnożnik wraca do mediany historycznego P/E i P/S 1-Year Forward.
- Wariant optymistyczny: mnożnik wraca do maksimum z historii, czyli do poziomu z „dobrych czasów” spółki.
- Konsensus EPS i konsensus sprzedaży na akcję na kolejne 12 miesięcy się sprawdzą.
- Horyzont wynosi 12 miesięcy: za rok dzisiejsza prognoza stanie się wynikiem raportowanym.
- Cena docelowa to średnia z metody P/E i metody P/S; przy EPS = 0 liczy się tylko metoda P/S.
- Dane pochodzą z jednego źródła (¹): ze Scrab, przez arkusz właściciela, a nie ze sprawozdań spółki.

To wycena przy założeniach właściciela, a nie prognoza kursu ani rekomendacja.


Wg twojego arkusza: cena docelowa wynosi 440,89 USD[^94] w wariancie konserwatywnym i 772,54 USD[^95] w wariancie optymistycznym. Wariant konserwatywny zakłada, że mnożnik C/Z na rok naprzód wróci do mediany z historii (28,9×[^96]), a prognoza EPS na dwanaście miesięcy (15,81 USD[^97]) się sprawdzi. Moim zdaniem ta cena i wycena odwrotna odpowiadają na różne pytania. Arkusz pyta, ile będzie warta spółka, jeśli rynek wróci do historycznego mnożnika. Wycena odwrotna pyta, jaki wzrost na dekadę już jest w cenie. Mediana mnożnika z okresu, w którym NVIDIA była dużo mniejszą spółką, zakłada wzrost, którego przy dzisiejszych przychodach nie potwierdza stopa bazowa. Dane arkusza pochodzą z jednego źródła (Scrab), a nie ze sprawozdań spółki.

## 9. Teza, antytezy, pre-mortem

**Co wycenia rynek.** Cena zakłada wzrost FCF o 13,7%[^4] rocznie przez dekadę przy obecnej rentowności.

**Moja teza (zdanie rozstrzygalne).** Zakładam, że do 31.01.2029 przychody NVIDII za FY2029 będą wyższe niż za FY2027, a marża operacyjna w FY2029 pozostanie powyżej połowy przychodów. Spełnienie tej tezy nie oznacza jeszcze, że spółka pobije oczekiwania zawarte w cenie.

**Prawdopodobieństwo.** Rozkładam tezę na trzy warunki konieczne:
1. nakłady na centra danych AI nie spadną przed FY2029 (moja ocena: około trzech na cztery, bo zarząd ma zamówienia i zabezpieczone dostawy na kilka lat);
2. własne układy klientów nie odbiorą istotnej części sprzedaży do hiperskalerów (około czterech na pięć w tym horyzoncie);
3. marża nie zapadnie się przez koszty pamięci i konkurencję cenową (około czterech na pięć).

Iloczyn daje mniej więcej połowę szans. Prawdopodobieństwo, że spółka pobije oczekiwania zawarte w cenie, czyli wzrost FCF w tempie 13,7%[^4] przez dekadę, oceniam niżej, na około jedną trzecią. Stopa bazowa: w klasie spółek z ponad stu miliardów USD przychodów praktycznie żadna nie rosła przez dziesięć lat w tempie kilkunastu procent rocznie (Base Rate Book). Liczby, które tę wartość podnoszą: zamówienia ograniczone podażą i prognoza na Q3 FY2027 (108,0 mld USD[^27]). Liczby, które ją obniżają: koncentracja klientów i finansowanie klientów przez spółkę.

**Dlaczego rynek może się mylić.** Moim zdaniem rynek patrzy dziś na dochodzenie wobec prezesa i na wskaźniki techniczne (RSI 23,95[^36]). Mnożnik C/Z na rok naprzód wygląda nisko, ale liczy się od zysku z okresu niedoboru. Nie mam przewagi informacyjnej nad rynkiem. Moja odmienność dotyczy tylko jednego czynnika: zakładam, że wzrost po FY2028 będzie dużo niższy, niż sugeruje konsensus, bo cykl nakładów kiedyś się odwróci.

**Katalizatory z datami:**
1. 17.11.2026: wyniki Q3 FY2027 i prognoza na Q4 FY2027 (marża brutto wobec 74,0%[^28]).
2. Wynik dochodzenia rady w sprawie prezesa (bez terminu).
3. Pierwsza połowa 2027 roku: zamknięcie przejęcia Hugging Face.
4. Luty 2027: raport roczny za FY2027 z danymi o klientach i zobowiązaniach.
5. FY2029: wejście w życie pierwszych gwarancji dla kampusu SB Energy.

**Antytezy z progami** (dokładne progi wpiszesz w karcie po swoim „tak”):
- Rynkowe: Fed podnosi stopy, a koszt kapitału rośnie powyżej dzisiejszego 9,4%[^42]. Wpływa na horyzont i wielkość pozycji.
- Specyficzne i sprawdzalne:
  - marża brutto spada poniżej prognozy na Q3 FY2027 (74,0%[^28]) przez dwa kwartały z rzędu;
  - DSO rośnie powyżej poziomu z Q2 FY2027 (60 dni[^76]);
  - zapasy rosną szybciej niż przychody przez dwa kwartały, przy zobowiązaniach na dostawy rzędu 279,0 mld USD[^39];
  - przychody hiperskalerów spadają kwartał do kwartału;
  - udział największego klienta rośnie powyżej poziomu z FY2026 (22,0%[^22]).
- Nieprzewidywalne (wpływają tylko na wielkość pozycji): odejście prezesa po dochodzeniu, nowe ograniczenia eksportowe, zakłócenia na Tajwanie.

**Pre-mortem: za dwa lata pozycja jest na minusie o połowę. Co się stało?** Hiperskalerzy przenieśli część pracy na własne układy. Nowe moce w chmurach AI okazały się nadwyżką. Klienci finansowani przez NVIDIĘ zaczęli mieć kłopoty z płatnościami, więc spółka odpisała należności i inwestycje. Spółka zamówiła pamięć i moce na lata i musiała odpisać zobowiązania zakupowe, a marża brutto spadła tak jak w FY2023. Do tego prezes odszedł, a rynek obniżył mnożnik za ryzyko zarządzania.

**Horyzont rozpoznania tezy:** dwa do trzech lat (do raportu za FY2029). Horyzont trzymania ustalasz osobno.

## 10. Wiadomości i scenariusze

Ostatnie wiadomości i ich wpływ na czynniki wartości (moja ocena):
- Negatywne: po pierwsze, 9.11.2026 kurs spadł po artykule New York Times o tym, że prezes był celem chińskiego wywiadu, i po ogłoszeniu dochodzenia rady. Ta wiadomość podnosi koszt kapitału przez ryzyko zarządzania. Po drugie, spółka wyłączyła Chiny z prognozy, co obniża wzrost. Po trzecie, zobowiązania zakupowe na pamięć wzrosły, a spółka prognozuje niższą marżę brutto na Q3 FY2027.
- Pozytywne: po pierwsze, zarząd prognozuje dalszy wzrost przychodów w Q3 FY2027; po drugie, spółka odkupuje akcje i podniosła dywidendę, co zmniejsza liczbę akcji; po trzecie, premiera Vera Rubin może utrzymać przewagę wydajności.
- Media opisują doniesienia, których nie potwierdzam dokumentem: udział FBI, artykuł The Information o wysyłkach układów do Chin, reakcję Kongresu. Komisja Izby Reprezentantów miała poprosić prezesa o zamknięte spotkanie 18.11.2026; to informacja z jednego wtórnego źródła.


| Scenariusz | Prawdopodobieństwo | Wartość na akcję | Stopa zwrotu przy obecnym kursie |
|---|---:|---:|---:|
| bazowy | 45,0%¹ | 98,98 USD | 6,8%¹ |
| byk | 25,0%¹ | 188,16 USD | 10,1%¹ |
| niedzwiedz | 30,0%¹ | 44,28 USD | 4,3%¹ |
| Wartość oczekiwana na akcję | 104,87 USD¹ |  | |
| Potencjał oczekiwany | -37,9%¹ |  | |
| Prawdopodobieństwo straty | 75,0%¹ |  | |
| Asymetria (zysk ÷ strata) | 0,07¹ |  | |


Scenariusze (prawdopodobieństwa i założenia to moje oceny):
- **Byk (25,0%[^98]):** przychody rosną o 15,0%[^99] rocznie przez dekadę przy marży FCF 40,0%[^100]. Warunek: budowa infrastruktury AI trwa dekadę, a własne układy klientów nie odbierają udziału. To powyżej dziewięćdziesiątego percentyla stopy bazowej.
- **Bazowy (45,0%[^101]):** dwa mocne lata, potem normalizacja nakładów; średnio 9,0%[^91] rocznie przy marży FCF 33,0%[^102].
- **Niedźwiedź (30,0%[^103]):** cykl nakładów pęka jak w półprzewodnikach w latach 2001 i 2022; wzrost 2,0%[^104] rocznie przy marży FCF 25,0%[^105].

Silnik liczy wartość oczekiwaną 104,87 USD[^8], potencjał oczekiwany -37,9%[^106] i asymetrię 0,1×[^107]. Nawet scenariusz byka daje wartość na akcję 188,16 USD[^108], niewiele powyżej kursu. Zakładam, że model zaniża wartość, bo przyjmuje stały wzrost przez dziesięć lat. Nie umie opisać dwóch lat bardzo szybkiego wzrostu, które zapowiada zarząd, a potem normalizacji. Brak zapisałem w `braki-silnika.md`. Wniosek jakościowy pozostaje: cena wymaga wzrostu powyżej stopy bazowej.

Byki mówią: NVIDIA ma zamówienia ograniczone podażą, jedyną platformę z pełnym ekosystemem oprogramowania i mnożnik C/Z na rok naprzód niższy niż w historii. Dochodzenie wobec prezesa to jednorazowy szok. Niedźwiedzie mówią: zyski są na szczycie cyklu, kilku klientów odpowiada za dużą część sprzedaży i projektuje własne układy, a spółka coraz mocniej finansuje swoich klientów. Ryzyko prezesa jest realne, bo spółka nie ujawnia planu sukcesji.

## 11. Karta w stylu Treli


Wynik: **8,6 / 10** z 5 filarów z 5.

| Filar | Waga | Punkty | Miary |
|---|---:|---:|---|
| wzrost | 30% | 10,0 | cagr_przychody_3l: 10,0; cagr_eps_rozwodniony_3l: 10,0; cagr_zysk_netto_3l: 10,0; wzrost_eps_konsensus: 10,0 |
| jakosc | 25% | 8,6 | roic: 10,0; konwersja_fcf: 4,6; dlug_netto_do_ebitda: 9,9; altman_z2: 10,0 |
| wycena | 20% | 7,3 | fcf_yield: 2,8; ev_ebit: 6,4; nadwyzka_wzrostu: 10,0; potencjal_trela_kons: 10,0 |
| analitycy | 15% | 10,0 | rewizje_eps_90d: brak; potencjal_do_ceny_docelowej: 10,0 |
| momentum | 10% | 5,2 | nadwyzka_momentum: 5,2 |


Karta daje wysoki wynik, bo filary wzrostu i jakości mają maksymalne punkty. Moim zdaniem filar wzrostu nagradza tu przeszłość: CAGR z trzech lat obejmuje skok z niskiej bazy FY2023, a Trela wymienia wzrost z bazy bliskiej zera wśród swoich czerwonych flag. Karta jest informacją, a nie bramką.

## 12. Dostęp przez IKE

NVDA.US jest dostępna w XTB i notowana w dolarach. Każde przewalutowanie kosztuje pół procenta. Od dywidend pobierany jest piętnastoprocentowy podatek u źródła przy złożonym formularzu W-8BEN; dywidenda NVIDII jest symboliczna wobec kursu. Wg twoich zasad NVDA.US trafiłaby do koszyka „Akcje zagraniczne” w części Agresywnej IKE z benchmarkiem S&P 500. Instrument nie ma jeszcze wpisu w bloku `instrumenty` w twoich zasadach. Nvidia jest jednym z największych składników SMH, który już masz, i jest w CNDX oraz IWDA. Pozycja w NVDA zwiększy udział półprzewodników w całym IKE, o czym wspomina historia zmian twoich zasad (`v1.4`).

## 13. Projekt karty

- **Teza w trzech zdaniach.** NVIDIA ma najszerszy ekosystem oprogramowania AI i zamówienia ograniczone podażą na najbliższe kwartały. Cena zakłada jednak wzrost FCF o 13,7%[^4] rocznie przez dekadę, czyli powyżej stopy bazowej dla spółek tej wielkości. Zakładam, że teza o utrzymaniu przychodów i marży do FY2029 ma mniej więcej połowę szans, a pobicie oczekiwań w cenie około jedną trzecią.
- **Co jest w cenie:** wzrost FCF 13,7%[^4] rocznie przez dziesięć lat; udział PVGO 49,8%[^87].
- **Pokrycie analityczne:** 62[^10] analityków · 2026-11-11 · Stock Analysis.
- **Antytezy z progami:** marża brutto poniżej 74,0%[^28] przez dwa kwartały; DSO powyżej 60 dni[^76]; zapasy rosną szybciej niż przychody przez dwa kwartały; spadek przychodów hiperskalerów kwartał do kwartału; odejście prezesa.
- **Pre-mortem:** część dziewiąta.
- **Wielkość pozycji:** decyzja właściciela. Zasada: przy pozycji X procent IKE scenariusz niedźwiedzia (44,28 USD[^109] na akcję) zabiera Y procent IKE. Wg twoich zasad kupujesz w transzach.
- **Kiedy sprzedam:** gdy teza jest złamana (dwie antytezy specyficzne naraz), gdy masz lepszą spółkę z kartą albo gdy uznasz, że nie kupiłbyś jej dziś.
- **Data przeglądu:** po wynikach Q3 FY2027 (17.11.2026) i po ogłoszeniu wyniku dochodzenia rady.
- **Co śledzić:** marżę brutto wobec prognozy, DSO, zapasy i zobowiązania zakupowe, udział największych klientów, przychody hiperskalerów, wynik dochodzenia rady.

## 14. Jakość danych


| Status faktów z dokumentów | Liczba |
|---|---:|
| zweryfikowany | 311 |
| jedno źródło | 835 |
| KONFLIKT źródeł | 6 |
| odrzucony | 0 |

**Konflikty źródeł:** eps_rozwodniony.FY2022 (doc-003); kapital_wlasny.2016-01-31 (zobowiazania+kapital=pasywa); liczba_akcji_rozwodniona.FY2022 (doc-003); pasywa_razem.2016-01-31 (zobowiazania+kapital=pasywa); zobowiazania.2016-01-31 (zobowiazania+kapital=pasywa); zysk_operacyjny.FY2023 (doc-003)
**Źródła w archiwum:** Damodaran (NYU Stern), FRED (St. Louis Fed), InvestingPro, SEC, SEC EDGAR (wyszukiwanie), Stock Analysis, U.S. Treasury, Yahoo Finance, arkusz właściciela (metoda Treli), spółka (45 dokumentów).


Czego nie sprawdziłem:
- Silnik uzupełnił rok FY2026 danymi z Stock Analysis, choć raport roczny jest w EDGAR; przyczyny nie sprawdziłem.
- Dwa zgłoszenia `Form 4` z października i listopada 2026 zwróciły błąd pobierania, więc nie przeczytałem najnowszych transakcji insiderów.
- Nie mam danych o udziałach rynkowych, więc nie oceniłem stabilności branży liczbami.
- Spółka nie podaje prognozy marży brutto na Q4 FY2027 w dokumentach z archiwum.
- Silnik nie znalazł spłaty leasingu za ostatnie lata; FCF dla właścicieli może jej nie uwzględniać.

Tropy z materiału InvestingPro (`doc-016`) i wynik sprawdzenia:
1. Kryzys wokół prezesa: potwierdzony co do dochodzenia rady i kancelarii Wachtell (`doc-045`, `doc-043`). Niepotwierdzony co do udziału FBI i treści zarzutów.
2. Ułatwianie wysyłek układów do Chin (The Information): niepotwierdzony. Spółka opisuje tylko ogólne ryzyko obchodzenia ograniczeń (`doc-020`).
3. Trzech niezależnych dyrektorów od lat dziewięćdziesiątych: potwierdzony (`doc-022`).
4. Udział prezesa w akcjach: potwierdzony (`doc-022`). Brak następcy: `DEF 14A` nie opisuje sukcesji.
5. Koncentracja klientów i zależność od TSMC: potwierdzony (`doc-019`, `doc-020`).
6. Podział centrów danych na hiperskalerów i ACIE: potwierdzony (`doc-031`).
7. Chiny poza prognozą: potwierdzony (`doc-031`).
8. Własne układy hiperskalerów: częściowo potwierdzony; spółka wymienia firmy, ale nie nazwy układów (`doc-019`).
9. Inwestycje w laboratoria AI i gwarancje finansowania: potwierdzony (`doc-020`, `doc-023`, `doc-031`).
10. Marża brutto w dół w Q4 FY2027 przez ceny pamięci: niepotwierdzony; dokumenty podają tylko prognozę na Q3 FY2027.
11. Rosnące zapasy i należności: potwierdzony (`doc-020`, `doc-031`).
12. Wzrost długu: potwierdzony (`doc-029`, `doc-031`).
13. Rozbieżność EPS w materiale: liczby w raporcie pochodzą z SEC, a nie z materiału.
14. Termin wyników Q3 FY2027: potwierdzony komunikatem spółki według przeglądu wiadomości; komunikatu nie ma w archiwum.

Tropy z materiału, które zmieniły analizę: wątek prezesa skierował mnie do komunikatów rady, a wątek finansowania laboratoriów AI do 8-K z 17.08.2026 z gwarancjami dla kampusu SB Energy.


## Przypisy: źródła liczb

[^1]: 89,0 mld USD, Q2 (27.04.2026–26.07.2026); źródło: SEC — 8-K 26.08.2026, załącznik 99.2: komentarz CFO do Q2 FY2027 (doc-031, pobrano 2026-11-11); cytat: „Data Center $89,023 $75,246 $41,096”; status: jedno źródło.
[^2]: 96,2 mld USD, Q2 (27.04.2026–26.07.2026); źródło: SEC — XBRL companyfacts (doc-001, pobrano 2026-11-11; xbrl: us-gaap:Revenues); status: zweryfikowany.
[^3]: 168,89 USD, na 10.11.2026; źródło: Yahoo Finance — notowania dzienne NVDA (doc-017, pobrano 2026-11-11; pole: zamknięcie); status: zweryfikowany; kontrola: 0.00% różnicy z drugim źródłem.
[^4]: 13,7%, na 10.11.2026; wyliczenie: wzrost FCF przez 10 lat, przy którym wartość = kapitalizacja; status: jedno źródło.
[^5]: 4,07 bln USD, na 10.11.2026; wyliczenie: kurs × akcje_w_obrocie; status: jedno źródło.
[^6]: 21,1×, na 10.11.2026; wyliczenie: kapitalizacja / zysk_netto.TTM2026-07-26; status: jedno źródło.
[^7]: 2,9%, na 10.11.2026; wyliczenie: fcf_wlascicieli.TTM2026-07-26 / kapitalizacja; status: jedno źródło.
[^8]: 104,87 USD, na 10.11.2026; wyliczenie: wartosc oczekiwana na akcje; status: jedno źródło.
[^9]: 75,0%, na 10.11.2026; wyliczenie: prawdopodobienstwo straty; status: jedno źródło.
[^10]: 62, na 11.11.2026; źródło: Stock Analysis — prognozy analityków (doc-011, pobrano 2026-11-11); status: jedno źródło.
[^11]: 88,3 mld USD, Q2 (27.04.2026–26.07.2026); źródło: SEC — 8-K 26.08.2026, załącznik 99.2: komentarz CFO do Q2 FY2027 (doc-031, pobrano 2026-11-11); cytat: „Compute & Networking $88,299 $74,550 $41,331”; status: jedno źródło.
[^12]: 62,7 mld USD, Q2 (27.04.2026–26.07.2026); źródło: SEC — 10-Q Q2 FY2027 (do 26.07.2026) (doc-020, pobrano 2026-11-11); cytat: „Compute & Networking $ 62,696 $ 28,363 $ 34,333 121 %”; status: jedno źródło.
[^13]: 7,9 mld USD, Q2 (27.04.2026–26.07.2026); źródło: SEC — 8-K 26.08.2026, załącznik 99.2: komentarz CFO do Q2 FY2027 (doc-031, pobrano 2026-11-11); cytat: „Graphics 7,922 7,065 5,412”; status: jedno źródło.
[^14]: 3,9 mld USD, Q2 (27.04.2026–26.07.2026); źródło: SEC — 10-Q Q2 FY2027 (do 26.07.2026) (doc-020, pobrano 2026-11-11); cytat: „Graphics 3,899 2,242 1,657 74 %”; status: jedno źródło.
[^15]: 48,7 mld USD, Q2 (27.04.2026–26.07.2026); źródło: SEC — 8-K 26.08.2026, załącznik 99.2: komentarz CFO do Q2 FY2027 (doc-031, pobrano 2026-11-11); cytat: „Hyperscale 48,710 43,050 24,168”; status: jedno źródło.
[^16]: 40,3 mld USD, Q2 (27.04.2026–26.07.2026); źródło: SEC — 8-K 26.08.2026, załącznik 99.2: komentarz CFO do Q2 FY2027 (doc-031, pobrano 2026-11-11); cytat: „AI Clouds, Industrial, & Enterprise 40,313 32,196 16,928”; status: jedno źródło.
[^17]: 7,2 mld USD, Q2 (27.04.2026–26.07.2026); źródło: SEC — 8-K 26.08.2026, załącznik 99.2: komentarz CFO do Q2 FY2027 (doc-031, pobrano 2026-11-11); cytat: „Edge Computing 7,198 6,369 5,647”; status: jedno źródło.
[^18]: 16,0%, Q2 (27.04.2026–26.07.2026); źródło: SEC — 10-Q Q2 FY2027 (do 26.07.2026) (doc-020, pobrano 2026-11-11); cytat: „For the second quarter of fiscal year 2027, one direct customer represented 16% of total revenue”; status: jedno źródło.
[^19]: 21,0%, Q1 (26.01.2026–26.04.2026); źródło: SEC — 10-Q Q1 FY2027 (do 26.04.2026) (doc-021, pobrano 2026-11-11); cytat: „For the first quarter of fiscal year 2027, three direct customers represented 21%, 17%, and 16% of total revenue”; status: jedno źródło.
[^20]: 17,0%, Q1 (26.01.2026–26.04.2026); źródło: SEC — 10-Q Q1 FY2027 (do 26.04.2026) (doc-021, pobrano 2026-11-11); cytat: „For the first quarter of fiscal year 2027, three direct customers represented 21%, 17%, and 16% of total revenue”; status: jedno źródło.
[^21]: 16,0%, Q1 (26.01.2026–26.04.2026); źródło: SEC — 10-Q Q1 FY2027 (do 26.04.2026) (doc-021, pobrano 2026-11-11); cytat: „For the first quarter of fiscal year 2027, three direct customers represented 21%, 17%, and 16% of total revenue”; status: jedno źródło.
[^22]: 22,0%, rok obrotowy 2026 (do 25.01.2026); źródło: SEC — 10-K FY2026 (do 25.01.2026) (doc-019, pobrano 2026-11-11); cytat: „For fiscal year 2026, sales to one direct customer represented 22% of total revenue and sales to another direct customer represented 14% of total revenue”; status: jedno źródło.
[^23]: 14,0%, rok obrotowy 2026 (do 25.01.2026); źródło: SEC — 10-K FY2026 (do 25.01.2026) (doc-019, pobrano 2026-11-11); cytat: „For fiscal year 2026, sales to one direct customer represented 22% of total revenue and sales to another direct customer represented 14% of total revenue”; status: jedno źródło.
[^24]: 60,1 mld USD, Q2 (27.04.2026–26.07.2026); źródło: SEC — 10-Q Q2 FY2027 (do 26.07.2026) (doc-020, pobrano 2026-11-11); cytat: „United States $ 60,074 $ 32,897 $ 123,843 $ 58,582”; status: jedno źródło.
[^25]: 27,0 mld USD, Q2 (27.04.2026–26.07.2026); źródło: SEC — 10-Q Q2 FY2027 (do 26.07.2026) (doc-020, pobrano 2026-11-11); cytat: „Taiwan 26,985 8,902 38,991 16,550”; status: jedno źródło.
[^26]: 7,9 mld USD, Q2 (27.04.2026–26.07.2026); źródło: SEC — 10-Q Q2 FY2027 (do 26.07.2026) (doc-020, pobrano 2026-11-11); cytat: „China (including Hong Kong) 7,880 3,985 12,430 13,644”; status: jedno źródło.
[^27]: 108,0 mld USD, Q3 (27.07.2026–25.10.2026); źródło: SEC — 8-K 26.08.2026, załącznik 99.2: komentarz CFO do Q2 FY2027 (doc-031, pobrano 2026-11-11); cytat: „Revenue is expected to be $108.0 billion, plus or minus 2%.”; status: jedno źródło.
[^28]: 74,0%, Q3 (27.07.2026–25.10.2026); źródło: SEC — 8-K 26.08.2026, załącznik 99.2: komentarz CFO do Q2 FY2027 (doc-031, pobrano 2026-11-11); cytat: „GAAP and non-GAAP gross margins are expected to be 74.0%, plus or minus 50 basis points.”; status: jedno źródło.
[^29]: 75,0%, Q2 (27.04.2026–26.07.2026); źródło: SEC — 8-K 26.08.2026, załącznik 99.1: wyniki Q2 FY2027 (doc-030, pobrano 2026-11-11); cytat: „For the quarter, GAAP and non-GAAP gross margins were both 75.0%.”; status: jedno źródło.
[^30]: 3,9%, na 23.03.2026; źródło: SEC — DEF 14A 2026 (doc-022, pobrano 2026-11-11); cytat: „Directors and executive officers as a group (14 persons) 957,307,217 (13) 6,300 957,313,517 3.94%”; status: jedno źródło.
[^31]: 3,6%, na 23.03.2026; źródło: SEC — DEF 14A 2026 (doc-022, pobrano 2026-11-11); cytat: „Jen-Hsun Huang 870,604,104 (1) — 870,604,104 3.58%”; status: jedno źródło.
[^32]: 7,4%, na 23.03.2026; źródło: SEC — DEF 14A 2026 (doc-022, pobrano 2026-11-11); cytat: „BlackRock, Inc. 1,805,935,550 (14) — 1,805,935,550 7.43%”; status: jedno źródło.
[^33]: 7,3%, na 23.03.2026; źródło: SEC — DEF 14A 2026 (doc-022, pobrano 2026-11-11); cytat: „Vanguard Capital Management 1,777,408,252 (15) — 1,777,408,252 7.31%”; status: jedno źródło.
[^34]: 27,7 mld USD, na 10.11.2026; źródło: Yahoo Finance — notowania dzienne NVDA (doc-017, pobrano 2026-11-11); status: jedno źródło.
[^35]: -22,3%, na 10.11.2026; źródło: Yahoo Finance — notowania dzienne NVDA (doc-017, pobrano 2026-11-11); status: jedno źródło.
[^36]: 23,95, na 10.11.2026; źródło: Yahoo Finance — notowania dzienne NVDA (doc-017, pobrano 2026-11-11); status: jedno źródło.
[^37]: 11,9 mld USD, na 02.09.2026; źródło: SEC — 8-K 3.09.2026 (pozycja 8.01) (doc-024, pobrano 2026-11-11); cytat: „The transaction includes an approximately $11.9 billion purchase price payable to Hugging Face stockholders”; status: jedno źródło.
[^38]: 15,7%, rok obrotowy 2023 (do 29.01.2023); wyliczenie: zysk_operacyjny / przychody; status: KONFLIKT źródeł.
[^39]: 279,0 mld USD, na 26.07.2026; źródło: SEC — 10-Q Q2 FY2027 (do 26.07.2026) (doc-020, pobrano 2026-11-11); cytat: „Supply and capacity $ 92 $ 87 $ 88 $ 6 $ 5 $ 1 $ 279”; status: jedno źródło.
[^40]: 65,1%, ostatnie 12 miesięcy do 26.07.2026; wyliczenie: zysk_operacyjny × (1 - stawka_podatku) / (kapital_wlasny + dlug - gotowka); status: jedno źródło.
[^41]: 16,9%, rok obrotowy 2023 (do 29.01.2023); wyliczenie: zysk_operacyjny × (1 - stawka_podatku) / (kapital_wlasny + dlug - gotowka); status: KONFLIKT źródeł.
[^42]: 9,4%, na 10.11.2026; wyliczenie: stopa_wolna_od_ryzyka + beta × premia_ryzyka_akcji; status: jedno źródło.
[^43]: 56,9%, rok obrotowy 2023 (do 29.01.2023); wyliczenie: zysk_brutto / przychody; status: zweryfikowany.
[^44]: 74,7%, ostatnie 12 miesięcy do 26.07.2026; wyliczenie: zysk_brutto / przychody; status: zweryfikowany.
[^45]: 36,3 mln USD, rok obrotowy 2026 (do 25.01.2026); źródło: SEC — DEF 14A 2026 (doc-022, pobrano 2026-11-11); cytat: „Jen-Hsun Huang 2026 1,497,627 24,800,511 6,000,000 4,045,691 (4) 36,343,830”; status: jedno źródło.
[^46]: 49,9 mln USD, rok obrotowy 2025 (do 26.01.2025); źródło: SEC — DEF 14A 2026 (doc-022, pobrano 2026-11-11); cytat: „Jen-Hsun Huang 2026 1,497,627 24,800,511 6,000,000 4,045,691 (4) 36,343,830 President and CEO 2025 1,486,199 38,811,306 6,000,000 3,568,746 49,866,251”; status: jedno źródło.
[^47]: 26,0 mld USD, Q2 (27.04.2026–26.07.2026); źródło: SEC — 8-K 26.08.2026, załącznik 99.1: wyniki Q2 FY2027 (doc-030, pobrano 2026-11-11); cytat: „NVIDIA returned approximately $26.0 billion to shareholders in the form of shares repurchased and cash dividends.”; status: jedno źródło.
[^48]: 203,0 mln akcji, półrocze do 26.07.2026; źródło: SEC — 10-Q Q2 FY2027 (do 26.07.2026) (doc-020, pobrano 2026-11-11); cytat: „and 203 million and 193 million shares of our common stock for $39.8 billion and $24.2 billion during the first half of fiscal years 2027 and 2026”; status: jedno źródło.
[^49]: 39,8 mld USD, półrocze do 26.07.2026; źródło: SEC — 10-Q Q2 FY2027 (do 26.07.2026) (doc-020, pobrano 2026-11-11); cytat: „and 203 million and 193 million shares of our common stock for $39.8 billion and $24.2 billion during the first half of fiscal years 2027 and 2026”; status: jedno źródło.
[^50]: 0,01 USD, na 18.05.2026; źródło: SEC — 10-Q Q2 FY2027 (do 26.07.2026) (doc-020, pobrano 2026-11-11); cytat: „we increased our quarterly cash dividend from $0.01 per share to $0.25 per share”; status: jedno źródło.
[^51]: 0,25 USD, na 01.10.2026; źródło: SEC — 8-K 26.08.2026, załącznik 99.1: wyniki Q2 FY2027 (doc-030, pobrano 2026-11-11); cytat: „NVIDIA will pay its next quarterly cash dividend of $0.25 per share on October 1, 2026”; status: jedno źródło.
[^52]: -0,7%, rok obrotowy 2026 (do 25.01.2026); wyliczenie: akcje_koniec_okresu.2026-01-25 / akcje_koniec_okresu.2025-01-26 - 1; status: jedno źródło.
[^53]: -42,4 mld USD, półrocze do 26.07.2026; źródło: SEC — 10-Q Q2 FY2027 (do 26.07.2026) (doc-020, pobrano 2026-11-11); cytat: „Purchases of equity securities (42,404) (1,245)”; status: jedno źródło.
[^54]: 22,3 mld USD, na 25.01.2026; źródło: SEC — 10-Q Q2 FY2027 (do 26.07.2026) (doc-020, pobrano 2026-11-11); cytat: „Non-marketable securities 51,157 22,251”; status: jedno źródło.
[^55]: 51,2 mld USD, na 26.07.2026; źródło: SEC — 10-Q Q2 FY2027 (do 26.07.2026) (doc-020, pobrano 2026-11-11); cytat: „Non-marketable securities 51,157 22,251”; status: jedno źródło.
[^56]: 25,0 mld USD, na 26.07.2026; źródło: SEC — 10-Q Q2 FY2027 (do 26.07.2026) (doc-020, pobrano 2026-11-11); cytat: „Equity investments 18 3 2 2 — — 25”; status: jedno źródło.
[^57]: 105,0 mld USD, na 17.08.2026; źródło: SEC — 8-K 17.08.2026 (pozycje 1.01, 2.03, 7.01) (doc-023, pobrano 2026-11-11); cytat: „NVIDIA’s aggregate payment obligation is cumulatively capped at $105 billion for its initial commitment under the Agreements.”; status: jedno źródło.
[^58]: 108,5 mld USD, na 17.08.2026; źródło: SEC — 8-K 26.08.2026, załącznik 99.2: komentarz CFO do Q2 FY2027 (doc-031, pobrano 2026-11-11); cytat: „Land, power, and shell guarantees for AI clouds $ 3.5 SB Energy Corp. guarantees 105.0 Total $ 108.5”; status: jedno źródło.
[^59]: 25,0 mld USD, Q2 (27.04.2026–26.07.2026); źródło: SEC — 8-K 26.08.2026, załącznik 99.2: komentarz CFO do Q2 FY2027 (doc-031, pobrano 2026-11-11); cytat: „We issued $25.0 billion of senior unsecured notes in the second quarter to be used for general corporate purposes.”; status: jedno źródło.
[^60]: 33,4 mld USD, na 26.07.2026; wyliczenie: dlug_dlugoterminowy.2026-07-26 + dlug_krotkoterminowy.2026-07-26; status: jedno źródło.
[^61]: 56,6 mld USD, na 26.07.2026; źródło: SEC — 8-K 26.08.2026, załącznik 99.2: komentarz CFO do Q2 FY2027 (doc-031, pobrano 2026-11-11); cytat: „Cash, cash equivalents, and marketable debt securities were $56.6 billion”; status: jedno źródło.
[^62]: 65,5%, rok obrotowy 2026 (do 25.01.2026); wyliczenie: przychody.FY2026 / przychody.FY2025 - 1; status: zweryfikowany.
[^63]: 215,9 mld USD, rok obrotowy 2026 (do 25.01.2026); źródło: SEC — XBRL companyfacts (doc-001, pobrano 2026-11-11; xbrl: us-gaap:Revenues); status: zweryfikowany; kontrola: 0.00% różnicy z drugim źródłem.
[^64]: 303,0 mld USD, ostatnie 12 miesięcy do 26.07.2026; wyliczenie: przychody.FY2026 + przychody.FY2027H1 - przychody.FY2026H1; status: zweryfikowany.
[^65]: 66,9%, rok obrotowy 2026 (do 25.01.2026); wyliczenie: (przychody.FY2026 / przychody.FY2021)^(1/5) - 1; status: zweryfikowany.
[^66]: 65,2%, ostatnie 12 miesięcy do 26.07.2026; wyliczenie: zysk_operacyjny / przychody; status: jedno źródło.
[^67]: 63,7%, ostatnie 12 miesięcy do 26.07.2026; wyliczenie: zysk_netto / przychody; status: jedno źródło.
[^68]: 7,8 mld USD, Q2 (27.04.2026–26.07.2026); źródło: SEC — 8-K 26.08.2026, załącznik 99.2: komentarz CFO do Q2 FY2027 (doc-031, pobrano 2026-11-11); cytat: „Net gains from equity securities for the second quarter were $7.8 billion.”; status: jedno źródło.
[^69]: 119,8 mld USD, ostatnie 12 miesięcy do 26.07.2026; wyliczenie: fcf - sbc; status: jedno źródło.
[^70]: 62,1%, ostatnie 12 miesięcy do 26.07.2026; wyliczenie: fcf_wlascicieli / zysk_netto; status: jedno źródło.
[^71]: 75,2%, rok obrotowy 2026 (do 25.01.2026); wyliczenie: fcf_wlascicieli / zysk_netto; status: zweryfikowany.
[^72]: 2,0×, ostatnie 12 miesięcy do 26.07.2026; wyliczenie: capex / amortyzacja; status: jedno źródło.
[^73]: 31,6 mld USD, na 26.07.2026; źródło: SEC — XBRL companyfacts (doc-001, pobrano 2026-11-11; xbrl: us-gaap:InventoryNet); status: jedno źródło.
[^74]: 25,8 mld USD, na 26.04.2026; źródło: SEC — 8-K 26.08.2026, załącznik 99.2: komentarz CFO do Q2 FY2027 (doc-031, pobrano 2026-11-11); cytat: „Inventory was $31.6 billion, up from $25.8 billion sequentially”; status: jedno źródło.
[^75]: 63,1 mld USD, na 26.07.2026; źródło: SEC — XBRL companyfacts (doc-001, pobrano 2026-11-11; xbrl: us-gaap:AccountsReceivableNetCurrent); status: jedno źródło.
[^76]: 60 dni, na 26.07.2026; źródło: SEC — 8-K 26.08.2026, załącznik 99.2: komentarz CFO do Q2 FY2027 (doc-031, pobrano 2026-11-11); cytat: „with 60 days sales outstanding (DSO), up from 45 days sequentially”; status: jedno źródło.
[^77]: 45 dni, na 26.04.2026; źródło: SEC — 8-K 26.08.2026, załącznik 99.2: komentarz CFO do Q2 FY2027 (doc-031, pobrano 2026-11-11); cytat: „with 60 days sales outstanding (DSO), up from 45 days sequentially”; status: jedno źródło.
[^78]: 0,1×, ostatnie 12 miesięcy do 26.07.2026; wyliczenie: dlug_netto / ebitda; status: jedno źródło.
[^79]: 425,8×, ostatnie 12 miesięcy do 26.07.2026; wyliczenie: zysk_operacyjny / koszty_odsetek; status: jedno źródło.
[^80]: -1,2%, rok obrotowy 2026 (do 25.01.2026); wyliczenie: liczba_akcji_rozwodniona.FY2026 / liczba_akcji_rozwodniona.FY2025 - 1; status: zweryfikowany.
[^81]: 2,0 mld USD, Q2 (27.04.2026–26.07.2026); źródło: SEC — XBRL companyfacts (doc-001, pobrano 2026-11-11; xbrl: us-gaap:AllocatedShareBasedCompensationExpense); status: jedno źródło.
[^82]: 400,0 mln USD, półrocze do 26.07.2026; źródło: SEC — 10-Q Q2 FY2027 (do 26.07.2026) (doc-020, pobrano 2026-11-11); cytat: „we incurred a $0.4 billion charge associated with H200 for excess inventory and purchase obligations”; status: jedno źródło.
[^83]: -1,15, rok obrotowy 2026 (do 25.01.2026); wyliczenie: Beneish M-score, model 8-zmiennowy (1999); próg −1,78; status: jedno źródło.
[^84]: 12,85, rok obrotowy 2026 (do 25.01.2026); wyliczenie: Altman Z'' = 6,56·KO/A + 3,26·ZZ/A + 6,72·EBIT/A + 1,05·KW/Z; status: jedno źródło.
[^85]: 4,00, rok obrotowy 2026 (do 25.01.2026); wyliczenie: 9 sygnałów Piotroskiego (ROA>0, CFO>0, ΔROA>0, CFO>ROA, Δdźwignia<0, Δpłynność>0, brak emisji, Δmarża brutto>0, Δrotacja aktywów>0); status: jedno źródło.
[^86]: 0,0%, rok obrotowy 2026 (do 25.01.2026); wyliczenie: 1 / (1 + e^(−O)); próg Ohlsona 0,038; status: jedno źródło.
[^87]: 49,8%, na 10.11.2026; wyliczenie: 1 − (zysk_netto.TTM2026-07-26 / koszt_kapitalu_wlasnego) / kapitalizacja; status: jedno źródło.
[^88]: 1,7 lat, na 10.11.2026; wyliczenie: lata wzrostu FCF w tempie cagr_przychody_5l, które uzasadniają kapitalizację; status: jedno źródło.
[^89]: 95,3%, na 11.11.2026; źródło: Stock Analysis — prognozy analityków (doc-011, pobrano 2026-11-11; pole: epsThis.growth (bieżący rok obrotowy)); status: jedno źródło.
[^90]: 411,9 mld USD, rok do 31.01.2027; źródło: Stock Analysis — prognozy analityków (doc-011, pobrano 2026-11-11; pole: revenue[2027-01-31].avg (rok obrotowy z prognozą)); status: jedno źródło.
[^91]: 9,0%, założenie; założenie: Okolice 70.–80. percentyla stopy bazowej, a nie mediana, bo spółka wchodzi w okres z zamówieniami ograniczonymi podażą: dwa mocne lata, potem normalizacja nakładów na centra danych i presja własnych układów klientów. Marża FCF spada o kilka punktów od obecnej, bo konkurencja i koszty pamięci obniżają marżę brutto.; status: jedno źródło.
[^92]: 325,25 USD, na 11.11.2026; źródło: Stock Analysis — prognozy analityków (doc-011, pobrano 2026-11-11); status: jedno źródło.
[^93]: 92,6%, na 10.11.2026; wyliczenie: cena_docelowa_srednia / kurs − 1; status: jedno źródło.
[^94]: 440,89 USD, na 11.11.2026; źródło: arkusz właściciela (metoda Treli) — cena-docelowa.xlsx: cena docelowa wg arkusza właściciela (doc-013, pobrano 2026-11-11); status: jedno źródło.
[^95]: 772,54 USD, na 11.11.2026; źródło: arkusz właściciela (metoda Treli) — cena-docelowa.xlsx: cena docelowa wg arkusza właściciela (doc-013, pobrano 2026-11-11); status: jedno źródło.
[^96]: 28,9×, na 11.11.2026; źródło: arkusz właściciela (metoda Treli) — cena-docelowa.xlsx: cena docelowa wg arkusza właściciela (doc-013, pobrano 2026-11-11); status: jedno źródło.
[^97]: 15,81 USD, na 11.11.2026; źródło: arkusz właściciela (metoda Treli) — cena-docelowa.xlsx: cena docelowa wg arkusza właściciela (doc-013, pobrano 2026-11-11); status: jedno źródło.
[^98]: 25,0%, założenie; założenie: Powyżej 90. percentyla stopy bazowej: w klasie spółek z ponad 100 mld USD przychodów praktycznie żadna nie rosła przez 10 lat w tempie kilkunastu procent rocznie (Base Rate Book). Warunek: budowa infrastruktury AI trwa przez dekadę, własne układy hiperskalerów nie odbierają udziału, marża FCF zostaje na obecnym poziomie. Wynik roku FY2028 (prognoza zarządu wzrostu ograniczonego podażą) daje silny start, co uzasadnia scenariusz powyżej stopy bazowej.; status: jedno źródło.
[^99]: 15,0%, założenie; założenie: Powyżej 90. percentyla stopy bazowej: w klasie spółek z ponad 100 mld USD przychodów praktycznie żadna nie rosła przez 10 lat w tempie kilkunastu procent rocznie (Base Rate Book). Warunek: budowa infrastruktury AI trwa przez dekadę, własne układy hiperskalerów nie odbierają udziału, marża FCF zostaje na obecnym poziomie. Wynik roku FY2028 (prognoza zarządu wzrostu ograniczonego podażą) daje silny start, co uzasadnia scenariusz powyżej stopy bazowej.; status: jedno źródło.
[^100]: 40,0%, założenie; założenie: Powyżej 90. percentyla stopy bazowej: w klasie spółek z ponad 100 mld USD przychodów praktycznie żadna nie rosła przez 10 lat w tempie kilkunastu procent rocznie (Base Rate Book). Warunek: budowa infrastruktury AI trwa przez dekadę, własne układy hiperskalerów nie odbierają udziału, marża FCF zostaje na obecnym poziomie. Wynik roku FY2028 (prognoza zarządu wzrostu ograniczonego podażą) daje silny start, co uzasadnia scenariusz powyżej stopy bazowej.; status: jedno źródło.
[^101]: 45,0%, założenie; założenie: Okolice 70.–80. percentyla stopy bazowej, a nie mediana, bo spółka wchodzi w okres z zamówieniami ograniczonymi podażą: dwa mocne lata, potem normalizacja nakładów na centra danych i presja własnych układów klientów. Marża FCF spada o kilka punktów od obecnej, bo konkurencja i koszty pamięci obniżają marżę brutto.; status: jedno źródło.
[^102]: 33,0%, założenie; założenie: Okolice 70.–80. percentyla stopy bazowej, a nie mediana, bo spółka wchodzi w okres z zamówieniami ograniczonymi podażą: dwa mocne lata, potem normalizacja nakładów na centra danych i presja własnych układów klientów. Marża FCF spada o kilka punktów od obecnej, bo konkurencja i koszty pamięci obniżają marżę brutto.; status: jedno źródło.
[^103]: 30,0%, założenie; założenie: Mediana i niżej stopy bazowej dla spółek tej wielkości (wzrost niski jednocyfrowy): cykl nakładów na AI pęka jak cykle półprzewodników z lat 2001 i 2022, nadwyżka mocy obniża ceny, a ograniczenia eksportowe i ryzyko odejścia prezesa osłabiają pozycję. Wyższe prawdopodobieństwo niż typowe 20–25%, bo przychody są dziś na szczycie wieloletniego wzrostu i silnie skoncentrowane u kilku klientów.; status: jedno źródło.
[^104]: 2,0%, założenie; założenie: Mediana i niżej stopy bazowej dla spółek tej wielkości (wzrost niski jednocyfrowy): cykl nakładów na AI pęka jak cykle półprzewodników z lat 2001 i 2022, nadwyżka mocy obniża ceny, a ograniczenia eksportowe i ryzyko odejścia prezesa osłabiają pozycję. Wyższe prawdopodobieństwo niż typowe 20–25%, bo przychody są dziś na szczycie wieloletniego wzrostu i silnie skoncentrowane u kilku klientów.; status: jedno źródło.
[^105]: 25,0%, założenie; założenie: Mediana i niżej stopy bazowej dla spółek tej wielkości (wzrost niski jednocyfrowy): cykl nakładów na AI pęka jak cykle półprzewodników z lat 2001 i 2022, nadwyżka mocy obniża ceny, a ograniczenia eksportowe i ryzyko odejścia prezesa osłabiają pozycję. Wyższe prawdopodobieństwo niż typowe 20–25%, bo przychody są dziś na szczycie wieloletniego wzrostu i silnie skoncentrowane u kilku klientów.; status: jedno źródło.
[^106]: -37,9%, na 10.11.2026; wyliczenie: potencjal oczekiwany; status: jedno źródło.
[^107]: 0,1×, na 10.11.2026; wyliczenie: asymetria; status: jedno źródło.
[^108]: 188,16 USD, na 10.11.2026; wyliczenie: (wartość przepływów: przychody × marża FCF, wzrost przez 10 lat, potem rezydualny − dlug_netto) / akcje_w_obrocie; status: jedno źródło.
[^109]: 44,28 USD, na 10.11.2026; wyliczenie: (wartość przepływów: przychody × marża FCF, wzrost przez 10 lat, potem rezydualny − dlug_netto) / akcje_w_obrocie; status: jedno źródło.
