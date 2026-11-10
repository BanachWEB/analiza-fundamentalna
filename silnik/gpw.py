"""Krok danych dla spółki z GPW: ESEF + raporty PDF → rejestr faktów → weryfikacja.

Uruchom:
  python -m silnik.gpw DNP --esef URL_ZIP [--esef ...] [--pdf URL_PDF ...] [--data 2026-11-10]
Potem model przygotowuje propozycje faktów z PDF (plik propozycje.json w katalogu
analizy) i uruchamia to samo polecenie jeszcze raz; silnik dołącza propozycje
po teście cytatu.

Wynik: analizy/<TICKER>/<data>/dokumenty.json, fakty.json, weryfikacja.md
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from silnik.fakty.cytat import dodaj_propozycje, wczytaj_propozycje
from silnik.fakty.rejestr import RejestrFaktow
from silnik.fakty.schemat import Status, TypDokumentu
from silnik.fakty.weryfikacja import Raport, drugie_zrodlo, grupa_okresu, podsumowanie_md, tozsamosci
from silnik.pobieranie import biznesradar, esef
from silnik.pobieranie.archiwum import Archiwum
from silnik.pobieranie.http import BladPobierania, pobierz

REPO = Path(__file__).resolve().parents[1]


def _do_archiwum(archiwum: Archiwum, url: str, typ: TypDokumentu, opis: str):
    istniejacy = archiwum.po_adresie(url)
    if istniejacy:
        return istniejacy
    plik = pobierz(url, limit_s=180)
    try:
        return archiwum.dodaj_plik(plik, typ, "spółka", adres=url, opis=opis)
    finally:
        plik.unlink(missing_ok=True)


def uruchom(ticker: str, dzien: date, esef_urls: list[str], pdf_urls: list[str],
            katalog_plikow: Path | None = None) -> Path:
    ticker = ticker.upper()
    katalog = REPO / "analizy" / ticker / dzien.isoformat()
    archiwum = Archiwum(ticker, katalog, katalog_plikow)

    dok_esef = [_do_archiwum(archiwum, u, TypDokumentu.esef, "raport roczny ESEF") for u in esef_urls]
    for u in pdf_urls:
        _do_archiwum(archiwum, u, TypDokumentu.raport_pdf, "raport okresowy PDF")

    rejestr = RejestrFaktow(ticker, dzien, dokumenty=archiwum.ids())
    # Starsze raporty najpierw; nowszy raport nadpisuje dane porównawcze i zostawia ślad zmiany.
    paczki = []
    for d in dok_esef:
        xhtml = esef.xhtml_z_pakietu(archiwum.sciezka(d.id).read_bytes())
        fakty = esef.wyciagnij_fakty(xhtml, d.id)
        paczki.append((max(f.okres.koniec for f in fakty), fakty))
    for _, fakty in sorted(paczki, key=lambda x: x[0]):
        for f in fakty:
            if f.id in rejestr:
                stary = rejestr[f.id]
                if abs(stary.wartosc_bazowa() - f.wartosc_bazowa()) > 0.5:
                    f = f.model_copy(update={"kontrole": list(f.kontrole) + [
                        f"zmiana_wersji:{stary.dokument}:{stary.wartosc_bazowa():g}"]})
                rejestr.dodaj(f, zastap=True)
            else:
                rejestr.dodaj(f)

    plik_propozycji = katalog / "propozycje.json"
    if plik_propozycji.exists():
        dodaj_propozycje(rejestr, archiwum.sciezka, wczytaj_propozycje(plik_propozycji))

    raport = Raport()
    try:
        dok_br = biznesradar.pobierz_do_archiwum(ticker, archiwum)
        rejestr.znane_dokumenty(archiwum.ids())
        dane_br = biznesradar.parsuj_dokumenty(archiwum, [d.id for d in dok_br])
        istniejace = {(f.pozycja, grupa_okresu(f), f.okres.koniec) for f in rejestr.fakty() if f.status != Status.odrzucony}
        for f in biznesradar.fakty_uzupelniajace(dane_br, istniejace):
            rejestr.dodaj(f)
    except (BladPobierania, biznesradar.BladBiznesradar) as e:
        dane_br = None
        print(f"Biznesradar niedostępny: {e}")
    tozsamosci(rejestr, raport)
    if dane_br:
        drugie_zrodlo(rejestr, dane_br, raport)

    rejestr.do_pliku(katalog / "fakty.json")
    (katalog / "weryfikacja.md").write_text(podsumowanie_md(rejestr, raport), encoding="utf-8")
    return katalog


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("ticker")
    p.add_argument("--esef", action="append", default=[], help="URL pakietu ESEF (ZIP); można podać kilka")
    p.add_argument("--pdf", action="append", default=[], help="URL raportu okresowego PDF; można podać kilka")
    p.add_argument("--data", type=date.fromisoformat, default=date.today())
    a = p.parse_args()
    katalog = uruchom(a.ticker, a.data, a.esef, a.pdf)
    print((katalog / "weryfikacja.md").read_text(encoding="utf-8"))
    odrzucone = RejestrFaktow.z_pliku(katalog / "fakty.json").ze_statusem(Status.odrzucony)
    if odrzucone:
        print("Propozycje odrzucone przez test cytatu:")
        for f in odrzucone:
            print(f"  {f.id}: {f.kontrole[-1]}")


if __name__ == "__main__":
    main()
