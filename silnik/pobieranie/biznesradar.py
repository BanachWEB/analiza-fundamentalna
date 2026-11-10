"""Drugie źródło dla spółek z GPW: tabele sprawozdań z Biznesradaru.

Biznesradar podaje dane w tys. PLN, roczne i kwartalne (kwartały osobno,
nie narastająco). Parser czyta tabelę deterministycznie. Wartości służą do
kontroli faktów z raportów spółki; nie trafiają do rejestru jako fakty.
Z kwartałów parser liczy też sumy narastające (H1, M9), żeby porównać je
z danymi z raportów kwartalnych, które podają okresy narastające.
"""

from __future__ import annotations

import calendar
import re
from datetime import date
from pathlib import Path

from lxml import html as lhtml

from silnik.fakty.schemat import TypDokumentu
from silnik.pobieranie.archiwum import Archiwum
from silnik.pobieranie.http import pobierz

STRONY = {
    "rachunek": "raporty-finansowe-rachunek-zyskow-i-strat",
    "bilans": "raporty-finansowe-bilans",
    "przeplywy": "raporty-finansowe-przeplywy-pieniezne",
}

# pole Biznesradaru → pozycja kanoniczna
MAPOWANIE = {
    "IncomeRevenues": "przychody",
    "IncomeEBIT": "zysk_operacyjny",
    "IncomeBeforeTaxProfit": "zysk_przed_opodatkowaniem",
    "IncomeShareholderNetProfit": "zysk_netto",
    "IncomeNetProfit": "zysk_netto_razem",
    "BalanceTotalAssets": "aktywa",
    "BalanceTotalEquityAndLiabilities": "pasywa_razem",
    "BalanceCapital": "kapital_wlasny",
    "BalanceCash": "gotowka",
    "BalanceInventory": "zapasy",
    "CashflowOperatingCashflow": "przeplywy_operacyjne",
    "CashflowInvestingCashflow": "przeplywy_inwestycyjne",
    "CashflowFinancingCashflow": "przeplywy_finansowe",
    "CashflowAmortization": "amortyzacja",
    "CashflowNetCashflow": "zmiana_gotowki",
}
POZYCJE_STANU = {"aktywa", "pasywa_razem", "kapital_wlasny", "gotowka", "zapasy"}
MIESIACE = {"sty": 1, "lut": 2, "mar": 3, "kwi": 4, "maj": 5, "cze": 6, "lip": 7, "sie": 8, "wrz": 9, "paź": 10, "paz": 10, "lis": 11, "gru": 12}


class BladBiznesradar(Exception):
    pass


def url(ticker: str, strona: str, kwartalne: bool) -> str:
    return f"https://www.biznesradar.pl/{STRONY[strona]}/{ticker.upper()}" + (",Q" if kwartalne else "")


def pobierz_do_archiwum(ticker: str, archiwum: Archiwum) -> list:
    dokumenty = []
    for strona in STRONY:
        for kwartalne in (False, True):
            adres = url(ticker, strona, kwartalne)
            plik = pobierz(adres, rozszerzenie=".html")
            try:
                opis = f"{strona} {'kwartalne' if kwartalne else 'roczne'}"
                dokumenty.append(archiwum.dodaj_plik(plik, TypDokumentu.strona, "Biznesradar", adres=adres, opis=opis))
            finally:
                plik.unlink(missing_ok=True)
    return dokumenty


def _koniec(naglowek: str) -> tuple[str, date] | None:
    """'2025 (gru 25)' → ('FY', 2025-12-31); '2026/Q3 (wrz 26)' → ('Q', 2026-09-30); 'O4K' → None."""
    m = re.search(r"\((\w+)\s+(\d{2})\)", naglowek)
    if not m or naglowek.strip().startswith("O4K"):
        return None
    miesiac = MIESIACE.get(m.group(1).lower())
    if not miesiac:
        return None
    rok = 2000 + int(m.group(2))
    typ = "Q" if "/Q" in naglowek else "FY"
    return typ, date(rok, miesiac, calendar.monthrange(rok, miesiac)[1])


def _liczba(tekst: str) -> float | None:
    t = tekst.replace(" ", " ").replace(" ", "").replace(",", ".").strip()
    if not t or t in ("-", "—"):
        return None
    try:
        return float(t)
    except ValueError:
        return None


