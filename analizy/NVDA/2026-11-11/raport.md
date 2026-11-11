# NVIDIA Corporation (NVDA) — wstępna analiza fundamentalna

Data analizy: 11.11.2026. Rynek: USA. Instrument w XTB: NVDA.US. Decyzja bramek: DALEJ, z flagami do śledzenia (dochodzenie rady wobec prezesa, Chiny, jakość zysków wg Beneisha).

## TL;DR

> NVIDIA sprzedaje platformy obliczeniowe dla centrów danych AI: układy GPU, procesory, sieć i oprogramowanie. Spółka nie ma własnych fabryk. W Q2 FY2027 centra danych dały {{przychody_centra_danych.FY2027Q2}} z {{przychody.FY2027Q2}} przychodów. Kurs {{kurs.2026-11-10}} zakłada, że FCF dla właścicieli będzie rósł o {{implikowany_wzrost_fcf.2026-11-10}} rocznie przez dziesięć lat. Moim zdaniem to oczekiwanie leży powyżej stopy bazowej dla spółek tej wielkości, więc szansę, że spółka pobije oczekiwania zawarte w cenie, oceniam na około jedną trzecią. Największe ryzyka to cykl nakładów na centra danych, koncentracja klientów i ograniczenia eksportowe. Do tego dochodzi świeże dochodzenie rady w sprawie prezesa. Wg twoich zasad: spółka ma duże pokrycie analityczne, a pauza po rajdzie jej nie dotyczy, bo kurs zmienił się w trzy miesiące o {{zmiana_kursu_3m.2026-11-10}}; a przed zakupem potrzebujesz karty w `spolki/NVDA.md`.

- Przewaga konkurencyjna: wąska, trend niepewny (uzasadnienie w części czwartej).
- Wycena: kapitalizacja {{kapitalizacja.2026-11-10}}, C/Z {{c_z.2026-11-10}}, FCF yield {{fcf_yield.2026-11-10}}.
- Wartość oczekiwana ze scenariuszy: {{wartosc_oczekiwana_na_akcje.2026-11-10}} przy kursie {{kurs.2026-11-10}}; prawdopodobieństwo straty {{prawdopodobienstwo_straty.2026-11-10}}. Model scenariuszy przyjmuje stały wzrost przez dziesięć lat, więc nie oddaje prognozy zarządu na najbliższe dwa lata (część dziesiąta).
- Karta w stylu Treli: wynik wysoki; wycenę i momentum karta ocenia słabiej niż wzrost i jakość (część jedenasta).
- Pokrycie analityczne: duże, {{liczba_analitykow.2026-11-11}} analityków.

## 1. Jak działa firma

NVIDIA opisuje się w raporcie rocznym jako spółka infrastruktury AI w skali centrum danych (`doc-019`). Klient kupuje od niej nie sam układ, lecz platformę: procesory graficzne, procesory centralne, układy sieciowe, systemy i oprogramowanie (`doc-031`). Podstawą platformy jest środowisko programistyczne CUDA. Spółka podaje, że z CUDA i innych narzędzi korzysta ponad siedem i pół miliona programistów (`doc-019`).

Spółka nie produkuje układów sama. Płytki krzemowe wytwarzają TSMC i Samsung, pamięć dostarczają SK Hynix, Micron i Samsung, a montaż wykonują firmy kontraktowe (`doc-019`). Produkcja i montaż koncentrują się na Tajwanie (`doc-019`).

Bezpośrednimi klientami są producenci kart, dystrybutorzy, producenci serwerów, dostawcy chmury, twórcy modeli AI i integratorzy (`doc-020`). Użytkownik końcowy często kupuje pośrednio, na przykład wynajmuje moc obliczeniową w chmurze. W raporcie rocznym spółka szacuje, że jedna firma badawcza AI wniosła znaczącą część przychodów przez zakupy usług chmurowych u klientów NVIDII (`doc-019`).

W 2026 roku spółka dodała nowy element modelu. Pomaga wybranym chmurom AI zdobyć grunt, energię i budynki pod centra danych, bo ci klienci rosną szybciej niż ich bilanse (`doc-031`). W zamian sprzedaje im infrastrukturę i przy spełnieniu warunków dostaje udział w ich przychodach (`doc-031`).

Jedno zdanie: dostawcy chmury, twórcy modeli i przedsiębiorstwa płacą NVIDII za kompletną infrastrukturę do trenowania i uruchamiania modeli AI. Moim zdaniem klienci wybierają ją, bo platforma ma najszerszy ekosystem oprogramowania; spółka sama opisuje swój ekosystem jako duży i rosnący (`doc-019`).

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

Spółka raportuje dwa segmenty: Compute & Networking oraz Graphics (`doc-019`). W Q2 FY2027 segment Compute & Networking dał {{przychody_compute_networking.FY2027Q2}} przychodów i {{zysk_operacyjny_compute_networking.FY2027Q2}} zysku operacyjnego. Segment Graphics dał {{przychody_graphics.FY2027Q2}} przychodów i {{zysk_operacyjny_graphics.FY2027Q2}} zysku operacyjnego (`doc-031`, `doc-020`). Zysk pochodzi więc prawie w całości z segmentu, o którym mówią nagłówki.

