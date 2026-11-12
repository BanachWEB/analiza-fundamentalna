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


def wartosc_przychody_marza(r0: float, g: float, n: int, gT: float, k: float, marza: float,
                            sciezka: tuple[float, ...] = ()) -> float:
    """Wartość z przychodów × marża FCF. `sciezka`: przychody w pierwszych latach (np. konsensus);
    od ostatniego roku ścieżki przychody rosną o g do roku n, potem wzrost rezydualny gT."""
    if not sciezka:
        return wartosc_fcf(r0 * marza, g, n, gT, k)
    if len(sciezka) >= n:
        raise BrakSensu("ścieżka przychodów nie może być dłuższa niż okres prognozy minus jeden rok")
    if k <= gT:
        raise BrakSensu("koszt kapitału nie jest wyższy od wzrostu rezydualnego")
    w, r = 0.0, r0
    for t in range(1, n + 1):
        r = sciezka[t - 1] if t <= len(sciezka) else r * (1 + g)
        w += r * marza / (1 + k) ** t
    return w + r * marza * (1 + gT) / ((k - gT) * (1 + k) ** n)


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


def _koszt_kapitalu(k: Kalkulator, beta: str, rynek: str, d: str, okres_d: Okres) -> Optional[Fakt]:
    erp = ostatni(k, "premia_ryzyka_akcji")
    rf = k.fakt("rentownosc_10l.zalozenie") or ostatni(k, "rentownosc_10l")  # założenie (--rf) nadpisuje źródło
    if not erp or not rf:
        k.braki.append("koszt kapitału: brak premii za ryzyko albo rentowności obligacji 10-letnich")
        return None
    if rynek == "GPW":
        spread = ostatni(k, "spread_kraju")
        if not spread:
            k.braki.append("koszt kapitału: brak spreadu niewypłacalności Polski")
            return None
        rf_lok = k.wylicz(f"stopa_wolna_od_ryzyka.{d}", "stopa_wolna_od_ryzyka",
                          "rentownosc_10l − spread_kraju (Damodaran: bez podwójnego liczenia ryzyka kraju)",
                          [rf.id, spread.id], lambda a, b: a - b, U, okres_d)
    else:
        rf_lok = k.wylicz(f"stopa_wolna_od_ryzyka.{d}", "stopa_wolna_od_ryzyka", "rentownosc_10l", [rf.id],
                          lambda a: a, U, okres_d)
    if not rf_lok:
        return None
    return k.wylicz(f"koszt_kapitalu_wlasnego.{d}", "koszt_kapitalu_wlasnego",
                    "stopa_wolna_od_ryzyka + beta × premia_ryzyka_akcji", [rf_lok.id, beta, erp.id],
                    lambda r, b, e: r + b * e, U, okres_d)


def wybierz_bete(k: Kalkulator, par: dict, okres_d: Okres) -> str:
    """Beta skorygowana Blume'a z bety z regresji (`beta_regresja`); bez niej beta domyślna jako założenie."""
    reg = ostatni(k, "beta_regresja", przed=okres_d.koniec)
    if reg:
        w = float(par["blume_waga_regresji"])
        f = k.wylicz(f"beta_skorygowana.{okres_d.koniec.isoformat()}", "beta_skorygowana",
                     f"{w:g} × beta_regresja + {1 - w:g} × 1 (Blume)", [reg.id],
                     lambda b: w * b + (1 - w), Jednostka.liczba, okres_d)
        if f:
            return f.id
    k.braki.append("beta: brak bety z regresji (za krótka historia notowań albo brak indeksu); wycena przyjmuje betę domyślną")
    return _zalozenie(k, "beta.zalozenie", "beta", par["beta_domyslna"],
                      "Beta = 1 (rynek jako całość): brak bety z regresji, bo historia notowań spółki i indeksu "
                      "jest za krótka albo niedostępna.", Jednostka.liczba)


