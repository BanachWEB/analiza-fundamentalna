"""Testy kroku 2 na danych syntetycznych (bez sieci)."""

from datetime import date, timedelta

import pytest

from silnik.fakty.rejestr import RejestrFaktow
from silnik.fakty.schemat import Fakt, Status
from silnik.fakty.weryfikacja import Raport, drugie_zrodlo, pozycje_przestarzale, tozsamosci
from silnik.pobieranie import sec, stockanalysis


def wpis(val, start, end, form="10-K", fy=2026, fp="FY", accn="0001", filed="2026-07-29"):
    w = {"val": val, "end": end, "accn": accn, "form": form, "fy": fy, "fp": fp, "filed": filed}
    if start:
        w["start"] = start
    return w


def facts(**znaczniki):
    return {"facts": {"us-gaap": {t: {"units": {"USD": w}} for t, w in znaczniki.items()}}}


# --- kalendarz fiskalny -----------------------------------------------------


@pytest.mark.parametrize(
    "miesiac,przes,koniec,rok,kw",
    [
        (6, 0, date(2022, 12, 31), 2023, "Q2"),  # Microsoft
        (6, 0, date(2022, 3, 31), 2022, "Q3"),
        (9, 0, date(2025, 12, 27), 2026, "Q1"),  # Apple, rok 52/53-tygodniowy
        (9, 0, date(2022, 10, 1), 2022, "Q4"),  # koniec roku tuż po 30.09
        (1, 0, date(2025, 4, 30), 2026, "Q1"),  # Walmart nazywa rok rokiem końca
        (1, -1, date(2026, 1, 31), 2025, "Q4"),  # sieć, która nazywa rok rokiem początku
    ],
)
def test_kalendarz(miesiac, przes, koniec, rok, kw):
    k = sec.KalendarzFiskalny(miesiac, przes)
    assert k.rok(koniec) == rok
    assert k.kwartal(koniec) == kw


def test_kalendarz_z_raportu_10k():
    f = facts(Revenues=[wpis(100, "2025-02-01", "2026-01-31", fy=2025)])
    k = sec.kalendarz(f)
    assert (k.miesiac_konca, k.przesuniecie) == (1, -1)


# --- wybór wartości z XBRL ----------------------------------------------------


MAPA = {"przychody": {"rodzaj": "okres", "jednostka": "pieniadz", "znaczniki": ["Revenues", "SalesRevenueNet"]}}


def test_priorytet_znacznikow_i_nazwy_okresow():
    f = facts(
        Revenues=[wpis(300, "2025-07-01", "2026-06-30"), wpis(80, "2026-07-01", "2026-09-30", form="10-Q", fy=2027, fp="Q1")],
        SalesRevenueNet=[wpis(299, "2025-07-01", "2026-06-30"), wpis(250, "2024-07-01", "2025-06-30")],
    )
    wynik = {x.id: x for x in sec.wyciagnij_fakty(f, "doc-001", MAPA)}
    assert wynik["przychody.FY2026"].wartosc == 300  # pierwszy znacznik wygrywa
    assert wynik["przychody.FY2025"].wartosc == 250  # starszy rok tylko w drugim znaczniku
    assert wynik["przychody.FY2027Q1"].okres.typ.value == "Q1"
    assert wynik["przychody.FY2026"].miejsce["xbrl"] == "us-gaap:Revenues"


def test_korekta_w_pozniejszym_raporcie():
    f = facts(Revenues=[
        wpis(300, "2025-07-01", "2026-06-30"),
        wpis(310, "2025-07-01", "2026-06-30", accn="0002", filed="2027-07-29"),
    ])
    x = {x.id: x for x in sec.wyciagnij_fakty(f, "doc-001", MAPA)}["przychody.FY2026"]
    assert x.wartosc == 310
    assert any(c.startswith("zmiana_wersji") for c in x.kontrole)


def test_okresy_narastajace_i_nietypowe():
    f = facts(Revenues=[wpis(300, "2025-07-01", "2026-06-30"),
                        wpis(150, "2025-07-01", "2025-12-31", form="10-Q", fy=2026, fp="Q2"),  # półrocze narastająco
                        wpis(90, "2025-07-01", "2025-10-31", form="10-Q")])  # 4 miesiące: pomijamy
    ids = sorted(x.id for x in sec.wyciagnij_fakty(f, "doc-001", MAPA))
    assert ids == ["przychody.FY2026", "przychody.FY2026H1"]


# --- weryfikacja ------------------------------------------------------------


def fakt(id, wartosc, koniec=date(2026, 6, 30), typ="dzien"):
    okres = {"typ": typ, "koniec": koniec}
    if typ == "FY":
        okres["poczatek"] = date(koniec.year - 1, koniec.month, koniec.day) + timedelta(days=1)
    return Fakt(id=id, rodzaj="raportowany", pozycja=id.split(".")[0], okres=okres, wartosc=wartosc,
                jednostka="pieniadz", waluta="USD", metoda="xbrl", status="jedno_zrodlo", dokument="doc-001",
                miejsce={"xbrl": "x"})


