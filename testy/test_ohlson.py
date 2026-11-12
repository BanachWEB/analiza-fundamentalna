"""Ohlson O-score: parsery FRED i NBP oraz wynik policzony ręcznie."""

from datetime import date

import pytest

from silnik.fakty.rejestr import RejestrFaktow
from silnik.fakty.schemat import Fakt
from silnik.obliczenia import jakosc
from silnik.obliczenia.kalkulator import Kalkulator
from silnik.pobieranie import makro

D = date


def F(id, wartosc, typ, koniec, poczatek=None, jednostka="pieniadz", waluta="USD"):
    okres = {"typ": typ, "koniec": koniec}
    if poczatek:
        okres["poczatek"] = poczatek
    return Fakt(id=id, rodzaj="raportowany", pozycja=id.split(".")[0], okres=okres, wartosc=wartosc,
                jednostka=jednostka, waluta=waluta if jednostka == "pieniadz" else None, metoda="xbrl",
                status="zweryfikowany", dokument="doc-001", miejsce={"xbrl": "x"})


def test_parser_fred_i_koniec_kwartalu():
    csv = "observation_date,GDPDEF\n1968-01-01,17.981\n1968-04-01,18.171\n1968-07-01,.\n1968-10-01,18.5\n"
    s = makro.deflator_fred(csv)
    assert s[D(1968, 3, 31)] == 17.981
    assert s[D(1968, 6, 30)] == 18.171
    assert D(1968, 9, 30) not in s  # brak obserwacji
    assert s[D(1968, 12, 31)] == 18.5
    assert makro.kwartaly_roku(2025) == [D(2025, 3, 31), D(2025, 6, 30), D(2025, 9, 30), D(2025, 12, 31)]


def test_parser_nbp_bierze_ostatni_kurs():
    tresc = ('{"table":"A","code":"USD","rates":[{"no":"250/A/NBP/2025","effectiveDate":"2025-12-30","mid":3.6},'
             '{"no":"251/A/NBP/2025","effectiveDate":"2025-12-31","mid":3.6016}]}')
    assert makro.kurs_nbp(tresc) == (D(2025, 12, 31), 3.6016, "251/A/NBP/2025")


def rejestr(waluta="USD", mnoznik=1.0, kurs=None):
    """Deflator stały (indeks = 100), aktywa 100 000 USD → SIZE = ln(1000)."""
    r = RejestrFaktow("X", D(2026, 11, 10))
    for rok, ni in ((2024, 5000), (2025, 10000)):
        r.dodaj(F(f"przychody.FY{rok}", 50000 * mnoznik, "FY", D(rok, 12, 31), D(rok, 1, 1), waluta=waluta))
        r.dodaj(F(f"zysk_netto.FY{rok}", ni * mnoznik, "FY", D(rok, 12, 31), D(rok, 1, 1), waluta=waluta))
    B = D(2025, 12, 31)
    for poz, v in (("aktywa", 100000), ("zobowiazania", 50000), ("aktywa_obrotowe", 40000),
                   ("zobowiazania_krotkoterminowe", 20000)):
        r.dodaj(F(f"{poz}.{B.isoformat()}", v * mnoznik, "dzien", B, waluta=waluta))
    r.dodaj(F("amortyzacja.FY2025", 5000 * mnoznik, "FY", B, D(2025, 1, 1), waluta=waluta))
    for rok in (1968, 2024):
        for kw in makro.kwartaly_roku(rok):
            r.dodaj(F(f"deflator_pkb_usa.{kw.isoformat()}", 20.0, "dzien", kw, jednostka="punkty"))
    if kurs:
        dz, v = kurs
        r.dodaj(F(f"kurs_usd_pln.{dz.isoformat()}", v, "dzien", dz, jednostka="mnoznik"))
    return r


# −1,32 − 0,407·ln(1000) + 6,03·0,5 − 1,43·0,2 + 0,0757·0,5 − 2,37·0,1 − 1,83·0,3 − 0,521·(5000/15000)
OCZEKIWANE_O = -2.324273


def test_ohlson_reczne_usd():
    r = rejestr()
    k = Kalkulator(r)
    jakosc.ohlson(k, k.okresy_fy())
    assert r["ohlson_o.FY2025"].wartosc == pytest.approx(OCZEKIWANE_O, abs=1e-5)
    assert r["ohlson_p.FY2025"].wartosc == pytest.approx(1 / (1 + 2.718281828 ** -OCZEKIWANE_O), abs=1e-6)
    assert "ohlson_o.FY2024" not in r  # pierwszy rok nie ma roku poprzedniego


def test_ohlson_pln_przelicza_aktywa_kursem_sprzed_bilansu():
    # aktywa w PLN = 4 × USD; kurs z 29.12 (bilans 31.12 w dzień bez tabeli NBP)
    r = rejestr("PLN", 4.0, (D(2025, 12, 29), 4.0))
    k = Kalkulator(r)
    jakosc.ohlson(k, k.okresy_fy())
    assert r["ohlson_o.FY2025"].wartosc == pytest.approx(OCZEKIWANE_O, abs=1e-5)
    assert "kurs_usd_pln.2025-12-29" in r["ohlson_o.FY2025"].wejscia


def test_ohlson_bez_kursu_zapisuje_brak():
    r = rejestr("PLN", 4.0)
    k = Kalkulator(r)
    jakosc.ohlson(k, k.okresy_fy())
    assert "ohlson_o.FY2025" not in r
    assert any(b.startswith("ohlson_o.FY2025") and "kurs_usd_pln" in b for b in k.braki)


def test_ohlson_inna_waluta_to_brak():
    r = rejestr("EUR")
    k = Kalkulator(r)
    jakosc.ohlson(k, k.okresy_fy())
    assert "ohlson_o.FY2025" not in r
    assert any("EUR/USD" in b for b in k.braki)


def test_raport_podaje_tylko_procent_upadlosci():
    """Decyzja właściciela z 12.11.2026: jedna liczba w procentach, bez wartości O-score."""
    from silnik.obliczenia.raport import obliczenia_md
    r = rejestr()
    k = Kalkulator(r)
    jakosc.ohlson(k, k.okresy_fy())
    tekst = obliczenia_md(k, {"ttm": None, "wycena": {}, "karta": []})
    linia = next(l for l in tekst.splitlines() if "upadłości" in l and l.startswith("- "))
    assert linia.startswith("- Prawdopodobieństwo upadłości w ciągu roku (model Ohlsona): ")
    assert "%" in linia and "O-score" not in tekst
