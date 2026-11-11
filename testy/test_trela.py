"""Cena docelowa wg Treli: matematyka, odczyt scrab.yaml i CSV, fakty, tabela raportu (bez sieci).

Liczby oczekiwane policzone ręcznie na danych NVDA ze zrzutu Scrab z 11.11.2026:
EPS 15,81; sprzedaż na akcję 28,57; mediana P/E 28,92; mediana P/S 14,86; kurs 168,89 USD.
"""

from datetime import date, timedelta

import pytest

from silnik.fakty.rejestr import RejestrFaktow
from silnik.fakty.schemat import Fakt
from silnik.obliczenia import karta_treli, trela
from silnik.obliczenia.kalkulator import BrakSensu, Kalkulator
from silnik.obliczenia.raport import trela_tabela
from silnik.pobieranie import archiwum

D = date(2026, 11, 11)

SCRAB = """# odczyt ze Scrab → MasterChart
data_odczytu: 2026-11-11
waluta: USD
kurs: 168.89
rok_obrotowy_prognozy: FY2028
eps_prognoza: 15.81
sprzedaz_na_akcje_prognoza: 28.57
pe_forward:
  mediana_5l: 28.92
  biezacy: 10.68
  seria_csv: pe.csv
ps_forward:
  mediana_5l: 14.86
  biezacy: 5.91
"""


@pytest.fixture(autouse=True)
def archiwum_tymczasowe(tmp_path, monkeypatch):
    monkeypatch.setattr(archiwum, "DOMYSLNY_KATALOG", tmp_path / "archiwum")


def rejestr_z_kursem(kurs=168.89, waluta="USD"):
    r = RejestrFaktow("NVDA", D)  # bez kontroli dokumentów: kurs z dokumentu spoza testowego archiwum
    r.dodaj(Fakt(id=f"kurs.{D.isoformat()}", rodzaj="raportowany", pozycja="kurs", okres={"typ": "dzien", "koniec": D},
                 wartosc=kurs, jednostka="pieniadz_na_akcje", waluta=waluta, metoda="api", status="zweryfikowany",
                 dokument="doc-001"))
    return r


def csv_serii(wartosci, od=date(2021, 12, 1)):
    wiersze = ["Date;PE Ratio (1-Year Forward)"]
    for i, v in enumerate(wartosci):
        wiersze.append(f"{(od + timedelta(days=i)).isoformat()};{str(v).replace('.', ',')}")
    return "\n".join(wiersze) + "\n"


def katalog_scrab(tmp_path, tekst=SCRAB, csv=None):
    D_ = tmp_path / "analiza"
    D_.mkdir()
    (D_ / "scrab.yaml").write_text(tekst, encoding="utf-8")
    if csv is not None:
        (D_ / "pe.csv").write_text(csv, encoding="utf-8")
    return D_


# --- matematyka ------------------------------------------------------------------------------


def test_percentyl_liniowy():
    seria = [float(x) for x in range(1, 102)]  # 1..101
    assert trela.percentyl(seria, 0.90) == pytest.approx(91.0)
    assert trela.percentyl(seria, 0.5) == pytest.approx(51.0)
    assert trela.percentyl([10.0, 20.0], 0.25) == pytest.approx(12.5)


def test_cena_z_mnoznika_i_siatka():
    assert trela.cena_z_mnoznika(28.92, 15.81) == pytest.approx(457.2252)
    with pytest.raises(BrakSensu):
        trela.cena_z_mnoznika(28.92, 0.0)
    s = trela.siatka(28.92, 15.81, [-2, 0, 2], [-0.10, 0, 0.10])
    assert s[1][1] == pytest.approx(457.2252)
    assert s[0][0] == pytest.approx(26.92 * 15.81 * 0.9)  # 383,04 jak w arkuszu Treli
    assert s[2][2] == pytest.approx(30.92 * 15.81 * 1.1)  # 537,73


def test_csv_z_przecinkiem_i_naglowkiem():
    punkty = trela.seria_z_csv("Date;PE\n2026-11-10;10,68\n2026-11-11;10,7\n\n")
    assert punkty == [(date(2026, 11, 10), 10.68), (date(2026, 11, 11), 10.7)]


def test_wiersz_pliku_rozroznia_sekcje():
    assert trela._wiersz_pliku(SCRAB, "pe_forward.mediana_5l") == "mediana_5l: 28.92"
    assert trela._wiersz_pliku(SCRAB, "ps_forward.mediana_5l") == "mediana_5l: 14.86"
    assert trela._wiersz_pliku(SCRAB, "eps_prognoza") == "eps_prognoza: 15.81"


# --- przebieg na rejestrze -------------------------------------------------------------------


