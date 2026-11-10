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
from silnik import obliczenia
from silnik.fakty.rejestr import RejestrFaktow
from silnik.fakty.schemat import Status, TypDokumentu
from silnik.fakty.weryfikacja import Raport, drugie_zrodlo, grupa_okresu, podsumowanie_md, tozsamosci
from silnik.fakty.schemat import Fakt
from silnik.pobieranie import biznesradar, esef, rynek
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


def _do_archiwum_strona(archiwum: Archiwum, url: str, zrodlo: str, opis: str, rozszerzenie: str = ".html"):
    plik = pobierz(url, rozszerzenie=rozszerzenie)
    try:
        return archiwum.dodaj_plik(plik, TypDokumentu.strona, zrodlo, adres=url, opis=opis)
    finally:
        plik.unlink(missing_ok=True)


def uruchom(ticker: str, dzien: date, esef_urls: list[str], pdf_urls: list[str],
            katalog_plikow: Path | None = None, rf: float | None = None, rf_zrodlo: str | None = None) -> Path:
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

    # dane rynkowe: kurs i WIG z Biznesradaru, kontrola kursu z Yahoo, liczba akcji, premia za ryzyko
    try:
        sesje, ids = rynek.historia(archiwum, "GPW", ticker)
        indeks, ids_i = rynek.historia(archiwum, "GPW", "WIG")
        rejestr.znane_dokumenty(archiwum.ids())
        for f in rynek.fakty_z_historii(sesje, ids, "PLN") + rynek.fakty_z_historii(indeks, ids_i, "PLN", "indeks_"):
            rejestr.dodaj(f, zastap=True)
        adres = f"https://www.biznesradar.pl/notowania/{ticker}"
        dok_n = archiwum.po_adresie(adres) or _do_archiwum_strona(archiwum, adres, "Biznesradar", "notowania (liczba akcji)")
        rejestr.znane_dokumenty(archiwum.ids())
        n = rynek.notowania_biznesradar(archiwum.tekst(dok_n.id))
        if "liczba_akcji" in n:
            dz = n.get("dzien", dzien)
            rejestr.dodaj(Fakt(id=f"akcje_w_obrocie.{dz.isoformat()}", rodzaj="raportowany", pozycja="akcje_w_obrocie",
                               okres={"typ": "dzien", "koniec": dz}, wartosc=n["liczba_akcji"], jednostka="akcje",
                               metoda="parser_strony", status="jedno_zrodlo", dokument=dok_n.id,
                               miejsce={"pole": "Liczba akcji"}), zastap=True)
        for f in rynek.fakty_stop(archiwum, "GPW", dzien):
            rejestr.znane_dokumenty(archiwum.ids())
            rejestr.dodaj(f, zastap=True)
        try:
            dok_y = _do_archiwum_strona(archiwum, rynek.url_yahoo(f"{ticker}.WA"), "Yahoo Finance", "kurs (kontrola)", ".json")
            rejestr.znane_dokumenty(archiwum.ids())
            sy = rynek.sesje_yahoo(archiwum.tekst(dok_y.id))
            if sy:  # porównanie kursu z tego samego dnia
                drugie_zrodlo(rejestr, {("kurs", "dzien", x.dzien): (x.zamkniecie, dok_y.id) for x in sy[-10:]}, raport)
        except (BladPobierania, rynek.BladRynku) as e:
            print(f"Kontrola kursu niedostępna: {e}")
    except (BladPobierania, rynek.BladRynku) as e:
        print(f"Dane rynkowe niepełne: {e}")
    if rf is not None:
        rejestr.dodaj(Fakt(id="rentownosc_10l.zalozenie", rodzaj="zalozenie", pozycja="rentownosc_10l",
                           okres={"typ": "brak"}, wartosc=rf, jednostka="ulamek", metoda="model", status="jedno_zrodlo",
                           uzasadnienie=f"Rentowność polskich obligacji 10-letnich: {rf_zrodlo or 'źródło nie podane'}"),
                      zastap=True)

    rejestr.do_pliku(katalog / "fakty.json")
    (katalog / "weryfikacja.md").write_text(podsumowanie_md(rejestr, raport), encoding="utf-8")
    obliczenia.uruchom_w_katalogu(katalog, "GPW")
    return katalog


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("ticker")
    p.add_argument("--esef", action="append", default=[], help="URL pakietu ESEF (ZIP); można podać kilka")
    p.add_argument("--pdf", action="append", default=[], help="URL raportu okresowego PDF; można podać kilka")
    p.add_argument("--data", type=date.fromisoformat, default=date.today())
    p.add_argument("--rf", type=float, help="rentowność polskich obligacji 10-letnich, np. 0.055")
    p.add_argument("--rf-zrodlo", help="źródło i data rentowności (trafia do uzasadnienia założenia)")
    a = p.parse_args()
    katalog = uruchom(a.ticker, a.data, a.esef, a.pdf, rf=a.rf, rf_zrodlo=a.rf_zrodlo)
    print((katalog / "weryfikacja.md").read_text(encoding="utf-8"))
    odrzucone = RejestrFaktow.z_pliku(katalog / "fakty.json").ze_statusem(Status.odrzucony)
    if odrzucone:
        print("Propozycje odrzucone przez test cytatu:")
        for f in odrzucone:
            print(f"  {f.id}: {f.kontrole[-1]}")


if __name__ == "__main__":
    main()
