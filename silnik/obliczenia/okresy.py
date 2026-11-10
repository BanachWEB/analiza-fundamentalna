"""Okresy pochodne: kwartały z danych narastających i TTM (ostatnie 12 miesięcy).

- Q4 = rok − 9 miesięcy narastająco; Q2 = półrocze − Q1; Q3 = 9 miesięcy − półrocze.
- TTM = ostatni rok obrotowy + bieżący okres narastający − ten sam okres rok wcześniej.
Wszystko powstaje przez RejestrFaktow.wylicz, więc każdy wynik ma wzór, wejścia i status.
"""

from __future__ import annotations

from datetime import date, timedelta

from silnik.fakty.schemat import Fakt, Jednostka, Okres, Status

from .kalkulator import Kalkulator

NIEADDYTYWNE = {"liczba_akcji_rozwodniona"}
TYPY_NARASTAJACE = ("Q1", "H1", "M9")


def _przeplywowe(k: Kalkulator) -> dict[str, list[Fakt]]:
    wynik: dict[str, list[Fakt]] = {}
    for f in k.r.fakty():
        if f.status == Status.odrzucony or f.okres.typ.value in ("dzien", "brak", "TTM"):
            continue
        if f.rodzaj.value not in ("raportowany", "wyliczony") or f.pozycja.startswith(("marza", "wzrost", "cagr")):
            continue
        wynik.setdefault(f.pozycja, []).append(f)
    return wynik


def _blisko(a: date, b: date, dni: int = 7) -> bool:
    return abs((a - b).days) <= dni


def uzupelnij_skladniki(k: Kalkulator) -> None:
    """Pozycje, które spółki podają w częściach albo wcale (z jawnym wzorem w rejestrze).

    - amortyzacja = amortyzacja środków trwałych + amortyzacja WNiP (np. Microsoft od FY2024);
    - zobowiązania = pasywa razem − kapitał własny (np. Walmart nie podaje zobowiązań razem).
    """
    for f in list(k.r.fakty()):
        if f.pozycja == "amortyzacja_srodkow_trwalych" and f.status != Status.odrzucony:
            S = f.id.split(".", 1)[1]
            if not k.jest(f"amortyzacja.{S}") and k.jest(f"amortyzacja_wnip.{S}"):
                k.wylicz(f"amortyzacja.{S}", "amortyzacja", "amortyzacja_srodkow_trwalych + amortyzacja_wnip",
                         [f.id, f"amortyzacja_wnip.{S}"], lambda a, b: a + b, f.jednostka, f.okres, f.waluta)
        if f.pozycja == "pasywa_razem" and f.status != Status.odrzucony:
            d = f.id.split(".", 1)[1]
            if k.jest(f"zobowiazania.{d}"):
                continue
            kapital = next((x for x in (f"kapital_wlasny_z_udzialami_niekontrolujacymi.{d}", f"kapital_wlasny.{d}")
                            if k.jest(x)), None)
            if kapital:
                k.wylicz(f"zobowiazania.{d}", "zobowiazania", f"pasywa_razem - {kapital.split('.')[0]}",
                         [f.id, kapital], lambda a, b: a - b, f.jednostka, f.okres, f.waluta)


def dodaj_kwartaly(k: Kalkulator) -> None:
    for pozycja, fakty in _przeplywowe(k).items():
        if pozycja in NIEADDYTYWNE or fakty[0].jednostka not in (Jednostka.pieniadz, Jednostka.pieniadz_na_akcje):
            continue
        po_typie = {}
        for f in fakty:
            po_typie.setdefault(f.okres.typ.value, []).append(f)
        for fy in po_typie.get("FY", []):
            etykieta = fy.id.split(".", 1)[1]  # np. FY2025
            s = fy.okres.poczatek

            def znajdz(typ):
                return next((f for f in po_typie.get(typ, []) if f.okres.poczatek and _blisko(f.okres.poczatek, s)), None)

            q1, h1, m9 = znajdz("Q1"), znajdz("H1"), znajdz("M9")
            pary = [("Q4", fy, m9), ("Q3", m9, h1), ("Q2", h1, q1)]
            for typ, duzy, maly in pary:
                if duzy is None or maly is None:
                    continue
                fid = f"{pozycja}.{etykieta}{typ}"
                if k.jest(fid):
                    continue
                okres = Okres(typ=typ, poczatek=maly.okres.koniec + timedelta(days=1), koniec=duzy.okres.koniec)
                k.wylicz(fid, pozycja, f"{duzy.id} - {maly.id}", [duzy.id, maly.id], lambda a, b: a - b,
                         duzy.jednostka, okres, duzy.waluta)


def koniec_ttm(k: Kalkulator) -> date | None:
    """Koniec ostatniego okresu sprawozdawczego (wg przychodów)."""
    fakty = [f for f in _przeplywowe(k).get("przychody", []) if f.okres.typ.value in ("FY",) + TYPY_NARASTAJACE]
    return max((f.okres.koniec for f in fakty), default=None)


def dodaj_ttm(k: Kalkulator) -> date | None:
    E = koniec_ttm(k)
    if E is None:
        return None
    for pozycja, fakty in _przeplywowe(k).items():
        fid = f"{pozycja}.TTM{E.isoformat()}"
        okres = Okres(typ="TTM", poczatek=date(E.year - 1, E.month, min(E.day, 28)) + timedelta(days=1) if E.day <= 28
                      else E - timedelta(days=364), koniec=E)
        fy = next((f for f in fakty if f.okres.typ.value == "FY" and f.okres.koniec == E), None)
        if fy:
            k.wylicz(fid, pozycja, f"{fy.id}", [fy.id], lambda a: a, fy.jednostka, okres, fy.waluta)
            continue
        biezacy = next((f for f in fakty if f.okres.typ.value in TYPY_NARASTAJACE and f.okres.koniec == E), None)
        if biezacy is None:
            continue
        if pozycja in NIEADDYTYWNE:
            k.wylicz(fid, pozycja, f"{biezacy.id} (ostatni okres)", [biezacy.id], lambda a: a, biezacy.jednostka, okres)
            continue
        poprzedni = next((f for f in fakty if f.okres.typ == biezacy.okres.typ
                          and _blisko(f.okres.koniec, E - timedelta(days=365), 10)), None)
        rok = next((f for f in fakty if f.okres.typ.value == "FY"
                    and _blisko(f.okres.koniec, biezacy.okres.poczatek - timedelta(days=1), 5)), None)
        if poprzedni and rok:
            k.wylicz(fid, pozycja, f"{rok.id} + {biezacy.id} - {poprzedni.id}", [rok.id, biezacy.id, poprzedni.id],
                     lambda r, b, p: r + b - p, biezacy.jednostka, okres, biezacy.waluta)
    return E
