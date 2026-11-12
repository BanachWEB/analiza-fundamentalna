# Co jest w cenie, teza, warunki konieczne, scenariusze

Źródło metody: raport z badania, część 4 (Mauboussin i Rappaport, Damodaran, Tetlock, Klein).

## Spis treści
1. Co jest w cenie
2. Teza
3. Warunki konieczne tezy
4. Scenariusze (`scenariusze.json`)
5. Wiadomości i konsensus
6. Margines bezpieczeństwa i wielkość pozycji

## 1. Co jest w cenie

Z `obliczenia.md` (wszystko policzone przez silnik):
- **implikowany wzrost FCF** przez 10 lat — „cena zakłada, że FCF dla właścicieli rośnie o {{implikowany_wzrost_fcf.<data>}} rocznie”;
- **implikowany CAP** — ile lat wzrostu w tempie historycznym uzasadnia cenę; niski CAP przy udowodnionej przewadze to klasyczna okazja, wysoki to wymagające oczekiwanie;
- **implikowana marża FCF** przy wzroście historycznym — porównaj z obecną marżą FCF;
- **udział PVGO** — część ceny płacona za przyszły wzrost; myli przy spółkach cyklicznych, bankach i w restrukturyzacji;
- trzy liczby obok siebie: wzrost zakładany przez cenę, konsensus (`wzrost_eps_konsensus`, jeśli jest) i twój scenariusz bazowy.

Spółka cykliczna: nie bierz zysku ze szczytu za normę; opisz, jaką marżę przez pełny cykl zakłada cena.

## 2. Teza

Szablon (odpowiada karcie właściciela):
1. Co wycenia rynek (implikowany wzrost, CAP, marża).
2. Twoja odmienna teza: który czynnik wartości będzie inny i w którą stronę. Teza zgodna z konsensusem nie daje przewagi.
3. Dlaczego rynek się myli (behawioralnie, analitycznie, informacyjnie, technicznie) i dlaczego błąd minie.
4. Katalizatory z datami, 3–5 kamieni milowych z progami.
5. Antytezy z progami: sortuj na rynkowe (horyzont i alokacja), specyficzne i sprawdzalne (wskaźnik i próg), nieprzewidywalne (tylko wielkość pozycji). Antyteza, której nie da się ani obalić, ani zmierzyć → wg twoich zasad: nie kupować.
6. Pre-mortem: „za 2 lata pozycja jest −50% — co się stało?”.
7. Horyzont rozpoznania tezy (2–5 lat) osobno od horyzontu trzymania.

Progi antytez opisujesz słownie względem faktów z rejestru, np. „marża operacyjna spada poniżej obecnego poziomu ({{marza_operacyjna.TTM2026-09-30}}) przez dwa kwartały z rzędu”. Dokładne wartości progów właściciel wpisuje w karcie po swoim „tak”.

## 3. Warunki konieczne tezy

Decyzja właściciela z 12.11.2026: nie podajesz prawdopodobieństwa tezy, bo ocena tezy należy do analizy miękkiej właściciela, a liczba od modelu działa jak kotwica.

1. Zapisz tezę jako zdanie rozstrzygalne z horyzontem.
2. Rozłóż ją na 3–5 warunków koniecznych: rzeczy, które muszą się spełnić, żeby teza była prawdziwa.
3. Przy każdym warunku podaj status:
   - **potwierdzony** — dokument z archiwum (numer `doc-…`) pokazuje, że warunek jest dziś spełniony albo na dobrej drodze;
   - **sprzeczny** — dokument z archiwum mu przeczy (numer `doc-…`);
   - **do sprawdzenia** — dokumenty nie rozstrzygają; podaj, gdzie to sprawdzić (konferencja wynikowa, raport konkurenta, relacje inwestorskie, dane branżowe).
4. Warunki „do sprawdzenia” przenieś do części 12 „Do dalszej analizy”.
5. Zrób pre-mortem: „za 2 lata pozycja jest −50% — co się stało?”.

Prawdopodobieństwa scenariuszy zostają, bo silnik liczy z nich wartość oczekiwaną. Zapisujesz je w `scenariusze.json` i wstawiasz miejscem `{{scenariusz_prawdopodobienstwo.<nazwa>}}`.

## 4. Scenariusze

`D/scenariusze.json`:

```json
{"scenariusze": [
  {"nazwa": "byk", "prawdopodobienstwo": 0.25, "wzrost_przychodow": 0.12, "marza_fcf": 0.30,
   "uzasadnienie": "80.–90. percentyl stopy bazowej dla spółek tej wielkości; warunek: …"},
  {"nazwa": "bazowy", "prawdopodobienstwo": 0.50, "wzrost_przychodow": 0.08, "marza_fcf": 0.25, "uzasadnienie": "…"},
  {"nazwa": "niedzwiedz", "prawdopodobienstwo": 0.25, "wzrost_przychodow": 0.02, "marza_fcf": 0.18, "uzasadnienie": "…"}
]}
```

- Bazowy przy medianie stopy bazowej, byk przy 80.–90. percentylu, niedźwiedź przy 10.–20. percentylu (ze spadkiem marży; gdzie trzeba, gałąź emisji albo upadłości).
- Nie przyjmuj 25/50/25 bez uzasadnienia — to kotwica.
- Wzrost przychodów obowiązuje przez 10 lat, potem wzrost rezydualny i koszt kapitału z wyceny (te same co w wycenie odwrotnej).
- Silnik liczy: wartość na akcję w każdym scenariuszu, wartość oczekiwaną, potencjał wobec kursu, prawdopodobieństwo straty, asymetrię.

## 5. Wiadomości i konsensus

- Każdą wiadomość tłumacz na zmianę jednego czynnika wartości (wzrost, marża, koszt kapitału, rozwodnienie), z prawdopodobieństwem i terminem. Trzy zdarzenia pozytywne i trzy negatywne.
- Konsensus czytasz dopiero po własnej analizie. Przy każdej liczbie z konsensusu: dostawca, data, liczba analityków (przypis robi to sam). Analitycy zawyżają długoterminowy wzrost (średnio 14,7% prognozy wobec 9,1% faktycznie, 1984–2006). Cena docelowa to kontekst, nie wartość godziwa.
- Pokrycie poniżej 3 analityków: „pokrycie analityczne małe, nie można na nim polegać” (bramka `B0.pokrycie` robi to sama).

## 6. Margines bezpieczeństwa i wielkość pozycji

- Trzy warunki marginesu: wartość oczekiwana wyraźnie powyżej ceny; strata w scenariuszu pesymistycznym do przeżycia; oczekiwania w cenie przy medianie stopy bazowej albo niżej.
- Wielkość pozycji jak w karcie właściciela: „przy X% IKE scenariusz pesymistyczny zabiera Y% IKE” — X i Y są decyzją właściciela, więc opisujesz zasadę słownie. Transze zgodne z krokiem 5 frameworku (`inwestowanie/analiza/framework.md`).
