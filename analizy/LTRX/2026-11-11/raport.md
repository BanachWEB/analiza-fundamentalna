# Lantronix (LTRX) — wstępna analiza fundamentalna

Data analizy: 11.11.2026. Rynek: USA. Instrument w XTB: LTRX.US. Decyzja bramek: DALEJ.

## TL;DR

> Lantronix projektuje moduły obliczeniowe, bramki i konsole do zdalnego zarządzania urządzeniami. Produkcję zleca podwykonawcom, a nowym motorem przychodów są moduły do dronów zgodne z wymogami armii USA. Spółka nie miała zysku netto w żadnym z pięciu ostatnich lat obrotowych. W połowie 2026 r. zebrała kapitał z emisji akcji, a w pierwszym kwartale FY2027 jej przepływy operacyjne były ujemne. Moim zdaniem przy kursie {{kurs.2026-11-10}} cena zakłada wyraźnie lepszą rentowność niż ta, którą spółka kiedykolwiek osiągała. Ze scenariuszy wychodzi wartość oczekiwana {{wartosc_oczekiwana_na_akcje.2026-11-10}} na akcję, a prawdopodobieństwo straty wynosi {{prawdopodobienstwo_straty.2026-11-10}} (silnik nie dolicza gotówki netto, patrz część „Co jest w cenie”). Największe ryzyko to kolejna emisja akcji przy trwałej stracie operacyjnej. Wg twoich zasad: spółka spełnia warunek pokrycia analitycznego i nie podlega pauzie po rajdzie, ale przed zakupem potrzebuje karty.

- Przewaga konkurencyjna: brak, trend niepewny.
- Wycena: kapitalizacja {{kapitalizacja.2026-11-10}}, C/Z nie ma sensu przy stracie netto, FCF yield {{fcf_yield.2026-11-10}}.
- Wartość oczekiwana ze scenariuszy: {{wartosc_oczekiwana_na_akcje.2026-11-10}} przy kursie {{kurs.2026-11-10}}; prawdopodobieństwo straty {{prawdopodobienstwo_straty.2026-11-10}}.
- Karta w stylu Treli: wynik średni, zawyżony przez filary „analitycy” i „momentum” (część „Karta w stylu Treli”).
- Pokrycie analityczne: średnie, {{liczba_analitykow.2026-11-11}} analityków.

## 1. Jak działa firma

Lantronix sprzedaje producentom urządzeń moduły obliczeniowe (SOM) i firmware, które ci wbudowują w swoje produkty. Klientom końcowym sprzedaje bramki IoT, konwertery mediów i konsole do zdalnego zarządzania sieciami (`doc-015`). Spółka ma jeden segment sprawozdawczy i dzieli przychody na trzy linie produktów: Embedded IoT Solutions, IoT System Solutions oraz Software and Services (`doc-015`).

Spółka nie ma własnych fabryk. Produkcję zleca podwykonawcom w Tajlandii i na Tajwanie, a moduły do dronów opiera na układach Qualcomm i od niedawna MediaTek (`doc-015`, `doc-017`). Większość sprzedaży przechodzi przez dystrybutorów (`doc-015`).

Cykl projektowy modułu u klienta trwa od dziewięciu miesięcy do dwóch lat. Gdy klient wbuduje moduł w swój produkt, spółka sprzedaje go przez cały cykl życia tego produktu (`doc-015`). Spółka zatrudniała {{liczba_pracownikow.2026-08-21}} osób na 21.08.2026 (`doc-015`).

Moim zdaniem w opowieści zarządu prawdopodobne jest to, że drony utrzymają wzrost w FY2027, bo zarząd trafił w swoją prognozę na FY2026. Wiarygodne, ale niepewne jest to, że oprogramowanie podniesie marżę spółki. Jedynie możliwe jest to, że konsole do zarządzania centrami danych AI staną się dużym rynkiem dla tak małej spółki.

## 2. Na czym zarabia

Przychody FY2026 według linii produktów (`doc-015`):

