# Szablon raportu (`D/raport.md`)

Raport może być długi; na początku sekcja TL;DR. Piszesz po polsku, na „ty”, według sekcji „Język i styl” w `CLAUDE.md`. Wszystkie liczby wstawia silnik.

## Miejsca na liczby

- `{{id_faktu}}` — dowolny fakt z `fakty.json` (np. `{{przychody.TTM2026-09-30}}`, `{{marza_operacyjna.FY2025}}`, `{{kurs.2026-11-09}}`, `{{implikowany_wzrost_fcf.2026-11-09}}`, `{{scenariusz_prawdopodobienstwo.bazowy}}`). Listę id masz w `fakty.json` i w kolumnach `obliczenia.md`.
- `{{tabela:panel}}`, `{{tabela:wycena}}`, `{{tabela:scenariusze}}`, `{{tabela:karta}}`, `{{tabela:bramki}}`, `{{tabela:jakosc_danych}}`.
- `{{wykres:przychody}}`, `{{wykres:marze}}`, `{{wykres:fcf_zysk}}`, `{{wykres:roic}}`.

Lint przepuszcza bez miejsc tylko: lata (1990–2049; starsze z „r.”/„roku”), daty, etykiety okresów (FY2025, Q3, H1, M9, TTM), numerację nagłówków i list, nazwy typu S&P 500, MSSF 16, 10-K. Liczby słownie („dwa segmenty”, „około połowy”) są dozwolone, ale nie zastępuj nimi danych finansowych — te zawsze przez miejsce.

## Układ

```markdown
# <Nazwa> (<TICKER>) — wstępna analiza fundamentalna

Data analizy: <dd.mm.rrrr>. Rynek: <USA|GPW>. Instrument w XTB: <TICKER.US|TICKER.PL>. Decyzja bramek: <DALEJ|PAUZA — kontynuacja za zgodą>.

## TL;DR

> <3–5 zdań: czym zajmuje się spółka; teza i jej prawdopodobieństwo (słownie albo przez scenariusz); co jest w cenie (implikowany wzrost/CAP); największe ryzyko; wg twoich zasad: …>

- Przewaga konkurencyjna: <brak|wąska|szeroka>, trend <…>.
- Wycena: kapitalizacja {{kapitalizacja.<d>}}, C/Z {{c_z.<d>}}, FCF yield {{fcf_yield.<d>}}.
- Wartość oczekiwana ze scenariuszy: {{wartosc_oczekiwana_na_akcje.<d>}} przy kursie {{kurs.<d>}}; prawdopodobieństwo straty {{prawdopodobienstwo_straty.<d>}}.
- Karta w stylu Treli: <wynik słownie albo odesłanie do części 11>.
- Pokrycie analityczne: <…>.

## 1. Jak działa firma
## 2. Na czym zarabia
## 3. Najważniejsze fakty (akcjonariat, zarząd, płynność, kalendarz)
## 4. Branża, konkurencja i przewaga konkurencyjna
## 5. Zarząd i alokacja kapitału
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
## 9. Teza, antytezy, pre-mortem
## 10. Wiadomości i scenariusze
{{tabela:scenariusze}}
<byki mówią / niedźwiedzie mówią>
## 11. Karta w stylu Treli
{{tabela:karta}}
## 12. Dostęp przez IKE
<instrument, waluta, przewalutowanie 0,5% (słownie: pół procenta), podatek u źródła od dywidend, nakładanie się z ETF-ami właściciela>
## 13. Projekt karty
<teza w 3 zdaniach, co jest w cenie, antytezy z progami (słownie względem faktów), pre-mortem, wielkość pozycji, kiedy sprzedam, data przeglądu, co śledzić>
## 14. Jakość danych
{{tabela:jakosc_danych}}
<czego nie sprawdziłeś>
```

Uwaga do części 12: koszty i stawki podatku to liczby — opisz je słownie („pół procenta przy każdym przewalutowaniu”, „piętnaście procent podatku u źródła z formularzem W-8BEN”), bo nie ma ich w rejestrze.
