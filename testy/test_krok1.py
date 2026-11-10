from datetime import date

import pytest
from pydantic import ValidationError

from silnik.fakty.rejestr import BladRejestru, RejestrFaktow
from silnik.fakty.schemat import Fakt, Jednostka, Okres, Status, TypDokumentu
from silnik.pobieranie.archiwum import Archiwum

FY25 = Okres(typ="FY", koniec=date(2025, 12, 31))


def fakt(id, wartosc, status="zweryfikowany", **kw):
    dane = dict(
        id=id,
        rodzaj="raportowany",
        pozycja=id.split(".")[0],
        okres=FY25,
        wartosc=wartosc,
        skala="mln",
        jednostka="pieniadz",
        waluta="USD",
        metoda="xbrl",
        status=status,
        dokument="doc-001",
        miejsce={"xbrl": "us-gaap:Revenues"},
    )
    dane.update(kw)
    return Fakt(**dane)


# --- schemat ---------------------------------------------------------------


def test_kwota_bez_waluty_odrzucona():
    with pytest.raises(ValidationError, match="walutę"):
        fakt("przychody.FY2025", 100, waluta=None)


def test_fakt_raportowany_bez_dokumentu_odrzucony():
    with pytest.raises(ValidationError, match="dokument"):
        fakt("przychody.FY2025", 100, dokument=None)


def test_fakt_od_modelu_bez_cytatu_odrzucony():
    with pytest.raises(ValidationError, match="cytat"):
        fakt("przychody.FY2025", 100, metoda="model", miejsce={"strona": 47})


def test_zalozenie_wymaga_uzasadnienia():
    with pytest.raises(ValidationError, match="uzasadnienie"):
        Fakt(
            id="koszt_kapitalu.zalozenie",
            rodzaj="zalozenie",
            pozycja="koszt_kapitalu",
            okres=Okres(typ="brak"),
            wartosc=0.093,
            jednostka="ulamek",
            metoda="model",
            status="jedno_zrodlo",
        )


def test_prognoza_wymaga_liczby_analitykow():
    with pytest.raises(ValidationError, match="liczbę analityków"):
        fakt("eps_konsensus.FY2026", 5.1, rodzaj="prognoza", jednostka="pieniadz_na_akcje", dostawca="Stock Analysis")


def test_zly_id_odrzucony():
    with pytest.raises(ValidationError, match="pozycja.okres"):
        fakt("Przychody", 100)


# --- rejestr ---------------------------------------------------------------


def test_wyliczony_dziedziczy_najslabszy_status_i_skale():
    r = RejestrFaktow("MSFT", date(2026, 11, 10))
    r.dodaj(fakt("przychody.FY2025", 200))
    r.dodaj(fakt("ebit.FY2025", 90, status="jedno_zrodlo", miejsce={"xbrl": "us-gaap:OperatingIncomeLoss"}))
    m = r.wylicz("marza_operacyjna.FY2025", "marza_operacyjna", "ebit / przychody",
                 ["ebit.FY2025", "przychody.FY2025"], lambda e, p: e / p, Jednostka.ulamek, FY25)
    assert m.wartosc == pytest.approx(0.45)
    assert m.status == Status.jedno_zrodlo
    assert m.waluta is None


def test_wyliczona_kwota_przejmuje_walute_w_jednostkach_bazowych():
    r = RejestrFaktow("MSFT", date(2026, 11, 10))
    r.dodaj(fakt("przychody.FY2025", 200))
    r.dodaj(fakt("koszty.FY2025", 150, miejsce={"xbrl": "x"}))
    w = r.wylicz("wynik.FY2025", "wynik", "przychody - koszty", ["przychody.FY2025", "koszty.FY2025"],
                 lambda p, k: p - k, Jednostka.pieniadz, FY25)
    assert w.wartosc == pytest.approx(50e6)
    assert w.waluta == "USD"


def test_nie_liczy_z_odrzuconych():
    r = RejestrFaktow("MSFT", date(2026, 11, 10))
    r.dodaj(fakt("przychody.FY2025", 200, status="odrzucony"))
    with pytest.raises(BladRejestru, match="odrzucone"):
        r.wylicz("x.FY2025", "x", "2*p", ["przychody.FY2025"], lambda p: 2 * p, Jednostka.pieniadz, FY25)


