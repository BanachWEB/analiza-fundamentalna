"""Testy raportu (krok 6): formaty, lint, renderowanie przypisów, budowa PDF."""

from datetime import date

import pytest

from silnik.fakty.rejestr import RejestrFaktow
from silnik.fakty.schemat import Fakt
from silnik.raport import formaty, lint
from silnik.raport.pdf import zbuduj


def F(id, v, jedn="pieniadz", status="zweryfikowany", typ="FY"):
    okres = {"typ": typ, "koniec": date(2025, 12, 31)}
    if typ == "FY":
        okres["poczatek"] = date(2025, 1, 1)
    return Fakt(id=id, rodzaj="raportowany", pozycja=id.split(".")[0], okres=okres, wartosc=v, jednostka=jedn,
                waluta="USD" if jedn in ("pieniadz", "pieniadz_na_akcje") else None, metoda="xbrl", status=status,
                dokument="doc-001", miejsce={"xbrl": "x"})


@pytest.mark.parametrize("v,wynik", [(331_839e6, "331,8 mld\u00a0USD"), (4.05e12, "4,05 bln\u00a0USD"),
                                     (47_401e6, "47,4 mld\u00a0USD"), (-1_842_205e3, "-1,8 mld\u00a0USD")])
def test_kwoty(v, wynik):
    assert formaty.kwota(v, "USD") == wynik


def test_formaty_jednostek():
    assert formaty.wartosc(F("marza.FY2025", 0.4712, "ulamek")) == "47,1%"
    assert formaty.wartosc(F("c_z.FY2025", 28.39, "mnoznik")) == "28,4×"
    assert formaty.okres(F("x.FY2025", 1)) == "rok obrotowy 2025 (do 31.12.2025)"


def rejestr():
    r = RejestrFaktow("X", date(2026, 11, 10))
    r.dodaj(F("przychody.FY2025", 1e9))
    r.dodaj(F("zysk_netto.FY2025", 1e8, status="odrzucony"))
    return r


@pytest.mark.parametrize("tekst", [
    "## 4. Branża i konkurencja",
    "1. Spółka działa od 1975 r.; raport z 30.09.2026 i FY2025Q3 oraz I półrocza (H1).",
    "Przychody wyniosły {{przychody.FY2025}}, a wykres: {{wykres:przychody}}, tabela: {{tabela:panel}}.",
    "Wg indeksu S&P 500 i WIG20; standard MSSF 16 i 10-K oraz `doc-003`.",
])
def test_lint_przepuszcza(tekst):
    assert lint.sprawdz(tekst, rejestr(), {"panel"}, {"przychody"}) == []


@pytest.mark.parametrize("tekst,powod", [
    ("Marża operacyjna wynosi 45 proc.", "liczba wpisana"),
    ("Spółka rośnie o kilkanaście % rocznie.", "znak %"),
    ("Zysk: {{zysk_netto.FY2025}}", "odrzucony"),
    ("Zysk: {{zysk_operacyjny.FY2025}}", "brak faktu"),
    ("{{tabela:nieistniejaca}}", "nieznana tabela"),
    ("Kapitalizacja to 4,05 bln\u00a0USD.", "liczba wpisana"),
    ("Spółka zarobiła 1850 mln.", "liczba wpisana"),
])
def test_lint_odrzuca(tekst, powod):
    bledy = lint.sprawdz(tekst, rejestr(), {"panel"}, set())
    assert bledy and any(powod in b.powod for b in bledy)


def test_pdf_buduje_sie(tmp_path):
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    ax.plot([1, 2], [1, 2])
    fig.savefig(tmp_path / "w.png")
    md = ("# Tytuł — zażółć gęślą jaźń\n\n## TL;DR\n\n> Teza **pogrubiona** i *kursywa*[^1].\n\n- punkt\n- punkt\n\n"
          "| A | B |\n|---|---:|\n| x | 1 |\n\n![w](w.png)\n\n[^1]: Źródło: test.\n")
    p = zbuduj(md, tmp_path / "r.pdf", "Test", tmp_path)
    assert p.exists() and p.stat().st_size > 5000