- Embedded IoT Solutions: {{przychody_embedded_iot.FY2026}} wobec {{przychody_embedded_iot.FY2025}} rok wcześniej, udział {{udzial_embedded_iot.FY2026}}. W tej linii są moduły do dronów.
- IoT System Solutions: {{przychody_iot_systems.FY2026}} wobec {{przychody_iot_systems.FY2025}}, udział {{udzial_iot_systems.FY2026}}.
- Software and Services: {{przychody_software_uslugi.FY2026}} wobec {{przychody_software_uslugi.FY2025}}, udział {{udzial_software_uslugi.FY2026}}.

Systemy bezzałogowe to wskaźnik zarządu wewnątrz linii Embedded, a nie segment. Przychody z nich wyniosły {{przychody_systemy_bezzalogowe.FY2026}} w FY2026. Wcześniejsza prognoza zarządu mówiła o przedziale od {{prognoza_zarzadu_systemy_bezzalogowe_dolna.FY2026}} do {{prognoza_zarzadu_systemy_bezzalogowe_gorna.FY2026}} (`doc-019`). Zarząd zapowiada, że w FY2027 systemy bezzałogowe dadzą od {{prognoza_zarzadu_udzial_systemy_bezzalogowe_dolna.FY2027}} do {{prognoza_zarzadu_udzial_systemy_bezzalogowe_gorna.FY2027}} przychodów (`doc-019`, `doc-018`).

Spadek linii IoT System Solutions w FY2026 wynika z utraty klienta Gridspertise. Rok wcześniej przychody od tego klienta wyniosły {{przychody_gridspertise.FY2025}}, a w FY2026 spółka nie miała od niego przychodu (`doc-015`). W pierwszym kwartale FY2027 linia Embedded urosła do {{przychody_embedded_iot.FY2027Q1}} z {{przychody_embedded_iot.FY2026Q1}}, a linia IoT System Solutions spadła do {{przychody_iot_systems.FY2027Q1}} z {{przychody_iot_systems.FY2026Q1}} (`doc-016`).

Przychody zależą od kilku odbiorców. Pięciu największych klientów dało {{udzial_top5_klientow.FY2026}} przychodów FY2026, a największy z nich, Klient A, dał {{udzial_klienta_a.FY2026}} (`doc-015`). Pięciu największych dystrybutorów dało {{udzial_top5_dystrybutorow.FY2026}} przychodów (`doc-015`). Ameryki dały {{udzial_ameryki.FY2026}} przychodów FY2026 (`doc-015`).

## 3. Najważniejsze fakty (akcjonariat, zarząd, płynność, kalendarz)

- Akcjonariat jest rozproszony. Największy akcjonariusz, Needham Investment Management, ma {{udzial_needham_im.2026-09-08}} akcji (`doc-022`). Zarząd i rada mają razem {{udzial_zarzadu_i_rady_w_akcjach.2026-09-08}} (`doc-022`).
- Spółka miała {{akcje_okladka_10q.2026-10-30}} akcji na 30.10.2026 wobec {{akcje_wyemitowane_bilans.2025-06-30}} na 30.06.2025 (`doc-016`, `doc-015`).
- Prezesem jest Saleel Awsare, od listopada 2023 r. (`doc-015`).
- Kapitalizacja wynosi {{kapitalizacja.2026-11-10}}, a średnie dzienne obroty z ostatnich sześćdziesięciu sesji wynoszą {{obroty_dzienne_60s.2026-11-10}}.
- Gotówka i krótkoterminowe papiery wartościowe wyniosły {{gotowka_i_papiery_wartosciowe.2026-09-30}} na 30.09.2026 (`doc-018`). Dług netto wyniósł {{dlug_netto.2026-09-30}}, czyli spółka ma gotówkę netto.
- Kalendarz: spółka opublikowała wyniki za pierwszy kwartał FY2027 9.11.2026. Kolejne wyniki, za drugi kwartał FY2027 (do 31.12.2026), spółka zwykle publikuje na początku lutego. Daty nie sprawdziłem.

## 4. Branża, konkurencja i przewaga konkurencyjna

Spółka nie wymienia konkurentów z nazwy w raporcie rocznym 10-K. Pisze tylko, że wielu z nich ma większe zasoby i sieci dystrybucji (`doc-015`). Spółka przyznaje, że ceny sprzedaży i marże w przeszłości spadały i że spodziewa się dalszej presji cenowej (`doc-015`). Część produktów sprzedaje na rynkach dojrzałych o malejącym popycie (`doc-015`). W archiwum nie ma dokumentu o wielkości rynku ani o udziałach, więc nie oceniam stabilności branży.

