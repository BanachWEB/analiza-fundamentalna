"""Panel wskaźników: marże, FCF, dług, ROE, ROIC, dynamika.

Każdy wskaźnik to fakt wyliczony (wzór + wejścia). Gdy brakuje danych,
wskaźnik nie powstaje, a powód trafia do listy braków.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

from silnik.fakty.schemat import Fakt, Jednostka, Metoda, Okres, Rodzaj, Status

from .kalkulator import BrakSensu, Kalkulator, cagr, dodatnia_baza, podzial_akcji

U = Jednostka.ulamek
P = Jednostka.pieniadz
X = Jednostka.mnoznik

STAWKA_PODATKU = {"USD": 0.21, "PLN": 0.19}


def _stawka(k: Kalkulator) -> Optional[str]:
    fid = "stawka_podatku.zalozenie"
    if k.jest(fid):
        return fid
    przychody = k.okresy_fy()
    waluta = przychody[-1].waluta if przychody else None
    if waluta not in STAWKA_PODATKU:
        k.braki.append("stawka_podatku: nieznana waluta sprawozdań")
        return None
    k.r.dodaj(Fakt(
        id=fid, rodzaj=Rodzaj.zalozenie, pozycja="stawka_podatku", okres=Okres(typ="brak"),
        wartosc=STAWKA_PODATKU[waluta], jednostka=U, metoda=Metoda.kod, status=Status.jedno_zrodlo,
        uzasadnienie=f"Domyślna stawka ustawowa podatku dochodowego od firm ({'USA' if waluta == 'USD' else 'Polska'}); "
                     "do NOPAT w ROIC i wycenie.",
    ))
    return fid


def _opcjonalne(k: Kalkulator, ids: list[str]) -> list[str]:
    return [i for i in ids if k.jest(i)]


def dlug(k: Kalkulator, B: date) -> tuple[Optional[str], Optional[str]]:
    """(dług finansowy bez leasingu, zobowiązania leasingowe) na dzień B jako fakty wyliczone."""
    d = B.isoformat()
    okres = Okres(typ="dzien", koniec=B)
    zbiorcze = _opcjonalne(k, [f"dlug_dlugoterminowy.{d}", f"dlug_krotkoterminowy.{d}"])
    skladniki = _opcjonalne(k, [f"kredyty_dlugoterminowe.{d}", f"kredyty_krotkoterminowe.{d}",
                                f"obligacje_dlugoterminowe.{d}", f"obligacje_krotkoterminowe.{d}"])
    wejscia = zbiorcze or skladniki
    dlug_id = None
    if wejscia:
        f = k.wylicz(f"dlug.{d}", "dlug", " + ".join(wejscia), wejscia, lambda *a: sum(a), P, okres)
        dlug_id = f.id if f else None
    else:
        k.braki.append(f"dlug.{d}: brak pozycji długu (może spółka nie ma długu, może brak mapowania)")
    leasing = _opcjonalne(k, [f"zobowiazania_leasingowe.{d}"]) or _opcjonalne(
        k, [f"leasing_dlugoterminowy.{d}", f"leasing_krotkoterminowy.{d}"])
    leasing_id = None
    if leasing:
        f = k.wylicz(f"leasing.{d}", "leasing", " + ".join(leasing), leasing, lambda *a: sum(a), P, okres)
        leasing_id = f.id if f else None
    return dlug_id, leasing_id


def dla_okresu(k: Kalkulator, S: str, okres: Okres, B: date, B_prev: Optional[date]) -> None:
    """Wskaźniki dla okresu S (np. FY2025 albo TTM2026-09-30); B — dzień bilansu na koniec okresu."""
    def i(poz):
        return f"{poz}.{S}"

    d = B.isoformat()
    # marże
    if k.jest(i("zysk_brutto")):
        k.wylicz(i("marza_brutto"), "marza_brutto", "zysk_brutto / przychody", [i("zysk_brutto"), i("przychody")],
                 lambda z, p: z / p, U, okres)
    elif k.jest(i("koszt_sprzedazy")):
        k.wylicz(i("marza_brutto"), "marza_brutto", "(przychody - koszt_sprzedazy) / przychody",
                 [i("przychody"), i("koszt_sprzedazy")], lambda p, c: (p - c) / p, U, okres)
    k.wylicz(i("marza_operacyjna"), "marza_operacyjna", "zysk_operacyjny / przychody",
             [i("zysk_operacyjny"), i("przychody")], lambda z, p: z / p, U, okres)
    k.wylicz(i("marza_netto"), "marza_netto", "zysk_netto / przychody", [i("zysk_netto"), i("przychody")],
             lambda z, p: z / p, U, okres)
    ebitda = k.wylicz(i("ebitda"), "ebitda", "zysk_operacyjny + amortyzacja", [i("zysk_operacyjny"), i("amortyzacja")],
                      lambda z, a: z + a, P, okres)
    if ebitda:
        k.wylicz(i("marza_ebitda"), "marza_ebitda", "ebitda / przychody", [ebitda.id, i("przychody")],
                 lambda e, p: e / p, U, okres)
    if not k.jest(i("koszty_sprzedazy_i_zarzadu")) and k.jest(i("koszty_dystrybucji")) and k.jest(i("koszty_zarzadu")):
        k.wylicz(i("koszty_sprzedazy_i_zarzadu"), "koszty_sprzedazy_i_zarzadu", "koszty_dystrybucji + koszty_zarzadu",
                 [i("koszty_dystrybucji"), i("koszty_zarzadu")], lambda a, b: a + b, P, okres)

    # FCF
    capex = [i("capex")] + _opcjonalne(k, [i("capex_niematerialne")])
    fcf = k.wylicz(i("fcf"), "fcf", "przeplywy_operacyjne - " + " - ".join(c.split(".")[0] for c in capex),
                   [i("przeplywy_operacyjne")] + capex, lambda o, *c: o - sum(c), P, okres)
    if fcf:
        korekty = _opcjonalne(k, [i("sbc"), i("splata_leasingu")])
        wzor = "fcf" + "".join(f" - {c.split('.')[0]}" for c in korekty)
        fcfw = k.wylicz(i("fcf_wlascicieli"), "fcf_wlascicieli", wzor, [fcf.id] + korekty,
                        lambda f, *c: f - sum(c), P, okres)
        if fcfw:
            k.wylicz(i("konwersja_fcf"), "konwersja_fcf", "fcf_wlascicieli / zysk_netto", [fcfw.id, i("zysk_netto")],
                     lambda f, z: f / z, U, okres)
            k.wylicz(i("marza_fcf"), "marza_fcf", "fcf_wlascicieli / przychody", [fcfw.id, i("przychody")],
                     lambda f, p: f / p, U, okres)
    k.wylicz(i("capex_do_amortyzacji"), "capex_do_amortyzacji", " + ".join(c.split(".")[0] for c in capex) + " / amortyzacja",
             capex + [i("amortyzacja")], lambda *a: sum(a[:-1]) / a[-1], X, okres)

    # dług i bilans
    dlug_id, leasing_id = dlug(k, B)
    gotowka = _opcjonalne(k, [f"gotowka.{d}", f"inwestycje_krotkoterminowe.{d}"])
    okres_b = Okres(typ="dzien", koniec=B)
    dn = None
    if dlug_id and gotowka:
        dn = k.wylicz(f"dlug_netto.{d}", "dlug_netto", "dlug - " + " - ".join(g.split(".")[0] for g in gotowka),
                      [dlug_id] + gotowka, lambda dl, *g: dl - sum(g), P, okres_b)
    elif gotowka and not dlug_id:
        k.braki.append(f"dlug_netto.{d}: brak długu, nie liczę")
    if dn and ebitda:
        k.wylicz(i("dlug_netto_do_ebitda"), "dlug_netto_do_ebitda", "dlug_netto / ebitda", [dn.id, ebitda.id],
                 lambda a, b: _do_ebitda(a, b), X, okres)
        if leasing_id:
            k.wylicz(i("dlug_netto_z_leasingiem_do_ebitda"), "dlug_netto_z_leasingiem_do_ebitda",
                     "(dlug_netto + leasing) / ebitda", [dn.id, leasing_id, ebitda.id],
                     lambda a, l, b: _do_ebitda(a + l, b), X, okres)
    odsetki = _opcjonalne(k, [i("koszty_odsetek")]) or _opcjonalne(k, [i("koszty_finansowe")])
    if odsetki:
        k.wylicz(i("pokrycie_odsetek"), "pokrycie_odsetek", f"zysk_operacyjny / {odsetki[0].split('.')[0]}",
                 [i("zysk_operacyjny"), odsetki[0]], lambda z, o: z / o, X, okres)

    # rentowność kapitału (średnia z początku i końca okresu, gdy jest bilans z początku)
    kw = k.stan("kapital_wlasny", B) or k.stan("kapital_wlasny_z_udzialami_niekontrolujacymi", B)
    kw_p = (k.stan("kapital_wlasny", B_prev) or k.stan("kapital_wlasny_z_udzialami_niekontrolujacymi", B_prev)) if B_prev else None
    if kw:
        wej = [i("zysk_netto"), kw.id] + ([kw_p.id] if kw_p else [])
        k.wylicz(i("roe"), "roe", "zysk_netto / średni kapitał_wlasny" if kw_p else "zysk_netto / kapital_wlasny (koniec)",
                 wej, lambda z, *kk: z / (sum(kk) / len(kk)), U, okres)
    stawka = _stawka(k)
    kapital_razem = k.stan("kapital_wlasny_z_udzialami_niekontrolujacymi", B) or kw
    if stawka and kapital_razem and dlug_id and gotowka:
        wej = [i("zysk_operacyjny"), stawka, kapital_razem.id, dlug_id] + gotowka
        k.wylicz(i("roic"), "roic", "zysk_operacyjny × (1 - stawka_podatku) / (kapital_wlasny + dlug - gotowka)", wej,
                 lambda z, t, kap, dl, *g: z * (1 - t) / (kap + dl - sum(g)), U, okres)


def _do_ebitda(dlug_netto: float, ebitda: float) -> float:
    """Dług netto ÷ EBITDA. Przy EBITDA ≤ 0 wskaźnik nie ma sensu: ujemny dług netto podzielony
    przez ujemną EBITDA daje dodatni wynik, który wygląda jak zadłużenie. Gotówkę netto
    (ujemny dług netto przy dodatniej EBITDA) raport opisuje słowami „gotówka netto”."""
    if ebitda <= 0:
        raise BrakSensu("EBITDA ≤ 0, dług netto ÷ EBITDA nie ma sensu")
    return dlug_netto / ebitda


def _bez_podzialu(x: float, y: float) -> float:
    if podzial_akcji(x, y):
        raise BrakSensu("prawdopodobny podział albo scalenie akcji między okresami; dane nieporównywalne")
    return x / y - 1


def _dynamika(k: Kalkulator, fid: str, pozycja: str, f, p, lat, okres) -> None:
    """Wzrost r/r (lat=None) albo CAGR; dla EPS sprawdza, czy między okresami nie było podziału akcji."""
    wej = [f.id, p.id]
    S, Sp = f.id.split(".", 1)[1], p.id.split(".", 1)[1]
    akcje = [f"liczba_akcji_rozwodniona.{S}", f"liczba_akcji_rozwodniona.{Sp}"]
    if f.pozycja == "eps_rozwodniony" and all(k.jest(a) for a in akcje):
        wej += akcje

    def fn(a, b, *sh):
        if sh and podzial_akcji(sh[0], sh[1]):
            raise BrakSensu("prawdopodobny podział akcji między okresami; EPS nieporównywalny")
        return dodatnia_baza(a, b) if lat is None else cagr(a, b, lat)

    wzor = f"{f.id} / {p.id} - 1" if lat is None else f"({f.id} / {p.id})^(1/{lat}) - 1"
    k.wylicz(fid, pozycja, wzor, wej, fn, U, okres)


def dynamika(k: Kalkulator) -> None:
    lata = k.okresy_fy()
    for pozycja in ("przychody", "zysk_operacyjny", "zysk_netto", "eps_rozwodniony", "fcf_wlascicieli"):
        po_roku = {f.id.split(".", 1)[1]: f for f in k.okresy_fy(pozycja)}
        kolejne = [f.id.split(".", 1)[1] for f in lata]
        for n, S in enumerate(kolejne):
            if S not in po_roku:
                continue
            f = po_roku[S]
            okres = Okres(typ="FY", poczatek=f.okres.poczatek, koniec=f.okres.koniec)
            if n >= 1 and kolejne[n - 1] in po_roku:
                p = po_roku[kolejne[n - 1]]
                _dynamika(k, f"wzrost_{pozycja}.{S}", f"wzrost_{pozycja}", f, p, None, okres)
            for lat in (3, 5):
                if n >= lat and kolejne[n - lat] in po_roku:
                    p = po_roku[kolejne[n - lat]]
                    _dynamika(k, f"cagr_{pozycja}_{lat}l.{S}", f"cagr_{pozycja}_{lat}l", f, p, lat, okres)
    # dynamika bieżącego okresu narastającego r/r
    for f in [f for f in k.r.fakty() if f.pozycja in ("przychody", "zysk_operacyjny", "zysk_netto")
              and f.okres.typ.value in ("Q1", "H1", "M9") and f.status != Status.odrzucony]:
        rok_wczesniej = next((g for g in k.r.fakty() if g.pozycja == f.pozycja and g.okres.typ == f.okres.typ
                              and abs((g.okres.koniec - (f.okres.koniec - timedelta(days=365))).days) <= 10), None)
        if rok_wczesniej:
            S = f.id.split(".", 1)[1]
            k.wylicz(f"wzrost_{f.pozycja}.{S}", f"wzrost_{f.pozycja}", f"{f.id} / {rok_wczesniej.id} - 1",
                     [f.id, rok_wczesniej.id], dodatnia_baza, U,
                     Okres(typ=f.okres.typ, poczatek=f.okres.poczatek, koniec=f.okres.koniec))
    # liczba akcji (rozwodnienie)
    akcje = {f.id.split(".", 1)[1]: f for f in k.okresy_fy("liczba_akcji_rozwodniona")}
    kolejne = sorted(akcje, key=lambda s: akcje[s].okres.koniec)
    for a, b in zip(kolejne, kolejne[1:]):
        f, p = akcje[b], akcje[a]
        k.wylicz(f"zmiana_liczby_akcji.{b}", "zmiana_liczby_akcji", f"{f.id} / {p.id} - 1", [f.id, p.id],
                 _bez_podzialu, U, Okres(typ="FY", poczatek=f.okres.poczatek, koniec=f.okres.koniec))
    # liczba akcji na koniec roku obrotowego: średnia ważona zaniża skutek emisji z końca roku
    for poprz, f in zip(lata, lata[1:]):
        a, p = _akcje_na_koniec(k, f.okres.koniec), _akcje_na_koniec(k, poprz.okres.koniec)
        if a is None or p is None:
            continue
        S = f.id.split(".", 1)[1]
        k.wylicz(f"zmiana_liczby_akcji_koniec.{S}", "zmiana_liczby_akcji_koniec", f"{a.id} / {p.id} - 1",
                 [a.id, p.id], _bez_podzialu, U, Okres(typ="FY", poczatek=f.okres.poczatek, koniec=f.okres.koniec))


def _akcje_na_koniec(k: Kalkulator, dzien: date) -> Optional[Fakt]:
    """Liczba akcji na dzień bilansowy: z bilansu (akcje_koniec_okresu), a gdy jej brak — akcje w obrocie
    z dnia oddalonego najwyżej o 5 dni (lata 52/53-tygodniowe)."""
    return k.stan("akcje_koniec_okresu", dzien) or k.stan("akcje_w_obrocie", dzien)


def oblicz(k: Kalkulator, ttm_koniec: Optional[date]) -> None:
    lata = k.okresy_fy()
    for n, f in enumerate(lata):
        S = f.id.split(".", 1)[1]
        B_prev = lata[n - 1].okres.koniec if n else None
        dla_okresu(k, S, Okres(typ="FY", poczatek=f.okres.poczatek, koniec=f.okres.koniec), f.okres.koniec, B_prev)
    if ttm_koniec and k.jest(f"przychody.TTM{ttm_koniec.isoformat()}"):
        S = f"TTM{ttm_koniec.isoformat()}"
        t = k.fakt(f"przychody.{S}")
        rok_wczesniej = ttm_koniec - timedelta(days=365)
        B_prev = rok_wczesniej if k.stan("kapital_wlasny", rok_wczesniej, 10) else None
        if B_prev:
            B_prev = k.stan("kapital_wlasny", rok_wczesniej, 10).okres.koniec
        dla_okresu(k, S, Okres(typ="TTM", poczatek=t.okres.poczatek, koniec=t.okres.koniec), ttm_koniec, B_prev)
    dynamika(k)
