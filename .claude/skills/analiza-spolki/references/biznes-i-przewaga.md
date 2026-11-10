# Biznes, branża, przewaga konkurencyjna, zarząd

Źródło metody: raport z badania „Analiza fundamentalna i wycena spółek” (9.11.2026), część 2. Progi liczbowe to heurystyki badaczy, nie wyniki badań.

## Spis treści
1. Jak działa firma (dla czytelnika, który jej nie zna)
2. Branża i konkurencja
3. Przewaga konkurencyjna: procedura
4. Test AI
5. Zarząd i alokacja kapitału

## 1. Jak działa firma

Jedna strona, która odpowiada na pytania:

| Element | Pytanie |
|---|---|
| Jedno zdanie | Kto komu płaci, za co i dlaczego wybiera właśnie tę spółkę? |
| Segmenty | Jaki udział w przychodach i w zysku operacyjnym ma każdy segment? Czy zysk pochodzi z segmentu, o którym mówią nagłówki? |
| Rozkład przychodów | Wolumen × cena albo klienci × przychód na klienta; przychody powtarzalne i jednorazowe; kraje; najwięksi klienci |
| Łańcuch wartości | Kto dostarcza, kto kupuje, kto ma siłę negocjacyjną? |
| Koszty i kapitałochłonność | Jaka część kosztów jest stała? Co decyduje o marży? Ile kapitału potrzeba na wzrost (capex ÷ amortyzacja z panelu)? |
| 3–5 czynników wartości | Jakie liczby śledzić co kwartał? |
| Test 3P (Damodaran) | Co w opowieści zarządu jest prawdopodobne, co tylko wiarygodne, a co jedynie możliwe? |

Liczby z segmentów i KPI operacyjnych dodajesz jako propozycje z cytatem z raportu.

## 2. Branża i konkurencja

- 5–10 konkurentów z opisem modelu (bez liczb z pamięci; liczby tylko z dokumentów w archiwum).
- Stabilność: średnia bezwzględna zmiana udziałów do 2 pp w 5 lat = branża stabilna (Mauboussin). Koncentracja: HHI > 1 800 = osłabiona rywalizacja.
- Faza cyklu życia, cykliczność (jak spółka przeszła 2020 i 2022–2023), regulacje, udział państwa.
- Złudzenie wielkiego rynku (Cornell i Damodaran): gdy zarząd powołuje się na wielki rynek, porównaj przychody zakładane przez cenę (wycena odwrotna) z wielkością rynku i zapytaj, dlaczego wygra ta spółka.

## 3. Przewaga konkurencyjna

1. Kandydaci na źródło przewagi: pięć kategorii Morningstar (aktywa niematerialne, koszty zmiany dostawcy, efekt sieciowy, przewaga kosztowa, efektywna skala) i dwie Helmera (kontrpozycjonowanie, przewaga procesowa).
2. Dla każdego kandydata: **korzyść** (wyższa cena albo niższy koszt) i **bariera** (dlaczego konkurenci nie skopiują), z dowodem z dokumentów.
3. Liczby (z panelu i wykresów): ROIC powyżej kosztu kapitału w co najmniej 8 z 10 lat, w tym w roku dekoniunktury; stabilna marża brutto, zwłaszcza w latach 2021–2023 (siła cenowa przy szoku kosztów); ROIC liczony bez korekty o wartości niematerialne zawyża wynik spółek z dużymi nakładami na badania.
4. Werdykt: **brak / wąska** (zwroty powyżej kosztu kapitału bardziej prawdopodobne niż nie przez 10 lat) **/ szeroka** (niemal pewne przez 10, bardziej prawdopodobne niż nie przez 20). Trend: rosnąca, stabilna, słabnąca.
5. Reguła nadrzędna: brak przewagi, gdy zadłużenie, regulacja, akcjonariusz kontrolujący albo AI mogą zniszczyć zysk ekonomiczny.
6. Stopa bazowa do raportu: nawet spółka z najwyższego kwintyla ROIC ma ok. 40–50% szans, że zostanie w nim po dekadzie.
7. Nie uznawaj za przewagę: dużego udziału w rynku, szybkiego wzrostu, marki bez premii cenowej, dobrego zarządu, jednego przebojowego produktu.
8. Bramka `B5.brak_przewagi` (flaga): brak przewagi przy wycenie zakładającej długi okres przewagi (implikowany CAP z `obliczenia.md`).

## 4. Test AI (pięć pytań)

1. Czy przychody zależą od godzin pracy ludzi albo liczby stanowisk?
2. Czy koszt zmiany dostawcy wynika z przyzwyczajenia (słaby), czy z certyfikacji, integracji z procesami fizycznymi albo odpowiedzialności prawnej (silniejszy)?
3. Czy spółka ma własne dane, których nie da się odtworzyć i które mierzalnie poprawiają produkt?
4. Czy AI obniży koszt wejścia konkurentom?
5. Czy oszczędności z AI zostaną w spółce, czy konkurencja je wyrówna?

Morningstar (marzec 2026): blisko połowa obniżonych ocen przewagi dotyczyła kosztów zmiany dostawcy; efekty sieciowe okazały się najodporniejsze. Dla software house'ów i outsourcingu IT domyślny trend przewagi to „słabnący albo niepewny”, chyba że spółka działa w regulowanej niszy.

## 5. Zarząd i alokacja kapitału

- Mapa własności: akcjonariusz kontrolujący, głosy a kapitał, akcje uprzywilejowane, zastawy na akcjach (USA: DEF 14A; GPW: raport roczny, ESPI o stanach posiadania). Akcjonariusz z ponad 90% głosów albo ryzyko przymusowego wykupu = STOP (`B4.akcjonariusz_90`).
- Programy motywacyjne i rozwodnienie (panel: zmiana liczby akcji; USA: SBC w FCF dla właścicieli).
- Cele z dawnych strategii i prognoz zarządu a wyniki.
- Źródła i zastosowania gotówki z 10 lat: przepływy, capex, przejęcia, dywidendy, skup akcji, emisje.
- Przejęcia: wiele małych (mediana +2,1% rocznie wobec konkurentów, McKinsey) a duże (rzut monetą).
- Transakcje z podmiotami powiązanymi (`B4.podmioty_powiazane`) i historia wezwań po zaniżonej cenie.
- GPW: spółki Skarbu Państwa osobno — cele polityczne działają jak czynnik zewnętrzny. USA: sprzedaż insiderów według planów 10b5-1 to szum; znaczenie mają transakcje okazjonalne.
