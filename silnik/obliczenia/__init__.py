"""Obliczenia na rejestrze faktów: okresy pochodne, wskaźniki, jakość, wycena, scenariusze, cena docelowa wg arkusza
właściciela, karta Treli."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from silnik.fakty.rejestr import RejestrFaktow

from . import aktualnosc, jakosc, karta_treli, okresy, pasma, scenariusze, trela, wskazniki, wycena
from .kalkulator import Kalkulator
from .raport import obliczenia_md


def rynek_z_waluty(rejestr: RejestrFaktow) -> str:
    waluty = {f.waluta for f in rejestr.fakty() if f.pozycja == "przychody" and f.waluta}
    return "GPW" if "PLN" in waluty else "USA"


def sektor(katalog: Optional[Path]) -> str:
    """Typ spółki z analiza.json (zapisuje go model na etapie 0): ogolny, cykliczny, finanse albo deweloper.
    „finanse” wyłącza miary, które dla banków nie działają; typ wybiera też metodę wyceny (wycena.oblicz)."""
    if katalog and (katalog / "analiza.json").exists():
        return json.loads((katalog / "analiza.json").read_text(encoding="utf-8")).get("sektor", "ogolny")
    return "ogolny"


def dodaj_propozycje_jesli_sa(rejestr: RejestrFaktow, katalog: Optional[Path]) -> None:
    """Propozycje modelu (PDF, wklejka z InvestingPro): nowe i wcześniej odrzucone."""
    if not katalog or not (katalog / "propozycje.json").exists():
        return
    from silnik.fakty.cytat import dodaj_propozycje, wczytaj_propozycje
    from silnik.pobieranie.archiwum import Archiwum

    from silnik.fakty.schemat import Status

    # nowe propozycje oraz wcześniej odrzucone (model mógł poprawić cytat albo wartość, albo silnik test)
    nowe = [p for p in wczytaj_propozycje(katalog / "propozycje.json")
            if p["id"] not in rejestr or rejestr[p["id"]].status == Status.odrzucony]
    if nowe:
        archiwum = Archiwum(rejestr.ticker, katalog)
        rejestr.znane_dokumenty(archiwum.ids())
        dodaj_propozycje(rejestr, archiwum.sciezka, nowe)


def uruchom(rejestr: RejestrFaktow, katalog: Optional[Path] = None, rynek: Optional[str] = None):
    rynek = rynek or rynek_z_waluty(rejestr)
    typ = sektor(katalog)
    finansowa = typ == "finanse"
    kapitalowa = typ in wycena.KAPITALOWE
    dodaj_propozycje_jesli_sa(rejestr, katalog)
    k = Kalkulator(rejestr)
    okresy.uzupelnij_skladniki(k)
    okresy.dodaj_kwartaly(k)
    koniec = okresy.dodaj_ttm(k)
    wskazniki.oblicz(k, koniec)
    if not finansowa:
        jakosc.oblicz(k)
    w = wycena.oblicz(k, koniec, rynek, sektor=typ)
    sc = scenariusze.oblicz(k, katalog / "scenariusze.json", w) if katalog else None
    wr = scenariusze.wrazliwosc(k, katalog / "scenariusze.json", w) if katalog and sc else None
    ps = pasma.oblicz(k, katalog, w)
    tr = trela.oblicz(k, katalog, rynek)  # przed kartą: potencjał konserwatywny to miara filaru „wycena”
    aktualnosc.sprawdz(k, tr, w)
    analitycy = [f for f in rejestr.fakty() if f.pozycja == "liczba_analitykow"]
    liczba = int(max(analitycy, key=lambda f: f.okres.koniec or f.id).wartosc) if analitycy else None
    karta = karta_treli.oblicz(k, rynek, w, w.get("okres_bazowy"), liczba, kapitalowa) if w.get("kapitalizacja") else []
    scrab = karta_treli.porownanie_scrab(k, karta) if karta else None
    return k, {"ttm": koniec, "rynek": rynek, "wycena": w, "scenariusze": sc, "trela": tr, "karta": karta, "analitycy": liczba,
               "scrab": scrab, "wrazliwosc": wr, "pasma": ps,
               "sektor": typ}


def uruchom_w_katalogu(katalog: Path, rynek: Optional[str] = None) -> Path:
    dokumenty = [d["id"] for d in json.loads((katalog / "dokumenty.json").read_text(encoding="utf-8"))["dokumenty"]]
    rejestr = RejestrFaktow.z_pliku(katalog / "fakty.json", dokumenty)
    k, wynik = uruchom(rejestr, katalog, rynek)
    rejestr.do_pliku(katalog / "fakty.json")
    (katalog / "obliczenia.md").write_text(obliczenia_md(k, wynik), encoding="utf-8")
    return katalog / "obliczenia.md"