def _ev_do(nazwa: str):
    """EV ÷ podstawa; przy podstawie ≤ 0 mnożnik nie ma sensu (jak C/Z przy stracie netto)."""
    def fn(ev: float, baza: float) -> float:
        if baza <= 0:
            raise BrakSensu(f"{nazwa} ≤ 0")
        return ev / baza
    return fn


def _cena_do_sprzedazy(kapitalizacja: float, przychody: float) -> float:
    if przychody <= 0:
        raise BrakSensu("konsensus przychodów ≤ 0, cena ÷ sprzedaż nie ma sensu")
    return kapitalizacja / przychody


def ostatni(k: Kalkulator, pozycja: str, przed: Optional[date] = None) -> Optional[Fakt]:
    fakty = [f for f in k.r.fakty() if f.pozycja == pozycja and f.okres.typ.value == "dzien" and f.status != Status.odrzucony
             and (przed is None or f.okres.koniec <= przed)]
    return max(fakty, key=lambda f: f.okres.koniec) if fakty else None


def okres_bazowy(k: Kalkulator, ttm: Optional[date], baza: str = "fcf_wlascicieli") -> Optional[str]:
    """Sufiks okresu przepływów do wyceny: TTM, a gdy go brak — ostatni rok obrotowy."""
    if ttm and k.jest(f"{baza}.TTM{ttm.isoformat()}"):
        return f"TTM{ttm.isoformat()}"
    lata = [f for f in k.okresy_fy(baza)]
    return lata[-1].id.split(".", 1)[1] if lata else None


SEKTORY = ("ogolny", "cykliczny", "finanse", "deweloper")
KAPITALOWE = ("finanse", "deweloper")  # wycena C/WK wobec ROE