Kandydaci na przewagę konkurencyjną:

1. **Zgodność z wymogami armii USA i lista Blue UAS.** Korzyść: moduł z tej listy skraca kwalifikację u producenta drona (`doc-017`). Bariera: przepisy ograniczają użycie zagranicznych komponentów w dronach dla rządu USA (`doc-015`). Moim zdaniem ta bariera chroni przed dostawcami z Chin, a nie przed innymi dostawcami z USA. Dokumenty nie mówią, ilu konkurentów ma ten sam status.
2. **Koszt zmiany dostawcy po wbudowaniu modułu.** Korzyść: przychód przez cały cykl życia produktu klienta. Bariera: zmiana modułu wymaga nowego projektu i certyfikacji (`doc-015`, `doc-018`). Moim zdaniem to realny, ale słaby koszt zmiany, bo dotyczy jednego pokolenia produktu klienta.
3. **Oprogramowanie (Percepxion, Nero).** Udział tej linii w przychodach jest nadal mały: {{udzial_software_uslugi.FY2026}} (`doc-015`).

Liczby nie pokazują przewagi. ROIC był ujemny w każdym roku od FY2022 do FY2026 (panel w części „Sprawozdania finansowe”). Marża brutto spadła w FY2024, gdy spółka sprzedawała dużo niskomarżowych produktów jednemu klientowi.

Moim zdaniem werdykt to **brak przewagi konkurencyjnej**, a trend jest niepewny. Spółka może zbudować wąską przewagę w modułach do dronów, ale dziś dokumenty tego nie dowodzą. Nawet spółki z najwyższą rentownością kapitału mają tylko około połowy szans, że utrzymają ją przez dekadę.

**Test AI.** Przychody nie zależą od godzin pracy ludzi, bo spółka sprzedaje sprzęt i oprogramowanie (`doc-015`). Koszt zmiany dostawcy wynika z certyfikacji i integracji z produktem fizycznym, czyli jest silniejszy niż samo przyzwyczajenie. Spółka nie opisuje własnych danych, które poprawiałyby produkt. Moim zdaniem AI na razie podnosi popyt na moduły obliczeniowe na krawędzi sieci, ale jednocześnie podnosi ceny pamięci, które spółka kupuje (`doc-015`, `doc-018`).

## 5. Zarząd i alokacja kapitału

Prezes Saleel Awsare kieruje spółką od listopada 2023 r. Wcześniej kierował jednostkami w Synaptics, Conexant i Nuvoton (`doc-015`). W FY2026 zarobił łącznie {{wynagrodzenie_ceo_razem.FY2026}}, w tym nagrody akcyjne {{wynagrodzenie_ceo_nagrody_akcyjne.FY2026}} (`doc-022`). Rada podniosła mu pensję od 1.08.2026 do {{pensja_ceo_od_2026_08_01.2026-08-01}} (`doc-021`).

Premia roczna zależy od przychodów i od zysku na akcję skorygowanego (`doc-022`). Cel przychodowy FY2026 wynosił {{cel_premii_przychody.FY2026}}, a spółka go nie osiągnęła, choć przekroczyła próg wypłaty {{prog_premii_przychody.FY2026}} (`doc-022`). Moim zdaniem rada ustawiła cele FY2026 nisko, bo sama nazwała FY2026 rokiem „resetu” (`doc-022`).

Zarząd dotrzymywał ostatnich prognoz. Przychody pierwszego kwartału FY2027 mieszczą się w prognozie od {{prognoza_zarzadu_przychody_dolna.FY2027Q1}} do {{prognoza_zarzadu_przychody_gorna.FY2027Q1}} (`doc-019`, `doc-017`). Przychody z systemów bezzałogowych w FY2026 też trafiły w prognozę.