def parsuj(tresc: str) -> dict[tuple[str, str, date], float]:
    """Zwraca {(pozycja, typ, koniec): wartość w PLN}; typ: FY, Q albo dzien."""
    drzewo = lhtml.fromstring(tresc)
    tabele = drzewo.xpath('//table[contains(@class,"report-table")]')
    if not tabele:
        raise BladBiznesradar("brak tabeli raportu; zmienił się układ strony albo spółka nie istnieje")
    t = tabele[0]
    kolumny = [_koniec(" ".join(th.text_content().split())) for th in t.xpath(".//tr[1]/th")[1:]]
    wynik = {}
    for tr in t.xpath(".//tr[@data-field]"):
        pozycja = MAPOWANIE.get(tr.get("data-field"))
        if not pozycja:
            continue
        for kol, td in zip(kolumny, tr.xpath("./td")[1:]):
            if kol is None:
                continue
            wartosci = td.xpath('.//span[@class="value"]')
            v = _liczba(wartosci[0].text_content()) if wartosci else None
            if v is None:
                continue
            typ, koniec = kol
            if pozycja in POZYCJE_STANU:
                typ = "dzien"
            wynik[(pozycja, typ, koniec)] = v * 1000  # tys. PLN → PLN
    return wynik


def sumy_narastajace(dane: dict[tuple[str, str, date], float], miesiac_konca_roku: int = 12) -> dict:
    """Dodaje H1 i M9 jako sumy kolejnych kwartałów tego samego roku obrotowego."""
    wynik = dict(dane)
    kwartaly = {(p, k): v for (p, t, k), v in dane.items() if t == "Q"}
    for (pozycja, koniec), _ in kwartaly.items():
        # numer kwartału w roku obrotowym
        nr = ((koniec.month - miesiac_konca_roku - 1) % 12) // 3 + 1
        if nr not in (2, 3):
            continue
        konce = []
        for i in range(nr):
            m = koniec.month - 3 * i
            r = koniec.year + (m - 1) // 12 if m > 0 else koniec.year - 1
            m = (m - 1) % 12 + 1
            konce.append(date(r, m, calendar.monthrange(r, m)[1]))
        if all((pozycja, k) in kwartaly for k in konce):
            wynik[(pozycja, "H1" if nr == 2 else "M9", koniec)] = sum(kwartaly[(pozycja, k)] for k in konce)
    return wynik


def parsuj_dokumenty(archiwum: Archiwum, dok_ids: list[str]) -> dict:
    wynik = {}
    for dok_id in dok_ids:
        for klucz, v in parsuj(Path(archiwum.sciezka(dok_id)).read_text(encoding="utf-8")).items():
            wynik.setdefault(klucz, (v, dok_id))
    # sumy narastające: dokument źródłowy = dokument kwartalny tej pozycji
    proste = {k: v for k, (v, _) in wynik.items()}
    dok_kw = {(p, k): d for (p, t, k), (_, d) in wynik.items() if t == "Q"}
    for klucz, v in sumy_narastajace(proste).items():
        if klucz not in wynik:
            wynik[klucz] = (v, dok_kw.get((klucz[0], klucz[2]), "?"))
    return wynik


def fakty_uzupelniajace(dane: dict, istniejace: set[tuple[str, str, date]], lat: int = 10) -> list:
    """Fakty roczne i stany na koniec roku z Biznesradaru dla okresów, których nie ma w raportach spółki.

    `dane`: wynik parsuj_dokumenty; `istniejace`: klucze (pozycja, grupa okresu, koniec) faktów z raportów.
    Kwartały i sumy narastające nie trafiają do rejestru: służą tylko do kontroli.
    """
    from silnik.fakty.schemat import Fakt, Jednostka, Metoda, Okres, Rodzaj, Skala, Status

    konce_roku = sorted({k for (_, t, k) in dane if t == "FY"})[-lat:]
    wynik = []
    for (pozycja, typ, koniec), (v, dok) in sorted(dane.items(), key=lambda x: (x[0][0], x[0][2])):
        if koniec not in konce_roku or typ not in ("FY", "dzien") or (pozycja, typ, koniec) in istniejace:
            continue
        if typ == "FY":
            poczatek = date(koniec.year - 1, koniec.month, calendar.monthrange(koniec.year - 1, koniec.month)[1])
            poczatek = date.fromordinal(poczatek.toordinal() + 1)
            okres = Okres(typ="FY", poczatek=poczatek, koniec=koniec)
            fid = f"{pozycja}.FY{koniec.year}"
        else:
            okres = Okres(typ="dzien", koniec=koniec)
            fid = f"{pozycja}.{koniec.isoformat()}"
        wynik.append(Fakt(
            id=fid, rodzaj=Rodzaj.raportowany, pozycja=pozycja, okres=okres, wartosc=v / 1000, skala=Skala.tys,
            jednostka=Jednostka.pieniadz, waluta="PLN", metoda=Metoda.parser_strony, status=Status.jedno_zrodlo,
            dokument=dok, miejsce={"zrodlo": "Biznesradar", "pole": pozycja},
            kontrole=["uzupelnienie:biznesradar:brak_raportu_spolki_w_archiwum"],
        ))
    return wynik