def test_cena_docelowa_konserwatywna(tmp_path):
    D_ = katalog_scrab(tmp_path, SCRAB.replace("  seria_csv: pe.csv\n", ""))
    r = rejestr_z_kursem()
    k = Kalkulator(r)
    w = trela.oblicz(k, D_)
    assert r[w["pe_kons"]].wartosc == pytest.approx(457.2252)
    assert r[w["ps_kons"]].wartosc == pytest.approx(424.5502)
    assert r[w["kons"]].wartosc == pytest.approx(440.8877)
    assert r[w["potencjal_kons"]].wartosc == pytest.approx(440.8877 / 168.89 - 1)
    # bez serii nie ma percentyla, więc nie ma wariantu optymistycznego
    assert w["optym"] is None and w["potencjal_optym"] is None
    assert any("brak serii mnożnika" in b for b in k.braki)
    # liczby ze Scrab: wklejka, jedno źródło, dosłowny wiersz pliku jako cytat
    eps = r[w["eps"]]
    assert eps.metoda.value == "wklejka" and eps.status.value == "jedno_zrodlo"
    assert eps.cytat == "eps_prognoza: 15.81" and eps.dokument == w["dokument"]
    assert r[w["kons"]].status.value == "jedno_zrodlo"
    # plik trafił do archiwum jako wklejka ze źródłem Scrab
    arch = archiwum.Archiwum("NVDA", D_)
    assert arch[w["dokument"]].zrodlo == "Scrab" and arch.sprawdz(w["dokument"])


def test_wariant_optymistyczny_z_percentyla_serii(tmp_path):
    stare = [500.0] * 30  # sprzed okna 5 lat: silnik je pomija
    nowe = [float(x) for x in range(1, 102)]
    tekst = csv_serii(stare, od=date(2020, 1, 1)) + csv_serii(nowe).split("\n", 1)[1]
    D_ = katalog_scrab(tmp_path, csv=tekst)
    r = rejestr_z_kursem()
    k = Kalkulator(r)
    w = trela.oblicz(k, D_)
    assert r[w["pe_percentyl"]].wartosc == pytest.approx(91.0)
    assert r[w["pe_percentyl"]].miejsce["punktow"] == 101
    assert r[w["pe_optym"]].wartosc == pytest.approx(91.0 * 15.81)
    # P/S nie ma serii, więc wariant optymistyczny to tylko metoda P/E
    assert r[w["optym"]].wartosc == pytest.approx(91.0 * 15.81)
    # mediana serii (51) daleko od mediany 5Y ze Scrab (28,92): trop do sprawdzenia
    assert any(b.startswith("trop: mediana P/E") for b in k.braki)


def test_ujemny_eps_daje_tylko_metode_ps(tmp_path):
    D_ = katalog_scrab(tmp_path, SCRAB.replace("eps_prognoza: 15.81", "eps_prognoza: -0.5").replace("  seria_csv: pe.csv\n", ""))
    r = rejestr_z_kursem()
    w = trela.oblicz(Kalkulator(r), D_)
    assert w["pe_kons"] is None
    assert r[w["kons"]].wartosc == pytest.approx(424.5502)
    assert w["metody"] == ["ps"]


def test_rozbiezny_kurs_to_trop(tmp_path):
    D_ = katalog_scrab(tmp_path, SCRAB.replace("  seria_csv: pe.csv\n", ""))
    k = Kalkulator(rejestr_z_kursem(kurs=150.0))
    w = trela.oblicz(k, D_)
    assert any("kurs ze Scrab" in b for b in k.braki)
    assert k.r[w["potencjal_kons"]].wartosc == pytest.approx(440.8877 / 150.0 - 1)


def test_blad_pliku_nie_przerywa_obliczen(tmp_path):
    D_ = katalog_scrab(tmp_path, "waluta: USD\neps_prognoza: 1\n")
    k = Kalkulator(rejestr_z_kursem())
    assert trela.oblicz(k, D_) == {}
    assert any("data_odczytu" in b for b in k.braki)


def test_brak_pliku(tmp_path):
    assert trela.oblicz(Kalkulator(rejestr_z_kursem()), tmp_path) == {}


def test_karta_ma_miare_potencjalu_treli(tmp_path):
    D_ = katalog_scrab(tmp_path, SCRAB.replace("  seria_csv: pe.csv\n", ""))
    r = rejestr_z_kursem()
    k = Kalkulator(r)
    trela.oblicz(k, D_)
    filary = karta_treli.oblicz(k, "USA", {}, None, None)
    wycena = next(f for f in filary if f.nazwa == "wycena")
    fid, wartosc, pkt = wycena.miary["potencjal_trela_kons"]
    assert fid.startswith("potencjal_trela_kons.") and pkt == 10  # potencjał +161% > próg 40%


def test_tabela_raportu(tmp_path):
    D_ = katalog_scrab(tmp_path, SCRAB.replace("  seria_csv: pe.csv\n", ""))
    r = rejestr_z_kursem()
    k = Kalkulator(r)
    w = trela.oblicz(k, D_)
    tekst = "\n".join(trela_tabela(k, {"trela": w}))
    assert "457,23 USD¹" in tekst and "**440,89 USD¹**" in tekst and "+161,1%¹" in tekst
    assert "Siatka wrażliwości P/E" in tekst and "Siatka wrażliwości P/S" in tekst
    assert "rok obrotowy FY2028" in tekst and "nie prognoza kursu ani rekomendacja" in tekst
    assert "Brak ceny docelowej" in "\n".join(trela_tabela(k, {}))