Źródła gotówki w FY2026 to głównie emisje akcji. Spółka sprzedała w maju 2026 r. {{liczba_akcji_emisja_2026_05_29.2026-05-29}} akcji w ofercie publicznej i {{liczba_akcji_atm.FY2026}} akcji w programie sprzedaży na rynku (`doc-015`). Łączne wpływy netto z emisji wyniosły {{wplywy_netto_emisje_akcji.FY2026}} (`doc-015`). Spółka spłaciła z tych pieniędzy dawny kredyt. Po końcu roku obrotowego zaciągnęła jednak nowy kredyt i miała {{dlug_brutto_nowy_kredyt.2026-09-30}} długu na 30.09.2026 (`doc-016`). Spółka kupiła Nero Global Tracking za około {{cena_przejecia_nero.2026-08-01}} (`doc-015`). Spółka nie wypłaca dywidend i nie skupuje akcji, a badacz nie przeczytał w całości części 10-K o polityce dywidendowej.

Walne zgromadzenie z 3.11.2026 zwiększyło pulę planu motywacyjnego o {{pula_planu_motywacyjnego_zwiekszenie.2026-11-03}} akcji (`doc-020`). Moim zdaniem zarząd alokuje kapitał w sposób typowy dla małej spółki wzrostowej: emituje akcje i kupuje małe firmy. Taki sposób działa tylko wtedy, gdy przejęcia szybko dają dodatni FCF.

## 6. Sprawozdania finansowe

{{tabela:panel}}

{{wykres:przychody}}

{{wykres:marze}}

{{wykres:fcf_zysk}}

**Wzrost.** Przychody wyniosły {{przychody.FY2026}} w FY2026 wobec {{przychody.FY2024}} w FY2024. Spadek wynika z wygaszenia dużego wdrożenia u jednego klienta (`doc-022`, `doc-015`). W pierwszym kwartale FY2027 przychody wzrosły r/r o {{wzrost_przychody.FY2027Q1}}. Przychody TTM do 30.09.2026 wyniosły {{przychody.TTM2026-09-30}}.

**Marże.** Marża brutto wyniosła {{marza_brutto.FY2026}} w FY2026. Marża operacyjna była ujemna i wyniosła {{marza_operacyjna.FY2026}} w FY2026 oraz {{marza_operacyjna.TTM2026-09-30}} TTM. Zysk netto TTM wyniósł {{zysk_netto.TTM2026-09-30}}. Zarząd zapowiada skorygowany zysk netto w drugim kwartale FY2027 od {{prognoza_zarzadu_zysk_netto_skorygowany_dolna.FY2027Q2}} do {{prognoza_zarzadu_zysk_netto_skorygowany_gorna.FY2027Q2}} (`doc-017`). Wynik skorygowany pomija między innymi koszt wynagrodzeń w akcjach.

**Jakość zysków.** FCF dla właścicieli (po koszcie wynagrodzeń w akcjach) wyniósł {{fcf_wlascicieli.FY2026}} w FY2026 i {{fcf_wlascicieli.TTM2026-09-30}} TTM. Przepływy operacyjne w pierwszym kwartale FY2027 były ujemne i wyniosły {{przeplywy_operacyjne.FY2027Q1}}. Zarząd tłumaczy to zakupami modułów i pamięci na zapas: zapasy netto wzrosły z {{zapasy_netto_przyblizone.2026-06-30}} do {{zapasy_netto_przyblizone.2026-09-30}} (`doc-018`).

**Zadłużenie.** Spółka ma gotówkę netto: dług netto na 30.09.2026 wyniósł {{dlug_netto.2026-09-30}}. Wskaźnik dług netto ÷ EBITDA w panelu nie ma sensu, bo zarówno dług netto, jak i EBITDA są ujemne. Nowa umowa kredytowa zastawia praktycznie wszystkie aktywa spółki (`doc-015`, `doc-016`).

**Rozwodnienie.** Panel pokazuje zmianę średniej liczby akcji r/r o {{zmiana_liczby_akcji.FY2026}} w FY2026. Ta miara zaniża skalę, bo emisje przypadły na koniec roku obrotowego. Liczba akcji na koniec okresu wzrosła z {{akcje_wyemitowane_bilans.2025-06-30}} do {{akcje_okladka_10q.2026-10-30}} (`doc-015`, `doc-016`).

## 7. Jakość zysków i czerwone flagi

{{tabela:bramki}}

Bramki nie znalazły twardej flagi. Biegły (Baker Tilly) wydał opinię bez zastrzeżeń, a zarząd i biegły stwierdzają skuteczną kontrolę wewnętrzną na 30.06.2026 (`doc-015`). Flaga „material weakness” pochodzi z ogólnego opisu zakresu badania.

