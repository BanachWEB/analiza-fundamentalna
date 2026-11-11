"""Konsensus analityków dla USA ze strony prognoz Stock Analysis (dane S&P Global).

Strona podaje za darmo: liczbę analityków, średnią cenę docelową, konsensus EPS na bieżący rok
obrotowy (z dynamiką) i konsensus przychodów na ten rok. Rewizji prognoz z 90 dni nie ma; dla GPW konsensus przychodzi
z wklejki z InvestingPro (propozycje z testem cytatu).
"""

from __future__ import annotations

import re
from datetime import date
from typing import Optional

from silnik.fakty.schemat import Fakt, Jednostka, Metoda, Okres, Rodzaj, Status, TypDokumentu
from silnik.pobieranie.archiwum import Archiwum
from silnik.pobieranie.http import pobierz

DOSTAWCA = "S&P Global (przez Stock Analysis)"


def url(ticker: str) -> str:
    return f"https://stockanalysis.com/stocks/{ticker.lower()}/forecast/"


def parsuj(tresc: str) -> dict:
    wynik = {}
    m = re.search(r"According to (\d+) analysts? polled by S&amp;P Global.*?average price target of \$([\d,]+(?:\.\d+)?)", tresc)
    if m:
        wynik["liczba_analitykow"] = int(m.group(1))
        wynik["cena_docelowa"] = float(m.group(2).replace(",", ""))
        wynik["cytat"] = re.sub(r"&amp;", "&", tresc[m.start():m.end()])
    m = re.search(r"epsThis:\{last:([-\d.]+),this:([-\d.]+),growth:([-\d.]+)\}", tresc)
    if m:
        wynik["eps_konsensus"] = float(m.group(2))
        wynik["wzrost_eps_konsensus"] = float(m.group(3)) / 100
    # średni konsensus przychodów na pierwszy rok obrotowy z prognozą (pierwszy wpis tabeli „revenue”)
    m = re.search(r'revenue:\{"(\d{4}-\d{2}-\d{2})":\{no:(\d+),avg:([-\d.e+]+)', tresc)
    if m:
        wynik["przychody_konsensus"] = (date.fromisoformat(m.group(1)), int(m.group(2)), float(m.group(3)))
    return wynik


def fakty(archiwum: Archiwum, ticker: str, dzien: date) -> list[Fakt]:
    adres = url(ticker)
    dok = archiwum.po_adresie(adres)
    if dok is None:
        plik = pobierz(adres, rozszerzenie=".html")
        try:
            dok = archiwum.dodaj_plik(plik, TypDokumentu.strona, "Stock Analysis", adres=adres, opis="prognozy analityków")
        finally:
            plik.unlink(missing_ok=True)
    d = parsuj(archiwum.tekst(dok.id))
    if "liczba_analitykow" not in d:
        return []
    okres = Okres(typ="dzien", koniec=dzien)
    n = d["liczba_analitykow"]
    wspolne = dict(okres=okres, status=Status.jedno_zrodlo, dokument=dok.id)
    wynik = [
        Fakt(id=f"liczba_analitykow.{dzien.isoformat()}", rodzaj=Rodzaj.raportowany, pozycja="liczba_analitykow",
             wartosc=n, jednostka=Jednostka.liczba, metoda=Metoda.parser_strony, miejsce={"tekst": d["cytat"][:200]}, **wspolne),
        Fakt(id=f"cena_docelowa_srednia.{dzien.isoformat()}", rodzaj=Rodzaj.prognoza, pozycja="cena_docelowa_srednia",
             wartosc=d["cena_docelowa"], jednostka=Jednostka.pieniadz_na_akcje, waluta="USD", metoda=Metoda.parser_strony,
             dostawca=DOSTAWCA, data_prognozy=dzien, liczba_analitykow=n, miejsce={"tekst": d["cytat"][:200]}, **wspolne),
    ]
    if "wzrost_eps_konsensus" in d:
        wynik.append(Fakt(id=f"wzrost_eps_konsensus.{dzien.isoformat()}", rodzaj=Rodzaj.prognoza, pozycja="wzrost_eps_konsensus",
                          wartosc=d["wzrost_eps_konsensus"], jednostka=Jednostka.ulamek, metoda=Metoda.parser_strony,
                          dostawca=DOSTAWCA, data_prognozy=dzien, liczba_analitykow=n,
                          miejsce={"pole": "epsThis.growth (bieżący rok obrotowy)"}, **wspolne))
    if "przychody_konsensus" in d:
        koniec, n_przych, wartosc = d["przychody_konsensus"]
        wynik.append(Fakt(id=f"przychody_konsensus.{koniec.isoformat()}", rodzaj=Rodzaj.prognoza,
                          pozycja="przychody_konsensus", okres=Okres(typ="FY", koniec=koniec), status=Status.jedno_zrodlo,
                          dokument=dok.id, wartosc=wartosc, jednostka=Jednostka.pieniadz, waluta="USD",
                          metoda=Metoda.parser_strony, dostawca=DOSTAWCA, data_prognozy=dzien, liczba_analitykow=n_przych,
                          miejsce={"pole": f"revenue[{koniec.isoformat()}].avg (rok obrotowy z prognozą)"}))
    return wynik
