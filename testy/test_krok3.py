"""Testy kroku 3 (GPW) na danych syntetycznych, bez sieci."""

import io
import json
import zipfile
from datetime import date

import pytest

from silnik.fakty import cytat
from silnik.fakty.rejestr import RejestrFaktow
from silnik.fakty.schemat import Status
from silnik.pobieranie import biznesradar, esef

# --- ESEF -----------------------------------------------------------------------

XHTML = b"""<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:ix="http://www.xbrl.org/2013/inlineXBRL"
 xmlns:xbrli="http://www.xbrl.org/2003/instance" xmlns:xbrldi="http://xbrl.org/2006/xbrldi"
 xmlns:iso4217="http://www.xbrl.org/2003/iso4217" xmlns:ifrs-full="https://xbrl.ifrs.org/taxonomy/2023-03-23/ifrs-full">
<body><ix:header><ix:resources>
 <xbrli:context id="d25"><xbrli:entity/><xbrli:period><xbrli:startDate>2025-01-01</xbrli:startDate><xbrli:endDate>2025-12-31</xbrli:endDate></xbrli:period></xbrli:context>
 <xbrli:context id="i25"><xbrli:entity/><xbrli:period><xbrli:instant>2025-12-31</xbrli:instant></xbrli:period></xbrli:context>
 <xbrli:context id="d25seg"><xbrli:entity><xbrli:segment><xbrldi:explicitMember dimension="x">y</xbrldi:explicitMember></xbrli:segment></xbrli:entity><xbrli:period><xbrli:startDate>2025-01-01</xbrli:startDate><xbrli:endDate>2025-12-31</xbrli:endDate></xbrli:period></xbrli:context>
 <xbrli:unit id="PLN"><xbrli:measure>iso4217:PLN</xbrli:measure></xbrli:unit>
</ix:resources></ix:header>
<p><ix:nonFraction name="ifrs-full:Revenue" contextRef="d25" unitRef="PLN" scale="3" decimals="-3" format="ixt:num-comma-decimal">33 634 155</ix:nonFraction></p>
<p><ix:nonFraction name="ifrs-full:Revenue" contextRef="d25seg" unitRef="PLN" scale="3" format="ixt:num-comma-decimal">1 000</ix:nonFraction></p>
<p>(<ix:nonFraction name="ifrs-full:CashFlowsFromUsedInInvestingActivities" contextRef="d25" unitRef="PLN" scale="3" sign="-" format="ixt:num-comma-decimal">2 464 017</ix:nonFraction>)</p>
<p><ix:nonFraction name="ifrs-full:Assets" contextRef="i25" unitRef="PLN" scale="3" format="ixt:num-comma-decimal">15 171 280</ix:nonFraction></p>
<p><ix:nonFraction name="ifrs-full:Equity" contextRef="i25" unitRef="PLN" scale="3" format="ixt:fixed-zero">-</ix:nonFraction></p>
</body></html>"""


def pakiet_zagniezdzony() -> bytes:
    wewn = io.BytesIO()
    with zipfile.ZipFile(wewn, "w") as z:
        z.writestr("raport/reports/raport.xhtml", XHTML)
    zewn = io.BytesIO()
    with zipfile.ZipFile(zewn, "w") as z:
        z.writestr("raport.xbri", wewn.getvalue())
        z.writestr("raport.xbri.xades", b"podpis")
    return zewn.getvalue()


def test_esef_zagniezdzony_pakiet_i_fakty():
    xhtml = esef.xhtml_z_pakietu(pakiet_zagniezdzony())
    f = {x.id: x for x in esef.wyciagnij_fakty(xhtml, "doc-001")}
    assert f["przychody.FY2025"].wartosc == 33634155  # bez danych z wymiarem (segment)
    assert f["przychody.FY2025"].skala.value == "tys"
    assert f["przychody.FY2025"].wartosc_bazowa() == 33634155000
    assert f["przeplywy_inwestycyjne.FY2025"].wartosc == -2464017  # atrybut sign="-"
    assert f["aktywa.2025-12-31"].waluta == "PLN"
    assert f["kapital_wlasny_z_udzialami_niekontrolujacymi.2025-12-31"].wartosc == 0  # fixed-zero