def oblicz(k: Kalkulator, ttm: Optional[date], rynek: str, finansowa: bool = False, sektor: str = "ogolny") -> dict:
    """Zwraca słownik id kluczowych faktów wyceny (do raportu i karty Treli).

    Typ spółki (`sektor`, decyzja właściciela z 12.11.2026):
    - `ogolny`: wycena odwrotna z FCF TTM;
    - `cykliczny`: jak `ogolny` i wariant z FCF znormalizowanym (marża FCF przez cykl × przychody TTM);
    - `finanse`, `deweloper`: podstawą wyceny odwrotnej jest zysk netto (przepływy banku to ruchy depozytów,
      a dewelopera zakupy gruntów), a obok uzasadnione C/WK i ROE implikowane przez kurs.
    `finansowa=True` to dawny zapis sektora „finanse”.
    """
    if finansowa:
        sektor = "finanse"
    if sektor not in SEKTORY:
        k.braki.append(f"wycena: nieznany typ spółki {sektor!r}; liczę jak dla „ogolny”")
        sektor = "ogolny"
    kapitalowa = sektor in KAPITALOWE
    finansowa = kapitalowa  # zysk netto zamiast FCF jako podstawa wyceny odwrotnej
    par = parametry()
    wynik: dict[str, Optional[str]] = {"metoda": "kapitalowa" if kapitalowa else sektor}
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

    # cena ÷ sprzedaż na rok naprzód (informacja, nie bramka): najbliższy rok obrotowy z konsensusem przychodów
    prz = sorted([f for f in k.r.fakty() if f.pozycja == "przychody_konsensus" and f.status != Status.odrzucony
                  and f.okres.koniec and f.okres.koniec > D], key=lambda f: f.okres.koniec)
    if prz and prz[0].waluta == cap.waluta:
        f = k.wylicz(f"c_s_konsensus.{d}", "c_s_konsensus", f"kapitalizacja / {prz[0].id}", [cap.id, prz[0].id],
                     _cena_do_sprzedazy, X, okres_d)
        wynik["c_s_konsensus"] = f.id if f else None
    elif prz:
        k.braki.append(f"c_s_konsensus: waluta konsensusu ({prz[0].waluta}) inna niż kapitalizacji ({cap.waluta})")

    # koszt kapitału własnego (bez niego silnik liczy tylko mnożniki, np. dla konkurentów)
    beta = wybierz_bete(k, par, okres_d)
    wynik["beta"] = beta
    ke = _koszt_kapitalu(k, beta, rynek, d, okres_d)
    gT = _zalozenie(k, "wzrost_rezydualny.zalozenie", "wzrost_rezydualny", par["wzrost_rezydualny_max"],
                    "Wzrost po okresie prognozy: nie wyżej niż stopa wolna od ryzyka (Damodaran); domyślnie 2,5% rocznie.")
    wynik.update(ke=ke.id if ke else None)
    n = par["lata_prognozy"]

    # mnożniki
    baza = "zysk_netto" if finansowa else "fcf_wlascicieli"
    S = okres_bazowy(k, ttm, baza)
    if S is None:
        k.braki.append("wycena: brak FCF dla właścicieli (TTM ani roczny)")
        return wynik
    def m(nazwa, wzor, wej, fn, jedn=X):
        f = k.wylicz(f"{nazwa}.{d}", nazwa, wzor, wej, fn, jedn, okres_d)
        wynik[nazwa] = f.id if f else None
        return f
    m("c_z", f"kapitalizacja / zysk_netto.{S}", [cap.id, f"zysk_netto.{S}"],
      lambda c, z: c / z if z > 0 else (_ for _ in ()).throw(BrakSensu("zysk netto ≤ 0")))
    if not finansowa:
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
            m("ev_ebit", f"ev / zysk_operacyjny.{S}", [ev.id, f"zysk_operacyjny.{S}"], _ev_do("zysk operacyjny"))
            m("ev_ebitda", f"ev / ebitda.{S}", [ev.id, f"ebitda.{S}"], _ev_do("EBITDA"))
    else:
        k.braki.append("wycena: brak długu netto — EV nie policzone")

    # dywidendy i skup akcji (stopa zwrotu dla akcjonariuszy)
    dyw = f"dywidendy_wyplacone.{S}" if k.jest(f"dywidendy_wyplacone.{S}") else None
    if dyw:
        m("stopa_dywidendy", f"|dywidendy_wyplacone.{S}| / kapitalizacja", [dyw, cap.id], lambda a, c: abs(a) / c, U)
    skladniki = [x for x in (dyw, f"skup_akcji.{S}", f"emisje_akcji.{S}") if x and k.jest(x)]
    if skladniki:
        znaki = [-1 if x.startswith("emisje_akcji") else 1 for x in skladniki]
        m("stopa_zwrotu_akcjonariuszy", "(|dywidendy| + |skup_akcji| − |emisje_akcji|) / kapitalizacja, z dostępnych pozycji: "
          + ", ".join(skladniki), skladniki + [cap.id],
          lambda *a: sum(z * abs(v) for z, v in zip(znaki, a[:-1])) / a[-1], U)

    wynik["okres_bazowy"] = S
    if not ke:
        return wynik

    # PVGO
    m("udzial_pvgo", f"1 − (zysk_netto.{S} / koszt_kapitalu_wlasnego) / kapitalizacja",
      [f"zysk_netto.{S}", ke.id, cap.id], lambda z, kk, c: 1 - (z / kk) / c, U)

    # wycena odwrotna
    m("implikowany_wzrost_fcf", f"wzrost FCF przez {n} lat, przy którym wartość = kapitalizacja",
      [cap.id, f"{baza}.{S}", gT, ke.id], lambda c, f, g, kk: implikowany_wzrost(c, f, n, g, kk), U)
    # Wzrost historyczny: niższy z CAGR 3- i 5-letniego (stopy bazowe: szybki wzrost wygasa).
    kandydaci = [k.okresy_fy(x)[-1] for x in ("cagr_przychody_3l", "cagr_przychody_5l") if k.okresy_fy(x)]
    hist = min(kandydaci, key=lambda f: f.wartosc).pozycja if kandydaci else None
    if hist:
        g_hist = min(kandydaci, key=lambda f: f.wartosc).id
        wynik["wzrost_historyczny"] = g_hist
        m("implikowany_cap", f"lata wzrostu FCF w tempie {hist}, które uzasadniają kapitalizację",
          [cap.id, f"{baza}.{S}", g_hist, gT, ke.id],
          lambda c, f, g, gt, kk: implikowany_cap(c, f, g, gt, kk, par["cap_max_lat"]), Jednostka.lata)
        if not finansowa:
          m("implikowana_marza_fcf", f"marża FCF przy wzroście przychodów w tempie {hist} przez {n} lat",
          [cap.id, f"przychody.{S}", g_hist, gT, ke.id], lambda c, r, g, gt, kk: implikowana_marza(c, r, g, n, gt, kk), U)
    else:
        k.braki.append("wycena odwrotna: brak historycznego CAGR przychodów (CAP i marża)")
    beta_sektorowa(k, wynik, par, cap, dn, okres_d)
    if not kapitalowa:
        sygnaly_cyklicznosci(k, par, sektor, okres_d)
    if sektor == "cykliczny":
        cykliczny(k, wynik, par, cap, S, gT, ke.id, n, okres_d)
    if kapitalowa:
        kapitalowa_wycena(k, wynik, par, cap, kw, dn, gT, ke.id, okres_d, sektor == "deweloper")
    return wynik


