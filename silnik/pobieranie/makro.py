"""Dane makro do Ohlson O-score: deflator PKB USA (FRED) i kurs USD/PLN (NBP).

Ohlson (1980) liczy wielkość spółki jako log(aktywa / indeks cen), gdzie indeks ma
wartość 100 w 1968 r., a jego rok to rok poprzedzający datę bilansu. Silnik bierze
kwartalny deflator PKB USA (seria GDPDEF z FRED) i zapisuje w rejestrze surowe
wartości kwartalne. Średnie roczne i przeliczenie na bazę 1968 liczy kod obliczeń.

Dla spółek z GPW aktywa trzeba przeliczyć na dolary: kurs średni NBP (tabela A)
z dnia bilansu albo z ostatniego dnia notowań przed nim.
"""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta

from silnik.fakty.schemat import Fakt, Jednostka, Metoda, Okres, Rodzaj, Status, TypDokumentu
from silnik.pobieranie.archiwum import Archiwum
from silnik.pobieranie.http import pobierz

URL_DEFLATOR = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=GDPDEF"
URL_NBP = "https://api.nbp.pl/api/exchangerates/rates/a/usd/{od}/{do}/?format=json"
ROK_BAZOWY = 1968


class BladMakro(ValueError):
    pass


def koniec_kwartalu(poczatek: date) -> date:
    """FRED datuje kwartał pierwszym dniem; rejestr trzyma koniec kwartału."""
    m = poczatek.month + 2
    nastepny = date(poczatek.year + (m // 12), m % 12 + 1, 1)
    return nastepny - timedelta(days=1)


def kwartaly_roku(rok: int) -> list[date]:
    return [koniec_kwartalu(date(rok, m, 1)) for m in (1, 4, 7, 10)]


def deflator_fred(tresc: str) -> dict[date, float]:
    """CSV z FRED: observation_date,GDPDEF → {koniec kwartału: wartość}."""
    wynik = {}
    linie = [l.strip() for l in tresc.strip().splitlines() if l.strip()]
    if not linie or "GDPDEF" not in linie[0]:
        raise BladMakro("FRED: brak kolumny GDPDEF")
    for l in linie[1:]:
        d, v = l.split(",")[:2]
        if v in ("", "."):
            continue
        wynik[koniec_kwartalu(datetime.strptime(d, "%Y-%m-%d").date())] = float(v)
    return wynik


def kurs_nbp(tresc: str) -> tuple[date, float, str]:
    """Ostatni kurs z odpowiedzi NBP: (dzień, PLN za 1 USD, numer tabeli)."""
    dane = json.loads(tresc)
    kursy = dane.get("rates") or []
    if not kursy:
        raise BladMakro("NBP: brak kursów w odpowiedzi")
    ost = kursy[-1]
    return datetime.strptime(ost["effectiveDate"], "%Y-%m-%d").date(), float(ost["mid"]), ost["no"]


def _do_archiwum(archiwum: Archiwum, url: str, zrodlo: str, opis: str, rozszerzenie: str):
    dok = archiwum.po_adresie(url)
    if dok:
        return dok
    plik = pobierz(url, rozszerzenie=rozszerzenie)
    try:
        return archiwum.dodaj_plik(plik, TypDokumentu.strona, zrodlo, adres=url, opis=opis)
    finally:
        plik.unlink(missing_ok=True)


def fakty_deflatora(archiwum: Archiwum, dni_bilansu: list[date]) -> list[Fakt]:
    """Kwartały 1968 r. i kwartały roku poprzedzającego każdy bilans."""
    dok = _do_archiwum(archiwum, URL_DEFLATOR, "FRED (St. Louis Fed)", "deflator PKB USA (GDPDEF)", ".csv")
    seria = deflator_fred(archiwum.tekst(dok.id))
    potrzebne = set(kwartaly_roku(ROK_BAZOWY))
    for b in dni_bilansu:
        potrzebne.update(kwartaly_roku(b.year - 1))
    wynik = []
    for kw in sorted(potrzebne):
        if kw not in seria:
            continue  # brak kwartału → obliczenie zapisze brak
        wynik.append(Fakt(id=f"deflator_pkb_usa.{kw.isoformat()}", rodzaj=Rodzaj.raportowany, pozycja="deflator_pkb_usa",
                          okres=Okres(typ="dzien", koniec=kw), wartosc=seria[kw], jednostka=Jednostka.punkty,
                          metoda=Metoda.api, status=Status.jedno_zrodlo, dokument=dok.id,
                          miejsce={"seria": "GDPDEF", "kwartał od": kw.replace(day=1, month=kw.month - 2).isoformat(),
                                   "znaczenie": "średnia kwartalna, 2017 = 100"}))
    return wynik


def fakty_kursu_usd_pln(archiwum: Archiwum, dni_bilansu: list[date], dni_wstecz: int = 10) -> list[Fakt]:
    """Kurs średni NBP na dzień bilansu albo ostatni przed nim (święta, weekendy)."""
    wynik = []
    for b in sorted(set(dni_bilansu)):
        url = URL_NBP.format(od=(b - timedelta(days=dni_wstecz)).isoformat(), do=b.isoformat())
        dok = _do_archiwum(archiwum, url, "NBP", f"kurs średni USD (tabela A) do {b.isoformat()}", ".json")
        dz, kurs, tabela = kurs_nbp(archiwum.tekst(dok.id))
        wynik.append(Fakt(id=f"kurs_usd_pln.{dz.isoformat()}", rodzaj=Rodzaj.raportowany, pozycja="kurs_usd_pln",
                          okres=Okres(typ="dzien", koniec=dz), wartosc=kurs, jednostka=Jednostka.mnoznik,
                          metoda=Metoda.api, status=Status.jedno_zrodlo, dokument=dok.id,
                          miejsce={"tabela": tabela, "pole": "mid", "znaczenie": "PLN za 1 USD"}))
    return wynik


def fakty(archiwum: Archiwum, dni_bilansu: list[date], waluta: str) -> list[Fakt]:
    wynik = fakty_deflatora(archiwum, dni_bilansu)
    if waluta == "PLN":
        wynik += fakty_kursu_usd_pln(archiwum, dni_bilansu)
    return wynik
