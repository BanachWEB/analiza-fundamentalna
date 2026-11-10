"""Krok danych dla spółki z USA: SEC → rejestr faktów → weryfikacja.

Uruchom: python -m silnik.usa MSFT [--data 2026-11-10]
Wynik: analizy/<TICKER>/<data>/dokumenty.json, fakty.json, weryfikacja.md
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from silnik import obliczenia
from silnik.fakty.rejestr import RejestrFaktow
from silnik.fakty.weryfikacja import Raport, drugie_zrodlo, podsumowanie_md, tozsamosci
from silnik.fakty.schemat import TypDokumentu
from silnik.pobieranie import rynek, sec, stockanalysis
from silnik.pobieranie.archiwum import Archiwum
from silnik.pobieranie.http import BladPobierania, pobierz

REPO = Path(__file__).resolve().parents[1]


def _strona(archiwum: Archiwum, url: str, zrodlo: str, opis: str):
    plik = pobierz(url, rozszerzenie=".html")
    try:
        return archiwum.dodaj_plik(plik, TypDokumentu.strona, zrodlo, adres=url, opis=opis)
    finally:
        plik.unlink(missing_ok=True)


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

    # dane rynkowe: kurs, momentum, obroty, S&P 500, rentowność obligacji, premia za ryzyko
    adres_sa = f"https://stockanalysis.com/stocks/{ticker.lower()}/history/"
    hist_sa = None
    try:
        hist_sa = archiwum.po_adresie(adres_sa) or _strona(archiwum, adres_sa, "Stock Analysis", "historia kursu")
        rejestr.znane_dokumenty(archiwum.ids())
    except BladPobierania as e:
        print(f"Stock Analysis (historia) niedostępny: {e}")
    zrodlo_kursu = "Yahoo"
    try:
        sesje, ids = rynek.historia(archiwum, "USA", ticker)
    except (BladPobierania, rynek.BladRynku) as e:
        print(f"Yahoo niedostępny ({e}); kurs z Stock Analysis, bez momentum")
        sesje, ids, zrodlo_kursu = (rynek.sesje_stockanalysis(archiwum.tekst(hist_sa.id)), [hist_sa.id], "SA") if hist_sa else ([], [], None)
    rejestr.znane_dokumenty(archiwum.ids())
    for f in rynek.fakty_z_historii(sesje, ids, "USD"):
        rejestr.dodaj(f, zastap=True)
    try:
        indeks, ids_i = rynek.historia(archiwum, "USA", "%5EGSPC")
        rejestr.znane_dokumenty(archiwum.ids())
        for f in rynek.fakty_z_historii(indeks, ids_i, "USD", "indeks_"):
            rejestr.dodaj(f, zastap=True)
    except (BladPobierania, rynek.BladRynku) as e:
        print(f"S&P 500 niedostępny: {e}")
    try:
        for f in rynek.fakty_stop(archiwum, "USA", dzien):
            rejestr.znane_dokumenty(archiwum.ids())
            rejestr.dodaj(f, zastap=True)
    except (BladPobierania, rynek.BladRynku) as e:
        print(f"Stopy i premie niedostępne: {e}")
    if hist_sa and zrodlo_kursu == "Yahoo":
        sa = rynek.sesje_stockanalysis(archiwum.tekst(hist_sa.id))[-10:]  # porównanie kursu z tego samego dnia
        drugie_zrodlo(rejestr, {("kurs", "dzien", x.dzien): (x.zamkniecie, hist_sa.id) for x in sa}, raport)

    rejestr.do_pliku(katalog / "fakty.json")
    (katalog / "weryfikacja.md").write_text(podsumowanie_md(rejestr, raport), encoding="utf-8")
    obliczenia.uruchom_w_katalogu(katalog, "USA")
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
