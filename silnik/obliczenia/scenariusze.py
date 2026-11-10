"""Scenariusze z prawdopodobieństwami: założenia od modelu, rachunek w kodzie.

Model zapisuje analizy/<TICKER>/<data>/scenariusze.json:
{"scenariusze": [
  {"nazwa": "bazowy", "prawdopodobienstwo": 0.5, "wzrost_przychodow": 0.08, "marza_fcf": 0.25,
   "uzasadnienie": "…stopa bazowa…, dowody…",
   "sciezka_przychodow": ["przychody_konsensus.FY2027", "przychody_konsensus.FY2028"]}, …]}
Pole „sciezka_przychodow” jest opcjonalne: id faktów z przychodami na kolejne lata (np. konsensus);
przez te lata przychody biorą się z faktów, potem rosną o wzrost_przychodow do końca okresu prognozy.
Silnik liczy wartość na akcję w każdym scenariuszu (przychody × marża FCF, ten sam koszt kapitału
i wzrost rezydualny co wycena odwrotna), wartość oczekiwaną, potencjał wobec kursu,
prawdopodobieństwo straty i asymetrię (oczekiwany zysk ÷ oczekiwana strata).
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

from silnik.fakty.schemat import Fakt, Jednostka, Metoda, Okres, Rodzaj, Status

from .kalkulator import Kalkulator
from .wycena import bisekcja, parametry, wartosc_przychody_marza


def stopa_implikowana(r0, g, n, gT, marza, akcje, kurs, sciezka=()) -> float:
    """Stopa dyskontowa k, przy której wartość scenariusza na akcję równa się kursowi."""
    return bisekcja(lambda k: -wartosc_przychody_marza(r0, g, n, gT, k, marza, sciezka) / akcje, -kurs, gT + 0.001, 0.60)

U = Jednostka.ulamek


class BladScenariuszy(Exception):
    pass


def wczytaj(plik: Path) -> list[dict]:
    dane = json.loads(plik.read_text(encoding="utf-8"))["scenariusze"]
    if not 2 <= len(dane) <= 5:
        raise BladScenariuszy("potrzeba od 2 do 5 scenariuszy")
    suma = sum(s["prawdopodobienstwo"] for s in dane)
    if abs(suma - 1) > 1e-6:
        raise BladScenariuszy(f"prawdopodobieństwa sumują się do {suma:.3f}, a muszą do 1")
    for s in dane:
        if not 0.05 <= s["prawdopodobienstwo"] <= 0.85:
            raise BladScenariuszy(f"{s['nazwa']}: prawdopodobieństwo poza przedziałem 5–85% (zasada kalibracji)")
        if not s.get("uzasadnienie"):
            raise BladScenariuszy(f"{s['nazwa']}: brak uzasadnienia")
        if not re.fullmatch(r"[a-z0-9_]+", s["nazwa"]):
            raise BladScenariuszy(f"{s['nazwa']}: nazwa tylko z małych liter, cyfr i _")
        sc = s.get("sciezka_przychodow", [])
        if not isinstance(sc, list) or not all(isinstance(x, str) for x in sc):
            raise BladScenariuszy(f"{s['nazwa']}: sciezka_przychodow to lista id faktów")
    return dane


def oblicz(k: Kalkulator, plik: Path, wycena: dict) -> Optional[dict]:
    if not plik.exists():
        return None
    scen = wczytaj(plik)
    cap_id, ke_id, S = wycena.get("kapitalizacja"), wycena.get("ke"), wycena.get("okres_bazowy")
    if not (cap_id and ke_id and S):
        k.braki.append("scenariusze: brak kapitalizacji, kosztu kapitału albo okresu bazowego")
        return None
    cap = k.fakt(cap_id)
    D = cap.okres.koniec.isoformat()
    akcje = next(f for f in k.r.fakty() if f.pozycja == "akcje_w_obrocie" and f.id in k.r[cap_id].wejscia)
    kurs = next(f for f in k.r.fakty() if f.pozycja == "kurs" and f.id in k.r[cap_id].wejscia)
    n = parametry()["lata_prognozy"]
    okres = Okres(typ="dzien", koniec=cap.okres.koniec)
    wartosci = []
    for s in scen:
        ids = []
        for par in ("prawdopodobienstwo", "wzrost_przychodow", "marza_fcf"):
            fid = f"scenariusz_{par}.{s['nazwa']}"
            k.r.dodaj(Fakt(id=fid, rodzaj=Rodzaj.zalozenie, pozycja=f"scenariusz_{par}", okres=Okres(typ="brak"),
                           wartosc=s[par], jednostka=U, metoda=Metoda.model, status=Status.jedno_zrodlo,
                           uzasadnienie=s["uzasadnienie"]), zastap=True)
            ids.append(fid)
        sc = list(s.get("sciezka_przychodow", []))
        opis_sc = f"; przychody w pierwszych {len(sc)} latach ze ścieżki" if sc else ""
        wej = [f"przychody.{S}", ids[1], ids[2], "wzrost_rezydualny.zalozenie", ke_id, akcje.id] + sc
        f = k.wylicz(f"wartosc_na_akcje.{s['nazwa']}", "wartosc_na_akcje",
                     f"(przychody × marża FCF, wzrost przez {n} lat, potem rezydualny{opis_sc}) / akcje_w_obrocie", wej,
                     lambda r, g, mz, gt, kk, a, *p: wartosc_przychody_marza(r, g, n, gt, kk, mz, p) / a,
                     Jednostka.pieniadz_na_akcje, okres, kurs.waluta)
        if f is None:
            return None
        wartosci.append((ids[0], f.id))
        # stopa zwrotu implikowana: koszt kapitału, przy którym wartość scenariusza = obecny kurs
        k.wylicz(f"stopa_zwrotu_implikowana.{s['nazwa']}", "stopa_zwrotu_implikowana",
                 f"stopa dyskontowa, przy której wartość scenariusza {s['nazwa']} równa się kursowi",
                 [f"przychody.{S}", ids[1], ids[2], "wzrost_rezydualny.zalozenie", akcje.id, kurs.id] + sc,
                 lambda r, g, mz, gt, a, ku, *p: stopa_implikowana(r, g, n, gt, mz, a, ku, p), U, okres)
    wej = [x for para in wartosci for x in para] + [kurs.id]

    def oczekiwana(*a):
        pary, k_ = a[:-1], a[-1]
        return sum(pary[i] * pary[i + 1] for i in range(0, len(pary), 2))

    def potencjal(*a):
        return oczekiwana(*a) / a[-1] - 1

    def p_straty(*a):
        pary, k_ = a[:-1], a[-1]
        return sum(pary[i] for i in range(0, len(pary), 2) if pary[i + 1] < k_)

    def asymetria(*a):
        pary, k_ = a[:-1], a[-1]
        zysk = sum(pary[i] * max(pary[i + 1] - k_, 0) for i in range(0, len(pary), 2))
        strata = sum(pary[i] * max(k_ - pary[i + 1], 0) for i in range(0, len(pary), 2))
        if strata == 0:
            from .kalkulator import BrakSensu
            raise BrakSensu("żaden scenariusz nie daje straty; asymetria nieokreślona")
        return zysk / strata

    wynik = {}
    for nazwa, fn, jedn in (("wartosc_oczekiwana_na_akcje", oczekiwana, Jednostka.pieniadz_na_akcje),
                            ("potencjal_oczekiwany", potencjal, U), ("prawdopodobienstwo_straty", p_straty, U),
                            ("asymetria", asymetria, Jednostka.mnoznik)):
        f = k.wylicz(f"{nazwa}.{D}", nazwa, nazwa.replace("_", " "), wej, fn, jedn, okres,
                     kurs.waluta if jedn == Jednostka.pieniadz_na_akcje else None)
        wynik[nazwa] = f.id if f else None
    return wynik