Od Q1 FY2027 spółka pokazuje też przychody według platform rynkowych (`doc-020`). W Q2 FY2027 centra danych dały {{przychody_centra_danych.FY2027Q2}}, w tym hiperskalerzy {{przychody_hyperscale.FY2027Q2}} i grupa ACIE {{przychody_acie.FY2027Q2}}. Edge Computing dał {{przychody_edge_computing.FY2027Q2}} (`doc-031`). W Q2 FY2027 spółka przeniosła jednego klienta z ACIE do hiperskalerów i przeliczyła okres porównawczy, więc podział na te dwie grupy nie jest ciągły (`doc-031`).

Przychody są skoncentrowane. W Q2 FY2027 jeden klient bezpośredni dał {{klient_bezposredni_1_udzial.FY2027Q2}} przychodów (`doc-020`). W Q1 FY2027 trzech klientów bezpośrednich dało {{klient_bezposredni_1_udzial.FY2027Q1}}, {{klient_bezposredni_2_udzial.FY2027Q1}} i {{klient_bezposredni_3_udzial.FY2027Q1}} przychodów (`doc-021`). W FY2026 dwóch klientów dało {{klient_bezposredni_1_udzial.FY2026}} i {{klient_bezposredni_2_udzial.FY2026}} przychodów (`doc-019`).

Według siedziby klienta bezpośredniego USA dały w Q2 FY2027 {{przychody_usa.FY2027Q2}}, Tajwan {{przychody_tajwan.FY2027Q2}}, a Chiny z Hongkongiem {{przychody_chiny.FY2027Q2}} (`doc-020`). Spółka zastrzega, że siedziba klienta nie musi być miejscem wysyłki ani użytkowania (`doc-020`).

Zarząd prognozuje na Q3 FY2027 przychody {{prognoza_zarzadu_przychody.FY2027Q3}} i marżę brutto {{prognoza_zarzadu_marza_brutto.FY2027Q3}}. W Q2 FY2027 marża brutto wyniosła {{marza_brutto_komunikat.FY2027Q2}} (`doc-030`, `doc-031`). Prognoza nie zakłada żadnych przychodów z centrów danych w Chinach (`doc-031`).

## 3. Najważniejsze fakty (akcjonariat, zarząd, płynność, kalendarz)

- Akcjonariat: zarząd i rada mają razem {{zarzad_udzial_w_akcjach.2026-03-23}} akcji, prezes Jensen Huang {{huang_udzial_w_akcjach.2026-03-23}}, BlackRock {{blackrock_udzial_w_akcjach.2026-03-23}}, a Vanguard {{vanguard_udzial_w_akcjach.2026-03-23}} (`doc-022`). Moim zdaniem żaden akcjonariusz nie kontroluje spółki.
- Prezes: Jensen Huang założył spółkę w 1993 roku i od początku kieruje nią jako prezes (`doc-022`). `DEF 14A` nie opisuje planu sukcesji. W raporcie rocznym spółka pisze, że w dużym stopniu zależy od wieloletniego zespołu kierowniczego (`doc-019`).
- Dochodzenie rady: 8.11.2026 rada ogłosiła niezależne dochodzenie po doniesieniach, że prezes był celem działań obcego wywiadu (`doc-045`). Rada pisze, że nie ma powodu sądzić, by naruszono bezpieczeństwo narodowe albo tajemnice spółki, i deklaruje zaufanie do prezesa (`doc-045`). Tego samego dnia prezes w liście do pracowników przyznał, że był niewierny żonie (`doc-044`). 10.11.2026 niezależni członkowie rady zatrudnili do dochodzenia kancelarię Wachtell, Lipton, Rosen & Katz (`doc-043`). Na liście zgłoszeń EDGAR (`doc-002`, pobranej 11.11.2026) nie ma raportu 8-K po 3.09.2026.
- Płynność: średnie obroty dzienne z sześćdziesięciu sesji wynoszą {{obroty_dzienne_60s.2026-11-10}}.
- Kurs: {{kurs.2026-11-10}}, zmiana w trzy miesiące {{zmiana_kursu_3m.2026-11-10}}, RSI czternastodniowy {{rsi_14.2026-11-10}}.
- Kalendarz: wyniki za Q3 FY2027 mają się ukazać 17.11.2026. Tę datę podaje materiał InvestingPro (`doc-016`) i przegląd wiadomości (komunikat spółki z 28.10.2026); komunikatu spółki nie ma w archiwum. Przejęcie Hugging Face za {{hugging_face_cena.2026-09-02}} ma się zamknąć w pierwszej połowie 2027 roku, po zgodach regulatorów (`doc-024`).

## 4. Branża, konkurencja i przewaga konkurencyjna

