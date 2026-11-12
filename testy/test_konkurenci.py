"""Tabela konkurentów (specyfikacja 1.1, punkt 8). Pobieranie z sieci podmienione."""

import json
from datetime import date

import pytest

from silnik import konkurenci
from silnik.fakty.rejestr import RejestrFaktow
from silnik.obliczenia.kalkulator import Kalkulator

from test_typy_spolek import fakt, fy

D = date(2026, 11, 12)


def rej(ticker, marza, cz):
    r = RejestrFaktow(ticker, D, dokumenty=["doc-001"])
    r.dodaj(fakt("marza_operacyjna.FY2025", marza, "ulamek", fy(2025)))
    r.dodaj(fakt("marza_operacyjna.FY2024", 0.01, "ulamek", fy(2024)))
    r.dodaj(fakt(f"c_z.{D}", cz, "mnoznik", {"typ": "dzien", "koniec": D}))
    return r


def katalog(tmp_path, wpisy):
    k = tmp_path / "analizy" / "X" / D.isoformat()
    k.mkdir(parents=True)
    (k / "dokumenty.json").write_text(json.dumps({"ticker": "X", "dokumenty": []}))
    (k / "konkurenci.json").write_text(json.dumps({"konkurenci": wpisy}))
    return k


def test_wczytaj_wymaga_uzasadnienia(tmp_path):
    k = katalog(tmp_path, [{"ticker": "A", "rynek": "USA"}])
    with pytest.raises(konkurenci.BladKonkurentow):
        konkurenci.wczytaj(k)


def test_uruchom_zapisuje_rejestry_i_pomija_inne_rynki(tmp_path, monkeypatch):
    k = katalog(tmp_path, [{"ticker": "A", "rynek": "USA", "nazwa": "Alfa", "uzasadnienie": "10-K", "dokument": "doc-1"},
                           {"ticker": "B.PL", "rynek": "GPW", "nazwa": "Beta", "uzasadnienie": "raport", "dokument": "doc-1"},
                           {"ticker": "C", "rynek": "inny", "nazwa": "Gamma", "uzasadnienie": "raport", "dokument": "doc-1"},
                           {"ticker": "X", "rynek": "USA", "nazwa": "sama spółka", "uzasadnienie": "błąd", "dokument": "doc-1"}])
    monkeypatch.setattr(konkurenci, "_usa", lambda t, kat, d, p: rej(t, 0.30, 25.0))
    def gpw(t, kat, d, p):
        raise RuntimeError("Biznesradar odmówił")
    monkeypatch.setattr(konkurenci, "_gpw", gpw)
    kom = konkurenci.uruchom(k)
    assert any(x.startswith("A: rejestr zapisany") for x in kom)
    assert any(x.startswith("B: brak danych") for x in kom)
    assert any(x.startswith("C: rynek spoza") for x in kom)
    assert not any(x.startswith("X") for x in kom)
    assert (k / "konkurenci" / "A" / "fakty.json").exists()


def test_tabela_z_mediana(tmp_path):
    k = katalog(tmp_path, [{"ticker": "A", "rynek": "USA", "nazwa": "Alfa", "uzasadnienie": "t"},
                           {"ticker": "B", "rynek": "USA", "nazwa": "Beta", "uzasadnienie": "t"},
                           {"ticker": "C", "rynek": "GPW", "nazwa": "Gamma", "uzasadnienie": "t"}])
    for t, m, cz in (("A", 0.30, 20.0), ("B", 0.10, 30.0)):
        kat = k / "konkurenci" / t
        kat.mkdir(parents=True)
        (kat / "dokumenty.json").write_text(json.dumps({"ticker": t, "dokumenty": [{"id": "doc-001"}]}))
        rej(t, m, cz).do_pliku(kat / "fakty.json")
    lista = konkurenci.wiersze(k)
    assert [w["ticker"] for w in lista] == ["A", "B", "C"] and lista[2]["fakty"] == {}
    assert lista[0]["fakty"]["marza_operacyjna"].id == "marza_operacyjna.FY2025"  # ostatni rok
    glowna = rej("X", 0.25, 18.0)
    tekst = "\n".join(konkurenci.tabela(Kalkulator(glowna), {"konkurenci": lista, "rynek": "USA"}))
    assert "| **X** |" in tekst
    wiersz_med = next(l for l in tekst.splitlines() if l.startswith("| Mediana"))
    assert "20,0%" in wiersz_med and "25,00" in wiersz_med
    assert "nie są wprost porównywalne" in tekst  # konkurent z GPW przy spółce z USA


def test_brak_konkurentow():
    assert konkurenci.wiersze(None) == []
    tekst = konkurenci.tabela(None, {"konkurenci": []})
    assert tekst[0].startswith("Brak tabeli konkurentów")
