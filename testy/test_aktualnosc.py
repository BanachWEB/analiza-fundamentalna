"""Ostrzeżenia o nieaktualnym materiale od właściciela (specyfikacja 1.1, punkt 3.3, zasada 6)."""

from datetime import date

from silnik.fakty.rejestr import RejestrFaktow
from silnik.fakty.schemat import Fakt
from silnik.obliczenia import aktualnosc
from silnik.obliczenia.kalkulator import Kalkulator

D = date(2026, 11, 12)


def F(id, v, jedn="pieniadz_na_akcje", metoda="api", dzien=D, **kw):
    okres = kw.pop("okres", {"typ": "dzien", "koniec": dzien})
    waluta = "USD" if jedn in ("pieniadz", "pieniadz_na_akcje") else None
    return Fakt(id=id, pozycja=id.split(".")[0], okres=okres, wartosc=v, jednostka=jedn, waluta=waluta,
                rodzaj=kw.pop("rodzaj", "raportowany"), metoda=metoda, status="jedno_zrodlo", dokument=kw.pop("dokument", "doc-001"),
                miejsce={}, **kw)


def kalk(*fakty):
    r = RejestrFaktow("X", D)
    for f in fakty:
        r.dodaj(f)
    return Kalkulator(r)


def test_arkusz_aktualny_bez_ostrzezen():
    k = kalk(F("kurs.2026-11-11", 100.0), F("kurs_arkusz.2026-11-12", 105.0, metoda="wklejka", dokument="doc-009"),
             F("eps_prognoza_arkusz.2026-11-12", 5.5, metoda="wklejka", dokument="doc-009"),
             F("eps_rozwodniony.FY2025", 5.0, okres={"typ": "FY", "koniec": date(2025, 12, 31)}))
    tr = {"kurs_arkusz": "kurs_arkusz.2026-11-12", "eps_prognoza_arkusz": "eps_prognoza_arkusz.2026-11-12", "dokument": "doc-009"}
    assert aktualnosc.sprawdz(k, tr, {}) == []
    assert abs(k.r["rozbieznosc_kursu_arkusza.2026-11-12"].wartosc - 0.05) < 1e-9


def test_arkusz_nieaktualny_kurs_i_eps():
    k = kalk(F("kurs.2026-11-11", 150.0), F("kurs_arkusz.2026-11-12", 100.0, metoda="wklejka", dokument="doc-009"),
             F("eps_prognoza_arkusz.2026-11-12", 3.0, metoda="wklejka", dokument="doc-009"),
             F("eps_rozwodniony.FY2025", 5.0, okres={"typ": "FY", "koniec": date(2025, 12, 31)}))
    tr = {"kurs_arkusz": "kurs_arkusz.2026-11-12", "eps_prognoza_arkusz": "eps_prognoza_arkusz.2026-11-12", "dokument": "doc-009"}
    ostrz = aktualnosc.sprawdz(k, tr, {})
    assert len(ostrz) == 2 and "kurs w arkuszu" in ostrz[0] and "prognoza EPS" in ostrz[1]
    assert k.ostrzezenia == ostrz


def test_stara_wklejka_i_rozbiezny_konsensus():
    stara = F("cena_docelowa_srednia.2026-09-01", 120.0, metoda="wklejka", dzien=date(2026, 9, 1), rodzaj="prognoza",
              dostawca="InvestingPro", data_prognozy=date(2026, 9, 1), liczba_analitykow=30, dokument="doc-005")
    swieza = F("cena_docelowa_srednia.2026-11-11", 100.0, metoda="parser_strony", dzien=date(2026, 11, 11), rodzaj="prognoza",
               dostawca="Stock Analysis", data_prognozy=date(2026, 11, 11), liczba_analitykow=40, dokument="doc-002")
    k = kalk(stara, swieza)
    ostrz = aktualnosc.sprawdz(k, {}, {})
    assert any("starsze niż 30 dni" in o and "cena_docelowa_srednia.2026-09-01" in o for o in ostrz)
    assert any(o.startswith("Konsensus:") and "+20%" in o for o in ostrz)
