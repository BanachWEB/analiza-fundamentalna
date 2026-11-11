"""Cena docelowa wg arkusza właściciela: odczyt komórek, fakty, tabela raportu, karta (bez sieci).

Arkusz testowy odtwarza układ zakładki „Cena docelowa” z pliku właściciela (NVDA, 11.11.2026).
Silnik nie liczy: oczekiwane liczby to dokładnie wartości wpisane w komórki.
"""

from datetime import date

import openpyxl
import pytest

from silnik.fakty.rejestr import RejestrFaktow
from silnik.fakty.schemat import Fakt
from silnik.obliczenia import karta_treli, trela
from silnik.obliczenia.kalkulator import Kalkulator
from silnik.obliczenia.raport import trela_tabela
from silnik.pobieranie import archiwum

D = date(2026, 11, 11)


@pytest.fixture(autouse=True)
def archiwum_tymczasowe(tmp_path, monkeypatch):
    monkeypatch.setattr(archiwum, "DOMYSLNY_KATALOG", tmp_path / "archiwum")


def arkusz(sciezka, ticker="NVDA", pusty_wynik=False, zakladka="Cena docelowa"):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = zakladka
    wiersze = [
        ["Cena docelowa"], ["Trading for a Living · tradingforaliving.pl"], [],
        ["DANE WEJŚCIOWE", "Wartość", "Skąd"],
        ["Spółka (ticker)", ticker, "Dowolny tekst"],
        ["Aktualny kurs akcji", 168.89, "Scrab → MasterChart → Price"],
        ["Prognoza zysku na akcję (EPS) na kolejne 12 mies.", 15.81, "Scrab"],
        ["Prognoza sprzedaży na akcję na kolejne 12 mies.", 28.57, "Scrab"],
        ["Mediana P/E 1-Year Forward", 28.92, "Scrab"],
        ["Maksimum historycznego P/E (poziom „dobrych czasów”)", 65.2, "Scrab"],
        ["Minimum historycznego P/E (opcjonalnie)", 10.68, "Scrab"],
        ["Mediana P/S 1-Year Forward", 14.56, "Scrab"],
        ["Maksimum historycznego P/S", 21.06, "Scrab"],
        [],
        ["WYNIK", "Konserwatywna", "Optymistyczna", "Potencjał (kons.)", "Potencjał (optym.)"],
        ["Cena docelowa z P/E (mnożnik × prognoza EPS)", 457.23, 1030.81, 1.707, 5.103],
        ["Cena docelowa z P/S (mnożnik × prognoza sprzedaży)", None if pusty_wynik else 415.98, 601.68, 1.463, 2.563],
        ["CENA DOCELOWA NA 12 MIESIĘCY (średnia z obu metod)", 436.60, 816.25, 1.585, 3.833],
        ["Siatka wrażliwości: P/E"],
    ]
    for w in wiersze:
        ws.append(w)
    wb.save(sciezka)


def rejestr(ticker="NVDA"):
    r = RejestrFaktow(ticker, D)
    r.dodaj(Fakt(id=f"kurs.{D.isoformat()}", rodzaj="raportowany", pozycja="kurs", okres={"typ": "dzien", "koniec": D},
                 wartosc=170.0, jednostka="pieniadz_na_akcje", waluta="USD", metoda="api", status="zweryfikowany",
                 dokument="doc-001"))
    return r


def katalog(tmp_path, **kw):
    D_ = tmp_path / "analiza"
    D_.mkdir()
    arkusz(D_ / trela.PLIK, **kw)
    return D_


def test_odczyt_wynikow_bez_przeliczania(tmp_path):
    D_ = katalog(tmp_path)
    r = rejestr()
    k = Kalkulator(r)
    w = trela.oblicz(k, D_)
    assert r[w["kons"]].wartosc == 436.60 and r[w["optym"]].wartosc == 816.25
    assert r[w["potencjal_kons"]].wartosc == 1.585 and r[w["potencjal_optym"]].wartosc == 3.833
    assert r[w["pe_kons"]].wartosc == 457.23 and r[w["ps_optym"]].wartosc == 601.68
    assert r[w["pe_forward_mediana_arkusz"]].wartosc == 28.92
    assert r[w["ps_forward_maksimum_arkusz"]].wartosc == 21.06
    f = r[w["kons"]]
    assert f.rodzaj.value == "raportowany" and f.metoda.value == "wklejka" and f.status.value == "jedno_zrodlo"
    assert f.miejsce == {"zakladka": "Cena docelowa", "komorka": "B18", "etykieta": "cena docelowa na 12"}
    assert f.waluta == "USD" and f.okres.koniec == D
    assert not k.braki
    arch = archiwum.Archiwum("NVDA", D_)
    assert arch[w["dokument"]].typ.value == "wklejka" and arch.sprawdz(w["dokument"])


def test_brak_pliku_pomija_bez_braku(tmp_path):
    k = Kalkulator(rejestr())
    assert trela.oblicz(k, tmp_path) == {}
    assert k.braki == []
    assert trela_tabela(k, {"trela": {}}) == []


def test_inny_ticker_nie_wstawia_liczb(tmp_path):
    D_ = katalog(tmp_path, ticker="AMD")
    r = rejestr()
    k = Kalkulator(r)
    assert trela.oblicz(k, D_) == {}
    assert any("arkusz dotyczy 'AMD'" in b for b in k.braki)
    assert not [f for f in r.fakty() if f.pozycja.startswith("cena_docelowa_trela")]


def test_ticker_gpw_z_przyrostkiem(tmp_path):
    D_ = katalog(tmp_path, ticker="XTB.WA")
    assert trela.oblicz(Kalkulator(rejestr("XTB")), D_)["kons"]


def test_pusta_komorka_to_brak(tmp_path):
    D_ = katalog(tmp_path, pusty_wynik=True)
    k = Kalkulator(rejestr())
    w = trela.oblicz(k, D_)
    assert w["ps_kons"] is None and w["kons"]
    assert any("B17" in b for b in k.braki)


def test_zly_plik(tmp_path):
    D_ = tmp_path / "analiza"
    D_.mkdir()
    arkusz(D_ / trela.PLIK, zakladka="Inna")
    k = Kalkulator(rejestr())
    assert trela.oblicz(k, D_) == {}
    assert any("nie odczytam" in b for b in k.braki)


def test_karta_bierze_potencjal_z_arkusza(tmp_path):
    D_ = katalog(tmp_path)
    k = Kalkulator(rejestr())
    trela.oblicz(k, D_)
    wycena = next(f for f in karta_treli.oblicz(k, "USA", {}, None, None) if f.nazwa == "wycena")
    fid, wartosc, pkt = wycena.miary["potencjal_trela_kons"]
    assert wartosc == 1.585 and pkt == 10


def test_karta_bez_arkusza_ma_brak_miary(tmp_path):
    k = Kalkulator(rejestr())
    wycena = next(f for f in karta_treli.oblicz(k, "USA", {}, None, None) if f.nazwa == "wycena")
    assert wycena.miary["potencjal_trela_kons"] is None


def test_tabela_raportu(tmp_path):
    D_ = katalog(tmp_path)
    k = Kalkulator(rejestr())
    tekst = "\n".join(trela_tabela(k, {"trela": trela.oblicz(k, D_)}))
    assert "436,60 USD¹" in tekst and "+158,5%¹" in tekst and "1 030,81 USD¹" in tekst
    assert "niczego nie przelicza" in tekst and "nie prognoza kursu ani rekomendacja" in tekst