Spółka wymienia jako konkurentów w akceleratorach AMD, Huawei i Intel (`doc-019`). Własne układy AI projektują duzi dostawcy chmury: Alibaba, Alphabet, Amazon, Baidu, Huawei i Microsoft (`doc-019`). W sieciach spółka konkuruje między innymi z Aristą, Broadcomem, Cisco i Marvellem (`doc-019`). Spółka oczekuje silniejszej konkurencji, w tym tańszych produktów nowych graczy (`doc-019`).

Chiny są dla spółki praktycznie zamknięte. W 10-Q za Q2 FY2027 spółka pisze, że ograniczenia eksportowe wykluczyły ją z chińskiego rynku centrów danych, a to pomogło konkurentom zbudować większe ekosystemy (`doc-020`). Rząd Chin zachęca klientów do zakupów u chińskich producentów (`doc-020`). Organy ochrony konkurencji w UE, USA, Wielkiej Brytanii, Chinach i Korei Południowej wysyłają spółce zapytania o sprzedaż i przydział dostaw (`doc-020`).

Branża jest w fazie gwałtownej budowy mocy. Nie mam w archiwum danych o udziałach rynkowych, więc nie liczę stabilności udziałów ani HHI. Branża półprzewodników jest cykliczna: w panelu widać, że w FY2023 przychody stały w miejscu, a marża operacyjna spadła do {{marza_operacyjna.FY2023}}.

Kandydaci na źródło przewagi:
- **Efekt sieciowy i koszty zmiany dostawcy (CUDA).** Korzyść: klient płaci wyższą cenę, bo oprogramowanie AI działa na NVIDII od razu. Bariera: miliony programistów i setki bibliotek, których konkurent nie skopiuje szybko (`doc-019`).
- **Pełna platforma.** Korzyść: spółka sprzedaje cały system, a nie pojedynczy układ. Bariera: integracja procesorów, sieci i oprogramowania w skali szafy serwerowej (`doc-019`).
- **Skala i zabezpieczone dostawy.** Spółka zabezpieczyła komponenty na kilka lat; zobowiązania na dostawy i moce wzrosły do {{zobowiazania_zaopatrzenie_pojemnosc.2026-07-26}} (`doc-020`, `doc-031`). To przewaga w okresie niedoboru, ale też ryzyko, gdy popyt spadnie.

Liczby: ROIC wynosi {{roic.TTM2026-07-26}}, a w FY2023, roku spadku, wyniósł {{roic.FY2023}}. Koszt kapitału własnego to {{koszt_kapitalu_wlasnego.2026-11-10}}. Marża brutto spadła w FY2023 do {{marza_brutto.FY2023}}, a potem wróciła do {{marza_brutto.TTM2026-07-26}}.

Moim zdaniem przewaga jest wąska, a trend niepewny. Zwroty powyżej kosztu kapitału przez dziesięć lat są bardziej prawdopodobne niż nie, bo ekosystem CUDA działa jak efekt sieciowy. Nie uznaję jej za szeroką z trzech powodów. Po pierwsze, najwięksi klienci budują własne układy i mają skalę, by przenieść część pracy. Po drugie, rząd USA już odebrał spółce chiński rynek centrów danych, a dalsze ograniczenia są możliwe. Po trzecie, dzisiejsze zwroty powstały w okresie niedoboru, a nie w pełnym cyklu. Stopa bazowa z badania metody w repozytorium (Mauboussin): nawet spółka z najwyższego kwintyla ROIC ma mniej więcej połowę szans, że zostanie w nim po dekadzie.

Test AI (moja ocena):
1. Przychody nie zależą od godzin pracy ludzi; AI to źródło popytu.
2. Koszt zmiany dostawcy wynika z integracji oprogramowania i infrastruktury, więc jest silniejszy niż przyzwyczajenie.
3. Spółka ma własne biblioteki i modele, ale nie dane klientów.
4. AI może obniżyć koszt przenoszenia oprogramowania na inne układy, a to osłabia barierę CUDA. Spółka sama pisze, że modele otwarte uruchamiane na platformach konkurentów mogą zmniejszyć popyt na jej produkty (`doc-020`).
5. Oszczędności z AI w samej spółce nie decydują o wyniku.

## 5. Zarząd i alokacja kapitału

Jensen Huang kieruje spółką od założenia (`doc-022`). Jego łączne wynagrodzenie w FY2026 wyniosło {{huang_wynagrodzenie_razem.FY2026}}, a w FY2025 {{huang_wynagrodzenie_razem.FY2025}} (`doc-022`). Wieloletnie akcje za wyniki zależą od zwrotu dla akcjonariuszy względem S&P 500 (`doc-022`). Rada ma niezależnego dyrektora wiodącego, a wszyscy jej członkowie poza prezesem są niezależni (`doc-022`). Trzech niezależnych dyrektorów zasiada w radzie od lat dziewięćdziesiątych: Tench Coxe i Harvey Jones od 1993 roku, Brooke Seawell od 1997 roku (`doc-022`). Moim zdaniem tak długi staż osłabia niezależność rady akurat w dochodzeniu wobec prezesa, z którym ci dyrektorzy pracują od dekad.

