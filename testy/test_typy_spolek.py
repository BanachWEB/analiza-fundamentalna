"""Wycena według typu spółki (specyfikacja 1.1, punkt 6; decyzja właściciela z 12.11.2026)."""

import json
from datetime import date

import pytest

from silnik.fakty.rejestr import RejestrFaktow
from silnik.fakty.schemat import Fakt
from silnik.obliczenia import scenariusze, wycena
from silnik.obliczenia.kalkulator import Kalkulator

D = date(2026, 11, 9)


def fakt(id, v, jedn="pieniadz", okres=None, rodzaj="raportowany"):
    poz = id.split(".")[0]
    okres = okres or {"typ": "dzien", "koniec": D}
    kw = dict(rodzaj=rodzaj, metoda="api", dokument="doc-001", miejsce={})
    return Fakt(id=id, pozycja=poz, okres=okres, wartosc=v, jednostka=jedn,
                waluta="USD" if jedn in ("pieniadz", "pieniadz_na_akcje") else None, status="zweryfikowany", **kw)


def fy(rok):
    return {"typ": "FY", "poczatek": date(rok, 1, 1), "koniec": date(rok, 12, 31)}


def rejestr(przychody, fcf=None, roe=None, kapital=None, dlug_netto=None):
    r = RejestrFaktow("X", D)
    r.dodaj(fakt("kurs.2026-11-09", 10.0, "pieniadz_na_akcje"))
    r.dodaj(fakt("akcje_w_obrocie.2026-11-09", 100.0, "akcje"))
    r.dodaj(fakt("premia_ryzyka_akcji.2026-11-09", 0.05, "ulamek"))
    r.dodaj(fakt("rentownosc_10l.2026-11-09", 0.04, "ulamek"))
    rok0 = 2025 - len(przychody) + 1
    for i, v in enumerate(przychody):
        r.dodaj(fakt(f"przychody.FY{rok0 + i}", v, okres=fy(rok0 + i)))
    for i, v in enumerate(fcf or []):
        r.dodaj(fakt(f"fcf_wlascicieli.FY{rok0 + i}", v, okres=fy(rok0 + i)))
    for i, v in enumerate(roe or []):
        rok = 2025 - len(roe) + 1 + i
        r.dodaj(fakt(f"roe.FY{rok}", v, "ulamek", fy(rok)))
        r.dodaj(fakt(f"zysk_netto.FY{rok}", 100.0, okres=fy(rok)))
    if kapital is not None:
        r.dodaj(fakt("kapital_wlasny.2025-12-31", kapital, okres={"typ": "dzien", "koniec": date(2025, 12, 31)}))
    if dlug_netto is not None:
        r.dodaj(fakt("dlug_netto.2025-12-31", dlug_netto, okres={"typ": "dzien", "koniec": date(2025, 12, 31)}))
    return r, Kalkulator(r)


def test_cykliczny_fcf_znormalizowany():
    r, k = rejestr([1000.0] * 10, fcf=[50.0, 250.0] * 5)  # ostatni rok to szczyt cyklu
    w = wycena.oblicz(k, None, "USA", sektor="cykliczny")
    assert w["metoda"] == "cykliczny"
    assert r[w["marza_fcf_cykl"]].wartosc == pytest.approx(0.15)
    assert r[w["fcf_znormalizowany"]].wartosc == pytest.approx(150.0)
    assert r[w["fcf_yield"]].wartosc == pytest.approx(0.25)  # FCF z ostatniego roku ÷ kapitalizacja 1000
    assert r[w["fcf_yield_znormalizowany"]].wartosc == pytest.approx(0.15)
    # przy niższym FCF cena wymaga wyższego wzrostu
    assert r[w["implikowany_wzrost_fcf_znormalizowany"]].wartosc > r[w["implikowany_wzrost_fcf"]].wartosc


def test_cykliczny_za_krotka_historia():
    r, k = rejestr([1000.0] * 5, fcf=[50.0, 250.0, 50.0, 250.0, 250.0])
    w = wycena.oblicz(k, None, "USA", sektor="cykliczny")
    assert "fcf_znormalizowany" not in w
    assert any("minimum 7" in b for b in k.braki)


def test_ogolny_z_cechami_cyklicznej_dostaje_ostrzezenie():
    r, k = rejestr([1000.0, 1100.0, 700.0, 900.0, 1000.0], fcf=[100.0, 120.0, 10.0, 80.0, 100.0])
    wycena.oblicz(k, None, "USA", sektor="ogolny")
    assert r["max_spadek_przychodow.2026-11-09"].wartosc == pytest.approx(700 / 1100 - 1)
    assert any("cykliczn" in o for o in k.ostrzezenia)


def test_ogolny_stabilny_bez_ostrzezenia():
    r, k = rejestr([1000.0, 1050.0, 1100.0, 1150.0, 1200.0], fcf=[100.0, 105.0, 110.0, 115.0, 120.0])
    wycena.oblicz(k, None, "USA", sektor="ogolny")
    assert not k.ostrzezenia


def test_finanse_uzasadnione_cwk_i_roe_implikowane():
    r, k = rejestr([1000.0] * 3, roe=[0.12, 0.14, 0.16], kapital=800.0)
    w = wycena.oblicz(k, None, "USA", sektor="finanse")
    ke, g = 0.04 + 1.0 * 0.05, 0.025  # beta domyślna 1
    assert w["metoda"] == "kapitalowa"
    assert r[w["roe_srednie"]].wartosc == pytest.approx(0.14)
    assert r[w["cwk_uzasadnione"]].wartosc == pytest.approx((0.14 - g) / (ke - g))
    assert r[w["c_wk"]].wartosc == pytest.approx(1000 / 800)
    assert r[w["roe_implikowane"]].wartosc == pytest.approx(g + 1.25 * (ke - g))
    assert "fcf_yield" not in w  # przepływy banku to ruchy depozytów


