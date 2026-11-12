"""Tabela wrażliwości i historyczne pasma wyceny (specyfikacja 1.1, punkt 7)."""

import json
from datetime import date, datetime, timedelta, timezone

import pytest

from silnik.fakty.rejestr import RejestrFaktow
from silnik.fakty.schemat import Fakt, TypDokumentu
from silnik.obliczenia import pasma, scenariusze, wycena
from silnik.obliczenia.kalkulator import Kalkulator
from silnik.obliczenia.raport import pasma_tabela, wrazliwosc_tabela

from test_typy_spolek import fakt, fy, rejestr


def test_percentyl_i_ranga():
    v = [1.0, 2.0, 3.0, 4.0, 5.0]
    assert pasma.percentyl(v, 50) == 3.0
    assert pasma.percentyl(v, 25) == 2.0
    assert pasma.percentyl(v, 90) == pytest.approx(4.6)
    assert pasma.ranga(v, 3.5) == 0.6


def _scen(tmp_path, *s):
    plik = tmp_path / "scenariusze.json"
    plik.write_text(json.dumps({"scenariusze": list(s)}))
    return plik


def test_wrazliwosc_fcf(tmp_path):
    r, k = rejestr([1000.0] * 3, fcf=[100.0] * 3)
    w = wycena.oblicz(k, None, "USA")
    plik = _scen(tmp_path,
                 {"nazwa": "bazowy", "prawdopodobienstwo": 0.6, "wzrost_przychodow": 0.05, "marza_fcf": 0.10, "uzasadnienie": "t"},
                 {"nazwa": "niedzwiedz", "prawdopodobienstwo": 0.4, "wzrost_przychodow": 0.0, "marza_fcf": 0.06, "uzasadnienie": "t"})
    scenariusze.oblicz(k, plik, w)
    wr = scenariusze.wrazliwosc(k, plik, w)
    srodek = r[wr["siatka1"][(0, 0)]].wartosc
    assert srodek == pytest.approx(r["wartosc_na_akcje.bazowy"].wartosc)
    assert r[wr["siatka1"][(0, 1)]].wartosc > srodek  # wyższa marża FCF
    assert r[wr["siatka2"][(1, 0)]].wartosc < srodek  # wyższy koszt kapitału
    # marża +2 pp przy marży 10% zmienia wartość o 20%: więcej niż wzrost +2 pp?
    assert r[wr["zalozenia"]["marza"]].wartosc == pytest.approx(0.2)
    assert wr["najwazniejsze"] in ("marza", "wzrost", "ke", "gt")
    tekst = "\n".join(wrazliwosc_tabela(k, {"wrazliwosc": wr}))
    assert "Najważniejsze założenie wyceny" in tekst and "bazowy" in tekst


def test_wrazliwosc_roe(tmp_path):
    r, k = rejestr([1000.0] * 3, roe=[0.12, 0.14, 0.16], kapital=800.0)
    w = wycena.oblicz(k, None, "USA", sektor="finanse")
    plik = _scen(tmp_path, {"nazwa": "bazowy", "prawdopodobienstwo": 0.5, "roe": 0.15, "uzasadnienie": "t"},
                 {"nazwa": "niedzwiedz", "prawdopodobienstwo": 0.5, "roe": 0.08, "uzasadnienie": "t"})
    scenariusze.oblicz(k, plik, w)
    wr = scenariusze.wrazliwosc(k, plik, w)
    assert wr["osie"] == ("roe", "ke")
    g, ke = 0.025, 0.09
    assert r[wr["siatka1"][(1, 0)]].wartosc == pytest.approx(800 * (0.17 - g) / (ke - g) / 100)
    assert set(wr["zalozenia"]) == {"roe", "ke", "gt"}