@pytest.mark.parametrize("tekst,fmt,wynik", [
    ("1 234,5", "ixt:num-comma-decimal", 1234.5),
    ("1.234,5", "ixt:num-comma-decimal", 1234.5),
    ("1,234.5", "ixt:num-dot-decimal", 1234.5),
    ("-", "ixt:fixed-zero", 0.0),
])
def test_esef_formaty_liczb(tekst, fmt, wynik):
    assert esef.liczba(tekst, fmt) == wynik


# --- Biznesradar ------------------------------------------------------------------

HTML_BR = """<table class="report-table"><tr><th></th>
<th>2025 (gru 25)</th><th>2026/Q1 (mar 26)</th><th>2026/Q2 (cze 26)</th><th>2026/Q3 (wrz 26)</th><th>O4K (wrz 26)*</th></tr>
<tr data-field="IncomeRevenues"><td>Przychody</td>
<td><span class="value">33 634 155</span></td><td><span class="value">8 439 401</span></td>
<td><span class="value">9 531 400</span></td><td><span class="value">9 708 326</span></td><td><span class="value">1</span></td></tr>
<tr data-field="BalanceTotalAssets"><td>Aktywa</td><td><span class="value">15 171 280</span></td><td></td><td></td><td></td><td></td></tr>
</table>"""


def test_biznesradar_parser_i_sumy():
    d = biznesradar.parsuj(HTML_BR)
    assert d[("przychody", "FY", date(2025, 12, 31))] == 33634155000
    assert d[("aktywa", "dzien", date(2025, 12, 31))] == 15171280000
    assert not any(k[1] == "O4K" for k in d)
    s = biznesradar.sumy_narastajace(d)
    assert s[("przychody", "M9", date(2026, 9, 30))] == pytest.approx(27679127000)
    assert s[("przychody", "H1", date(2026, 6, 30))] == pytest.approx(17970801000)


# --- test cytatu ----------------------------------------------------------------------

STRONA = ("Przychody ze sprzedaży ........ 27 679 127 24 738 104\n"
          "Środki pieniężne netto z działalności inwestycyjnej .... (1 842 205) (1 568 460)\n"
          "Zysk na akcję w PLN ..... 1,22 1,21\n")


def test_liczba_w_cytacie():
    assert cytat.liczba_w_cytacie(27679127, STRONA)
    assert cytat.liczba_w_cytacie(-1842205, STRONA)
    assert cytat.liczba_w_cytacie(1.22, STRONA)
    assert not cytat.liczba_w_cytacie(1842205, STRONA)  # w raporcie wartość jest ujemna
    assert not cytat.liczba_w_cytacie(27679172, STRONA)  # przestawione cyfry


@pytest.fixture
def dokument(tmp_path):
    p = tmp_path / "raport.txt"
    p.write_text(STRONA, encoding="utf-8")
    return p


def propozycja(**kw):
    p = {"id": "przychody.FY2026M9", "pozycja": "przychody",
         "okres": {"typ": "M9", "poczatek": "2026-01-01", "koniec": "2026-09-30"},
         "wartosc": 27679127, "skala": "tys", "jednostka": "pieniadz", "waluta": "PLN", "dokument": "doc-001",
         "miejsce": {}, "cytat": "Przychody ze sprzedaży ........ 27 679 127 24 738 104"}
    p.update(kw)
    return p


@pytest.mark.parametrize("zmiana,status,powod", [
    ({}, Status.jedno_zrodlo, "ok"),
    ({"wartosc": 27679000}, Status.odrzucony, "wartości nie ma w cytacie"),  # model zaokrąglił
    ({"cytat": "Przychody netto ze sprzedaży 27 679 127"}, Status.odrzucony, "cytatu nie ma"),  # zmyślony cytat
    ({"wartosc": 24738104}, Status.jedno_zrodlo, "ok"),  # zła kolumna: test jej nie łapie, łapie drugie źródło
])
def test_dodaj_propozycje(dokument, zmiana, status, powod):
    r = RejestrFaktow("DNP", date(2026, 11, 10), dokumenty=["doc-001"])
    f = cytat.dodaj_propozycje(r, lambda _id: dokument, [propozycja(**zmiana)])[0]
    assert f.status == status
    assert powod in f.kontrole[-1]


