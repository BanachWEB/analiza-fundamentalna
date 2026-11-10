"""Co jest w cenie: koszt kapitału, wycena odwrotna (3 warianty), PVGO, mnożniki.

Model wartości kapitału własnego (FCF dla właścicieli dyskontowany kosztem kapitału własnego):
  W = Σ_{t=1..n} FCF_t / (1+k)^t + FCF_n·(1+gT) / ((k−gT)·(1+k)^n)
Warianty wyceny odwrotnej (Mauboussin i Rappaport, „Expectations Investing”):
  1. implikowany wzrost FCF przez n lat (FCF bazowy = FCF dla właścicieli TTM);
  2. implikowany okres przewagi (CAP): ile lat wzrostu w tempie historycznym (CAGR przychodów)
     uzasadnia cenę;
  3. implikowana marża FCF przy wzroście przychodów w tempie historycznym (działa także,
     gdy dzisiejszy FCF jest ujemny).
Wszystkie wyniki to fakty wyliczone; założenia (beta, wzrost rezydualny) są w rejestrze.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional

import yaml

from silnik.fakty.schemat import Fakt, Jednostka, Metoda, Okres, Rodzaj, Status

from .kalkulator import BrakSensu, Kalkulator

KONFIGURACJA = Path(__file__).resolve().parents[2] / "konfiguracja" / "wycena.yaml"
U, P, X = Jednostka.ulamek, Jednostka.pieniadz, Jednostka.mnoznik


def parametry() -> dict:
    return yaml.safe_load(KONFIGURACJA.read_text(encoding="utf-8"))


# --- matematyka ------------------------------------------------------------------------


def wartosc_fcf(fcf0: float, g: float, n: int, gT: float, k: float) -> float:
    if k <= gT:
        raise BrakSensu("koszt kapitału nie jest wyższy od wzrostu rezydualnego")
    w, f = 0.0, fcf0
    for t in range(1, n + 1):
        f *= 1 + g
        w += f / (1 + k) ** t
    return w + f * (1 + gT) / ((k - gT) * (1 + k) ** n)


def wartosc_przychody_marza(r0: float, g: float, n: int, gT: float, k: float, marza: float) -> float:
    return wartosc_fcf(r0 * marza, g, n, gT, k)


def bisekcja(fn, cel: float, lo: float, hi: float, iteracji: int = 200) -> float:
    flo, fhi = fn(lo) - cel, fn(hi) - cel
    if flo * fhi > 0:
        raise BrakSensu(f"cena poza zakresem modelu (szukano między {lo:.0%} a {hi:.0%})")
    for _ in range(iteracji):
        m = (lo + hi) / 2
        fm = fn(m) - cel
        if abs(fm) < 1e-9 * max(1.0, abs(cel)):
            return m
        if (fm < 0) == (flo < 0):
            lo, flo = m, fm
        else:
            hi = m
    return (lo + hi) / 2


def implikowany_wzrost(cap: float, fcf0: float, n: int, gT: float, k: float) -> float:
    if fcf0 <= 0:
        raise BrakSensu("FCF dla właścicieli ≤ 0: wariant przez wzrost FCF nie działa (patrz wariant marży)")
    return bisekcja(lambda g: wartosc_fcf(fcf0, g, n, gT, k), cap, -0.5, 1.5)


def implikowany_cap(cap: float, fcf0: float, g: float, gT: float, k: float, max_lat: int) -> float:
    if fcf0 <= 0:
        raise BrakSensu("FCF dla właścicieli ≤ 0: CAP przez FCF nie działa")
    if g <= gT:
        raise BrakSensu("wzrost historyczny nie przekracza wzrostu rezydualnego; CAP nie ma sensu")
    if wartosc_fcf(fcf0, g, 0, gT, k) >= cap:
        return 0.0
    for n in range(1, max_lat + 1):
        if wartosc_fcf(fcf0, g, n, gT, k) >= cap:
            # interpolacja liniowa między n−1 a n
            a, b = wartosc_fcf(fcf0, g, n - 1, gT, k), wartosc_fcf(fcf0, g, n, gT, k)
            return n - 1 + (cap - a) / (b - a)
    raise BrakSensu(f"nawet {max_lat} lat wzrostu w tempie historycznym nie uzasadnia ceny")


def implikowana_marza(cap: float, r0: float, g: float, n: int, gT: float, k: float) -> float:
    jednostkowa = wartosc_przychody_marza(r0, g, n, gT, k, 1.0)
    return cap / jednostkowa


# --- fakty ---------------------------------------------------------------------------------


def _zalozenie(k: Kalkulator, fid: str, pozycja: str, wartosc: float, uzasadnienie: str, jednostka=U) -> str:
    if not k.jest(fid):
        k.r.dodaj(Fakt(id=fid, rodzaj=Rodzaj.zalozenie, pozycja=pozycja, okres=Okres(typ="brak"), wartosc=wartosc,
                       jednostka=jednostka, metoda=Metoda.kod, status=Status.jedno_zrodlo, uzasadnienie=uzasadnienie))
    return fid


def ostatni(k: Kalkulator, pozycja: str, przed: Optional[date] = None) -> Optional[Fakt]:
    fakty = [f for f in k.r.fakty() if f.pozycja == pozycja and f.okres.typ.value == "dzien" and f.status != Status.odrzucony
             and (przed is None or f.okres.koniec <= przed)]
    return max(fakty, key=lambda f: f.okres.koniec) if fakty else None


def okres_bazowy(k: Kalkulator, ttm: Optional[date]) -> Optional[str]:
    """Sufiks okresu przepływów do wyceny: TTM, a gdy go brak — ostatni rok obrotowy."""
    if ttm and k.jest(f"fcf_wlascicieli.TTM{ttm.isoformat()}"):
        return f"TTM{ttm.isoformat()}"
    lata = [f for f in k.okresy_fy("fcf_wlascicieli")]
    return lata[-1].id.split(".", 1)[1] if lata else None


def oblicz(k: Kalkulator, ttm: Optional[date], rynek: str) -> dict:
    """Zwraca słownik id kluczowych faktów wyceny (do raportu i karty Treli)."""
    par = parametry()
    wynik: dict[str, Optional[str]] = {}
    kurs = ostatni(k, "kurs")
    akcje = ostatni(k, "akcje_w_obrocie")
    if not kurs or not akcje:
        k.braki.append("wycena: brak kursu albo liczby akcji")
        return wynik
    D = kurs.okres.koniec
    d = D.isoformat()
    okres_d = Okres(typ="dzien", koniec=D)
    cap = k.wylicz(f"kapitalizacja.{d}", "kapitalizacja", "kurs × akcje_w_obrocie", [kurs.id, akcje.id],
                   lambda a, b: a * b, P, okres_d, kurs.waluta)
    if not cap:
        return wynik
    wynik["kapitalizacja"] = cap.id

    # koszt kapitału własnego
    beta = _zalozenie(k, "beta.zalozenie", "beta", par["beta_domyslna"],
                      "Beta = 1 (rynek jako całość): brak wiarygodnej bety z własnych danych; do zmiany przez model z uzasadnieniem.",
                      Jednostka.liczba)
    erp = ostatni(k, "premia_ryzyka_akcji")
    rf = k.fakt("rentownosc_10l.zalozenie") or ostatni(k, "rentownosc_10l")  # założenie (--rf) nadpisuje źródło
    if not erp or not rf:
        k.braki.append("koszt kapitału: brak premii za ryzyko albo rentowności obligacji 10-letnich")
        return wynik
    spread = ostatni(k, "spread_kraju")
    if rynek == "GPW":
        if not spread:
            k.braki.append("koszt kapitału: brak spreadu niewypłacalności Polski")
            return wynik
        rf_lok = k.wylicz(f"stopa_wolna_od_ryzyka.{d}", "stopa_wolna_od_ryzyka",
                          "rentownosc_10l − spread_kraju (Damodaran: bez podwójnego liczenia ryzyka kraju)",
                          [rf.id, spread.id], lambda a, b: a - b, U, okres_d)
    else:
        rf_lok = k.wylicz(f"stopa_wolna_od_ryzyka.{d}", "stopa_wolna_od_ryzyka", "rentownosc_10l", [rf.id],
                          lambda a: a, U, okres_d)
    if not rf_lok:
        return wynik
    ke = k.wylicz(f"koszt_kapitalu_wlasnego.{d}", "koszt_kapitalu_wlasnego",
                  "stopa_wolna_od_ryzyka + beta × premia_ryzyka_akcji", [rf_lok.id, beta, erp.id],
                  lambda r, b, e: r + b * e, U, okres_d)
    gT = _zalozenie(k, "wzrost_rezydualny.zalozenie", "wzrost_rezydualny", par["wzrost_rezydualny_max"],
                    "Wzrost po okresie prognozy: nie wyżej niż stopa wolna od ryzyka (Damodaran); domyślnie 2,5% rocznie.")
    wynik.update(ke=ke.id if ke else None)
    if not ke:
        return wynik
    n = par["lata_prognozy"]

    # mnożniki
    S = okres_bazowy(k, ttm)
    if S is None:
        k.braki.append("wycena: brak FCF dla właścicieli (TTM ani roczny)")
        return wynik
    def m(nazwa, wzor, wej, fn, jedn=X):
        f = k.wylicz(f"{nazwa}.{d}", nazwa, wzor, wej, fn, jedn, okres_d)
        wynik[nazwa] = f.id if f else None
        return f
    m("c_z", f"kapitalizacja / zysk_netto.{S}", [cap.id, f"zysk_netto.{S}"],
      lambda c, z: c / z if z > 0 else (_ for _ in ()).throw(BrakSensu("zysk netto ≤ 0")))
    m("fcf_yield", f"fcf_wlascicieli.{S} / kapitalizacja", [f"fcf_wlascicieli.{S}", cap.id], lambda f, c: f / c, U)
    kw = ostatni(k, "kapital_wlasny", D) or ostatni(k, "kapital_wlasny_z_udzialami_niekontrolujacymi", D)
    if kw:
        m("c_wk", "kapitalizacja / kapital_wlasny", [cap.id, kw.id], lambda c, b: c / b)
    dn = ostatni(k, "dlug_netto", D)
    if dn:
        ev = k.wylicz(f"ev.{d}", "ev", "kapitalizacja + dlug_netto", [cap.id, dn.id], lambda c, x: c + x, P, okres_d,
                      kurs.waluta)
        if ev:
            wynik["ev"] = ev.id
            m("ev_ebit", f"ev / zysk_operacyjny.{S}", [ev.id, f"zysk_operacyjny.{S}"], lambda e, z: e / z)
            m("ev_ebitda", f"ev / ebitda.{S}", [ev.id, f"ebitda.{S}"], lambda e, z: e / z)
    else:
        k.braki.append("wycena: brak długu netto — EV nie policzone")

    # PVGO
    m("udzial_pvgo", f"1 − (zysk_netto.{S} / koszt_kapitalu_wlasnego) / kapitalizacja",
      [f"zysk_netto.{S}", ke.id, cap.id], lambda z, kk, c: 1 - (z / kk) / c, U)

    # wycena odwrotna
    m("implikowany_wzrost_fcf", f"wzrost FCF przez {n} lat, przy którym wartość = kapitalizacja",
      [cap.id, f"fcf_wlascicieli.{S}", gT, ke.id], lambda c, f, g, kk: implikowany_wzrost(c, f, n, g, kk), U)
    # Wzrost historyczny: niższy z CAGR 3- i 5-letniego (stopy bazowe: szybki wzrost wygasa).
    kandydaci = [k.okresy_fy(x)[-1] for x in ("cagr_przychody_3l", "cagr_przychody_5l") if k.okresy_fy(x)]
    hist = min(kandydaci, key=lambda f: f.wartosc).pozycja if kandydaci else None
    if hist:
        g_hist = min(kandydaci, key=lambda f: f.wartosc).id
        wynik["wzrost_historyczny"] = g_hist
        m("implikowany_cap", f"lata wzrostu FCF w tempie {hist}, które uzasadniają kapitalizację",
          [cap.id, f"fcf_wlascicieli.{S}", g_hist, gT, ke.id],
          lambda c, f, g, gt, kk: implikowany_cap(c, f, g, gt, kk, par["cap_max_lat"]), Jednostka.lata)
        m("implikowana_marza_fcf", f"marża FCF przy wzroście przychodów w tempie {hist} przez {n} lat",
          [cap.id, f"przychody.{S}", g_hist, gT, ke.id], lambda c, r, g, gt, kk: implikowana_marza(c, r, g, n, gt, kk), U)
    else:
        k.braki.append("wycena odwrotna: brak historycznego CAGR przychodów (CAP i marża)")
    wynik["okres_bazowy"] = S
    return wynik