# --- typy spółek -----------------------------------------------------------------------------


def _lata_pary(k: Kalkulator, a: str, b: str, okno: int) -> list[tuple[str, str]]:
    """Pary id faktów rocznych (a.FY, b.FY) z tych samych lat obrotowych, najwyżej `okno` ostatnich."""
    po_b = {f.id.split(".", 1)[1] for f in k.okresy_fy(b)}
    pary = [(f.id, f"{b}.{f.id.split('.', 1)[1]}") for f in k.okresy_fy(a) if f.id.split(".", 1)[1] in po_b]
    return pary[-okno:]


def sygnaly_cyklicznosci(k: Kalkulator, par: dict, sektor: str, okres_d: Okres) -> None:
    """Największy spadek przychodów r/r i zmienność marży FCF z najwyżej `okno_cyklu_lat` lat.
    Spółka oznaczona jako `ogolny` z wynikami typowymi dla spółki cyklicznej dostaje ostrzeżenie."""
    d = okres_d.koniec.isoformat()
    przych = k.okresy_fy("przychody")[-par["okno_cyklu_lat"]:]
    spadek = None
    if len(przych) >= 3:
        wej = [f.id for f in przych]
        spadek = k.wylicz(f"max_spadek_przychodow.{d}", "max_spadek_przychodow",
                          f"najniższa dynamika przychodów r/r w latach {przych[0].id.split('.', 1)[1]}–{przych[-1].id.split('.', 1)[1]}",
                          wej, lambda *v: min(b / a - 1 for a, b in zip(v, v[1:]) if a > 0), U, okres_d)
    pary = _lata_pary(k, "fcf_wlascicieli", "przychody", par["okno_cyklu_lat"])
    zm = None
    if len(pary) >= 3:
        wej = [x for p in pary for x in p]
        def odchylenie(*v):
            marze = [v[i] / v[i + 1] for i in range(0, len(v), 2) if v[i + 1] > 0]
            sr = sum(marze) / len(marze)
            return (sum((m - sr) ** 2 for m in marze) / (len(marze) - 1)) ** 0.5
        zm = k.wylicz(f"zmiennosc_marzy_fcf.{d}", "zmiennosc_marzy_fcf",
                      f"odchylenie standardowe marży FCF (fcf_wlascicieli / przychody) z {len(pary)} lat", wej, odchylenie, U, okres_d)
    if sektor == "ogolny":
        powody = []
        if spadek and spadek.wartosc <= par["prog_spadek_przychodow"]:
            powody.append("głęboki spadek przychodów r/r")
        if zm and zm.wartosc >= par["prog_zmiennosc_marzy_fcf"]:
            powody.append("dużą zmienność marży FCF")
        if powody:
            k.ostrzezenia.append("Typ spółki: oznaczona jako „ogólna”, ale ma " + " i ".join(powody)
                                 + " — sprawdź, czy nie jest spółką cykliczną (wariant z FCF znormalizowanym).")


