# Styl Tomasza Treli, karta punktowa i Scrab

Źródło: raport z badania, część 7.

## Styl

- Horyzont długi („kolejnych 100 lat”), „dobre akcje, solidne biznesy, dobre perspektywy”, gra zgodnie z trendem.
- Dane, które da się zweryfikować, zamiast opinii; analitycy o sprawdzonej skuteczności.
- Kryteria (forum, 2022): ponadprzeciętny wzrost przychodów i zysków, rosnące przepływy operacyjne, niskie zadłużenie, zdrowe fundamenty, atrakcyjna wycena, potencjał do cen docelowych, pozytywne rewizje prognoz.
- Model punktowy: wzrost (najcięższy), wycena, stabilność finansowa, momentum, prognozy analityków; punkty liniowo między progami.
- Jego czerwone flagi: przepływy operacyjne poniżej zysku netto przez kilka lat, rosnący albo drogi dług, ryzyko upadłości, wzrost z bazy bliskiej zera.
- Ograniczenia: jedyne wyniki to jego backtesty; Trela pobiera prowizję od abonamentów Scrab. Próg 5 mld USD i wykluczenie spółek z małą liczbą analityków odcinają prawie całą GPW — dla GPW karta jest adaptacją. Przedstawiaj metodę Treli jako ramę, nie jako udowodnioną przewagę.

## Karta punktowa w skillu

Liczy ją silnik (`konfiguracja/karta-treli.yaml`): wzrost 30%, jakość i stabilność 25%, wycena 20%, analitycy 15%, momentum 10%; progi osobne dla USA i GPW. Filar bez danych przekazuje wagę pozostałym. Wagi i progi to propozycja zatwierdzona przez właściciela, nie publikowana metoda Treli. Karta jest informacją, nie bramką. W raporcie: `{{tabela:karta}}`.

## Cena docelowa z arkusza właściciela

Właściciel liczy ją w swoim arkuszu (metoda Treli, dane ze Scrab) i czasem dołącza plik. Silnik tylko odczytuje wyniki (`specyfikacja.md`, punkt 7.1). W raporcie: `{{tabela:cena_docelowa_trela}}` w części 8, opisana jako „wg twojego arkusza”. Bez pliku tabela jest pusta, a ty nie piszesz o tej cenie.

## Podział pracy ze Scrab

1. Właściciel: sito w Scrab (osobne progi dla USA i GPW), szybki przegląd, krótka lista.
2. Właściciel: wklejka z Scrab, TipRanks albo InvestingPro (wynik punktowy, konsensus, liczby) — opcjonalnie. To tropy i dane wyjściowe, nie źródło prawdy (`specyfikacja.md`, punkt 3.3, „Materiały od właściciela”).
3. Skill: pogłębiona analiza jednej spółki, bramki, PDF.
4. Skill: gdy właściciel wkleił wynik Scrab, porównaj go z kartą skilla; duża rozbieżność często ujawnia błąd danych — napisz o tym.
5. Właściciel: decyzja i karta w `inwestowanie/spolki/<TICKER>.md`.