Trzy flagi wymagają uwagi:

1. **Rozwodnienie.** Spółka wyemitowała akcje dwa razy w ciągu miesiąca, w tym w ofercie publicznej z dyskontem do kursu (`doc-025`, `doc-026`). Moim zdaniem to nie jest szkoda dla mniejszości, bo oferta była publiczna i bez warrantów. Spółka ma jednak aktywną półkę rejestracyjną i niewykorzystaną część programu sprzedaży akcji na rynku (`doc-015`).
2. **Sprzedaż przez insidera.** Dyrektor ds. strategii Mathi Gurusamy sprzedał akcje na rynku 13.03.2026, a zawiadomienie nie wskazuje planu sprzedaży ustalonego z góry (`doc-060`). To jedyna sprzedaż na rynku w przejrzanych zawiadomieniach z 2026 r. Prezes kupił akcje na rynku 9.09.2026 (`doc-036`).
3. **Kluczowa sprawa badania.** Biegły wskazał rezerwę na zapasy nadmiarowe i przestarzałe (`doc-015`). Moim zdaniem ta sprawa ma znaczenie, bo spółka w pierwszym kwartale FY2027 świadomie zwiększyła zapasy.

Wskaźniki statystyczne nie zatrzymują analizy. Beneish M-score wynosi {{beneish_m.FY2026}} i jest poniżej progu manipulacji. Altman Z'' wynosi {{altman_z2.FY2026}} i leży w strefie szarej. Ohlson szacuje prawdopodobieństwo upadłości w ciągu roku na {{ohlson_p.FY2026}}.

## 8. Co jest w cenie

{{tabela:wycena}}

Przy kursie {{kurs.2026-11-10}} kapitalizacja wynosi {{kapitalizacja.2026-11-10}}, a EV {{ev.2026-11-10}}. Silnik nie policzył implikowanego wzrostu FCF ani okresu przewagi (CAP), bo FCF dla właścicieli TTM jest ujemny. Wariant marży mówi, że przy historycznym tempie przychodów cena zakłada marżę FCF {{implikowana_marza_fcf.2026-11-10}}. Najlepsza marża FCF w ostatnich pięciu latach wyniosła {{marza_fcf.FY2024}} w FY2024. Historyczne tempo wzrostu przychodów ({{cagr_przychody_3l.FY2026}} rocznie przez trzy lata) zaniża jednak obraz, bo obejmuje utratę dużego klienta.

Udział PVGO w cenie wynosi {{udzial_pvgo.2026-11-10}}. Inwestor płaci więc całą cenę za przyszły wzrost, bo obecne przepływy nie uzasadniają żadnej wartości.

Konsensus: {{liczba_analitykow.2026-11-11}} analityków (S&P Global, przez Stock Analysis) daje średnią cenę docelową {{cena_docelowa_srednia.2026-11-11}} i prognozuje wzrost EPS o {{wzrost_eps_konsensus.2026-11-11}}. Prognoza EPS dotyczy wyniku skorygowanego. Analitycy historycznie zawyżają długoterminowy wzrost, więc cena docelowa to kontekst, a nie wartość godziwa.

Trzy liczby obok siebie: cena przy wzroście historycznym zakłada marżę FCF {{implikowana_marza_fcf.2026-11-10}}. Konsensus zakłada szybki wzrost EPS skorygowanego. Mój scenariusz bazowy zakłada wzrost przychodów {{scenariusz_wzrost_przychodow.bazowy}} rocznie i marżę FCF {{scenariusz_marza_fcf.bazowy}}.

**Ważne zastrzeżenie.** Silnik liczy wartość scenariuszy z przepływów i nie dodaje gotówki netto ({{dlug_netto.2026-09-30}} długu netto, czyli gotówka netto). Gotówka netto podniosłaby wartość każdego scenariusza, a prawdopodobieństwo straty może być przez to zawyżone. Ten brak jest opisany w `braki-silnika.md`; poprawioną wartość policzy silnik po uzupełnieniu kodu.

## 9. Teza, antytezy, pre-mortem

**Co wycenia rynek.** Zakładam, że rynek wycenia trwały powrót do dodatniego FCF przy dwucyfrowym wzroście przychodów napędzanym przez drony i oprogramowanie.

