"""Dane rynkowe: kursy, obroty, rentowność obligacji USA, premie za ryzyko (Damodaran).

Źródła (sprawdzone 10.11.2026):
- USA: historia kursów z Yahoo (chart API), kontrola ostatniego kursu ze Stock Analysis;
  rentowność 10-letnich obligacji USA z Treasury.gov (CSV).
- GPW: historia kursów spółki i indeksu WIG z Biznesradaru (notowania historyczne),
  liczba akcji ze strony notowań Biznesradaru.
- Premia za ryzyko rynku akcji i spread niewypłacalności kraju: tabela Damodarana (ctryprem.html).
- Rentowność polskich obligacji 10-letnich: tabela „Rentowności obligacji wybranych państw”
  Strefy Inwestorów (publikowana w dni robocze); gdy jej brak, model albo właściciel podaje
  wartość jako założenie ze źródłem i datą (parametr --rf).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional

from lxml import html as lhtml

from silnik.fakty.schemat import Fakt, Jednostka, Metoda, Okres, Rodzaj, Status, TypDokumentu
from silnik.pobieranie.archiwum import Archiwum
from silnik.pobieranie.http import pobierz


@dataclass
class Sesja:
    dzien: date
    zamkniecie: float
    wolumen: float


class BladRynku(Exception):
    pass


def _do_archiwum(archiwum: Archiwum, url: str, zrodlo: str, opis: str, rozszerzenie: str):
    plik = pobierz(url, rozszerzenie=rozszerzenie)
    try:
        return archiwum.dodaj_plik(plik, TypDokumentu.strona, zrodlo, adres=url, opis=opis)
    finally:
        plik.unlink(missing_ok=True)


# --- historia kursów ------------------------------------------------------------


def url_yahoo(symbol: str) -> str:
    return f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=2y&interval=1d"


def sesje_yahoo(tresc: str) -> list[Sesja]:
    d = json.loads(tresc)["chart"]
    if d.get("error") or not d.get("result"):
        raise BladRynku(f"Yahoo: {d.get('error')}")
    r = d["result"][0]
    zamk = r["indicators"]["quote"][0]["close"]
    wol = r["indicators"]["quote"][0].get("volume") or [0] * len(zamk)
    wynik = []
    for t, c, v in zip(r["timestamp"], zamk, wol):
        if c is None:
            continue
        wynik.append(Sesja(datetime.fromtimestamp(t, tz=timezone.utc).date(), float(c), float(v or 0)))
    return wynik


def url_biznesradar_historia(symbol: str, strona: int) -> str:
    return f"https://www.biznesradar.pl/notowania-historyczne/{symbol}" + (f",{strona}" if strona > 1 else "")


def sesje_biznesradar(tresc: str) -> list[Sesja]:
    drzewo = lhtml.fromstring(tresc)
    tabele = drzewo.xpath('//table[contains(@class,"qTableFull")]')
    if not tabele:
        raise BladRynku("Biznesradar: brak tabeli notowań")
    wynik = []
    for tr in tabele[0].xpath(".//tr")[1:]:
        k = [" ".join(td.text_content().split()) for td in tr.xpath("./td")]
        if len(k) < 6:
            continue
        try:
            dz = datetime.strptime(k[0], "%d.%m.%Y").date()
            wynik.append(Sesja(dz, float(k[4].replace(" ", "")), float(k[5].replace(" ", "") or 0)))
        except ValueError:
            continue
    return wynik


def historia(archiwum: Archiwum, rynek: str, symbol: str, sesji: int = 280) -> tuple[list[Sesja], list[str]]:
    """Zwraca (sesje od najstarszej, id dokumentów)."""
    if rynek == "USA":
        dok = _do_archiwum(archiwum, url_yahoo(symbol), "Yahoo Finance", f"notowania dzienne {symbol}", ".json")
        return sorted(sesje_yahoo(archiwum.tekst(dok.id)), key=lambda s: s.dzien), [dok.id]
    sesje, ids = [], []
    for nr in range(1, 1 + (sesji // 50) + 1):
        dok = _do_archiwum(archiwum, url_biznesradar_historia(symbol, nr), "Biznesradar",
                           f"notowania historyczne {symbol}, strona {nr}", ".html")
        ids.append(dok.id)
        nowe = sesje_biznesradar(archiwum.tekst(dok.id))
        if not nowe:
            break
        sesje += nowe
        if len(sesje) >= sesji:
            break
    unik = {s.dzien: s for s in sesje}
    return sorted(unik.values(), key=lambda s: s.dzien), ids


def stopa_zwrotu_12_1(sesje: list[Sesja]) -> Optional[tuple[float, date, date]]:
    """Stopa zwrotu od ok. 12 miesięcy do ok. 1 miesiąca temu (momentum 12–1)."""
    if not sesje:
        return None
    koniec = sesje[-1].dzien
    def blisko(dni):
        cel = date.fromordinal(koniec.toordinal() - dni)
        kandydaci = [s for s in sesje if s.dzien <= cel]
        return kandydaci[-1] if kandydaci else None
    a, b = blisko(365), blisko(30)
    if a is None or b is None or (koniec - a.dzien).days < 350:
        return None
    return b.zamkniecie / a.zamkniecie - 1, a.dzien, b.dzien


def zmiana_kursu_3m(sesje: list[Sesja]) -> Optional[tuple[float, date]]:
    """Zmiana kursu od ostatniej sesji sprzed ok. 3 miesięcy (91 dni) do ostatniej sesji.

    Zasady właściciela: „pauza po rajdzie” — nie kupuje, gdy kurs jest o ponad 25% wyższy niż 3 miesiące wcześniej.
    """
    if not sesje:
        return None
    koniec = sesje[-1].dzien
    cel = date.fromordinal(koniec.toordinal() - 91)
    kandydaci = [s for s in sesje if s.dzien <= cel]
    if not kandydaci or (cel - kandydaci[-1].dzien).days > 7:
        return None
    a = kandydaci[-1]
    return sesje[-1].zamkniecie / a.zamkniecie - 1, a.dzien


# --- fakty rynkowe -------------------------------------------------------------------


def _fakt(fid, pozycja, okres, wartosc, jednostka, dok, miejsce, waluta=None, metoda=Metoda.api):
    return Fakt(id=fid, rodzaj=Rodzaj.raportowany, pozycja=pozycja, okres=okres, wartosc=wartosc, jednostka=jednostka,
                waluta=waluta, metoda=metoda, status=Status.jedno_zrodlo, dokument=dok, miejsce=miejsce)


def fakty_z_historii(sesje: list[Sesja], dok_ids: list[str], waluta: str, prefiks: str = "") -> list[Fakt]:
    """Kurs ostatni, momentum 12–1, zmiana kursu z 3 miesięcy i średnie dzienne obroty z 60 sesji."""
    if not sesje:
        return []
    ost = sesje[-1]
    dok = dok_ids[0]
    metoda = Metoda.api if dok_ids and len(dok_ids) == 1 else Metoda.parser_strony
    p = prefiks
    wynik = [_fakt(f"{p}kurs.{ost.dzien.isoformat()}", f"{p}kurs", Okres(typ="dzien", koniec=ost.dzien), ost.zamkniecie,
                   Jednostka.pieniadz_na_akcje if not p else Jednostka.punkty, dok,
                   {"sesja": ost.dzien.isoformat(), "pole": "zamknięcie"}, waluta if not p else None, metoda)]
    m = stopa_zwrotu_12_1(sesje)
    if m:
        wynik.append(_fakt(f"{p}momentum_12_1.{ost.dzien.isoformat()}", f"{p}momentum_12_1",
                           Okres(typ="dzien", koniec=ost.dzien), m[0], Jednostka.ulamek, dok,
                           {"od": m[1].isoformat(), "do": m[2].isoformat(), "obliczenie": "kurs(do) / kurs(od) - 1",
                            "dokumenty": dok_ids}, metoda=metoda))
    z3 = zmiana_kursu_3m(sesje)
    if z3 and not p:
        wynik.append(_fakt(f"zmiana_kursu_3m.{ost.dzien.isoformat()}", "zmiana_kursu_3m",
                           Okres(typ="dzien", koniec=ost.dzien), z3[0], Jednostka.ulamek, dok,
                           {"od": z3[1].isoformat(), "do": ost.dzien.isoformat(), "obliczenie": "kurs(do) / kurs(od) - 1",
                            "dokumenty": dok_ids}, metoda=metoda))
    if not p:
        ostatnie = sesje[-60:]
        obroty = sum(s.zamkniecie * s.wolumen for s in ostatnie) / len(ostatnie)
        wynik.append(_fakt(f"obroty_dzienne_60s.{ost.dzien.isoformat()}", "obroty_dzienne_60s",
                           Okres(typ="dzien", koniec=ost.dzien), obroty, Jednostka.pieniadz, dok,
                           {"obliczenie": "średnia z 60 sesji: zamknięcie × wolumen", "od": ostatnie[0].dzien.isoformat(),
                            "dokumenty": dok_ids}, waluta, metoda))
    return wynik


# --- kontrola kursu i liczba akcji ------------------------------------------------------


def sesje_stockanalysis(tresc: str) -> list[Sesja]:
    """Historia z Stock Analysis (za darmo ok. 6 miesięcy): wariant awaryjny, gdy Yahoo nie odpowiada."""
    wynik = []
    for m in re.finditer(r"\{([^{}]*t:\"\d{4}-\d{2}-\d{2}\"[^{}]*)\}", tresc):
        pola = dict(re.findall(r"(\w+):(\"[^\"]*\"|-?[\d.]+)", m.group(1)))
        try:
            wynik.append(Sesja(date.fromisoformat(pola["t"].strip('"')), float(pola["c"]), float(pola.get("v", 0))))
        except (KeyError, ValueError):
            continue
    return sorted({s.dzien: s for s in wynik}.values(), key=lambda s: s.dzien)


def kurs_stockanalysis(tresc: str) -> Optional[tuple[date, float]]:
    m = re.search(r'data:\[\{t:"(\d{4}-\d{2}-\d{2})",o:[\d.]+,h:[\d.]+,l:[\d.]+,c:([\d.]+)', tresc)
    return (date.fromisoformat(m.group(1)), float(m.group(2))) if m else None


def notowania_biznesradar(tresc: str) -> dict:
    tekst = " ".join(lhtml.fromstring(tresc).text_content().split())
    wynik = {}
    m = re.search(r"Liczba akcji:\s*([\d ]+)", tekst)
    if m:
        wynik["liczba_akcji"] = float(m.group(1).replace(" ", ""))
    m = re.search(r"Notowania\s+\S+\s+\(([^)]+)\)", tekst)
    if m:
        wynik["nazwa"] = m.group(1).strip()
    m = re.search(r'datetime="(\d{4}-\d{2}-\d{2})', tresc)
    if m:
        wynik["dzien"] = date.fromisoformat(m.group(1))
    return wynik


# --- stopy i premie ----------------------------------------------------------------------

URL_TREASURY = ("https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/"
                "{rok}/all?type=daily_treasury_yield_curve&field_tdr_date_value={rok}&page&_format=csv")
URL_DAMODARAN = "https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/ctryprem.html"


def rentownosc_treasury(tresc: str) -> tuple[date, float]:
    linie = [l for l in tresc.strip().splitlines() if l]
    naglowek = [h.strip('"') for h in linie[0].split(",")]
    kol = naglowek.index("10 Yr")
    pierwszy = linie[1].split(",")
    return datetime.strptime(pierwszy[0], "%m/%d/%Y").date(), float(pierwszy[kol]) / 100


def damodaran_kraj(tresc: str, kraj: str) -> dict:
    """Wiersz kraju z ctryprem.html: rating, spread, premia kraju, premia rynku akcji razem."""
    tekst = re.sub(r"<[^>]+>", " ", tresc)
    tekst = re.sub(r"&nbsp;", " ", tekst)
    m = re.search(re.escape(kraj) + r"\s+([A-Za-z0-9]+)\s+([\d.]+)%\s+([\d.]+)%\s+([\d.]+)%", tekst)
    if not m:
        raise BladRynku(f"Damodaran: brak wiersza dla {kraj}")
    return {"rating": m.group(1), "spread": float(m.group(2)) / 100, "premia_kraju": float(m.group(3)) / 100,
            "premia_rynku": float(m.group(4)) / 100}


URL_STREFA = "https://strefainwestorow.pl/wiadomosci/{d}/rentownosci-obligacji-wybranych-panstw-tabela"


def rentownosc_strefa(tresc: str) -> tuple[date, float]:
    tekst = " ".join(lhtml.fromstring(tresc).text_content().split())
    m = re.search(r"Rentowności (\d\d\.\d\d\.\d{4}).*?Polska 10-letnie ([\d,]+)", tekst)
    if not m:
        raise BladRynku("Strefa Inwestorów: brak wiersza „Polska 10-letnie”")
    return datetime.strptime(m.group(1), "%d.%m.%Y").date(), float(m.group(2).replace(",", ".")) / 100


def fakt_rentownosc_pl(archiwum: Archiwum, dzien: date, dni_wstecz: int = 7) -> Fakt:
    from silnik.pobieranie.http import BladPobierania

    for i in range(dni_wstecz + 1):
        d = date.fromordinal(dzien.toordinal() - i)
        url = URL_STREFA.format(d=d.strftime("%Y%m%d"))
        try:
            dok = archiwum.po_adresie(url) or _do_archiwum(archiwum, url, "Strefa Inwestorów", "rentowności obligacji", ".html")
        except BladPobierania:
            continue
        dz, r = rentownosc_strefa(archiwum.tekst(dok.id))
        return _fakt(f"rentownosc_10l.{dz.isoformat()}", "rentownosc_10l", Okres(typ="dzien", koniec=dz), r,
                     Jednostka.ulamek, dok.id, {"wiersz": "Polska 10-letnie", "kolumna": "rentowność aktualna"},
                     metoda=Metoda.parser_strony)
    raise BladRynku(f"brak tabeli rentowności Strefy Inwestorów z ostatnich {dni_wstecz} dni")


def fakty_stop(archiwum: Archiwum, rynek: str, dzien: date) -> list[Fakt]:
    wynik = []
    dok = _do_archiwum(archiwum, URL_DAMODARAN, "Damodaran (NYU Stern)", "premie za ryzyko krajów", ".html")
    kraj = "United States" if rynek == "USA" else "Poland"
    d = damodaran_kraj(archiwum.tekst(dok.id), kraj)
    okres = Okres(typ="dzien", koniec=dzien)
    wynik.append(_fakt(f"premia_ryzyka_akcji.{dzien.isoformat()}", "premia_ryzyka_akcji", okres, d["premia_rynku"],
                       Jednostka.ulamek, dok.id, {"kraj": kraj, "kolumna": "Total Equity Risk Premium", "rating": d["rating"]},
                       metoda=Metoda.parser_strony))
    if rynek != "USA":
        wynik.append(_fakt(f"spread_kraju.{dzien.isoformat()}", "spread_kraju", okres, d["spread"], Jednostka.ulamek,
                           dok.id, {"kraj": kraj, "kolumna": "Adj. Default Spread"}, metoda=Metoda.parser_strony))
    if rynek != "USA":
        try:
            wynik.append(fakt_rentownosc_pl(archiwum, dzien))
        except BladRynku:
            pass  # wtedy model albo właściciel podaje --rf
    if rynek == "USA":
        dok_t = _do_archiwum(archiwum, URL_TREASURY.format(rok=dzien.year), "U.S. Treasury", "rentowności obligacji", ".csv")
        dz, r = rentownosc_treasury(archiwum.tekst(dok_t.id))
        wynik.append(_fakt(f"rentownosc_10l.{dz.isoformat()}", "rentownosc_10l", Okres(typ="dzien", koniec=dz), r,
                           Jednostka.ulamek, dok_t.id, {"kolumna": "10 Yr", "dzien": dz.isoformat()}))
    return wynik
