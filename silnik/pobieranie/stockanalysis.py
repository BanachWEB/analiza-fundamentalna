"""Drugie źródło dla spółek z USA: dane roczne wbudowane w strony Stock Analysis.

Strony zawierają obiekt JavaScript z tablicami (datekey, revenue, opinc, ...).
Parser czyta te tablice deterministycznie; model nie bierze w tym udziału.
Wartości z tego źródła nie trafiają do rejestru jako fakty: służą do kontroli
faktów z SEC (wynik zapisujemy w polu „kontrole”).
"""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

from silnik.fakty.schemat import TypDokumentu
from silnik.pobieranie.archiwum import Archiwum
from silnik.pobieranie.http import pobierz

STRONY = ("income-statement", "balance-sheet", "cash-flow-statement")

# klucz Stock Analysis → (pozycja kanoniczna, mnożnik znaku)
MAPOWANIE = {
    "revenue": ("przychody", 1),
    "gp": ("zysk_brutto", 1),
    "opinc": ("zysk_operacyjny", 1),
    "netinc": ("zysk_netto", 1),
    "epsdil": ("eps_rozwodniony", 1),
    "sharesDiluted": ("liczba_akcji_rozwodniona", 1),
    "assets": ("aktywa", 1),
    "liabilities": ("zobowiazania", 1),
    "equity": ("kapital_wlasny_razem", 1),  # z udziałami niekontrolującymi; patrz ALIASY w weryfikacji
    "ncfo": ("przeplywy_operacyjne", 1),
    "capex": ("capex", -1),  # Stock Analysis podaje wydatki ze znakiem minus
    "sbcomp": ("sbc", 1),
}


class BladStockAnalysis(Exception):
    pass


def url(ticker: str, strona: str) -> str:
    return f"https://stockanalysis.com/stocks/{ticker.lower()}/financials/{strona}/"


def pobierz_do_archiwum(ticker: str, archiwum: Archiwum) -> list:
    dokumenty = []
    for strona in STRONY:
        adres = url(ticker, strona)
        plik = pobierz(adres, rozszerzenie=".html")
        try:
            dokumenty.append(archiwum.dodaj_plik(plik, TypDokumentu.strona, "Stock Analysis", adres=adres, opis=strona))
        finally:
            plik.unlink(missing_ok=True)
    return dokumenty


def _tablica(html: str, start: int, klucz: str):
    m = re.compile(r"[,{]" + re.escape(klucz) + r":\[([^\]]*)\]").search(html, start)
    if not m:
        return None
    return json.loads("[" + m.group(1) + "]")


POZYCJE_STANU = {"aktywa", "zobowiazania", "kapital_wlasny_razem"}


def parsuj(html: str) -> dict[tuple[str, str, date], float]:
    """Zwraca {(pozycja, typ, koniec okresu): wartość}; typ FY albo dzien (bez kolumny TTM)."""
    start = html.find("datekey:[")
    if start < 0:
        raise BladStockAnalysis("brak tablicy datekey; zmienił się układ strony")
    daty = _tablica(html, start - 1, "datekey")
    wynik = {}
    for klucz, (pozycja, znak) in MAPOWANIE.items():
        wartosci = _tablica(html, start, klucz)
        if not wartosci or len(wartosci) != len(daty):
            continue
        for d, v in zip(daty, wartosci):
            if d == "TTM" or v is None:
                continue
            typ = "dzien" if pozycja in POZYCJE_STANU else "FY"
            wynik[(pozycja, typ, date.fromisoformat(d))] = float(v) * znak
    return wynik


def parsuj_dokumenty(archiwum: Archiwum, dok_ids: list[str]) -> dict[tuple[str, str, date], tuple[float, str]]:
    """Łączy dane ze stron; wartość ma przy sobie id dokumentu źródłowego."""
    wynik = {}
    for dok_id in dok_ids:
        for klucz, v in parsuj(Path(archiwum.sciezka(dok_id)).read_text(encoding="utf-8")).items():
            wynik.setdefault(klucz, (v, dok_id))
    return wynik
