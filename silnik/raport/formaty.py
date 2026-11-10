"""Formatowanie liczb z rejestru po polsku: wartość, okres, źródło (do przypisu)."""

from __future__ import annotations

from datetime import date

from silnik.fakty.schemat import Fakt, Jednostka, Status

MIESIACE = ["", "stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca", "lipca", "sierpnia", "września",
            "października", "listopada", "grudnia"]


def _pl(x: float, miejsca: int) -> str:
    s = f"{x:,.{miejsca}f}"
    return s.replace(",", " ").replace(".", ",").replace(" ", " ")


def kwota(v: float, waluta: str) -> str:
    a = abs(v)
    if a >= 1e12:
        s = f"{_pl(v / 1e12, 2)} bln"
    elif a >= 1e9:
        s = f"{_pl(v / 1e9, 1)} mld"
    elif a >= 1e6:
        s = f"{_pl(v / 1e6, 1)} mln"
    elif a >= 1e4:
        s = f"{_pl(v / 1e3, 1)} tys."
    else:
        s = _pl(v, 0)
    return f"{s} {waluta}"


def wartosc(f: Fakt) -> str:
    v = f.wartosc_bazowa()
    j = f.jednostka
    if j == Jednostka.pieniadz:
        return kwota(v, f.waluta or "")
    if j == Jednostka.pieniadz_na_akcje:
        return f"{_pl(v, 2)} {f.waluta}"
    if j == Jednostka.ulamek:
        return f"{_pl(v * 100, 1)}%"
    if j == Jednostka.mnoznik:
        return f"{_pl(v, 1)}×"
    if j == Jednostka.punkty:
        return _pl(v, 2)
    if j == Jednostka.akcje:
        return f"{_pl(v / 1e6, 1)} mln akcji" if v >= 1e6 else f"{_pl(v, 0)} akcji"
    if j == Jednostka.lata:
        return f"{_pl(v, 1)} lat"
    if j == Jednostka.dni:
        return f"{_pl(v, 0)} dni"
    return _pl(v, 0) if abs(v - round(v)) < 1e-9 else _pl(v, 2)


def data_pl(d: date) -> str:
    return d.strftime("%d.%m.%Y")


def okres(f: Fakt) -> str:
    o = f.okres
    t = o.typ.value
    sufiks = f.id.split(".", 1)[1] if "." in f.id else ""
    if t == "FY":
        return f"rok obrotowy {sufiks.replace('FY', '')} (do {data_pl(o.koniec)})" if sufiks.startswith("FY") else f"rok do {data_pl(o.koniec)}"
    if t == "TTM":
        return f"ostatnie 12 miesięcy do {data_pl(o.koniec)}"
    if t == "dzien":
        return f"na {data_pl(o.koniec)}"
    if t in ("Q1", "Q2", "Q3", "Q4"):
        return f"{t} ({data_pl(o.poczatek)}–{data_pl(o.koniec)})"
    if t == "H1":
        return f"półrocze do {data_pl(o.koniec)}"
    if t == "M9":
        return f"9 miesięcy do {data_pl(o.koniec)}"
    return "założenie"


STATUS = {
    Status.zweryfikowany: "zweryfikowany",
    Status.jedno_zrodlo: "jedno źródło",
    Status.konflikt: "KONFLIKT źródeł",
    Status.odrzucony: "odrzucony",
}