**Teza (zdanie rozstrzygalne).** Do 30.06.2028 Lantronix osiągnie dwucyfrowy wzrost przychodów w FY2027 i dodatni FCF dla właścicieli w FY2028, bez nowej emisji akcji.

**Prawdopodobieństwo.** Zakładam, że stopa bazowa dla małej, nierentownej spółki sprzętowej, która trwale przechodzi na dodatni FCF, wynosi około jednej trzeciej. Teza wymaga czterech warunków: dwucyfrowego wzrostu w FY2027 (zarząd go zapowiada i trafiał w ostatnie prognozy), utrzymania marży brutto mimo droższej pamięci, braku nowej emisji oraz dodatniego FCF po kosztach wynagrodzeń w akcjach. Te warunki są ze sobą powiązane, więc ich iloczyn zaniża wynik. Moim zdaniem teza ma około jednej czwartej szans. Taki wynik jest zgodny z wagą scenariusza byka.

**Moja odmienna teza.** Moim zdaniem nie mam przewagi informacyjnej nad rynkiem. Rynek widzi te same wiadomości o dronach, a ja widzę dodatkowo, że FCF dla właścicieli nigdy nie był trwale dodatni. Moja teza jest więc ostrożniejsza od konsensusu, a nie odmienna w stronę wzrostu.

**Katalizatory.**
1. Wyniki za drugi kwartał FY2027 (zwykle luty 2027): przychody w prognozie od {{prognoza_zarzadu_przychody_dolna.FY2027Q2}} do {{prognoza_zarzadu_przychody_gorna.FY2027Q2}} i powrót przepływów operacyjnych powyżej zera.
2. Raport roczny za FY2027 (sierpień 2027): udział systemów bezzałogowych w przychodach w zapowiadanym przedziale.
3. Pierwsze zamówienia na moduły z listy Blue UAS w programach rządowych.
4. Udział linii Software and Services w przychodach powyżej poziomu z FY2026 ({{udzial_software_uslugi.FY2026}}).

**Antytezy z progami.**
- Sprawdzalne: przepływy operacyjne są ujemne w dwóch kolejnych kwartałach po pierwszym kwartale FY2027 ({{przeplywy_operacyjne.FY2027Q1}}). Marża brutto spada poniżej poziomu z FY2026 ({{marza_brutto.FY2026}}) przez dwa kwartały z rzędu. Spółka ogłasza kolejną emisję akcji.
- Specyficzne: główny klient z listy największych odbiorców wygasza zamówienia, jak wcześniej Gridspertise. Zarząd obniża zapowiedź dwucyfrowego wzrostu.
- Rynkowe: budżet obronny USA albo przepisy o dronach po wyborach z 3.11.2026 zmieniają priorytety (`doc-017`).
- Nieprzewidywalne: niedobór pamięci odcina dostawy modułów. To ryzyko ogranicza tylko wielkość pozycji.

**Pre-mortem.** Za dwa lata pozycja traci połowę. Moim zdaniem najbardziej prawdopodobna przyczyna to taka: drony rosną, ale mają niższą marżę, ceny pamięci rosną, a starsze produkty dalej spadają. Spółka przepala gotówkę na zapasy i przejęcia, a potem emituje akcje z dyskontem.

**Horyzont.** Teza rozstrzygnie się w ciągu dwóch lat (FY2027 i FY2028). Horyzont trzymania to decyzja właściciela.

## 10. Wiadomości i scenariusze

Kurs spadł mocno w sesji 10.11.2026, dzień po publikacji wyników za pierwszy kwartał FY2027 (`doc-007`). Subagent wiadomości nie znalazł źródła, które wyjaśnia ten spadek. Moim zdaniem możliwe przyczyny to ujemne przepływy operacyjne, wzrost zapasów i spadek linii IoT System Solutions, ale tego nie udokumentowałem. W ciągu trzech miesięcy kurs zmienił się o {{zmiana_kursu_3m.2026-11-10}}.

Wiadomości przetłumaczone na czynniki wartości:
- Pozytywne: wpis modułu na listę Blue UAS (wzrost przychodów, `doc-017`), przejęcie Nero z przychodami powtarzalnymi (marża, `doc-015`), wejście do produktów Trimble i SambaNova (wzrost przychodów, `doc-017`, `doc-018`).
- Negatywne: emisje akcji w maju i czerwcu 2026 r. (rozwodnienie, `doc-025`), wzrost zapasów i ujemne przepływy operacyjne (kapitał obrotowy, `doc-018`), droższa pamięć (marża brutto, `doc-015`).