W 2026 roku spółka wymieniła głównego księgowego: od 4.05.2026 jest nim Scott Gawel, wcześniej w Intelu (`doc-027`). Szef sprzedaży światowej Ajay Puri przechodzi na emeryturę, a jego następca Nicholas Parker przychodzi z Microsoftu (`doc-025`).

Zwrot kapitału: w Q2 FY2027 spółka zwróciła akcjonariuszom około {{zwrot_dla_akcjonariuszy_komunikat.FY2027Q2}} przez odkup i dywidendy (`doc-030`). W pierwszym półroczu FY2027 odkupiła {{odkup_akcji_liczba.FY2027H1}} akcji za {{odkup_akcji_kwota.FY2027H1}} (`doc-020`). Rada podniosła dywidendę kwartalną z {{dywidenda_kwartalna_na_akcje.2026-05-18}} do {{dywidenda_kwartalna_na_akcje.2026-10-01}} na akcję (`doc-020`). Liczba akcji na koniec roku spadła w FY2026 o {{zmiana_liczby_akcji_koniec.FY2026}}.

Nowe zastosowania kapitału zmieniają profil ryzyka:
- Spółka kupiła w półroczu papiery kapitałowe za {{zakup_papierow_kapitalowych.FY2027H1}}; papiery nienotowane wzrosły od początku roku z {{papiery_nienotowane.2026-01-25}} do {{papiery_nienotowane.2026-07-26}} (`doc-020`). Spółka zobowiązała się do dalszych inwestycji w twórców modeli AI i firmy finansujące infrastrukturę za {{zobowiazania_inwestycje_kapitalowe.2026-07-26}} (`doc-020`).
- W sierpniu 2026 spółka udzieliła gwarancji wartości rezydualnej dzierżaw kampusu SB Energy, którego najemcą jest spółka powiązana z OpenAI, z limitem {{gwarancje_sb_energy_limit.2026-08-17}} (`doc-023`). Łączna maksymalna ekspozycja z gwarancji wynosi {{gwarancje_razem_maks_ekspozycja.2026-08-17}} (`doc-031`). OpenAI zobowiązał się zwrócić NVIDII wypłaty, a gwarancje zaczną działać etapami od FY2029 (`doc-023`, `doc-031`).
- W Q2 FY2027 spółka wyemitowała obligacje za {{emisja_obligacji.FY2027Q2}} (`doc-031`). Dług wynosi {{dlug.2026-07-26}}, a gotówka z papierami dłużnymi {{gotowka_i_papiery_dluzne.2026-07-26}} (`doc-020`, `doc-031`).

Moim zdaniem spółka finansuje dziś własnych klientów: inwestuje w nich, gwarantuje ich dzierżawy i wydłuża im terminy płatności. To wspiera sprzedaż, ale wiąże wynik NVIDII z kondycją kilku klientów, w tym chmur AI, które według spółki nie mają dziś finansowania na poziomie inwestycyjnym (`doc-020`). Spółka sama pisze, że te zobowiązania zależą od wyników klientów i partnerów (`doc-020`).

## 6. Sprawozdania finansowe

{{tabela:panel}}

{{wykres:przychody}}

{{wykres:marze}}

{{wykres:fcf_zysk}}

{{wykres:roic}}

Wzrost: przychody wzrosły w FY2026 o {{wzrost_przychody.FY2026}} do {{przychody.FY2026}}. Za cztery kwartały do 26.07.2026 przychody wyniosły {{przychody.TTM2026-07-26}}. CAGR przychodów z pięciu lat to {{cagr_przychody_5l.FY2026}}.

Marże: marża brutto wynosi {{marza_brutto.TTM2026-07-26}}, marża operacyjna {{marza_operacyjna.TTM2026-07-26}}, a marża netto {{marza_netto.TTM2026-07-26}}. Zysk netto Q2 FY2027 zawiera zyski z papierów kapitałowych w wysokości {{zyski_z_papierow_kapitalowych_komunikat.FY2027Q2}} (`doc-031`), więc marża netto TTM jest zawyżona przez wynik spoza działalności podstawowej.

Jakość zysków: FCF dla właścicieli za cztery kwartały wyniósł {{fcf_wlascicieli.TTM2026-07-26}}, czyli {{konwersja_fcf.TTM2026-07-26}} zysku netto. W FY2026 konwersja wyniosła {{konwersja_fcf.FY2026}}. Capex rośnie szybciej niż amortyzacja: relacja wynosi {{capex_do_amortyzacji.TTM2026-07-26}}.

Kapitał obrotowy: zapasy wzrosły do {{zapasy.2026-07-26}} z {{zapasy_komentarz_cfo.2026-04-26}} kwartał wcześniej; spółka tłumaczy to przygotowaniem do premiery Vera Rubin (`doc-031`). Należności handlowe wynoszą {{naleznosci_handlowe.2026-07-26}}, a DSO wzrosło do {{dso.2026-07-26}} z {{dso.2026-04-26}} (`doc-031`). Spółka podaje jako przyczynę dłuższe terminy płatności, do roku, w dużych umowach z klientami o ratingu inwestycyjnym (`doc-020`).