def cykliczny(k: Kalkulator, wynik: dict, par: dict, cap: Fakt, S: str, gT: str, ke: str, n: int, okres_d: Okres) -> None:
    """FCF znormalizowany = marża FCF przez cykl (Σ FCF ÷ Σ przychody) × przychody z okresu bazowego."""
    d = okres_d.koniec.isoformat()
    pary = _lata_pary(k, "fcf_wlascicieli", "przychody", par["okno_cyklu_lat"])
    if len(pary) < par["min_lat_cyklu"]:
        k.braki.append(f"spółka cykliczna: tylko {len(pary)} lat FCF i przychodów (minimum {par['min_lat_cyklu']}); "
                       "brak wariantu znormalizowanego")
        return
    od, do = pary[0][0].split(".", 1)[1], pary[-1][0].split(".", 1)[1]
    marza = k.wylicz(f"marza_fcf_cykl.{d}", "marza_fcf_cykl", f"Σ fcf_wlascicieli ÷ Σ przychody, {od}–{do}",
                     [x for p in pary for x in p],
                     lambda *v: sum(v[0::2]) / sum(v[1::2]) if sum(v[1::2]) > 0 else (_ for _ in ()).throw(BrakSensu("przychody ≤ 0")),
                     U, okres_d)
    wynik["marza_fcf_cykl"] = marza.id if marza else None
    if not marza:
        return
    fcf = k.wylicz(f"fcf_znormalizowany.{d}", "fcf_znormalizowany", f"marza_fcf_cykl × przychody.{S}",
                   [marza.id, f"przychody.{S}"], lambda m, r: m * r, P, okres_d, cap.waluta)
    wynik["fcf_znormalizowany"] = fcf.id if fcf else None
    if not fcf:
        return
    def m(nazwa, wzor, wej, fn, jedn=U):
        f = k.wylicz(f"{nazwa}.{d}", nazwa, wzor, wej, fn, jedn, okres_d)
        wynik[nazwa] = f.id if f else None
    m("fcf_yield_znormalizowany", "fcf_znormalizowany / kapitalizacja", [fcf.id, cap.id], lambda f, c: f / c)
    m("implikowany_wzrost_fcf_znormalizowany", f"wzrost FCF znormalizowanego przez {n} lat, przy którym wartość = kapitalizacja",
      [cap.id, fcf.id, gT, ke], lambda c, f, g, kk: implikowany_wzrost(c, f, n, g, kk))
    if wynik.get("wzrost_historyczny"):
        m("implikowany_cap_znormalizowany", "lata wzrostu FCF znormalizowanego w tempie historycznym, które uzasadniają kapitalizację",
          [cap.id, fcf.id, wynik["wzrost_historyczny"], gT, ke],
          lambda c, f, g, gt, kk: implikowany_cap(c, f, g, gt, kk, par["cap_max_lat"]), Jednostka.lata)


def cwk_uzasadnione(roe: float, g: float, ke: float) -> float:
    """C/WK = (ROE − g) ÷ (koszt kapitału − g)."""
    if ke <= g:
        raise BrakSensu("koszt kapitału nie jest wyższy od wzrostu rezydualnego")
    w = (roe - g) / (ke - g)
    if w <= 0:
        raise BrakSensu("ROE nie przekracza wzrostu rezydualnego; uzasadnione C/WK ≤ 0")
    return w


def roe_implikowane(cwk: float, g: float, ke: float) -> float:
    """ROE, przy którym uzasadnione C/WK równa się dzisiejszemu C/WK: g + C/WK × (koszt kapitału − g)."""
    if ke <= g:
        raise BrakSensu("koszt kapitału nie jest wyższy od wzrostu rezydualnego")
    return g + cwk * (ke - g)