def test_tozsamosc_bilansu_oznacza_statusy():
    r = RejestrFaktow("X", date(2026, 11, 10))
    r.dodaj(fakt("aktywa.2026-06-30", 100))
    r.dodaj(fakt("pasywa_razem.2026-06-30", 100))
    r.dodaj(fakt("zobowiazania.2026-06-30", 70))
    r.dodaj(fakt("kapital_wlasny.2026-06-30", 20))  # 70 + 20 ≠ 100
    raport = tozsamosci(r, Raport())
    assert r["aktywa.2026-06-30"].status == Status.zweryfikowany
    assert r["zobowiazania.2026-06-30"].status == Status.konflikt
    assert r["pasywa_razem.2026-06-30"].status == Status.konflikt  # konflikt wygrywa z wcześniejszym „ok”
    assert sum(not k.ok for k in raport.kontrole) == 1


def test_drugie_zrodlo_z_aliasem_i_tolerancja():
    r = RejestrFaktow("X", date(2026, 11, 10))
    r.dodaj(fakt("kapital_wlasny.2026-06-30", 90))
    r.dodaj(fakt("kapital_wlasny_z_udzialami_niekontrolujacymi.2026-06-30", 100))
    r.dodaj(fakt("przychody.FY2026", 1000, typ="FY"))
    dane = {
        ("kapital_wlasny_razem", "dzien", date(2026, 6, 30)): (100.2, "doc-002"),
        ("przychody", "FY", date(2026, 6, 30)): (1010, "doc-002"),  # 1% różnicy
    }
    drugie_zrodlo(r, dane, Raport())
    assert r["kapital_wlasny_z_udzialami_niekontrolujacymi.2026-06-30"].status == Status.zweryfikowany
    assert r["kapital_wlasny.2026-06-30"].status == Status.jedno_zrodlo
    assert r["przychody.FY2026"].status == Status.konflikt


def test_pozycje_przestarzale():
    r = RejestrFaktow("X", date(2026, 11, 10))
    r.dodaj(fakt("przychody.FY2026", 1, typ="FY"))
    r.dodaj(fakt("amortyzacja.FY2013", 1, koniec=date(2013, 6, 30), typ="FY"))
    assert pozycje_przestarzale(r) == ["amortyzacja"]


# --- Stock Analysis -----------------------------------------------------------


def test_parser_stock_analysis():
    html = ('...data:{datekey:["TTM","2026-06-30","2025-06-30"],fiscalYear:["2027","2026","2025"],'
            'revenue:[346,331,281],capex:[-10,-9,null],equity:[5,4,3]}...')
    d = stockanalysis.parsuj(html)
    assert d[("przychody", "FY", date(2026, 6, 30))] == 331
    assert d[("capex", "FY", date(2026, 6, 30))] == 9  # znak odwrócony
    assert ("capex", "FY", date(2025, 6, 30)) not in d  # null pominięty
    assert len([k for k in d if k[0] == "przychody"]) == 2  # bez kolumny TTM
    assert d[("kapital_wlasny_razem", "dzien", date(2025, 6, 30))] == 3


def test_parser_liczby_bez_zera_przed_kropka():
    # LTRX, 11.11.2026: EPS zapisany jako „-.077152”, parser wywracał cały przebieg USA.
    html = 'x{datekey:["TTM","2026-06-30","2025-06-30"],epsdil:[-.077152,.104147,-1.5],revenue:[3,2,1]}'
    assert stockanalysis._tablica(html, html.find("datekey:["), "epsdil") == [-0.077152, 0.104147, -1.5]
    stockanalysis.parsuj(html)


def test_parser_bez_danych_zglasza_blad():
    with pytest.raises(stockanalysis.BladStockAnalysis):
        stockanalysis.parsuj("<html>nic</html>")


# --- ticker → CIK -------------------------------------------------------------


def test_cik_z_konfiguracji_bez_sieci(tmp_path, monkeypatch):
    from silnik.pobieranie import http

    plik = tmp_path / "sec-cik.yaml"
    plik.write_text("MSFT: 789019\n", encoding="utf-8")
    monkeypatch.setattr(http, "pobierz", lambda url: pytest.fail("nie powinien pobierać"))
    assert sec.cik_dla("msft", plik) == 789019


def test_cik_bez_kontaktu_zglasza_blad(tmp_path, monkeypatch):
    from silnik.pobieranie import http

    plik = tmp_path / "sec-cik.yaml"
    plik.write_text("", encoding="utf-8")
    monkeypatch.setattr(http, "USER_AGENT", "narzedzie bez adresu")
    with pytest.raises(sec.BladSEC, match="ANALIZA_USER_AGENT"):
        sec.cik_dla("NVDA", plik)


def test_cik_z_listy_sec_dopisuje_do_konfiguracji(tmp_path, monkeypatch):
    from silnik.pobieranie import http

    plik = tmp_path / "sec-cik.yaml"
    plik.write_text("MSFT: 789019\n", encoding="utf-8")
    lista = tmp_path / "lista.json"
    lista.write_text('{"0": {"cik_str": 1045810, "ticker": "NVDA", "title": "NVIDIA"}}', encoding="utf-8")
    monkeypatch.setattr(http, "USER_AGENT", "analiza-fundamentalna kontakt@example.com")
    monkeypatch.setattr(http, "pobierz", lambda url: lista)
    assert sec.cik_dla("NVDA", plik) == 1045810
    assert "NVDA: 1045810" in plik.read_text(encoding="utf-8")