Zadłużenie: dług netto do EBITDA wynosi {{dlug_netto_do_ebitda.TTM2026-07-26}}, a pokrycie odsetek {{pokrycie_odsetek.TTM2026-07-26}}. Moim zdaniem bilans spółki nie jest napięty mimo emisji obligacji.

Rozwodnienie: liczba akcji (średnia ważona) spadła w FY2026 o {{zmiana_liczby_akcji.FY2026}}. Wynagrodzenia akcyjne w Q2 FY2027 wyniosły {{sbc.FY2027Q2}}.

## 7. Jakość zysków i czerwone flagi

{{tabela:bramki}}

Opis flag:
- **Dochodzenie rady wobec prezesa (flaga).** Rada bada, czy prezes był celem obcego wywiadu, i deklaruje zaufanie do niego (`doc-045`). Prezes przyznał w liście do pracowników, że był niewierny żonie (`doc-044`). Moim zdaniem brak dowodu oszustwa oznacza flagę, a nie stop. Z materiału InvestingPro nie potwierdziłem dokumentem spółki zarzutów o ułatwianie wysyłek układów do Chin ani udziału FBI.
- **Chiny (flaga).** Spółka pisze, że jest praktycznie wykluczona z chińskiego rynku centrów danych (`doc-020`). Poniosła odpis na zapasy i zobowiązania związane z układami `H200` w wysokości {{h200_oplata_zapasy_zobowiazania.FY2027H1}} (`doc-020`). Moim zdaniem rdzeń biznesu działa bez Chin, więc to flaga, a nie stop.
- **Beneish M-score (flaga diagnostyczna).** M-score za FY2026 wynosi {{beneish_m.FY2026}}, powyżej progu. Wskaźnik reaguje na szybki wzrost należności. Spółka tłumaczy ten wzrost dłuższymi terminami płatności (`doc-020`). Moim zdaniem to nie dowód manipulacji, ale realne ryzyko kredytowe, które warto śledzić.
- **„Material weakness”.** Zwrot występuje w raporcie rocznym tylko w opisie ryzyk. Zarząd i biegły stwierdzają skuteczną kontrolę wewnętrzną, a opinia biegłego jest bez zastrzeżeń (`doc-019`).
- **Insiderzy.** Sprzedaże radcy prawnego, dyrektor finansowej i jednego z dyrektorów z ostatnich miesięcy są oznaczone jako transakcje w planach `10b5-1` (`doc-035`, `doc-037`, `doc-041`). Prezes we wrześniu 2026 przekazał akcje na podatek i w darowiznach (`doc-042`). Jeden dyrektor sprzedał akcje we wrześniu bez wzmianki o planie (`doc-033`).

Wskaźniki statystyczne: Altman Z'' wynosi {{altman_z2.FY2026}} (strefa bezpieczna), Piotroski F-score {{piotroski_f.FY2026}}, a prawdopodobieństwo upadłości wg Ohlsona {{ohlson_p.FY2026}}. Żaden z nich nie zatrzymuje analizy.

## 8. Co jest w cenie

{{tabela:wycena}}

Kurs {{kurs.2026-11-10}} zakłada, że FCF dla właścicieli będzie rósł o {{implikowany_wzrost_fcf.2026-11-10}} rocznie przez dziesięć lat przy koszcie kapitału {{koszt_kapitalu_wlasnego.2026-11-10}}. Udział PVGO, czyli część ceny płacona za przyszły wzrost, wynosi {{udzial_pvgo.2026-11-10}}. Przy wzroście w tempie historycznym ({{cagr_przychody_5l.FY2026}}) cenę uzasadnia już {{implikowany_cap.2026-11-10}} wzrostu. Moim zdaniem ta liczba myli, bo tempa z okresu boomu nie da się powtórzyć przy dzisiejszej skali.

Trzy liczby obok siebie:
- wzrost zakładany przez cenę: {{implikowany_wzrost_fcf.2026-11-10}} rocznie przez dziesięć lat;
- konsensus wzrostu EPS: {{wzrost_eps_konsensus.2026-11-11}} na najbliższy rok, a konsensus przychodów na rok obrotowy do 31.01.2027 to {{przychody_konsensus.2027-01-31}};
- mój scenariusz bazowy: wzrost przychodów {{scenariusz_wzrost_przychodow.bazowy}} rocznie przez dziesięć lat.

Moim zdaniem spółka cykliczna na szczycie wzrostu nie powinna być wyceniana od zysku z jednego roku. Cena zakłada, że FCF za dekadę będzie kilka razy wyższy niż dziś, a dzisiejszy FCF i tak powstaje w warunkach niedoboru i przy marży operacyjnej bliskiej rekordu.

Konsensus: średnia cena docelowa analityków to {{cena_docelowa_srednia.2026-11-11}}, czyli {{potencjal_do_ceny_docelowej.2026-11-10}} powyżej kursu. Cena docelowa to kontekst, a nie wartość godziwa. Według badania metody w repozytorium analitycy historycznie zawyżają długoterminowy wzrost.

{{tabela:cena_docelowa_trela}}