{{tabela:scenariusze}}

Scenariusz byka ({{scenariusz_prawdopodobienstwo.byk}}) zakłada wzrost przychodów {{scenariusz_wzrost_przychodow.byk}} rocznie i marżę FCF {{scenariusz_marza_fcf.byk}}. Scenariusz bazowy ({{scenariusz_prawdopodobienstwo.bazowy}}) zakłada wzrost {{scenariusz_wzrost_przychodow.bazowy}} i marżę FCF {{scenariusz_marza_fcf.bazowy}}. Scenariusz niedźwiedzia ({{scenariusz_prawdopodobienstwo.niedzwiedz}}) zakłada wzrost {{scenariusz_wzrost_przychodow.niedzwiedz}} i marżę FCF {{scenariusz_marza_fcf.niedzwiedz}}. Wagę niedźwiedzia ustawiłem wyżej niż zwykle, bo spółka nie miała zysku netto w żadnym z pięciu ostatnich lat obrotowych.

Byki mówią: drony i przepisy faworyzujące dostawców z USA dają spółce nowy rynek, a gotówka netto daje czas na wzrost. Niedźwiedzie mówią: spółka od lat nie zarabia, przychody zależą od kilku klientów i rządu, a każdy rok wzrostu kończy się emisją akcji.

## 11. Karta w stylu Treli

{{tabela:karta}}

Moim zdaniem wynik karty jest zawyżony. Filar „analitycy” dostaje maksimum za wysoką cenę docelową, a filar „momentum” za ruch kursu z ostatniego roku, który już się odwrócił. Filar „jakość” ma niski wynik, bo ROIC jest ujemny.

## 12. Dostęp przez IKE

Instrument w XTB to LTRX.US, notowany w USD na NASDAQ. Dostępności tej akcji w IKE w XTB nie sprawdziłem. Każde przewalutowanie z PLN na USD kosztuje w XTB pół procenta. Spółka nie wypłaca dywidend, więc podatek u źródła od dywidend (piętnaście procent z formularzem W-8BEN) dziś cię nie dotyczy. Twoje ETF-y z portfela Core (IWDA, CNDX, EIMI) praktycznie nie zawierają tak małej spółki, ale tego nie sprawdziłem w składzie funduszy.

Wg twoich zasad: LTRX trafia do koszyka „Akcje zagraniczne” w portfelu Agresywnym, a benchmarkiem jest S&P 500. Spółkę śledzi więcej niż trzech analityków, więc warunek pokrycia jest spełniony. Kurs spadł w ciągu trzech miesięcy, więc pauza po rajdzie nie obowiązuje. Przed zakupem potrzebujesz karty spółki i kupujesz w transzach.

## 13. Projekt karty

**Teza w trzech zdaniach.** Lantronix przestawia się z wygasających dużych wdrożeń na moduły do dronów zgodne z wymogami armii USA i na oprogramowanie. Teza wymaga dwucyfrowego wzrostu przychodów w FY2027 i dodatniego FCF dla właścicieli w FY2028 bez nowej emisji. Moim zdaniem ma około jednej czwartej szans.

**Co jest w cenie.** Cała cena to przyszły wzrost (PVGO {{udzial_pvgo.2026-11-10}}). Cena zakłada marżę FCF wyraźnie powyżej najlepszego roku spółki.

**Antytezy z progami.** Przepływy operacyjne ujemne przez dwa kolejne kwartały. Marża brutto poniżej poziomu z FY2026 przez dwa kwartały. Nowa emisja akcji. Obniżenie zapowiedzi wzrostu na FY2027. Dokładne progi wpisujesz sam.

**Pre-mortem.** Drony rosną z niską marżą, pamięć drożeje, spółka przepala gotówkę i emituje akcje z dyskontem.

**Wielkość pozycji.** Scenariusz niedźwiedzia zabiera większość wartości pozycji. Wielkość pozycji wybierasz tak, żeby taka strata była do przyjęcia w limicie portfela Agresywnego.

