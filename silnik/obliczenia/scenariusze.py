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
Wartość kapitału = wartość bieżąca przepływów − dług netto (ten sam fakt dlug_netto co w EV),
więc gotówka netto podnosi wartość na akcję, a dług ją obniża. Gdy długu netto brak
(np. bank), silnik liczy bez niego i zapisuje to w braku oraz we wzorze.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

from silnik.fakty.schemat import Fakt, Jednostka, Metoda, Okres, Rodzaj, Status

from .kalkulator import BrakSensu, Kalkulator
from .wycena import bisekcja, ostatni, parametry, wartosc_przychody_marza


def wartosc_kapitalu(r0, g, n, gT, k, marza, dlug_netto=0.0, sciezka=()) -> float:
    """Wartość kapitału własnego: wartość bieżąca przepływów (przychody × marża FCF) − dług netto."""
    return wartosc_przychody_marza(r0, g, n, gT, k, marza, sciezka) - dlug_netto


def stopa_implikowana(r0, g, n, gT, marza, akcje, kurs, sciezka=(), dlug_netto=0.0) -> float:
    """Stopa dyskontowa k, przy której wartość scenariusza na akcję równa się kursowi."""
    return bisekcja(lambda k: -wartosc_kapitalu(r0, g, n, gT, k, marza, dlug_netto, sciezka) / akcje, -kurs,
                    gT + 0.001, 0.60)

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


def _dlug_netto(k: Kalkulator, wycena: dict, cap: Fakt) -> Optional[Fakt]:
    """Dług netto z EV wyceny (ten sam fakt), a gdy EV brak — ostatni dług netto przed dniem kursu."""
    ev = k.fakt(wycena["ev"]) if wycena.get("ev") else None
    if ev:
        for fid in ev.wejscia:
            f = k.fakt(fid)
            if f and f.pozycja == "dlug_netto":
                return f
    return ostatni(k, "dlug_netto", cap.okres.koniec)


def _na_akcje(r, g, n, gt, kk, mz, akcje, reszta, z_dlugiem: bool) -> float:
    """reszta: [dlug_netto, *ścieżka przychodów] albo [*ścieżka przychodów], gdy długu netto brak."""
    dlug = reszta[0] if z_dlugiem else 0.0
    sciezka = tuple(reszta[1:] if z_dlugiem else reszta)
    return wartosc_kapitalu(r, g, n, gt, kk, mz, dlug, sciezka) / akcje


def wartosc_roe(kapital: float, roe: float, gT: float, ke: float, akcje: float) -> float:
    """Wartość na akcję spółki finansowej albo dewelopera: kapitał własny × (ROE − g) ÷ (koszt kapitału − g) ÷ akcje."""
    if ke <= gT:
        raise BrakSensu("koszt kapitału nie jest wyższy od wzrostu rezydualnego")
    return kapital * (roe - gT) / (ke - gT) / akcje


def stopa_roe(kapital: float, roe: float, gT: float, akcje: float, kurs: float) -> float:
    """Stopa dyskontowa, przy której wartość scenariusza ROE równa się kursowi: g + (ROE − g) × kapitał ÷ kapitalizacja."""
    return gT + (roe - gT) * kapital / (kurs * akcje)