Wg twojego arkusza: cena docelowa wynosi {{cena_docelowa_trela_kons.2026-11-11}} w wariancie konserwatywnym i {{cena_docelowa_trela_optym.2026-11-11}} w wariancie optymistycznym. Wariant konserwatywny zakłada, że mnożnik C/Z na rok naprzód wróci do mediany z historii ({{pe_forward_mediana_arkusz.2026-11-11}}), a prognoza EPS na dwanaście miesięcy ({{eps_prognoza_arkusz.2026-11-11}}) się sprawdzi. Moim zdaniem ta cena i wycena odwrotna odpowiadają na różne pytania. Arkusz pyta, ile będzie warta spółka, jeśli rynek wróci do historycznego mnożnika. Wycena odwrotna pyta, jaki wzrost na dekadę już jest w cenie. Mediana mnożnika z okresu, w którym NVIDIA była dużo mniejszą spółką, zakłada wzrost, którego przy dzisiejszych przychodach nie potwierdza stopa bazowa. Dane arkusza pochodzą z jednego źródła (Scrab), a nie ze sprawozdań spółki.

## 9. Teza, antytezy, pre-mortem

**Co wycenia rynek.** Cena zakłada wzrost FCF o {{implikowany_wzrost_fcf.2026-11-10}} rocznie przez dekadę przy obecnej rentowności.

**Moja teza (zdanie rozstrzygalne).** Zakładam, że do 31.01.2029 przychody NVIDII za FY2029 będą wyższe niż za FY2027, a marża operacyjna w FY2029 pozostanie powyżej połowy przychodów. Spełnienie tej tezy nie oznacza jeszcze, że spółka pobije oczekiwania zawarte w cenie.

**Prawdopodobieństwo.** Rozkładam tezę na trzy warunki konieczne:
1. nakłady na centra danych AI nie spadną przed FY2029 (moja ocena: około trzech na cztery, bo zarząd ma zamówienia i zabezpieczone dostawy na kilka lat);
2. własne układy klientów nie odbiorą istotnej części sprzedaży do hiperskalerów (około czterech na pięć w tym horyzoncie);
3. marża brutto nie zapadnie się przez koszty pamięci i konkurencję cenową (około czterech na pięć).

Iloczyn daje mniej więcej połowę szans. Prawdopodobieństwo, że spółka pobije oczekiwania zawarte w cenie, czyli wzrost FCF w tempie {{implikowany_wzrost_fcf.2026-11-10}} przez dekadę, oceniam niżej, na około jedną trzecią. Stopa bazowa z badania metody w repozytorium (Base Rate Book, Mauboussin): żadna spółka z co najmniej stu miliardami USD przychodów nie rosła przez dziesięć lat w tempie kilkunastu procent rocznie. Liczby, które tę wartość podnoszą: zamówienia ograniczone podażą i prognoza na Q3 FY2027 ({{prognoza_zarzadu_przychody.FY2027Q3}}). Liczby, które ją obniżają: koncentracja klientów i finansowanie klientów przez spółkę.

**Dlaczego rynek może się mylić.** Moim zdaniem rynek patrzy dziś na dochodzenie wobec prezesa i na wskaźniki techniczne (RSI {{rsi_14.2026-11-10}}). Mnożnik C/Z na rok naprzód wygląda nisko, ale liczy się od zysku z okresu niedoboru. Nie mam przewagi informacyjnej nad rynkiem. Moja odmienność dotyczy tylko jednego czynnika: zakładam, że wzrost przychodów r/r po FY2028 będzie dużo niższy, niż sugeruje konsensus, bo cykl nakładów kiedyś się odwróci.

**Katalizatory z datami:**
1. 17.11.2026 (data z materiału InvestingPro): wyniki Q3 FY2027 i prognoza na Q4 FY2027 (marża brutto wobec {{prognoza_zarzadu_marza_brutto.FY2027Q3}}).
2. Wynik dochodzenia rady w sprawie prezesa (bez terminu).
3. Pierwsza połowa 2027 roku: zamknięcie przejęcia Hugging Face.
4. Luty 2027: raport roczny za FY2027 z danymi o klientach i zobowiązaniach.
5. FY2029: wejście w życie pierwszych gwarancji dla kampusu SB Energy.

**Antytezy z progami** (dokładne progi wpiszesz w karcie po swoim „tak”):
- Rynkowe: Fed podnosi stopy, a koszt kapitału rośnie powyżej dzisiejszego {{koszt_kapitalu_wlasnego.2026-11-10}}. Wpływa na horyzont i wielkość pozycji.
- Specyficzne i sprawdzalne:
  - marża brutto spada poniżej prognozy na Q3 FY2027 ({{prognoza_zarzadu_marza_brutto.FY2027Q3}}) przez dwa kwartały z rzędu;
  - DSO rośnie powyżej poziomu z Q2 FY2027 ({{dso.2026-07-26}});
  - zapasy rosną szybciej niż przychody przez dwa kwartały, przy zobowiązaniach na dostawy rzędu {{zobowiazania_zaopatrzenie_pojemnosc.2026-07-26}};
  - przychody hiperskalerów spadają kwartał do kwartału;
  - udział największego klienta rośnie powyżej poziomu z FY2026 ({{klient_bezposredni_1_udzial.FY2026}}).
