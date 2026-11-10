"""Testy kroku 4b: matematyka wyceny, scenariusze, karta Treli, parsery danych rynkowych (bez sieci)."""

import json
from datetime import date, timedelta

import pytest

from silnik.obliczenia import karta_treli, scenariusze, wycena
from silnik.obliczenia.kalkulator import BrakSensu
from silnik.pobieranie import rynek

# --- matematyka wyceny ------------------------------------------------------------------


def test_wartosc_fcf_bez_wzrostu_to_renta():
    # bez wzrostu w okresie prognozy i bez wzrostu rezydualnego wartość = FCF / k
    assert wycena.wartosc_fcf(100, 0.0, 10, 0.0, 0.10) == pytest.approx(1000)


def test_wartosc_fcf_gordon():
    # wzrost stały g w prognozie i po niej: wartość = FCF·(1+g) / (k − g)
    assert wycena.wartosc_fcf(100, 0.03, 10, 0.03, 0.10) == pytest.approx(100 * 1.03 / 0.07)


def test_implikowany_wzrost_odwraca_wycene():
    cap = wycena.wartosc_fcf(100, 0.12, 10, 0.025, 0.09)
    assert wycena.implikowany_wzrost(cap, 100, 10, 0.025, 0.09) == pytest.approx(0.12, abs=1e-6)


def test_implikowany_wzrost_przy_ujemnym_fcf():
    with pytest.raises(BrakSensu, match="FCF"):
        wycena.implikowany_wzrost(1000, -5, 10, 0.025, 0.09)


def test_implikowany_cap():
    cap = wycena.wartosc_fcf(100, 0.15, 7, 0.025, 0.09)
    assert wycena.implikowany_cap(cap, 100, 0.15, 0.025, 0.09, 40) == pytest.approx(7, abs=0.01)
    with pytest.raises(BrakSensu, match="40 lat"):
        wycena.implikowany_cap(1e9, 100, 0.05, 0.025, 0.09, 40)


def test_implikowana_marza_liniowa():
    cap = wycena.wartosc_przychody_marza(1000, 0.08, 10, 0.025, 0.09, 0.2)
    assert wycena.implikowana_marza(cap, 1000, 0.08, 10, 0.025, 0.09) == pytest.approx(0.2)


def test_koszt_kapitalu_ponizej_wzrostu():
    with pytest.raises(BrakSensu):
        wycena.wartosc_fcf(100, 0.05, 10, 0.10, 0.09)


# --- scenariusze -------------------------------------------------------------------------


def zapisz(tmp_path, scen):
    p = tmp_path / "scenariusze.json"
    p.write_text(json.dumps({"scenariusze": scen}), encoding="utf-8")
    return p


S = lambda n, p, g=0.05, m=0.1: {"nazwa": n, "prawdopodobienstwo": p, "wzrost_przychodow": g, "marza_fcf": m,  # noqa: E731
                                 "uzasadnienie": "test"}


def test_wartosc_ze_sciezka_przychodow():
    # ścieżka równa stałemu wzrostowi daje tę samą wartość co model bez ścieżki
    bez = wycena.wartosc_przychody_marza(100, 0.1, 10, 0.02, 0.09, 0.2)
    ze = wycena.wartosc_przychody_marza(100, 0.1, 10, 0.02, 0.09, 0.2, (110.0, 121.0))
    assert ze == pytest.approx(bez)
    # skok przychodów na początku podnosi wartość
    assert wycena.wartosc_przychody_marza(100, 0.1, 10, 0.02, 0.09, 0.2, (150.0, 200.0)) > bez
    with pytest.raises(Exception):
        wycena.wartosc_przychody_marza(100, 0.1, 3, 0.02, 0.09, 0.2, (1.0, 2.0, 3.0))


def test_scenariusze_walidacja(tmp_path):
    assert len(scenariusze.wczytaj(zapisz(tmp_path, [S("byk", 0.3), S("bazowy", 0.5), S("niedzwiedz", 0.2)]))) == 3
    with pytest.raises(scenariusze.BladScenariuszy, match="sumują"):
        scenariusze.wczytaj(zapisz(tmp_path, [S("a", 0.5), S("b", 0.4)]))
    with pytest.raises(scenariusze.BladScenariuszy, match="5–85%"):
        scenariusze.wczytaj(zapisz(tmp_path, [S("a", 0.9), S("b", 0.1)]))
    with pytest.raises(scenariusze.BladScenariuszy, match="nazwa"):
        scenariusze.wczytaj(zapisz(tmp_path, [S("Byk!", 0.5), S("b", 0.5)]))


