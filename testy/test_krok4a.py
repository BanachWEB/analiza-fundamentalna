"""Testy obliczeń (krok 4a) na rejestrze syntetycznym, z wynikami policzonymi ręcznie."""

from datetime import date

import pytest

from silnik.fakty.rejestr import RejestrFaktow
from silnik.fakty.schemat import Fakt, Status
from silnik.obliczenia import jakosc, okresy, wskazniki
from silnik.obliczenia.kalkulator import Kalkulator, podzial_akcji


def F(id, wartosc, typ, koniec, poczatek=None, jednostka="pieniadz", status="zweryfikowany"):
    okres = {"typ": typ, "koniec": koniec}
    if poczatek:
        okres["poczatek"] = poczatek
    return Fakt(id=id, rodzaj="raportowany", pozycja=id.split(".")[0], okres=okres, wartosc=wartosc,
                jednostka=jednostka, waluta="USD" if jednostka == "pieniadz" else None, metoda="xbrl",
                status=status, dokument="doc-001", miejsce={"xbrl": "x"})


D = date


def rejestr_roczny():
    r = RejestrFaktow("X", D(2026, 11, 10))
    for rok, p in ((2024, 100), (2025, 120)):
        r.dodaj(F(f"przychody.FY{rok}", p, "FY", D(rok, 12, 31), D(rok, 1, 1)))
    r.dodaj(F("przychody.FY2025M9", 85, "M9", D(2025, 9, 30), D(2025, 1, 1)))
    r.dodaj(F("przychody.FY2026M9", 100, "M9", D(2026, 9, 30), D(2026, 1, 1)))
    r.dodaj(F("przychody.FY2025H1", 50, "H1", D(2025, 6, 30), D(2025, 1, 1)))
    r.dodaj(F("przychody.FY2025Q1", 20, "Q1", D(2025, 3, 31), D(2025, 1, 1)))
    return r


def test_kwartaly_z_danych_narastajacych():
    r = rejestr_roczny()
    k = Kalkulator(r)
    okresy.dodaj_kwartaly(k)
    assert r["przychody.FY2025Q4"].wartosc == 35  # 120 − 85
    assert r["przychody.FY2025Q3"].wartosc == 35  # 85 − 50
    assert r["przychody.FY2025Q2"].wartosc == 30  # 50 − 20
    assert r["przychody.FY2025Q4"].wejscia == ["przychody.FY2025", "przychody.FY2025M9"]


def test_ttm():
    r = rejestr_roczny()
    k = Kalkulator(r)
    koniec = okresy.dodaj_ttm(k)
    assert koniec == D(2026, 9, 30)
    assert r["przychody.TTM2026-09-30"].wartosc == 135  # 120 + 100 − 85


def test_ttm_dziedziczy_status():
    r = rejestr_roczny()
    r.dodaj(r["przychody.FY2026M9"].model_copy(update={"status": Status.jedno_zrodlo}), zastap=True)
    k = Kalkulator(r)
    okresy.dodaj_ttm(k)
    assert r["przychody.TTM2026-09-30"].status == Status.jedno_zrodlo


@pytest.mark.parametrize("a,b,wynik", [(3000, 1000, True), (1000, 10000, True), (1050, 1000, False), (1500, 1000, False)])
def test_podzial_akcji(a, b, wynik):
    assert podzial_akcji(a, b) is wynik


def test_dynamika_nie_przechodzi_przez_podzial():
    r = RejestrFaktow("X", D(2026, 11, 10))
    for rok, p, sh in ((2024, 100, 1000), (2025, 110, 3000)):
        r.dodaj(F(f"przychody.FY{rok}", p, "FY", D(rok, 12, 31), D(rok, 1, 1)))
        r.dodaj(F(f"liczba_akcji_rozwodniona.FY{rok}", sh, "FY", D(rok, 12, 31), D(rok, 1, 1), jednostka="akcje"))
    k = Kalkulator(r)
    wskazniki.dynamika(k)
    assert r["wzrost_przychody.FY2025"].wartosc == pytest.approx(0.10)
    assert "zmiana_liczby_akcji.FY2025" not in r
    assert any("podział" in b for b in k.braki)


