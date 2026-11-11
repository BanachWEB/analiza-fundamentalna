"""Karta punktowa w stylu Treli: pięć filarów, skala 0–10, suma ważona (konfiguracja/karta-treli.yaml).

Karta jest informacją, a nie bramką. Filar bez danych dostaje „brak danych”, a jego waga
przechodzi proporcjonalnie na pozostałe; raport pokazuje, z ilu filarów powstała karta.
Przy pokryciu analitycznym 3 analityków lub mniej (zasady właściciela v1.6) filar „analitycy” zawsze ma brak danych.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

from silnik.fakty.schemat import Fakt, Jednostka, Okres

from .kalkulator import Kalkulator

KONFIGURACJA = Path(__file__).resolve().parents[2] / "konfiguracja" / "karta-treli.yaml"


@dataclass
class Filar:
    nazwa: str
    waga: float
    punkty: Optional[float]
    miary: dict = field(default_factory=dict)  # miara → (id faktu, wartość, punkty) albo None


def punkty(wartosc: float, zero: float, dziesiec: float) -> float:
    t = (wartosc - zero) / (dziesiec - zero)
    return max(0.0, min(10.0, 10 * t))


BEZ_STARSZYCH_LAT = {"dlug_netto_do_ebitda", "dlug_netto_z_leasingiem_do_ebitda"}


def _ostatnia(k: Kalkulator, pozycja: str, preferowany: Optional[str]) -> Optional[Fakt]:
    if preferowany and k.jest(f"{pozycja}.{preferowany}"):
        return k.fakt(f"{pozycja}.{preferowany}")
    fy = k.okresy_fy(pozycja)
    if fy:
        # Dług netto ÷ EBITDA nie powstaje przy EBITDA ≤ 0; wtedy starszy rok dałby punkty
        # za nieaktualny stan spółki. Dla innych miar zostaje dotychczasowa zasada (ostatni rok z wartością).
        lata = k.okresy_fy()
        if pozycja in BEZ_STARSZYCH_LAT and lata and fy[-1].okres.koniec < lata[-1].okres.koniec:
            return None
        return fy[-1]
    stany = [f for f in k.r.fakty() if f.pozycja == pozycja and f.okres.typ.value == "dzien"]
    return max(stany, key=lambda f: f.okres.koniec) if stany else None


def oblicz(k: Kalkulator, rynek: str, wycena: dict, ttm_sufiks: Optional[str], liczba_analitykow: Optional[int],
           finansowa: bool = False) -> list[Filar]:
    pelna = yaml.safe_load(KONFIGURACJA.read_text(encoding="utf-8"))
    cfg = pelna["filary"]
    if finansowa:  # banki, ubezpieczyciele, brokerzy: marża, FCF, dług netto i Z'' nie działają
        cfg = {**cfg, "jakosc": {**cfg["jakosc"], "miary": pelna["jakosc_finansowe"]},
               "wycena": {**cfg["wycena"], "miary": pelna["wycena_finansowe"]}}
    D = k.fakt(wycena["kapitalizacja"]).okres.koniec if wycena.get("kapitalizacja") else None
    d = D.isoformat() if D else None

    # miary złożone jako fakty wyliczone
    if wycena.get("implikowany_wzrost_fcf") and wycena.get("wzrost_historyczny"):
        k.wylicz(f"nadwyzka_wzrostu.{d}", "nadwyzka_wzrostu", "CAGR przychodów historyczny − implikowany wzrost FCF",
                 [wycena["wzrost_historyczny"], wycena["implikowany_wzrost_fcf"]], lambda h, i: h - i,
                 Jednostka.ulamek, Okres(typ="dzien", koniec=D))
    cel = [f for f in k.r.fakty() if f.pozycja == "cena_docelowa_srednia" and f.status.value != "odrzucony"]
    kursy = [f for f in k.r.fakty() if f.pozycja == "kurs"]
    if cel and kursy:
        c, ku = max(cel, key=lambda f: f.okres.koniec), max(kursy, key=lambda f: f.okres.koniec)
        k.wylicz(f"potencjal_do_ceny_docelowej.{ku.okres.koniec.isoformat()}", "potencjal_do_ceny_docelowej",
                 "cena_docelowa_srednia / kurs − 1", [c.id, ku.id], lambda a, b: a / b - 1, Jednostka.ulamek,
                 Okres(typ="dzien", koniec=ku.okres.koniec))
    mom = [f for f in k.r.fakty() if f.pozycja == "momentum_12_1"]
    mom_i = [f for f in k.r.fakty() if f.pozycja == "indeks_momentum_12_1"]
    if mom and mom_i:
        a, b = max(mom, key=lambda f: f.okres.koniec), max(mom_i, key=lambda f: f.okres.koniec)
        k.wylicz(f"nadwyzka_momentum.{a.okres.koniec.isoformat()}", "nadwyzka_momentum", "momentum_12_1 − indeks_momentum_12_1",
                 [a.id, b.id], lambda x, y: x - y, Jednostka.ulamek, Okres(typ="dzien", koniec=a.okres.koniec))

    filary = []
    for nazwa, f_cfg in cfg.items():
        filar = Filar(nazwa, f_cfg["waga"], None)
        wyniki = []
        for miara, progi in f_cfg["miary"].items():
            if nazwa == "analitycy" and (liczba_analitykow is None or liczba_analitykow <= 3):
                filar.miary[miara] = None
                continue
            pref = d if miara in ("fcf_yield", "ev_ebit", "nadwyzka_wzrostu", "potencjal_do_ceny_docelowej") else ttm_sufiks
            if miara == "potencjal_trela_kons":  # fakt z datą odczytu Scrab (scrab.yaml), nie z datą kursu
                pref = None
            fakt = _ostatnia(k, miara, pref)
            if fakt is None:
                filar.miary[miara] = None
                continue
            p = progi[rynek]
            pkt = punkty(fakt.wartosc_bazowa(), p["zero"], p["dziesiec"])
            filar.miary[miara] = (fakt.id, fakt.wartosc_bazowa(), pkt)
            wyniki.append(pkt)
        filar.punkty = sum(wyniki) / len(wyniki) if wyniki else None
        filary.append(filar)
    return filary


MIN_FILAROW = 3  # karta z mniejszej liczby filarów wprowadza w błąd


def wynik_ogolny(filary: list[Filar]) -> tuple[Optional[float], int]:
    dostepne = [f for f in filary if f.punkty is not None]
    if len(dostepne) < MIN_FILAROW:
        return None, len(dostepne)
    suma_wag = sum(f.waga for f in dostepne)
    return sum(f.punkty * f.waga / suma_wag for f in dostepne), len(dostepne)
