"""Obliczenia na rejestrze faktów: okresy pochodne, wskaźniki, jakość zysków."""

from __future__ import annotations

from pathlib import Path

from silnik.fakty.rejestr import RejestrFaktow

from . import jakosc, okresy, wskazniki
from .kalkulator import Kalkulator
from .raport import obliczenia_md


def uruchom(rejestr: RejestrFaktow) -> tuple[Kalkulator, object]:
    k = Kalkulator(rejestr)
    okresy.uzupelnij_skladniki(k)
    okresy.dodaj_kwartaly(k)
    koniec = okresy.dodaj_ttm(k)
    wskazniki.oblicz(k, koniec)
    jakosc.oblicz(k)
    return k, koniec


def uruchom_w_katalogu(katalog: Path) -> Path:
    import json

    dokumenty = [d["id"] for d in json.loads((katalog / "dokumenty.json").read_text(encoding="utf-8"))["dokumenty"]]
    rejestr = RejestrFaktow.z_pliku(katalog / "fakty.json", dokumenty)
    k, koniec = uruchom(rejestr)
    rejestr.do_pliku(katalog / "fakty.json")
    (katalog / "obliczenia.md").write_text(obliczenia_md(k, koniec), encoding="utf-8")
    return katalog / "obliczenia.md"