- Nieprzewidywalne (wpływają tylko na wielkość pozycji): odejście prezesa po dochodzeniu, nowe ograniczenia eksportowe, zakłócenia na Tajwanie.

**Pre-mortem: za dwa lata pozycja jest na minusie o połowę. Co się stało?** Hiperskalerzy przenieśli część pracy na własne układy. Nowe moce w chmurach AI okazały się nadwyżką. Klienci finansowani przez NVIDIĘ zaczęli mieć kłopoty z płatnościami, więc spółka odpisała należności i inwestycje. Spółka zamówiła pamięć i moce na lata i musiała odpisać zobowiązania zakupowe, a marża brutto spadła tak jak w FY2023. Do tego prezes odszedł, a rynek obniżył mnożnik za ryzyko zarządzania.

**Horyzont rozpoznania tezy:** dwa do trzech lat (do raportu za FY2029). Horyzont trzymania ustalasz osobno.

## 10. Wiadomości i scenariusze

Ostatnie wiadomości i ich wpływ na czynniki wartości (moja ocena):
- Negatywne: po pierwsze, rada ogłosiła 8.11.2026 dochodzenie w sprawie doniesień, że prezes był celem obcego wywiadu (`doc-045`); według materiału InvestingPro (`doc-016`) doniesienia opublikował New York Times, a kurs spadł w kolejnych dniach. Moim zdaniem ta wiadomość podnosi koszt kapitału przez ryzyko zarządzania. Po drugie, spółka wyłączyła Chiny z prognozy, co obniża wzrost. Po trzecie, zobowiązania zakupowe na pamięć wzrosły, a spółka prognozuje niższą marżę brutto na Q3 FY2027.
- Pozytywne: po pierwsze, zarząd prognozuje dalszy wzrost przychodów w Q3 FY2027; po drugie, spółka odkupuje akcje i podniosła dywidendę, co zmniejsza liczbę akcji; po trzecie, premiera Vera Rubin może utrzymać przewagę wydajności.
- Media opisują doniesienia, których nie potwierdzam dokumentem: udział FBI, artykuł The Information o wysyłkach układów do Chin, reakcję Kongresu. Przegląd wiadomości znalazł też w jednym wtórnym serwisie informację o prośbie komisji Izby Reprezentantów o spotkanie z prezesem; nie potwierdziłem jej.

{{tabela:scenariusze}}

Scenariusze (prawdopodobieństwa i założenia to moje oceny):
- **Byk ({{scenariusz_prawdopodobienstwo.byk}}):** przychody rosną o {{scenariusz_wzrost_przychodow.byk}} rocznie przez dekadę przy marży FCF {{scenariusz_marza_fcf.byk}}. Warunek: budowa infrastruktury AI trwa dekadę, a własne układy klientów nie odbierają udziału. Moim zdaniem to powyżej dziewięćdziesiątego percentyla stopy bazowej.
- **Bazowy ({{scenariusz_prawdopodobienstwo.bazowy}}):** dwa mocne lata, potem normalizacja nakładów; średnio {{scenariusz_wzrost_przychodow.bazowy}} rocznie przy marży FCF {{scenariusz_marza_fcf.bazowy}}.
- **Niedźwiedź ({{scenariusz_prawdopodobienstwo.niedzwiedz}}):** cykl nakładów pęka, jak w FY2023, gdy przychody spółki stanęły w miejscu; wzrost {{scenariusz_wzrost_przychodow.niedzwiedz}} rocznie przy marży FCF {{scenariusz_marza_fcf.niedzwiedz}}.

Silnik liczy wartość oczekiwaną {{wartosc_oczekiwana_na_akcje.2026-11-10}}, potencjał oczekiwany {{potencjal_oczekiwany.2026-11-10}} i asymetrię {{asymetria.2026-11-10}}. Nawet scenariusz byka daje wartość na akcję {{wartosc_na_akcje.byk}}, niewiele powyżej kursu. Zakładam, że model zaniża wartość, bo przyjmuje stały wzrost przez dziesięć lat. Nie umie opisać dwóch lat bardzo szybkiego wzrostu, które zapowiada zarząd, a potem normalizacji. Brak zapisałem w `braki-silnika.md`. Wniosek jakościowy pozostaje: cena wymaga wzrostu powyżej stopy bazowej.

Argumenty za (moja ocena): NVIDIA ma zamówienia ograniczone podażą, jedyną platformę z pełnym ekosystemem oprogramowania i mnożnik C/Z na rok naprzód niższy niż w historii. Dochodzenie wobec prezesa to jednorazowy szok. Argumenty przeciw (moja ocena): zyski są na szczycie cyklu, kilku klientów odpowiada za dużą część sprzedaży i projektuje własne układy, a spółka coraz mocniej finansuje swoich klientów. Ryzyko prezesa jest realne, bo spółka nie ujawnia planu sukcesji.

## 11. Karta w stylu Treli