def _yahoo(sesje):
    ts = [int(datetime(d.year, d.month, d.day, 21, tzinfo=timezone.utc).timestamp()) for d, _ in sesje]
    return json.dumps({"chart": {"error": None, "result": [{"timestamp": ts, "indicators": {
        "quote": [{"close": [c for _, c in sesje], "volume": [1000] * len(sesje)}]}}]}})


def test_pasma_z_archiwum(tmp_path, monkeypatch):
    from silnik.pobieranie import archiwum as arch
    monkeypatch.setattr(arch, "DOMYSLNY_KATALOG", tmp_path / "pliki")
    katalog = tmp_path / "analiza"
    katalog.mkdir()
    # notowania: kurs rośnie liniowo od 50 do 150 przez ok. 4 lata (dni robocze)
    start = date(2022, 11, 1)
    dni = [start + timedelta(days=i) for i in range(4 * 365) if (start + timedelta(days=i)).weekday() < 5]
    sesje = [(d, 50 + 100 * i / (len(dni) - 1)) for i, d in enumerate(dni)]
    plik = tmp_path / "yahoo.json"
    plik.write_text(_yahoo(sesje))
    a = arch.Archiwum("X", katalog)
    dok = a.dodaj_plik(plik, TypDokumentu.strona, "Yahoo Finance", adres="https://example.invalid/x", opis="notowania")
    D = dni[-1]
    r = RejestrFaktow("X", D)
    r.znane_dokumenty([dok.id])
    for rok in range(2020, 2026):
        r.dodaj(fakt(f"przychody.FY{rok}", 1000.0, okres=fy(rok)))
        r.dodaj(fakt(f"zysk_netto.FY{rok}", 100.0, okres=fy(rok)))
        r.dodaj(fakt(f"fcf_wlascicieli.FY{rok}", 80.0, okres=fy(rok)))
        r.dodaj(fakt(f"liczba_akcji_rozwodniona.FY{rok}", 10.0, "akcje", okres=fy(rok)))
    dz = {"typ": "dzien", "koniec": D}
    r.dodaj(Fakt(id=f"obroty_dzienne_60s.{D}", pozycja="obroty_dzienne_60s", okres=dz, wartosc=1.0, jednostka="pieniadz",
                 waluta="USD", rodzaj="raportowany", metoda="api", status="jedno_zrodlo", dokument=dok.id,
                 miejsce={"dokumenty": [dok.id]}))
    r.dodaj(fakt(f"kurs.{D}", 150.0, "pieniadz_na_akcje", okres=dz))
    r.dodaj(fakt(f"akcje_w_obrocie.{D}", 10.0, "akcje", okres=dz))
    r.dodaj(fakt(f"premia_ryzyka_akcji.{D}", 0.05, "ulamek", okres=dz))
    r.dodaj(fakt(f"rentownosc_10l.{D}", 0.04, "ulamek", okres=dz))
    k = Kalkulator(r)
    w = wycena.oblicz(k, None, "USA")
    ps = pasma.oblicz(k, katalog, w)
    cz = ps["mnozniki"]["c_z"]
    # C/Z = kurs × 10 / 100 = kurs / 10: od ok. 5 do 15, dziś 15 → najwyższy percentyl
    assert r[cz[50]].wartosc == pytest.approx(10.0, abs=0.6)
    assert r[cz[10]].wartosc < r[cz[90]].wartosc
    assert r[cz["percentyl"]].wartosc == pytest.approx(1.0)
    assert r[ps["mnozniki"]["fcf_yield"]["percentyl"]].wartosc < 0.05  # najniższy FCF yield w historii
    assert "ev_ebit" not in ps["mnozniki"]  # brak zysku operacyjnego i długu netto
    tekst = "\n".join(pasma_tabela(k, {"pasma": ps}))
    assert "| C/Z |" in tekst


def test_pasma_bez_historii():
    r, k = rejestr([1000.0] * 3, fcf=[100.0] * 3)
    w = wycena.oblicz(k, None, "USA")
    assert pasma.oblicz(k, None, w) is None
