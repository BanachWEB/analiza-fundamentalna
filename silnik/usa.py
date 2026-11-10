"""Krok danych dla spółki z USA: SEC → rejestr faktów → weryfikacja.

Uruchom: python -m silnik.usa MSFT [--data 2026-11-10]
Wynik: analizy/<TICKER>/<data>/dokumenty.json, fakty.json, weryfikacja.md
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from silnik.fakty.rejestr import RejestrFaktow
from silnik.fakty.weryfikacja import Raport, drugie_zrodlo, podsumowanie_md, tozsamosci
from silnik.pobieranie import sec, stockanalysis
from silnik.pobieranie.archiwum import Archiwum
from silnik.pobieranie.http import BladPobierania

REPO = Path(__file__).resolve().parents[1]


def uruchom(ticker: str, dzien: date, katalog_plikow: Path | None = None) -> Path:
    ticker = ticker.upper()
    katalog = REPO / "analizy" / ticker / dzien.isoformat()
    archiwum = Archiwum(ticker, katalog, katalog_plikow)

    cik = sec.cik_dla(ticker)
    dok_facts, _ = sec.pobierz_do_archiwum(cik, archiwum)
    rejestr = RejestrFaktow(ticker, dzien, dokumenty=archiwum.ids())
    for f in sec.wyciagnij_fakty(sec.wczytaj(archiwum, dok_facts.id), dok_facts.id):
        rejestr.dodaj(f)

    raport = Raport()
    tozsamosci(rejestr, raport)
    try:
        dok_sa = stockanalysis.pobierz_do_archiwum(ticker, archiwum)
        rejestr.znane_dokumenty(archiwum.ids())
        drugie_zrodlo(rejestr, stockanalysis.parsuj_dokumenty(archiwum, [d.id for d in dok_sa]), raport)
    except (BladPobierania, stockanalysis.BladStockAnalysis) as e:
        print(f"Drugie źródło niedostępne: {e}")

    rejestr.do_pliku(katalog / "fakty.json")
    (katalog / "weryfikacja.md").write_text(podsumowanie_md(rejestr, raport), encoding="utf-8")
    return katalog


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("ticker")
    p.add_argument("--data", type=date.fromisoformat, default=date.today())
    a = p.parse_args()
    katalog = uruchom(a.ticker, a.data)
    print((katalog / "weryfikacja.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