def test_scenariusze_na_rejestrze(tmp_path):
    from silnik.fakty.rejestr import RejestrFaktow
    from silnik.fakty.schemat import Fakt
    from silnik.obliczenia.kalkulator import Kalkulator

    D = date(2026, 11, 9)
    r = RejestrFaktow("X", D)
    def f(id, v, jedn="pieniadz", typ="dzien", waluta="USD"):
        okres = {"typ": typ, "koniec": D} if typ != "brak" else {"typ": "brak"}
        if typ == "TTM":
            okres["poczatek"] = D - timedelta(days=364)
        kw = dict(rodzaj="raportowany", metoda="api", dokument="doc-001", miejsce={})
        if typ == "brak":
            kw = dict(rodzaj="zalozenie", metoda="kod", uzasadnienie="test")
        return Fakt(id=id, pozycja=id.split(".")[0], okres=okres, wartosc=v, jednostka=jedn,
                    waluta=waluta if jedn in ("pieniadz", "pieniadz_na_akcje") else None, status="zweryfikowany", **kw)
    r.dodaj(f("kurs.2026-11-09", 10.0, "pieniadz_na_akcje"))
    r.dodaj(f("akcje_w_obrocie.2026-11-09", 100.0, "akcje"))
    r.dodaj(f("przychody.TTM2026-11-09", 1000.0, typ="TTM"))
    r.dodaj(f("wzrost_rezydualny.zalozenie", 0.025, "ulamek", "brak"))
    r.dodaj(f("koszt_kapitalu_wlasnego.2026-11-09", 0.09, "ulamek"))
    r.wylicz("kapitalizacja.2026-11-09", "kapitalizacja", "kurs × akcje", ["kurs.2026-11-09", "akcje_w_obrocie.2026-11-09"],
             lambda a, b: a * b, "pieniadz", {"typ": "dzien", "koniec": D}, "USD")
    k = Kalkulator(r)
    plik = zapisz(tmp_path, [S("byk", 0.25, 0.10, 0.12), S("bazowy", 0.5, 0.05, 0.08), S("niedzwiedz", 0.25, 0.0, 0.03)])
    w = {"kapitalizacja": "kapitalizacja.2026-11-09", "ke": "koszt_kapitalu_wlasnego.2026-11-09",
         "okres_bazowy": "TTM2026-11-09"}
    wynik = scenariusze.oblicz(k, plik, w)
    wartosci = {n: r[f"wartosc_na_akcje.{n}"].wartosc for n in ("byk", "bazowy", "niedzwiedz")}
    oczekiwana = 0.25 * wartosci["byk"] + 0.5 * wartosci["bazowy"] + 0.25 * wartosci["niedzwiedz"]
    assert r[wynik["wartosc_oczekiwana_na_akcje"]].wartosc == pytest.approx(oczekiwana)
    assert r[wynik["potencjal_oczekiwany"]].wartosc == pytest.approx(oczekiwana / 10 - 1)
    strata = sum(p for n, p in (("byk", 0.25), ("bazowy", 0.5), ("niedzwiedz", 0.25)) if wartosci[n] < 10)
    assert r[wynik["prawdopodobienstwo_straty"]].wartosc == pytest.approx(strata)
    assert r["scenariusz_marza_fcf.byk"].rodzaj.value == "zalozenie"


# --- karta Treli ----------------------------------------------------------------------------


def test_punkty_liniowe_i_odwrocone():
    assert karta_treli.punkty(0.125, 0.0, 0.25) == pytest.approx(5)
    assert karta_treli.punkty(1.0, 0.0, 0.25) == 10
    assert karta_treli.punkty(2.0, 4.0, 0.0) == pytest.approx(5)  # dług: mniej = lepiej
    assert karta_treli.punkty(-1.0, 4.0, 0.0) == 10


def test_wynik_ogolny_przenosi_wage_brakujacego_filaru():
    filary = [karta_treli.Filar("a", 0.4, 8.0), karta_treli.Filar("b", 0.3, 4.0), karta_treli.Filar("c", 0.2, 6.0),
              karta_treli.Filar("d", 0.1, None)]
    wynik, n = karta_treli.wynik_ogolny(filary)
    assert n == 3
    assert wynik == pytest.approx((8 * 0.4 + 4 * 0.3 + 6 * 0.2) / 0.9)


# --- parsery danych rynkowych ------------------------------------------------------------------


