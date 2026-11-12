"""Tabela konkurentów (specyfikacja 1.1, punkt 8; decyzja właściciela z 12.11.2026).

Badacz biznesu zapisuje `D/konkurenci.json` (4–6 spółek z USA albo z GPW, z uzasadnieniem z dokumentów).
Polecenie `python -m silnik.konkurenci D` buduje dla każdego konkurenta osobny rejestr faktów
w `D/konkurenci/<TICKER>/` (dokumenty.json i fakty.json), tą samą ścieżką co dla badanej spółki:
- USA: dane XBRL z SEC i notowania z Yahoo;
- GPW: dane z Biznesradaru i notowania z Biznesradaru.
Konkurent z innej giełdy dostaje „brak danych”. Rejestry konkurentów nie mieszają się z rejestrem spółki.

Pobieranie sprawdzi pierwszy przebieg z dostępem do sieci; testy obejmują budowę tabeli z zapisanych rejestrów.
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from statistics import median
from typing import Optional

from silnik.fakty.rejestr import RejestrFaktow
from silnik.fakty.schemat import Fakt, Status, TypDokumentu

RYNKI = ("USA", "GPW")
METRYKI = [
    ("marza_brutto", "Marża brutto"),
    ("marza_operacyjna", "Marża operacyjna"),
    ("wzrost_przychody", "Wzrost przychodów r/r"),
    ("roic", "ROIC"),
    ("c_z", "C/Z"),
    ("ev_ebit", "EV/EBIT"),
]
DZIENNE = {"c_z", "ev_ebit"}


class BladKonkurentow(Exception):
    pass


def wczytaj(katalog: Path) -> list[dict]:
    plik = Path(katalog) / "konkurenci.json"
    if not plik.exists():
        return []
    dane = json.loads(plik.read_text(encoding="utf-8")).get("konkurenci", [])
    for d in dane:
        if not d.get("ticker") or d.get("rynek") not in RYNKI + ("inny",):
            raise BladKonkurentow(f"konkurenci.json: każdy wpis potrzebuje „ticker” i „rynek” (USA, GPW albo inny): {d}")
        if not d.get("uzasadnienie"):
            raise BladKonkurentow(f"konkurenci.json: {d['ticker']} bez uzasadnienia")
    return dane


# --- pobieranie (sieć) -----------------------------------------------------------------------


def _usa(ticker: str, katalog_k: Path, dzien: date, katalog_plikow: Optional[Path]) -> RejestrFaktow:
    from silnik.pobieranie import rynek, sec
    from silnik.pobieranie.archiwum import Archiwum

    archiwum = Archiwum(ticker, katalog_k, katalog_plikow)
    cik = sec.cik_dla(ticker)
    dok, _ = sec.pobierz_do_archiwum(cik, archiwum)
    rejestr = RejestrFaktow(ticker, dzien, dokumenty=archiwum.ids())
    for f in sec.wyciagnij_fakty(sec.wczytaj(archiwum, dok.id), dok.id):
        rejestr.dodaj(f)
    sesje, ids = rynek.historia(archiwum, "USA", ticker)
    rejestr.znane_dokumenty(archiwum.ids())
    for f in rynek.fakty_z_historii(sesje, ids, "USD"):
        rejestr.dodaj(f, zastap=True)
    return rejestr


def _gpw(ticker: str, katalog_k: Path, dzien: date, katalog_plikow: Optional[Path]) -> RejestrFaktow:
    from silnik.pobieranie import biznesradar, rynek
    from silnik.pobieranie.archiwum import Archiwum
    from silnik.pobieranie.http import pobierz

    archiwum = Archiwum(ticker, katalog_k, katalog_plikow)
    dok_br = biznesradar.pobierz_do_archiwum(ticker, archiwum)
    rejestr = RejestrFaktow(ticker, dzien, dokumenty=archiwum.ids())
    for f in biznesradar.fakty_uzupelniajace(biznesradar.parsuj_dokumenty(archiwum, [d.id for d in dok_br]), set()):
        rejestr.dodaj(f)
    sesje, ids = rynek.historia(archiwum, "GPW", ticker)
    adres = f"https://www.biznesradar.pl/notowania/{ticker}"
    dok_n = archiwum.po_adresie(adres)
    if dok_n is None:
        plik = pobierz(adres, rozszerzenie=".html")
        try:
            dok_n = archiwum.dodaj_plik(plik, TypDokumentu.strona, "Biznesradar", adres=adres, opis="notowania (liczba akcji)")
        finally:
            plik.unlink(missing_ok=True)
    rejestr.znane_dokumenty(archiwum.ids())
    for f in rynek.fakty_z_historii(sesje, ids, "PLN"):
        rejestr.dodaj(f, zastap=True)
    n = rynek.notowania_biznesradar(archiwum.tekst(dok_n.id))
    if "liczba_akcji" in n:
        dz = n.get("dzien", dzien)
        rejestr.dodaj(Fakt(id=f"akcje_w_obrocie.{dz.isoformat()}", rodzaj="raportowany", pozycja="akcje_w_obrocie",
                           okres={"typ": "dzien", "koniec": dz}, wartosc=n["liczba_akcji"], jednostka="akcje",
                           metoda="parser_strony", status="jedno_zrodlo", dokument=dok_n.id,
                           miejsce={"pole": "Liczba akcji"}), zastap=True)
    return rejestr


def uruchom(katalog: Path, katalog_plikow: Optional[Path] = None) -> list[str]:
    """Buduje rejestry konkurentów; zwraca listę komunikatów (co się udało, czego brak)."""
    from silnik import obliczenia

    katalog = Path(katalog)
    glowny = json.loads((katalog / "dokumenty.json").read_text(encoding="utf-8"))["ticker"]
    dzien = date.fromisoformat(katalog.name)
    komunikaty = []
    for d in wczytaj(katalog):
        t = d["ticker"].upper().replace(".US", "").replace(".PL", "").replace(".WA", "")
        if t == glowny:
            continue
        if d["rynek"] not in RYNKI:
            komunikaty.append(f"{t}: rynek spoza USA i GPW — brak danych")
            continue
        katalog_k = katalog / "konkurenci" / t
        try:
            rejestr = (_usa if d["rynek"] == "USA" else _gpw)(t, katalog_k, dzien, katalog_plikow)
            obliczenia.uruchom(rejestr, katalog_k, d["rynek"])
            rejestr.do_pliku(katalog_k / "fakty.json")
            komunikaty.append(f"{t}: rejestr zapisany ({sum(1 for _ in rejestr.fakty())} faktów)")
        except Exception as e:  # jeden konkurent nie zatrzymuje pozostałych (sieć, brak CIK, format strony)
            komunikaty.append(f"{t}: brak danych ({type(e).__name__}: {e})")
    return komunikaty


# --- tabela (bez sieci) ----------------------------------------------------------------------


def _ostatni(r: RejestrFaktow, pozycja: str) -> Optional[Fakt]:
    fs = [f for f in r.fakty() if f.pozycja == pozycja and f.status != Status.odrzucony]
    if not fs:
        return None
    if pozycja in DZIENNE:
        return max(fs, key=lambda f: f.okres.koniec)
    ttm = [f for f in fs if f.okres.typ.value == "TTM"]
    fy = [f for f in fs if f.okres.typ.value == "FY"]
    return max(ttm or fy or fs, key=lambda f: f.okres.koniec)


def _wiersz(r: RejestrFaktow, nazwa: str, rynek: str) -> dict:
    return {"ticker": r.ticker, "nazwa": nazwa, "rynek": rynek, "fakty": {m: _ostatni(r, m) for m, _ in METRYKI}}


def wiersze(katalog: Optional[Path]) -> list[dict]:
    """Wiersze konkurentów z zapisanych rejestrów (bez sieci)."""
    if not katalog:
        return []
    try:
        lista = wczytaj(Path(katalog))
    except BladKonkurentow:
        return []
    wynik = []
    for d in lista:
        t = d["ticker"].upper().replace(".US", "").replace(".PL", "").replace(".WA", "")
        kat = Path(katalog) / "konkurenci" / t
        if not (kat / "fakty.json").exists():
            wynik.append({"ticker": t, "nazwa": d.get("nazwa", t), "rynek": d["rynek"], "fakty": {}})
            continue
        ids = [x["id"] for x in json.loads((kat / "dokumenty.json").read_text(encoding="utf-8"))["dokumenty"]] \
            if (kat / "dokumenty.json").exists() else None
        wynik.append(_wiersz(RejestrFaktow.z_pliku(kat / "fakty.json", ids), d.get("nazwa", t), d["rynek"]))
    return wynik


def tabela(k, wynik: dict) -> list[str]:
    """Tabela do raportu: spółka, konkurenci i mediana konkurentów (liczona z wierszy tabeli)."""
    from silnik.obliczenia.raport import format_

    lista = wynik.get("konkurenci") or []
    if not lista:
        return ["Brak tabeli konkurentów (brak pliku konkurenci.json albo rejestrów konkurentów)."]
    rynek = wynik.get("rynek")
    glowny = _wiersz(k.r, "badana spółka", rynek or "")
    linie = ["| Spółka | Rynek | " + " | ".join(n for _, n in METRYKI) + " |", "|---|---|" + "---:|" * len(METRYKI)]

    def komorka(f):
        return format_(f) if f else "—"
    linie.append(f"| **{glowny['ticker']}** | {glowny['rynek']} | " + " | ".join(komorka(glowny["fakty"].get(m)) for m, _ in METRYKI) + " |")
    for w in lista:
        linie.append(f"| {w['ticker']} ({w['nazwa']}) | {w['rynek']} | "
                     + " | ".join(komorka(w["fakty"].get(m)) for m, _ in METRYKI) + " |")
    med = []
    for m, _ in METRYKI:
        v = [w["fakty"][m].wartosc_bazowa() for w in lista if w["fakty"].get(m)]
        if not v:
            med.append("—")
            continue
        x = median(v)
        med.append(f"{x * 100:,.1f}%".replace(",", " ").replace(".", ",") if m not in DZIENNE
                   else f"{x:,.2f}".replace(",", " ").replace(".", ","))
    linie.append("| Mediana konkurentów | | " + " | ".join(med) + " |")
    okresy = sorted({f.id.split(".", 1)[1] for w in [glowny] + lista for m, f in w["fakty"].items() if f and m not in DZIENNE})
    linie += ["", f"Marże, wzrost i ROIC z ostatniego okresu TTM albo roku obrotowego każdej spółki ({', '.join(okresy)}); "
              "mnożniki z ostatniego kursu. Mediana liczona przez silnik z wierszy konkurentów. "
              "Dane konkurentów: osobne rejestry w katalogu konkurenci/, z jednego źródła na spółkę."]
    if any(w["rynek"] != rynek for w in lista):
        linie.append("Konkurenci z innego rynku: mnożniki z USA i z GPW nie są wprost porównywalne, bo koszt kapitału "
                     "w Polsce jest wyższy niż w USA.")
    return linie


def main() -> None:
    p = argparse.ArgumentParser(description="Rejestry konkurentów z D/konkurenci.json")
    p.add_argument("katalog", type=Path)
    a = p.parse_args()
    for linia in uruchom(a.katalog):
        print(linia)


if __name__ == "__main__":
    main()