{{tabela:karta}}

Karta daje wysoki wynik, bo filary wzrostu i jakości mają maksymalne punkty. Moim zdaniem filar wzrostu nagradza tu przeszłość: CAGR z trzech lat obejmuje skok z niskiej bazy FY2023, a według pliku referencyjnego skilla o metodzie Treli wzrost z bazy bliskiej zera należy do jego czerwonych flag. Karta jest informacją, a nie bramką.

## 12. Dostęp przez IKE

NVDA.US jest dostępna w XTB i notowana w dolarach. Każde przewalutowanie kosztuje pół procenta. Zakładam, że USA pobiorą od dywidend piętnastoprocentowy podatek u źródła przy złożonym formularzu W-8BEN (bez dokumentu w archiwum); dywidenda NVIDII jest symboliczna wobec kursu. Wg twoich zasad NVDA.US trafiłaby do koszyka „Akcje zagraniczne” w części Agresywnej IKE z benchmarkiem S&P 500. Instrument nie ma jeszcze wpisu w bloku `instrumenty` w twoich zasadach. Według twojej karty SMH Nvidia jest dużym składnikiem tego funduszu, a według twoich zasad półprzewodniki są też w CNDX, IWDA i EIMI. Pozycja w NVDA zwiększy udział półprzewodników w całym IKE, o czym wspomina historia zmian twoich zasad (`v1.4`).

## 13. Projekt karty

- **Teza w trzech zdaniach.** NVIDIA ma najszerszy ekosystem oprogramowania AI i zamówienia ograniczone podażą na najbliższe kwartały. Cena zakłada jednak wzrost FCF o {{implikowany_wzrost_fcf.2026-11-10}} rocznie przez dekadę, czyli powyżej stopy bazowej dla spółek tej wielkości. Zakładam, że teza o utrzymaniu przychodów i marży do FY2029 ma mniej więcej połowę szans, a pobicie oczekiwań w cenie około jedną trzecią.
- **Co jest w cenie:** wzrost FCF {{implikowany_wzrost_fcf.2026-11-10}} rocznie przez dziesięć lat; udział PVGO {{udzial_pvgo.2026-11-10}}.
- **Pokrycie analityczne:** {{liczba_analitykow.2026-11-11}} analityków · 2026-11-11 · Stock Analysis.
- **Antytezy z progami:** marża brutto poniżej {{prognoza_zarzadu_marza_brutto.FY2027Q3}} przez dwa kwartały; DSO powyżej {{dso.2026-07-26}}; zapasy rosną szybciej niż przychody przez dwa kwartały; spadek przychodów hiperskalerów kwartał do kwartału; odejście prezesa.
- **Pre-mortem:** część dziewiąta.
- **Wielkość pozycji:** decyzja właściciela. Zasada: przy pozycji X procent IKE scenariusz niedźwiedzia ({{wartosc_na_akcje.niedzwiedz}} na akcję) zabiera Y procent IKE. Wg twoich zasad kupujesz w transzach.
- **Kiedy sprzedam:** gdy teza jest złamana (dwie antytezy specyficzne naraz), gdy masz lepszą spółkę z kartą albo gdy uznasz, że nie kupiłbyś jej dziś.
- **Data przeglądu:** po wynikach Q3 FY2027 (według materiału InvestingPro 17.11.2026) i po ogłoszeniu wyniku dochodzenia rady.
- **Co śledzić:** marżę brutto wobec prognozy, DSO, zapasy i zobowiązania zakupowe, udział największych klientów, przychody hiperskalerów, wynik dochodzenia rady.

## 14. Jakość danych

{{tabela:jakosc_danych}}

Czego nie sprawdziłem:
- Silnik uzupełnił rok FY2026 danymi z Stock Analysis, choć raport roczny jest w EDGAR; przyczyny nie sprawdziłem.
- Dwa zgłoszenia `Form 4` z października i listopada 2026 zwróciły błąd pobierania, więc nie przeczytałem najnowszych transakcji insiderów.
- Nie mam danych o udziałach rynkowych, więc nie oceniłem stabilności branży liczbami.
- Spółka nie podaje prognozy marży brutto na Q4 FY2027 w dokumentach z archiwum.
- Silnik nie znalazł spłaty leasingu za ostatnie lata; FCF dla właścicieli może jej nie uwzględniać.

Tropy z materiału InvestingPro (`doc-016`) i wynik sprawdzenia:
1. Kryzys wokół prezesa: potwierdzony co do dochodzenia rady, kancelarii Wachtell i przyznania się prezesa do niewierności (`doc-045`, `doc-043`, `doc-044`). Niepotwierdzony co do udziału FBI i tożsamości osoby z doniesień.
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
14. Termin wyników Q3 FY2027: niepotwierdzony dokumentem w archiwum; przegląd wiadomości wskazuje komunikat spółki z 28.10.2026.

Tropy z materiału, które zmieniły analizę: wątek prezesa skierował mnie do komunikatów rady, a wątek finansowania laboratoriów AI do 8-K z 17.08.2026 z gwarancjami dla kampusu SB Energy.