def _kapitalowe(k: Kalkulator, scen: list[dict], wycena: dict, ke_id: str, akcje: Fakt, kurs: Fakt, okres: Okres,
                wartosci: list) -> bool:
    """Scenariusze opisane przez ROE (typ finanse albo deweloper, decyzja właściciela z 12.11.2026)."""
    kw = wycena.get("kapital_wlasny")
    if not kw:
        k.braki.append("scenariusze ROE: brak kapitału własnego")
        return False
    for s in scen:
        if "roe" not in s:
            raise BladScenariuszy(f"{s['nazwa']}: typ spółki finanse/deweloper wymaga pola „roe” (zamiast wzrostu i marży FCF)")
        ids = []
        for par in ("prawdopodobienstwo", "roe"):
            fid = f"scenariusz_{par}.{s['nazwa']}"
            k.r.dodaj(Fakt(id=fid, rodzaj=Rodzaj.zalozenie, pozycja=f"scenariusz_{par}", okres=Okres(typ="brak"),
                           wartosc=s[par], jednostka=U, metoda=Metoda.model, status=Status.jedno_zrodlo,
                           uzasadnienie=s["uzasadnienie"]), zastap=True)
            ids.append(fid)
        f = k.wylicz(f"wartosc_na_akcje.{s['nazwa']}", "wartosc_na_akcje",
                     "kapital_wlasny × (roe − wzrost_rezydualny) / (koszt_kapitalu − wzrost_rezydualny) / akcje_w_obrocie",
                     [kw, ids[1], "wzrost_rezydualny.zalozenie", ke_id, akcje.id], wartosc_roe,
                     Jednostka.pieniadz_na_akcje, okres, kurs.waluta)
        if f is None:
            return False
        wartosci.append((ids[0], f.id))
        k.wylicz(f"stopa_zwrotu_implikowana.{s['nazwa']}", "stopa_zwrotu_implikowana",
                 f"stopa dyskontowa, przy której wartość scenariusza {s['nazwa']} równa się kursowi",
                 [kw, ids[1], "wzrost_rezydualny.zalozenie", akcje.id, kurs.id], stopa_roe, U, okres)
    return True


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
    dn = _dlug_netto(k, wycena, cap)
    dn_wej = [dn.id] if dn else []
    opis_dn = " − dlug_netto" if dn else " (bez długu netto: brak danych)"
    if dn is None:
        k.braki.append("scenariusze: brak długu netto; wartość kapitału bez korekty o dług albo gotówkę netto")
    wartosci = []
    if wycena.get("metoda") == "kapitalowa":
        if not _kapitalowe(k, scen, wycena, ke_id, akcje, kurs, okres, wartosci):
            return None
        scen = []  # wartości już policzone
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
        wej = [f"przychody.{S}", ids[1], ids[2], "wzrost_rezydualny.zalozenie", ke_id, akcje.id] + dn_wej + sc
        f = k.wylicz(f"wartosc_na_akcje.{s['nazwa']}", "wartosc_na_akcje",
                     f"(wartość przepływów: przychody × marża FCF, wzrost przez {n} lat, potem rezydualny{opis_sc}"
                     f"{opis_dn}) / akcje_w_obrocie", wej,
                     lambda r, g, mz, gt, kk, a, *p: _na_akcje(r, g, n, gt, kk, mz, a, p, bool(dn)),
                     Jednostka.pieniadz_na_akcje, okres, kurs.waluta)
        if f is None:
            return None
        wartosci.append((ids[0], f.id))
        # stopa zwrotu implikowana: koszt kapitału, przy którym wartość scenariusza = obecny kurs
        k.wylicz(f"stopa_zwrotu_implikowana.{s['nazwa']}", "stopa_zwrotu_implikowana",
                 f"stopa dyskontowa, przy której wartość scenariusza {s['nazwa']} równa się kursowi",
                 [f"przychody.{S}", ids[1], ids[2], "wzrost_rezydualny.zalozenie", akcje.id, kurs.id] + dn_wej + sc,
                 lambda r, g, mz, gt, a, ku, *p: stopa_implikowana(r, g, n, gt, mz, a, ku, p[1:] if dn else p,
                                                                   p[0] if dn else 0.0), U, okres)
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


# --- tabela wrażliwości (specyfikacja 1.1, punkt 7) -------------------------------------------

NAZWY_ZALOZEN = {"wzrost": "wzrost przychodów", "marza": "marża FCF", "roe": "ROE", "ke": "koszt kapitału",
                 "gt": "wzrost rezydualny"}


def _etykieta(*pary) -> str:
    return "_".join(f"{n}_{'p' if x >= 0 else 'm'}{abs(x)}" for n, x in pary)


