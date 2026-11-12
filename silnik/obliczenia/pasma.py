"""Historyczne pasma wyceny (specyfikacja 1.1, punkt 7; decyzja właściciela z 12.11.2026).

Dla każdego tygodnia z historii notowań w archiwum (do 5 lat) silnik liczy mnożnik z kursu i danych
z ostatniego roku obrotowego, którego raport był już opublikowany (koniec roku + opóźnienie z konfiguracji).
Wynik: percentyle mnożnika i percentyl dzisiejszego mnożnika na tle historii spółki. Silnik nie przelicza
pasm na kursy, bo punkty wejścia ustala inny segment.
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Optional

from silnik.fakty.schemat import Fakt, Jednostka, Okres, Status

from .kalkulator import BrakSensu, Kalkulator
from .wycena import parametry

X, U = Jednostka.mnoznik, Jednostka.ulamek

# mnożnik → (opis, pozycje roczne w mianowniku/liczniku, czy dodatnia baza wymagana, jednostka)
MNOZNIKI = {
    "c_z": ("kapitalizacja ÷ zysk netto", "zysk_netto", X),
    "ev_ebit": ("EV ÷ zysk operacyjny", "zysk_operacyjny", X),
    "ev_ebitda": ("EV ÷ EBITDA", "ebitda", X),
    "c_wk": ("kapitalizacja ÷ kapitał własny", "kapital_wlasny", X),
    "fcf_yield": ("FCF dla właścicieli ÷ kapitalizacja", "fcf_wlascicieli", U),
}


def percentyl(wartosci: list[float], p: float) -> float:
    """Percentyl z interpolacją liniową (jak numpy, metoda „linear”)."""
    s = sorted(wartosci)
    if not s:
        raise BrakSensu("brak wartości")
    pos = (len(s) - 1) * p / 100
    lo = int(pos)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (pos - lo)


def ranga(wartosci: list[float], x: float) -> float:
    """Udział wartości historycznych mniejszych albo równych x."""
    return sum(1 for v in wartosci if v <= x) / len(wartosci)


def sesje_z_archiwum(k: Kalkulator, katalog: Path):
    """Sesje spółki z dokumentów notowań w archiwum (te same, z których silnik wziął kurs i obroty)."""
    from silnik.pobieranie import rynek
    from silnik.pobieranie.archiwum import Archiwum

    zrodlowe = [f for f in k.r.fakty() if f.pozycja == "obroty_dzienne_60s" and f.status != Status.odrzucony]
    if not zrodlowe:
        return [], []
    f = max(zrodlowe, key=lambda f: f.okres.koniec)
    ids = (f.miejsce or {}).get("dokumenty") or [f.dokument]
    archiwum = Archiwum(k.r.ticker, katalog)
    po_id = {d.id: d for d in archiwum.rejestr.dokumenty}
    sesje = []
    for i in ids:
        d = po_id.get(i)
        if d is None:
            continue
        tekst = archiwum.tekst(i)
        if d.zrodlo.startswith("Yahoo"):
            sesje += rynek.sesje_yahoo(tekst)
        elif d.zrodlo.startswith("Biznesradar"):
            sesje += rynek.sesje_biznesradar(tekst)
        elif d.zrodlo.startswith("Stock Analysis"):
            sesje += rynek.sesje_stockanalysis(tekst)
    unik = {s.dzien: s for s in sesje}
    return sorted(unik.values(), key=lambda s: s.dzien), ids


def _dane_roczne(k: Kalkulator) -> list[dict]:
    """Dla każdego roku obrotowego: koniec roku i id faktów potrzebnych do mnożników."""
    lata = []
    for f in k.okresy_fy("przychody"):
        S = f.id.split(".", 1)[1]
        B = f.okres.koniec
        akcje = k.stan("akcje_koniec_okresu", B) or k.fakt(f"liczba_akcji_rozwodniona.{S}")
        if not akcje:
            continue
        rok = {"koniec": B, "akcje": akcje.id}
        for poz in ("zysk_netto", "zysk_operacyjny", "ebitda", "fcf_wlascicieli"):
            if k.jest(f"{poz}.{S}"):
                rok[poz] = f"{poz}.{S}"
        for poz in ("kapital_wlasny", "dlug_netto"):
            st = k.stan(poz, B)
            if st:
                rok[poz] = st.id
        lata.append(rok)
    return lata


def _mnoznik(m: str, kap: float, rok: dict, k: Kalkulator) -> Optional[float]:
    poz = MNOZNIKI[m][1]
    if poz not in rok:
        return None
    baza = k.fakt(rok[poz]).wartosc_bazowa()
    if m == "fcf_yield":
        return baza / kap
    if baza <= 0:
        return None
    licznik = kap
    if m.startswith("ev_"):
        if "dlug_netto" not in rok:
            return None
        licznik = kap + k.fakt(rok["dlug_netto"]).wartosc_bazowa()
    return licznik / baza


def oblicz(k: Kalkulator, katalog: Optional[Path], wycena: dict) -> Optional[dict]:
    if not katalog or not wycena.get("kapitalizacja"):
        return None
    cfg = parametry()["pasma"]
    try:
        sesje, ids = sesje_z_archiwum(k, katalog)
    except Exception as e:  # uszkodzony albo nieznany dokument notowań
        k.braki.append(f"pasma wyceny: nie odczytam historii notowań ({e})")
        return None
    from silnik.pobieranie.rynek import tygodniowe

    tyg = tygodniowe(sesje)
    lata = _dane_roczne(k)
    if len(tyg) < cfg["min_tygodni"] or not lata:
        k.braki.append(f"pasma wyceny: za krótka historia notowań ({len(tyg)} tygodni, minimum {cfg['min_tygodni']}) "
                       "albo brak danych rocznych z liczbą akcji")
        return None
    cap = k.fakt(wycena["kapitalizacja"])
    D = cap.okres.koniec
    okres_d = Okres(typ="dzien", koniec=D)
    opozn = timedelta(days=cfg["opoznienie_raportu_dni"])
    wynik: dict = {"od": tyg[0][0], "do": tyg[-1][0], "tygodni": len(tyg), "mnozniki": {}}
    for m, (opis, _, jedn) in MNOZNIKI.items():
        wartosci, uzyte = [], set()
        for dzien, kurs in tyg:
            rok = next((r for r in reversed(lata) if r["koniec"] + opozn <= dzien), None)
            if rok is None:
                continue
            kap = kurs * k.fakt(rok["akcje"]).wartosc_bazowa()
            v = _mnoznik(m, kap, rok, k)
            if v is not None:
                wartosci.append(v)
                uzyte.add(rok["akcje"])
                uzyte.update(rok[p] for p in (MNOZNIKI[m][1], "dlug_netto") if p in rok and (p != "dlug_netto" or m.startswith("ev_")))
        if len(wartosci) < cfg["min_tygodni"] // 2:
            k.braki.append(f"pasmo {m}: tylko {len(wartosci)} tygodni z dodatnią podstawą mnożnika")
            continue
        wej = sorted(uzyte) + [cap.id]
        opis_ = (f"{opis}: tygodniowe zamknięcia z dokumentów {', '.join(ids)} ({tyg[0][0]}–{tyg[-1][0]}) × liczba akcji "
                 f"z ostatniego roku obrotowego opublikowanego co najmniej {cfg['opoznienie_raportu_dni']} dni wcześniej")
        ids_m = {}
        for p in cfg["percentyle"]:
            v = percentyl(wartosci, p)
            f = k.wylicz(f"pasmo_{m}_p{p}.{D.isoformat()}", f"pasmo_{m}_p{p}", f"percentyl {p} — {opis_}", wej,
                         lambda *a, v=v: v, jedn, okres_d)
            ids_m[p] = f.id if f else None
        dzis = wycena.get(m)
        if dzis and k.jest(dzis):
            x = k.fakt(dzis).wartosc
            f = k.wylicz(f"percentyl_{m}.{D.isoformat()}", f"percentyl_{m}",
                         f"udział tygodni z mnożnikiem ≤ dzisiejszemu ({dzis}) — {opis_}", wej + [dzis],
                         lambda *a, x=x: ranga(wartosci, x), U, okres_d)
            ids_m["dzis"] = dzis
            ids_m["percentyl"] = f.id if f else None
        ids_m["tygodni"] = len(wartosci)
        wynik["mnozniki"][m] = ids_m
    return wynik
