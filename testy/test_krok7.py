"""Testy narzędzi dodanych w kroku 7 (bez sieci)."""

from datetime import date

import pytest

from silnik.fakty import cytat
from silnik.obliczenia.scenariusze import stopa_implikowana
from silnik.obliczenia.wycena import wartosc_przychody_marza
from silnik.pobieranie import konsensus
from silnik.raport import formaty, lint


def test_konsensus_parser():
    html = ('According to 58 analysts polled by S&amp;P Global, Microsoft stock has a consensus rating of "Strong Buy" '
            'and an average price target of $636.12. The average ... epsThis:{last:17.28,this:20.01357,growth:15.8192}')
    d = konsensus.parsuj(html)
    assert d["liczba_analitykow"] == 58 and d["cena_docelowa"] == 636.12
    assert d["wzrost_eps_konsensus"] == pytest.approx(0.158192)


def test_cytat_z_zerem_po_przecinku(tmp_path):
    p = tmp_path / "r.txt"
    p.write_text("an increase in net income of $5.0 billion and $0.67", encoding="utf-8")
    assert cytat.sprawdz(p, None, "an increase in net income of $5.0 billion", 5.0)[0]
    assert not cytat.sprawdz(p, None, "an increase in net income of $5.0 billion", 50.0)[0]


def test_tekst_html_bez_znacznikow(tmp_path):
    p = tmp_path / "r.html"
    p.write_text("<html><script>var x=1</script><table><tr><td>Revenue</td><td>$ 139,996</td></tr></table></html>",
                 encoding="utf-8")
    t = cytat.tekst_dokumentu(p, None)
    assert "var x" not in t
    assert cytat.sprawdz(p, None, "Revenue $ 139,996", 139996)[0]


def test_stopa_implikowana_odwraca_wycene():
    w = wartosc_przychody_marza(1000, 0.06, 10, 0.025, 0.08, 0.2)
    assert stopa_implikowana(1000, 0.06, 10, 0.025, 0.2, 10, w / 10) == pytest.approx(0.08, abs=1e-6)


def test_lint_nazwy_produktow():
    from silnik.fakty.rejestr import RejestrFaktow
    r = RejestrFaktow("X", date(2026, 1, 1))
    assert lint.sprawdz("Microsoft 365 i Dynamics 365, formularz W-8BEN, `DEF 14A`.", r, set(), set()) == []
    assert lint.sprawdz("Microsoft 366 klientów.", r, set(), set())


def test_liczba_calkowita_bez_przecinka():
    from silnik.fakty.schemat import Fakt
    f = Fakt(id="liczba_analitykow.2026-11-10", rodzaj="raportowany", pozycja="liczba_analitykow",
             okres={"typ": "dzien", "koniec": date(2026, 11, 10)}, wartosc=58, jednostka="liczba", metoda="parser_strony",
             status="jedno_zrodlo", dokument="doc-001", miejsce={})
    assert formaty.wartosc(f) == "58"