def test_treasury_csv():
    csv = 'Date,"1 Mo","10 Yr","30 Yr"\n11/09/2026,4.04,4.88,5.26\n11/06/2026,4.02,4.86,5.26\n'
    assert rynek.rentownosc_treasury(csv) == (date(2026, 11, 9), pytest.approx(0.0488))


def test_damodaran_wiersz():
    html = "<tr><td>Poland</td><td>A2</td><td>0.72%</td><td>1.10%</td><td>5.33%</td><td>19.00%</td></tr>"
    d = rynek.damodaran_kraj(html, "Poland")
    assert d["rating"] == "A2" and d["spread"] == pytest.approx(0.0072) and d["premia_rynku"] == pytest.approx(0.0533)


def test_strefa_inwestorow():
    html = "<p>Obligacje Rentowności 10.11.2026 1D 5D Polska 2-letnie 4,77 4,77 Polska 10-letnie 6,14 6,10</p>"
    assert rynek.rentownosc_strefa(html) == (date(2026, 11, 10), pytest.approx(0.0614))


def test_yahoo_i_momentum():
    start = date(2025, 1, 1)
    ts = [int((date.fromordinal(start.toordinal() + i) - date(1970, 1, 1)).total_seconds()) + 50000 for i in range(400)]
    ceny = [100 + i * 0.1 for i in range(400)]
    tresc = json.dumps({"chart": {"error": None, "result": [{"timestamp": ts, "indicators": {
        "quote": [{"close": ceny, "volume": [1000] * 400}]}}]}})
    sesje = rynek.sesje_yahoo(tresc)
    assert len(sesje) == 400
    m = rynek.stopa_zwrotu_12_1(sesje)
    assert m is not None
    zwrot, od, do = m
    assert (sesje[-1].dzien - od).days == 365 and (sesje[-1].dzien - do).days == 30
    assert zwrot == pytest.approx(ceny[399 - 30] / ceny[399 - 365] - 1)


def test_zmiana_kursu_3m():
    sesje = [rynek.Sesja(date(2026, 1, 1) + timedelta(days=i), 100.0 + i, 1.0) for i in range(200)]
    zmiana, od = rynek.zmiana_kursu_3m(sesje)
    assert (sesje[-1].dzien - od).days == 91
    assert zmiana == pytest.approx(299 / (100 + 199 - 91) - 1)
    assert rynek.zmiana_kursu_3m(sesje[:60]) is None  # za krótka historia
    fakty = {f.pozycja: f for f in rynek.fakty_z_historii(sesje, ["doc-001"], "USD")}
    assert fakty["zmiana_kursu_3m"].wartosc == pytest.approx(zmiana)


def test_momentum_za_krotka_historia():
    sesje = [rynek.Sesja(date(2026, 1, 1) + timedelta(days=i), 10.0, 1.0) for i in range(120)]
    assert rynek.stopa_zwrotu_12_1(sesje) is None


def test_stockanalysis_historia():
    tresc = 'data:[{t:"2026-11-09",o:544.49,h:548.28,l:538.7,c:545.18,v:25337483,a:545.18,ch:2.75},' \
            '{a:530.61,c:530.61,h:538.33,l:524.47,o:525.69,t:"2026-11-06",v:26956423,ch:-.99}]'
    s = rynek.sesje_stockanalysis(tresc)
    assert [(x.dzien, x.zamkniecie) for x in s] == [(date(2026, 11, 6), 530.61), (date(2026, 11, 9), 545.18)]


def test_biznesradar_notowania_i_historia():
    n = rynek.notowania_biznesradar('<div>Liczba akcji: 980 400 000 Kapitalizacja: 1</div>'
                                    '<time datetime="2026-11-09T17:02:34">x</time>')
    assert n["liczba_akcji"] == 980400000 and n["dzien"] == date(2026, 11, 9)
    h = ('<table class="qTableFull"><tr><th>Data</th></tr><tr><td>09.11.2026</td><td>37.60</td><td>38.77</td>'
         '<td>37.17</td><td>38.15</td><td>3 755 268</td><td>1</td></tr></table>')
    s = rynek.sesje_biznesradar(h)
    assert s[0].zamkniecie == 38.15 and s[0].wolumen == 3755268


def test_karta_wymaga_trzech_filarow():
    filary = [karta_treli.Filar("a", 0.5, 8.0), karta_treli.Filar("b", 0.3, 4.0), karta_treli.Filar("c", 0.2, None)]
    assert karta_treli.wynik_ogolny(filary) == (None, 2)