**Kiedy sprzedam.** Gdy spełni się któraś antyteza sprawdzalna albo gdy uznasz, że nie kupiłbyś spółki dziś.

**Data przeglądu.** Po wynikach za drugi kwartał FY2027 (luty 2027).

**Co śledzić co kwartał.** Przychody z systemów bezzałogowych, marżę brutto, przepływy operacyjne i zapasy, liczbę akcji, udział linii Software and Services.

## 14. Jakość danych

{{tabela:jakosc_danych}}

Silnik wykrył dwa problemy z danymi. Spółka oznacza znacznikiem XBRL dla kosztu sprzedaży tylko drobną pozycję, więc tożsamość „przychody − koszt sprzedaży = zysk brutto” nie przechodzi. Przychody i zysk brutto są poprawne, więc marża brutto też. Zysk operacyjny z drugiego źródła (S&P Global przez Stock Analysis) różni się od danych spółki. Raport używa danych spółki z XBRL.

Czego nie sprawdziłem: nazw konkurentów i wielkości rynku, nazwy Klienta A, marży brutto modułów do dronów, wartości zamówień rządowych, daty kolejnych wyników, dostępności akcji w IKE.

Tropy z materiałów od ciebie (InvestingPro `doc-028`, zrzut ekranu `doc-029`):

- `T1`, spadek kursu po wynikach: potwierdzony notowaniami (`doc-007`). Przyczyny nie udokumentowałem.
- `T2`, emisja akcji w FY2026: potwierdzony, wpływy netto {{wplywy_netto_emisje_akcji.FY2026}} (`doc-015`).
- `T3`, brak długu i gotówka na koniec FY2026: potwierdzony (`doc-019`, `doc-015`). Po końcu roku spółka zaciągnęła jednak nowy kredyt (`doc-016`).
- `T4`, przejęcie Nero: cena potwierdzona (`doc-015`). Przychody powtarzalne (ARR) według spółki wynoszą {{arr_nero_oczekiwany.FY2027}}, czyli mniej niż w materiale (`doc-019`).
- `T5`, systemy bezzałogowe: liczby potwierdzone (`doc-019`, `doc-018`). To nie jest segment sprawozdawczy, tylko wskaźnik zarządu.
- `T6`, lista Blue UAS: potwierdzony (`doc-017`).
- `T7`, niższa marża brutto dronów: potwierdzony jakościowo (`doc-016`). Liczby spółka nie podaje.
- `T8`, zależność od rządu i skutek shutdownu: ryzyko potwierdzone (`doc-015`). Skutku shutdownu dla przychodów FY2026 dokumenty nie podają.
- `T9`, dezinwestycja Gridspertise: sprzeczny z dokumentami. Gridspertise to utracony klient, a nie sprzedana część spółki (`doc-015`).
- `T10`, dwucyfrowy wzrost w FY2027: potwierdzony jako zapowiedź zarządu (`doc-017`, `doc-019`).
- `T11`, rozbieżność zysku operacyjnego FY2026: potwierdzona. Raport używa danych spółki z XBRL, a przyczyny rozbieżności nie sprawdziłem.
- `T12`, luka bezpieczeństwa w urządzeniu XPort: niepotwierdzony. Dokumenty w archiwum o niej nie wspominają.
- `T13`, ceny pamięci: zjawisko potwierdzone (`doc-015`, `doc-018`). Skutku dla marży dokumenty nie podają.
- `T14`, zawiadomienie prezesa z listopada 2026 r.: potwierdzony. Zawiadomienie nie pokazuje sprzedaży na rynku (`doc-035`).
- `T15`, zmiana w radzie: potwierdzony (`doc-022`, `doc-020`).
- `T16`, wartość godziwa i oceny kondycji InvestingPro: nie wchodzą do raportu, bo nie mają jawnej metody.
- `T17`, cena docelowa na zrzucie ekranu: różni się od średniej z drugiego źródła ({{cena_docelowa_srednia.2026-11-11}}). Wskaźnika cena ÷ sprzedaż na rok naprzód silnik nie liczy, więc tej części tropu nie sprawdziłem.
- `T18`, RSI blisko strefy wyprzedania: niesprawdzony, bo silnik nie liczy RSI.

Przychody TTM ze zrzutu ekranu zgadzają się z danymi silnika ({{przychody.TTM2026-09-30}}).