def wrazliwosc(k: Kalkulator, plik: Path, wycena: dict) -> Optional[dict]:
    """Wartość na akcję przy krokach założeń wokół scenariusza bazowego (fakty wyliczone) i założenie,
    które przy jednym kroku najmocniej zmienia wartość. Bazowy = scenariusz „bazowy” albo najbardziej prawdopodobny."""
    if not plik.exists() or not wycena.get("kapitalizacja") or not wycena.get("ke"):
        return None
    scen = wczytaj(plik)
    baza = next((s for s in scen if s["nazwa"] == "bazowy"), max(scen, key=lambda s: s["prawdopodobienstwo"]))
    b = baza["nazwa"]
    if not k.jest(f"wartosc_na_akcje.{b}"):
        return None
    cfg = parametry()["wrazliwosc"]
    cap = k.fakt(wycena["kapitalizacja"])
    akcje = next(f for f in k.r.fakty() if f.pozycja == "akcje_w_obrocie" and f.id in cap.wejscia)
    okres = Okres(typ="dzien", koniec=cap.okres.koniec)
    ke_id, gt_id = wycena["ke"], "wzrost_rezydualny.zalozenie"
    n = parametry()["lata_prognozy"]
    kapitalowa = wycena.get("metoda") == "kapitalowa"
    if kapitalowa:
        wej = [wycena["kapital_wlasny"], f"scenariusz_roe.{b}", gt_id, ke_id, akcje.id]
        def wartosc(d: dict):
            def fn(kw, roe, gt, kk, a):
                return wartosc_roe(kw, roe + d.get("roe", 0), gt + d.get("gt", 0), kk + d.get("ke", 0), a)
            return fn
        osie = ("roe", "ke")
        opis = "kapital_wlasny × (roe − g) / (koszt_kapitalu − g) / akcje"
    else:
        S = wycena["okres_bazowy"]
        dn = _dlug_netto(k, wycena, cap)
        sc = list(baza.get("sciezka_przychodow", []))
        wej = [f"przychody.{S}", f"scenariusz_wzrost_przychodow.{b}", f"scenariusz_marza_fcf.{b}", gt_id, ke_id, akcje.id] \
            + ([dn.id] if dn else []) + sc
        def wartosc(d: dict):
            def fn(r, g, mz, gt, kk, a, *p):
                return _na_akcje(r, g + d.get("wzrost", 0), n, gt + d.get("gt", 0), kk + d.get("ke", 0),
                                 mz + d.get("marza", 0), a, p, bool(dn))
            return fn
        osie = ("wzrost", "marza")
        opis = "wartość scenariusza bazowego (przychody × marża FCF, wzrost przez lata prognozy, dług netto)"
    wynik: dict = {"bazowy": b, "osie": osie, "siatka1": {}, "siatka2": {}, "zalozenia": {}}
    kroki = cfg["kroki"]
    for i in kroki:
        for j in kroki:
            d = {osie[0]: i * cfg[osie[0]], osie[1]: j * cfg[osie[1]]}
            et = _etykieta((osie[0], i), (osie[1], j))
            f = k.wylicz(f"wrazliwosc_wartosc.{et}", "wrazliwosc_wartosc",
                         f"{opis}; {osie[0]} {i:+d} krok(i), {osie[1]} {j:+d} krok(i)", wej, wartosc(d),
                         Jednostka.pieniadz_na_akcje, okres, cap.waluta)
            wynik["siatka1"][(i, j)] = f.id if f else None
    for i in kroki:
        for j in (-1, 0, 1):
            d = {"ke": i * cfg["ke"], "gt": j * cfg["gt"]}
            et = _etykieta(("ke", i), ("gt", j))
            f = k.wylicz(f"wrazliwosc_wartosc.{et}", "wrazliwosc_wartosc",
                         f"{opis}; koszt kapitału {i:+d} krok(i), wzrost rezydualny {j:+d} krok", wej, wartosc(d),
                         Jednostka.pieniadz_na_akcje, okres, cap.waluta)
            wynik["siatka2"][(i, j)] = f.id if f else None
    baza_wart = k.fakt(f"wartosc_na_akcje.{b}").wartosc
    for z in dict.fromkeys(osie + ("ke", "gt")):
        krok = cfg[z]
        f = k.wylicz(f"wrazliwosc_zalozenia.{z}", "wrazliwosc_zalozenia",
                     f"wartość przy {NAZWY_ZALOZEN[z]} +{krok * 100:g} pp ÷ wartość scenariusza {b} − 1", wej,
                     (lambda fz: lambda *a: fz(*a) / baza_wart - 1)(wartosc({z: krok})), U, okres)
        wynik["zalozenia"][z] = f.id if f else None
    znane = {z: abs(k.fakt(fid).wartosc) for z, fid in wynik["zalozenia"].items() if fid}
    wynik["najwazniejsze"] = max(znane, key=znane.get) if znane else None
    return wynik
