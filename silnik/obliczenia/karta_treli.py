"""Karta punktowa w stylu Treli: pięć filarów, skala 0–10, suma ważona (konfiguracja/karta-treli.yaml).

Karta jest informacją, a nie bramką. Filar bez danych dostaje „brak danych”, a jego waga
przechodzi proporcjonalnie na pozostałe; raport pokazuje, z ilu filarów powstała karta.
Przy pokryciu analitycznym poniżej 3 analityków filar „analitycy” zawsze ma brak danych.
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


def _ostatnia(k: Kalkulator, pozycja: str, preferowany: Optional[str]) -> Optional[Fakt]:
    if preferowany and k.jest(f"{pozycja}.{preferowany}"):
        return k.fakt(f"{pozycja}.{preferowany}")
    fy = k.okresy_fy(pozycja)
    if fy:
        return fy[-1]
    stany = [f for f in k.r.fakty() if f.pozycja == pozycja and f.okres.typ.value == "dzien"]
    return max(stany, key=lambda f: f.okres.koniec) if stany else None


def oblicz(k: Kalkulator, rynek: str, wycena: dict, ttm_sufiks: Optional[str], liczba_analitykow: Optional[int]) -> list[Filar]:
    cfg = yaml.safe_load(KONFIGURACJA.read_text(encoding="utf-8"))["filary"]
    D = k.fakt(wycena["kapitalizacja"]).okres.koniec if wycena.get("kapitalizacja") else None
    d = D.isoformat() if D else None

    # miary złożone jako fakty wyliczone
    if wycena.get("implikowany_wzrost_fcf") and wycena.get("wzrost_historyczny"):
        k.wylicz(f"nadwyzka_wzrostu.{d}", "nadwyzka_wzrostu", "CAGR przychodów historyczny − implikowany wzrost FCF",
                 [wycena["wzrost_historyczny"], wycena["implikowany_wzrost_fcf"]], lambda h, i: h - i,
                 Jednostka.ulamek, Okres(typ="dzien", koniec=D))
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
            if nazwa == "analitycy" and (liczba_analitykow is None or liczba_analitykow < 3):
                filar.miary[miara] = None
                continue
            pref = d if miara in ("fcf_yield", "ev_ebit", "nadwyzka_wzrostu") else ttm_sufiks
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


def wynik_ogolny(filary: list[Filar]) -> tuple[Optional[float], int]:
    dostepne = [f for f in filary if f.punkty is not None]
    if not dostepne:
        return None, 0
    suma_wag = sum(f.waga for f in dostepne)
    return sum(f.punkty * f.waga / suma_wag for f in dostepne), len(dostepne)