def test_propozycja_bez_cytatu_niedozwolona(dokument):
    r = RejestrFaktow("DNP", date(2026, 11, 10), dokumenty=["doc-001"])
    with pytest.raises(Exception, match="cytat"):
        cytat.dodaj_propozycje(r, lambda _id: dokument, [propozycja(cytat=None)])


def test_odrzucone_nie_wchodza_do_obliczen(dokument):
    from silnik.fakty.rejestr import BladRejestru
    from silnik.fakty.schemat import Jednostka, Okres

    r = RejestrFaktow("DNP", date(2026, 11, 10), dokumenty=["doc-001"])
    cytat.dodaj_propozycje(r, lambda _id: dokument, [propozycja(wartosc=1)])
    with pytest.raises(BladRejestru, match="odrzucone"):
        r.wylicz("x.FY2026M9", "x", "2*p", ["przychody.FY2026M9"], lambda p: 2 * p, Jednostka.pieniadz,
                 Okres(typ="M9", poczatek=date(2026, 1, 1), koniec=date(2026, 9, 30)))


def test_pdf_liczby_z_kolumn(tmp_path):
    """W PDF kolumny dzieli szeroki odstęp; fragment liczby nie przechodzi testu."""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    p = tmp_path / "raport.pdf"
    c = canvas.Canvas(str(p), pagesize=A4)
    c.setFont("Helvetica", 9)
    y = 700
    c.drawString(70, y, "Liczba akcji (w szt.) ........")
    for x, tekst in ((300, "980 400 000"), (360, "980 400 000")):
        c.drawString(x, y, tekst)
    c.drawString(70, y - 20, "Przychody ze sprzedazy ........")
    for x, tekst in ((300, "27 679 127"), (360, "24 738 104")):
        c.drawString(x, y - 20, tekst)
    c.save()
    cyt_akcje = "Liczba akcji (w szt.) ........ 980 400 000 980 400 000"
    cyt_przych = "Przychody ze sprzedazy ........ 27 679 127 24 738 104"
    assert cytat.sprawdz(p, 1, cyt_akcje, 980400000)[0]
    assert cytat.sprawdz(p, 1, cyt_przych, 24738104)[0]
    ok, powod = cytat.sprawdz(p, 1, cyt_przych, 679127)
    assert not ok and "fragmentem" in powod
    assert not cytat.sprawdz(p, 2, cyt_przych, 27679127)[0]  # zła strona


def test_uzupelnienie_z_biznesradaru_i_brak_samopotwierdzenia():
    from silnik.fakty.weryfikacja import Raport, drugie_zrodlo

    dane = {
        ("przychody", "FY", date(2019, 12, 31)): (10_000_000.0, "doc-009"),
        ("przychody", "FY", date(2025, 12, 31)): (33_634_155_000.0, "doc-009"),
        ("przychody", "Q", date(2025, 12, 31)): (1.0, "doc-010"),
    }
    istniejace = {("przychody", "FY", date(2025, 12, 31))}
    fakty = biznesradar.fakty_uzupelniajace(dane, istniejace)
    assert [f.id for f in fakty] == ["przychody.FY2019"]
    f = fakty[0]
    assert f.wartosc == 10_000 and f.skala.value == "tys" and f.metoda.value == "parser_strony"
    assert f.okres.poczatek == date(2019, 1, 1)
    r = RejestrFaktow("DNP", date(2026, 11, 10))
    r.dodaj(f)
    drugie_zrodlo(r, dane, Raport())
    assert r["przychody.FY2019"].status == Status.jedno_zrodlo  # nie potwierdza sam siebie
