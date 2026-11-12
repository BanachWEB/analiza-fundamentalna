# Szablon raportu (`D/raport.md`)

Raport może być długi; na początku sekcja TL;DR. Piszesz po polsku, na „ty”, według sekcji „Język i styl” w `CLAUDE.md`. Wszystkie liczby wstawia silnik.

## Miejsca na liczby

- `{{id_faktu}}` — dowolny fakt z `fakty.json` (np. `{{przychody.TTM2026-09-30}}`, `{{marza_operacyjna.FY2025}}`, `{{kurs.2026-11-09}}`, `{{implikowany_wzrost_fcf.2026-11-09}}`, `{{scenariusz_prawdopodobienstwo.bazowy}}`). Listę id masz w `fakty.json` i w kolumnach `obliczenia.md`.
- `{{tabela:panel}}`, `{{tabela:wycena}}`, `{{tabela:pasma}}`, `{{tabela:ryzyko}}`, `{{tabela:scenariusze}}`, `{{tabela:wrazliwosc}}`, `{{tabela:konkurenci}}`, `{{tabela:karta}}`, `{{tabela:bramki}}`, `{{tabela:jakosc_danych}}`. Tabela bez danych (np. brak konkurentów) renderuje się jako krótka informacja o braku.
- `{{wykres:przychody}}`, `{{wykres:marze}}`, `{{wykres:fcf_zysk}}`, `{{wykres:roic}}`.

Lint przepuszcza bez miejsc tylko: lata (1990–2049; starsze z „r.”/„roku”), daty, etykiety okresów (FY2025, Q3, H1, M9, TTM), numerację nagłówków i list, nazwy typu S&P 500, MSSF 16, 10-K. Liczby słownie („dwa segmenty”, „około połowy”) są dozwolone, ale nie zastępuj nimi danych finansowych — te zawsze przez miejsce.

## Układ

```markdown
# <Nazwa> (<TICKER>) — wstępna analiza fundamentalna

Data analizy: <dd.mm.rrrr>. Rynek: <USA|GPW>. Typ spółki: <ogólny|cykliczny|finanse|deweloper>. Decyzja bramek: <DALEJ|PAUZA — kontynuacja za zgodą>.

## TL;DR

> <3–5 zdań: czym zajmuje się spółka; teza i stan jej warunków koniecznych (ile potwierdzają dokumenty, ile zostaje do sprawdzenia); co jest w cenie (implikowany wzrost/CAP albo ROE implikowane); największe ryzyko; wg twoich zasad: …>

- Przewaga konkurencyjna: <brak|wąska|szeroka>, trend <…>.
- Wycena: kapitalizacja {{kapitalizacja.<d>}}, C/Z {{c_z.<d>}}, FCF yield {{fcf_yield.<d>}}.
- Wartość oczekiwana ze scenariuszy: {{wartosc_oczekiwana_na_akcje.<d>}} przy kursie {{kurs.<d>}}; prawdopodobieństwo straty {{prawdopodobienstwo_straty.<d>}}.
- Karta w stylu Treli: <wynik słownie albo odesłanie do części 11>.
- Pokrycie analityczne: <…>.

## 1. Jak działa firma
## 2. Na czym zarabia
## 3. Najważniejsze fakty (akcjonariat, zarząd, płynność, kalendarz)
## 4. Branża, konkurencja i przewaga konkurencyjna
{{tabela:konkurenci}}
<pozycja spółki wobec mediany konkurentów: marże, wzrost r/r, ROIC, mnożniki>
## 5. Zarząd i alokacja kapitału
<jedno zdanie o dywidendach i skupie akcji: {{stopa_zwrotu_akcjonariuszy.<d>}}, {{stopa_dywidendy.<d>}}; bez omawiania podatków i IKE>
## 6. Sprawozdania finansowe
{{tabela:panel}}
{{wykres:przychody}}
{{wykres:marze}}
{{wykres:fcf_zysk}}
<omówienie: wzrost, marże, jakość zysków (FCF a zysk netto), zadłużenie, rozwodnienie>
## 7. Jakość zysków i czerwone flagi
{{tabela:bramki}}
## 8. Co jest w cenie
{{tabela:wycena}}
{{tabela:pasma}}
<dzisiejsze mnożniki na tle percentyli z historii spółki; bez przeliczania na kursy>
{{tabela:ryzyko}}
<beta, zmienność, obsunięcie i korelacja wobec benchmarku; bez porównania z portfelem>
{{tabela:cena_docelowa_trela}}
<tylko gdy jest D/cena-docelowa.xlsx: „wg twojego arkusza: …” — co zakłada powrót mnożnika do mediany albo maksimum, jak ta cena ma się do wyceny odwrotnej; bez słów „kupuj” i „sprzedawaj”; bez pliku nie pisz o cenie docelowej z arkusza>
## 9. Teza, warunki konieczne, antytezy, pre-mortem
<teza bez prawdopodobieństwa; 3–5 warunków koniecznych, przy każdym: potwierdzony (doc-…), sprzeczny (doc-…) albo do sprawdzenia (gdzie)>
## 10. Wiadomości i scenariusze
{{tabela:scenariusze}}
{{tabela:wrazliwosc}}
<byki mówią / niedźwiedzie mówią>
## 11. Karta w stylu Treli
{{tabela:karta}}
<komentarz tylko wtedy, gdy obliczenia.md oznacza rozbieżność karty z wynikiem Scrab; inaczej sama tabela>
## 12. Do dalszej analizy
<otwarte pytania z D/notatki-biznes.md (sekcja „Pytania bez odpowiedzi”), każde ze źródłem do sprawdzenia; założenie, które najmocniej zmienia wycenę (z tabeli wrażliwości); kalendarz zdarzeń z datami i dokumentem; progi zmiany tezy z antytez>
## 13. Projekt karty
<teza w 3 zdaniach, co jest w cenie, antytezy z progami (słownie względem faktów), pre-mortem, wielkość pozycji, kiedy sprzedam, data przeglądu, co śledzić>
## 14. Jakość danych
{{tabela:jakosc_danych}}
<czego nie sprawdziłeś>
<jeśli był materiał od właściciela: tropy z D/tropy.md i wynik każdego (potwierdzony dokumentem, sprzeczny, niepotwierdzony, niesprawdzony); liczby z materiału tylko przez miejsca {{…}}>
```