def test_ujemna_baza_daje_brak_a_nie_nan():
    r = RejestrFaktow("X", D(2026, 11, 10))
    r.dodaj(F("zysk_netto.FY2024", -10, "FY", D(2024, 12, 31), D(2024, 1, 1)))
    r.dodaj(F("zysk_netto.FY2025", 5, "FY", D(2025, 12, 31), D(2025, 1, 1)))
    r.dodaj(F("przychody.FY2024", 100, "FY", D(2024, 12, 31), D(2024, 1, 1)))
    r.dodaj(F("przychody.FY2025", 100, "FY", D(2025, 12, 31), D(2025, 1, 1)))
    k = Kalkulator(r)
    wskazniki.dynamika(k)
    assert "wzrost_zysk_netto.FY2025" not in r
    assert any("ujemna" in b for b in k.braki)


def test_zobowiazania_i_amortyzacja_ze_skladnikow():
    r = RejestrFaktow("X", D(2026, 11, 10))
    r.dodaj(F("pasywa_razem.2025-12-31", 100, "dzien", D(2025, 12, 31)))
    r.dodaj(F("kapital_wlasny.2025-12-31", 40, "dzien", D(2025, 12, 31)))
    r.dodaj(F("amortyzacja_srodkow_trwalych.FY2025", 7, "FY", D(2025, 12, 31), D(2025, 1, 1)))
    r.dodaj(F("amortyzacja_wnip.FY2025", 3, "FY", D(2025, 12, 31), D(2025, 1, 1)))
    k = Kalkulator(r)
    okresy.uzupelnij_skladniki(k)
    assert r["zobowiazania.2025-12-31"].wartosc == 60
    assert r["amortyzacja.FY2025"].wartosc == 10


def test_altman_z2_reczne():
    r = RejestrFaktow("X", D(2026, 11, 10))
    B = D(2025, 12, 31)
    for poz, v in (("aktywa_obrotowe", 400), ("zobowiazania_krotkoterminowe", 200), ("zyski_zatrzymane", 300),
                   ("kapital_wlasny", 500), ("zobowiazania", 500), ("aktywa", 1000)):
        r.dodaj(F(f"{poz}.{B.isoformat()}", v, "dzien", B))
    r.dodaj(F("zysk_operacyjny.FY2025", 100, "FY", B, D(2025, 1, 1)))
    r.dodaj(F("przychody.FY2025", 1000, "FY", B, D(2025, 1, 1)))
    k = Kalkulator(r)
    jakosc.altman(k, k.okresy_fy())
    # 6,56·0,2 + 3,26·0,3 + 6,72·0,1 + 1,05·1,0 = 1,312 + 0,978 + 0,672 + 1,05
    assert r["altman_z2.FY2025"].wartosc == pytest.approx(4.012)


def test_beneish_dla_spolki_bez_zmian_to_stala_modelu():
    """Gdy wszystkie relacje są identyczne rok do roku i zysk = gotówka, M = −4,84 + suma współczynników."""
    r = RejestrFaktow("X", D(2026, 11, 10))
    for rok in (2024, 2025):
        B, S = D(rok, 12, 31), f"FY{rok}"
        for poz, v in (("naleznosci_handlowe", 100), ("aktywa_obrotowe", 300), ("rzeczowe_aktywa_trwale", 400),
                       ("aktywa", 1000), ("zobowiazania_krotkoterminowe", 200), ("dlug_dlugoterminowy_f", 100)):
            r.dodaj(F(f"{poz}.{B.isoformat()}", v, "dzien", B))
        for poz, v in (("przychody", 1000), ("amortyzacja", 50), ("koszty_sprzedazy_i_zarzadu", 100),
                       ("zysk_netto", 80), ("przeplywy_operacyjne", 80)):
            r.dodaj(F(f"{poz}.{S}", v, "FY", B, D(rok, 1, 1)))
        r.dodaj(Fakt(id=f"marza_brutto.{S}", rodzaj="raportowany", pozycja="marza_brutto",
                     okres={"typ": "FY", "poczatek": D(rok, 1, 1), "koniec": B}, wartosc=0.3, jednostka="ulamek",
                     metoda="xbrl", status="zweryfikowany", dokument="doc-001", miejsce={"xbrl": "x"}))
    k = Kalkulator(r)
    jakosc.beneish(k, k.okresy_fy())
    assert r["beneish_m.FY2025"].wartosc == pytest.approx(-4.84 + 0.92 + 0.528 + 0.404 + 0.892 + 0.115 - 0.172 - 0.327)
