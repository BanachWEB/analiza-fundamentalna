"""Profil ryzyka kursu i beta sektorowa Damodarana (specyfikacja 1.1, punkt 7)."""

from datetime import date, timedelta

import pytest

from silnik.obliczenia import wycena
from silnik.obliczenia.raport import ryzyko_tabela
from silnik.pobieranie import rynek

from test_typy_spolek import fakt, rejestr


def tyg(ceny, start=date(2024, 1, 5)):
    return [(start + timedelta(weeks=i), c) for i, c in enumerate(ceny)]


def test_obsuniecie_z_powrotem_i_bez():
    ob = rynek.obsuniecie(tyg([100, 120, 90, 60, 80, 125, 130]))
    assert ob["wartosc"] == pytest.approx(60 / 120 - 1)
    assert ob["szczyt"] == date(2024, 1, 12) and ob["dolek"] == date(2024, 1, 26)
    assert ob["powrot"] == date(2024, 2, 9)
    ob = rynek.obsuniecie(tyg([100, 80, 90]))
    assert ob["powrot"] is None


def test_zmiennosc_i_korelacja():
    a = tyg([100 * (1.01 if i % 2 else 0.99) ** i for i in range(60)])
    assert rynek.zmiennosc_roczna(a) > 0
    assert rynek.korelacja(a, a) == pytest.approx(1.0)
    odwrotny = tyg([100 / c for _, c in a])
    assert rynek.korelacja(a, odwrotny) < -0.5  # kurs odwrotny: stopy zwrotu przeciwnego znaku


def _sesje(dni, mnoznik, start=date(2021, 11, 1)):
    s, i_, ci, cs, n = [], [], 100.0, 50.0, 0
    zwroty = [0.004, -0.003, 0.002, -0.001, 0.003]
    for d in range(dni):
        dz = start + timedelta(days=d)
        if dz.weekday() >= 5:
            continue
        r = zwroty[n % len(zwroty)]
        n += 1
        ci *= 1 + r
        cs *= 1 + mnoznik * r
        i_.append(rynek.Sesja(dz, ci, 1.0))
        s.append(rynek.Sesja(dz, cs, 1.0))
    return s, i_


def test_fakty_profilu():
    s, i_ = _sesje(5 * 366, 2.0)
    fakty = {f.pozycja: f for f in rynek.fakty_profilu(s, ["doc-001"], i_, ["doc-002"], "S&P 500")}
    assert {"zmiennosc_roczna", "max_obsuniecie", "korelacja_z_indeksem", "indeks_zmiennosc_roczna",
            "indeks_max_obsuniecie"} <= set(fakty)
    assert fakty["zmiennosc_roczna"].wartosc == pytest.approx(2 * fakty["indeks_zmiennosc_roczna"].wartosc, rel=0.05)
    assert fakty["korelacja_z_indeksem"].wartosc > 0.99
    assert rynek.fakty_profilu(s[:300], ["doc-001"], i_, ["doc-002"], "S&P 500") == []


DAMODARAN = """<html><body><table>
<tr><td>Date updated:</td><td>05-Jan-26</td></tr>
<tr><td>Industry Name</td><td>Number of firms</td><td>Beta </td><td>D/E Ratio</td><td>Effective Tax rate</td>
<td>Unlevered beta</td><td>Cash/Firm value</td><td>Unlevered beta corrected for cash</td></tr>
<tr><td>Semiconductor</td><td>68</td><td>1.45</td><td>3.10%</td><td>9.5%</td><td>1.42</td><td>2.9%</td><td>1.46</td></tr>
<tr><td>Software (System &amp; Application)</td><td>350</td><td>1.20</td><td>4%</td><td>5%</td><td>1.17</td><td>3%</td><td>1.21</td></tr>
</table></body></html>"""


def test_parser_damodaran():
    w = rynek.beta_damodaran(DAMODARAN, "semiconductor")
    assert w == {"beta": 1.46, "kolumna": "unlevered beta corrected for cash", "firm": 68}
    assert rynek.beta_damodaran(DAMODARAN, "Software (System & Application)")["beta"] == 1.21
    assert rynek.beta_damodaran(DAMODARAN, "Brak takiej branży") is None
    with pytest.raises(rynek.BladRynku):
        rynek.beta_damodaran("<table><tr><td>x</td></tr></table>", "Semiconductor")


def test_beta_sektorowa_przeliczona_na_zadluzenie():
    r, k = rejestr([1000.0] * 3, fcf=[100.0] * 3)
    D = date(2026, 11, 9)
    dz = {"typ": "dzien", "koniec": D}
    r.dodaj(fakt("dlug.2025-12-31", 250.0, okres={"typ": "dzien", "koniec": date(2025, 12, 31)}))
    r.dodaj(fakt("gotowka.2025-12-31", 50.0, okres={"typ": "dzien", "koniec": date(2025, 12, 31)}))
    r.wylicz("dlug_netto.2025-12-31", "dlug_netto", "dlug - gotowka", ["dlug.2025-12-31", "gotowka.2025-12-31"],
             lambda a, b: a - b, "pieniadz", {"typ": "dzien", "koniec": date(2025, 12, 31)}, "USD")
    r.dodaj(fakt("beta_sektorowa_bez_dlugu.2026-11-09", 1.4, "liczba", okres=dz))
    r.dodaj(fakt("beta_regresja.2026-11-06", 3.0, "liczba", okres={"typ": "dzien", "koniec": date(2026, 11, 6)}))
    w = wycena.oblicz(k, None, "USA")
    assert r[w["beta_sektorowa"]].wartosc == pytest.approx(1.4 * (1 + 0.79 * 250 / 1000))
    assert any(o.startswith("Beta:") for o in k.ostrzezenia)  # 0,67 × 3 + 0,33 = 2,34 wobec ok. 1,68
    tekst = "\n".join(ryzyko_tabela(k, {"wycena": w}))
    assert "Brak profilu ryzyka" in tekst  # brak faktów zmienności w tym rejestrze


def test_parser_damodaran_z_wierszy_xls():
    """Pliki regionalne (XLS) dają wiersze komórek; liczby jako tekst z xlrd."""
    wiersze = [["Date updated:", "46027.0"], ["Industry Name", "Number of firms", "Beta ", "D/E Ratio", "Effective Tax rate",
                                              "Unlevered beta", "Cash/Firm value", "Unlevered beta corrected for cash"],
               ["Semiconductor", "212.0", "1.31", "0.1", "0.15", "1.2", "0.1", "1.3333"]]
    assert rynek.beta_damodaran(wiersze, "Semiconductor") == {"beta": 1.3333, "kolumna": "unlevered beta corrected for cash",
                                                              "firm": 212}