def kapitalowa_wycena(k: Kalkulator, wynik: dict, par: dict, cap: Fakt, kw: Optional[Fakt], dn: Optional[Fakt],
                      gT: str, ke: str, okres_d: Okres, deweloper: bool) -> None:
    d = okres_d.koniec.isoformat()
    wynik["kapital_wlasny"] = kw.id if kw else None
    roe = k.okresy_fy("roe")[-par["okno_roe_lat"]:]
    if len(roe) < par["min_lat_roe"]:
        k.braki.append(f"wycena C/WK: tylko {len(roe)} lat ROE (minimum {par['min_lat_roe']})")
    else:
        sr = k.wylicz(f"roe_srednie.{d}", "roe_srednie", f"średnie ROE z {len(roe)} lat", [f.id for f in roe],
                      lambda *v: sum(v) / len(v), U, okres_d)
        wynik["roe_srednie"] = sr.id if sr else None
        if sr:
            f = k.wylicz(f"cwk_uzasadnione.{d}", "cwk_uzasadnione", "(roe_srednie − wzrost_rezydualny) / (koszt_kapitalu − wzrost_rezydualny)",
                         [sr.id, gT, ke], cwk_uzasadnione, X, okres_d)
            wynik["cwk_uzasadnione"] = f.id if f else None
    if wynik.get("c_wk"):
        f = k.wylicz(f"roe_implikowane.{d}", "roe_implikowane", "wzrost_rezydualny + c_wk × (koszt_kapitalu − wzrost_rezydualny)",
                     [wynik["c_wk"], gT, ke], roe_implikowane, U, okres_d)
        wynik["roe_implikowane"] = f.id if f else None
    if deweloper and kw and dn:
        f = k.wylicz(f"dlug_netto_do_kapitalu.{d}", "dlug_netto_do_kapitalu", "dlug_netto / kapital_wlasny", [dn.id, kw.id],
                     lambda a, b: a / b if b > 0 else (_ for _ in ()).throw(BrakSensu("kapitał własny ≤ 0")), X, okres_d)
        wynik["dlug_netto_do_kapitalu"] = f.id if f else None


def beta_sektorowa(k: Kalkulator, wynik: dict, par: dict, cap: Fakt, dn: Optional[Fakt], okres_d: Okres) -> None:
    """Beta sektorowa Damodarana przeliczona na zadłużenie spółki: β = β bez długu × (1 + (1 − t) × dług ÷ kapitalizacja).
    Kontrola bety skorygowanej; nie wchodzi do kosztu kapitału (decyzja właściciela z 12.11.2026)."""
    bu = ostatni(k, "beta_sektorowa_bez_dlugu")
    if not bu:
        return
    from .wskazniki import _stawka
    d = okres_d.koniec.isoformat()
    dlug = next((x for x in (dn.wejscia if dn and dn.wejscia else []) if x.startswith("dlug.")), None)
    t = _stawka(k)
    if dlug and t:
        f = k.wylicz(f"beta_sektorowa.{d}", "beta_sektorowa", "beta_sektorowa_bez_dlugu × (1 + (1 − stawka_podatku) × dlug / kapitalizacja)",
                     [bu.id, t, dlug, cap.id], lambda b, tt, dl, c: b * (1 + (1 - tt) * dl / c), Jednostka.liczba, okres_d)
    else:
        f = k.wylicz(f"beta_sektorowa.{d}", "beta_sektorowa", "beta_sektorowa_bez_dlugu (brak długu w danych: bez przeliczenia)",
                     [bu.id], lambda b: b, Jednostka.liczba, okres_d)
    wynik["beta_sektorowa"] = f.id if f else None
    b = k.fakt(wynik.get("beta")) if wynik.get("beta") else None
    if f and b and abs(b.wartosc - f.wartosc) > par["beta_rozbieznosc"]:
        branza = (bu.miejsce or {}).get("branza", "")
        k.ostrzezenia.append(f"Beta: beta użyta w koszcie kapitału ({b.id}) różni się od bety sektorowej Damodarana "
                             f"(branża „{branza}”) o więcej niż {par['beta_rozbieznosc']:g} — sprawdź okno regresji i branżę.")