def test_deweloper_dlug_do_kapitalu():
    r, k = rejestr([1000.0] * 3, roe=[0.10, 0.12, 0.14], kapital=800.0, dlug_netto=200.0)
    w = wycena.oblicz(k, None, "USA", sektor="deweloper")
    assert r[w["dlug_netto_do_kapitalu"]].wartosc == pytest.approx(0.25)
    assert w.get("cwk_uzasadnione")


def test_nieznany_typ_liczy_jak_ogolny():
    r, k = rejestr([1000.0] * 3, fcf=[100.0] * 3)
    w = wycena.oblicz(k, None, "USA", sektor="bank")
    assert w["metoda"] == "ogolny" and any("nieznany typ" in b for b in k.braki)


def test_scenariusze_roe(tmp_path):
    r, k = rejestr([1000.0] * 3, roe=[0.12, 0.14, 0.16], kapital=800.0)
    w = wycena.oblicz(k, None, "USA", sektor="finanse")
    plik = tmp_path / "scenariusze.json"
    plik.write_text(json.dumps({"scenariusze": [
        {"nazwa": "bazowy", "prawdopodobienstwo": 0.6, "roe": 0.15, "uzasadnienie": "test"},
        {"nazwa": "niedzwiedz", "prawdopodobienstwo": 0.4, "roe": 0.08, "uzasadnienie": "test"}]}))
    wynik = scenariusze.oblicz(k, plik, w)
    ke, g = 0.09, 0.025
    assert r["wartosc_na_akcje.bazowy"].wartosc == pytest.approx(800 * (0.15 - g) / (ke - g) / 100)
    assert r["stopa_zwrotu_implikowana.bazowy"].wartosc == pytest.approx(g + (0.15 - g) * 800 / 1000)
    oczek = 0.6 * r["wartosc_na_akcje.bazowy"].wartosc + 0.4 * r["wartosc_na_akcje.niedzwiedz"].wartosc
    assert r[wynik["wartosc_oczekiwana_na_akcje"]].wartosc == pytest.approx(oczek)


def test_scenariusze_roe_wymagaja_pola_roe(tmp_path):
    r, k = rejestr([1000.0] * 3, roe=[0.12, 0.14, 0.16], kapital=800.0)
    w = wycena.oblicz(k, None, "USA", sektor="finanse")
    plik = tmp_path / "scenariusze.json"
    plik.write_text(json.dumps({"scenariusze": [
        {"nazwa": "a", "prawdopodobienstwo": 0.5, "wzrost_przychodow": 0.05, "marza_fcf": 0.1, "uzasadnienie": "t"},
        {"nazwa": "b", "prawdopodobienstwo": 0.5, "wzrost_przychodow": 0.01, "marza_fcf": 0.1, "uzasadnienie": "t"}]}))
    with pytest.raises(scenariusze.BladScenariuszy):
        scenariusze.oblicz(k, plik, w)


# --- dywidendy i stopa zwrotu dla akcjonariuszy (etap F) ---------------------------------------


def test_stopa_dywidendy_i_zwrotu_akcjonariuszy():
    r, k = rejestr([1000.0] * 3, fcf=[100.0] * 3)
    r.dodaj(fakt("zysk_netto.FY2025", 80.0, okres=fy(2025)))
    r.dodaj(fakt("dywidendy_wyplacone.FY2025", -40.0, okres=fy(2025)))  # znak z przepływów finansowych
    r.dodaj(fakt("skup_akcji.FY2025", 30.0, okres=fy(2025)))
    r.dodaj(fakt("emisje_akcji.FY2025", 10.0, okres=fy(2025)))
    w = wycena.oblicz(k, None, "USA")
    assert r[w["stopa_dywidendy"]].wartosc == pytest.approx(40 / 1000)
    assert r[w["stopa_zwrotu_akcjonariuszy"]].wartosc == pytest.approx((40 + 30 - 10) / 1000)


def test_wyplata_dywidendy_z_zysku_i_fcf():
    from silnik.obliczenia import wskazniki
    from silnik.fakty.schemat import Okres
    r, k = rejestr([1000.0] * 3, fcf=[100.0] * 3)
    r.dodaj(fakt("zysk_netto.FY2025", 80.0, okres=fy(2025)))
    r.dodaj(fakt("dywidendy_wyplacone.FY2025", 40.0, okres=fy(2025)))
    wskazniki.dla_okresu(k, "FY2025", Okres(**fy(2025)), date(2025, 12, 31), None)
    assert r["wyplata_dywidendy.FY2025"].wartosc == pytest.approx(0.5)
    assert r["wyplata_dywidendy_z_fcf.FY2025"].wartosc == pytest.approx(0.4)


def test_ev_ebit_bez_sensu_przy_ujemnym_zysku_operacyjnym():
    r, k = rejestr([1000.0] * 3, fcf=[100.0] * 3)
    r.dodaj(fakt("zysk_operacyjny.FY2025", -20.0, okres=fy(2025)))
    r.dodaj(fakt("dlug_netto.2025-12-31", 100.0, okres={"typ": "dzien", "koniec": date(2025, 12, 31)}))
    w = wycena.oblicz(k, None, "USA")
    assert w.get("ev") and not w.get("ev_ebit")
    assert any("zysk operacyjny ≤ 0" in b for b in k.braki)
