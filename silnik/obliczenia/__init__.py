"""Obliczenia na rejestrze faktów: okresy pochodne, wskaźniki, jakość, wycena, scenariusze, karta Treli."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from silnik.fakty.rejestr import RejestrFaktow

from . import jakosc, karta_treli, okresy, scenariusze, wskazniki, wycena
from .kalkulator import Kalkulator
from .raport import obliczenia_md


def rynek_z_waluty(rejestr: RejestrFaktow) -> str:
    waluty = {f.waluta for f in rejestr.fakty() if f.pozycja == "przychody" and f.waluta}
    return "GPW" if "PLN" in waluty else "USA"


def uruchom(rejestr: RejestrFaktow, katalog: Optional[Path] = None, rynek: Optional[str] = None):
    rynek = rynek or rynek_z_waluty(rejestr)
    k = Kalkulator(rejestr)
    okresy.uzupelnij_skladniki(k)
    okresy.dodaj_kwartaly(k)
    koniec = okresy.dodaj_ttm(k)
    wskazniki.oblicz(k, koniec)
    jakosc.oblicz(k)
    w = wycena.oblicz(k, koniec, rynek)
    sc = scenariusze.oblicz(k, katalog / "scenariusze.json", w) if katalog else None
    analitycy = [f for f in rejestr.fakty() if f.pozycja == "liczba_analitykow"]
    liczba = int(max(analitycy, key=lambda f: f.okres.koniec or f.id).wartosc) if analitycy else None
    karta = karta_treli.oblicz(k, rynek, w, w.get("okres_bazowy"), liczba) if w.get("kapitalizacja") else []
    return k, {"ttm": koniec, "rynek": rynek, "wycena": w, "scenariusze": sc, "karta": karta, "analitycy": liczba}


def uruchom_w_katalogu(katalog: Path, rynek: Optional[str] = None) -> Path:
    dokumenty = [d["id"] for d in json.loads((katalog / "dokumenty.json").read_text(encoding="utf-8"))["dokumenty"]]
    rejestr = RejestrFaktow.z_pliku(katalog / "fakty.json", dokumenty)
    k, wynik = uruchom(rejestr, katalog, rynek)
    rejestr.do_pliku(katalog / "fakty.json")
    (katalog / "obliczenia.md").write_text(obliczenia_md(k, wynik), encoding="utf-8")
    return katalog / "obliczenia.md"