def test_duplikat_wymaga_zgody():
    r = RejestrFaktow("MSFT", date(2026, 11, 10))
    r.dodaj(fakt("przychody.FY2025", 200))
    with pytest.raises(BladRejestru, match="już istnieje"):
        r.dodaj(fakt("przychody.FY2025", 201))


def test_dokument_musi_istniec_w_archiwum():
    r = RejestrFaktow("MSFT", date(2026, 11, 10), dokumenty=["doc-002"])
    with pytest.raises(BladRejestru, match="nie istnieje"):
        r.dodaj(fakt("przychody.FY2025", 200))


def test_zapis_i_odczyt_z_rodowodem(tmp_path):
    r = RejestrFaktow("MSFT", date(2026, 11, 10))
    r.dodaj(fakt("przychody.FY2025", 200))
    r.dodaj(fakt("ebit.FY2025", 90, miejsce={"xbrl": "y"}))
    r.wylicz("marza_operacyjna.FY2025", "marza_operacyjna", "ebit / przychody",
             ["ebit.FY2025", "przychody.FY2025"], lambda e, p: e / p, Jednostka.ulamek, FY25)
    p = tmp_path / "fakty.json"
    r.do_pliku(p)
    r2 = RejestrFaktow.z_pliku(p)
    assert len(r2) == 3
    assert r2["marza_operacyjna.FY2025"].wartosc == pytest.approx(0.45)
    assert r2.rodowod("marza_operacyjna.FY2025") == ["marza_operacyjna.FY2025", "ebit.FY2025", "przychody.FY2025"]


# --- archiwum --------------------------------------------------------------


def test_archiwum_nadaje_id_i_wykrywa_duplikaty(tmp_path):
    a = Archiwum("MSFT", tmp_path / "analiza", tmp_path / "pliki")
    src = tmp_path / "10k.htm"
    src.write_text("Total revenue 245,122", encoding="utf-8")
    d1 = a.dodaj_plik(src, TypDokumentu.raport_10k, "SEC", adres="https://www.sec.gov/x")
    d2 = a.dodaj_plik(src, TypDokumentu.raport_10k, "SEC")
    d3 = a.dodaj_tekst("EPS 2026: 15,20", TypDokumentu.wklejka, "InvestingPro")
    assert d1.id == "doc-001" and d2.id == "doc-001" and d3.id == "doc-002"
    assert a.sprawdz("doc-001")
    assert "245,122" in a.tekst("doc-001")


def test_archiwum_odczytuje_dokumenty_json(tmp_path):
    a = Archiwum("MSFT", tmp_path / "analiza", tmp_path / "pliki")
    a.dodaj_tekst("abc", TypDokumentu.wklejka, "InvestingPro")
    b = Archiwum("MSFT", tmp_path / "analiza", tmp_path / "pliki")
    assert b.ids() == ["doc-001"]
    r = RejestrFaktow("MSFT", date(2026, 11, 10), dokumenty=b.ids())
    r.dodaj(fakt("przychody.FY2025", 200))  # doc-001 istnieje


def test_schemat_json_aktualny():
    """schemat/*.schema.json musi odpowiadać kodowi; po zmianie uruchom eksport_schematu."""
    import json
    from pathlib import Path

    from silnik.fakty.schemat import RejestrDokumentow, RejestrFaktowPlik

    katalog = Path(__file__).resolve().parents[1] / "schemat"
    for nazwa, model in (("fakty", RejestrFaktowPlik), ("dokumenty", RejestrDokumentow)):
        assert json.loads((katalog / f"{nazwa}.schema.json").read_text(encoding="utf-8")) == model.model_json_schema()


def test_archiwum_odtwarza_brakujacy_plik(tmp_path):
    a = Archiwum("MSFT", tmp_path / "analiza", tmp_path / "pliki")
    src = tmp_path / "r.txt"
    src.write_text("abc", encoding="utf-8")
    d = a.dodaj_plik(src, TypDokumentu.inny, "test")
    a.sciezka(d.id).chmod(0o644)
    a.sciezka(d.id).unlink()
    assert not a.sprawdz(d.id)
    b = Archiwum("MSFT", tmp_path / "analiza", tmp_path / "pliki")
    assert b.dodaj_plik(src, TypDokumentu.inny, "test").id == d.id
    assert b.sprawdz(d.id)
