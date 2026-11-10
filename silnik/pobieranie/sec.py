"""Dane z SEC (XBRL companyfacts) prosto do rejestru faktów, bez udziału modelu.

Zasady wyboru wartości:
- okres roczny: 350–380 dni, z raportu 10-K (albo 10-K/A);
- kwartał: 80–100 dni, z raportu 10-Q, 10-K albo poprawek;
- stan na dzień: wartość z dniem końca okresu;
- ta sama wartość pojawia się w kilku raportach (dane porównawcze); bierzemy
  wersję z najpóźniej złożonego raportu, a różnice między wersjami zapisujemy
  w kontrolach faktu jako „zmiana_wersji”.
Rok obrotowy (FY) i kwartał liczymy z daty końca okresu i kalendarza spółki
(KalendarzFiskalny), a numer roku bierzemy z ostatniego raportu 10-K.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

import yaml

from silnik.fakty.schemat import Fakt, Jednostka, Metoda, Okres, Rodzaj, Skala, Status, TypDokumentu
from silnik.pobieranie.archiwum import Archiwum
from silnik.pobieranie.http import pobierz

KONFIGURACJA = Path(__file__).resolve().parents[2] / "konfiguracja"
FORMY_ROCZNE = {"10-K", "10-K/A", "10-KT"}
FORMY_KWARTALNE = {"10-Q", "10-Q/A", "10-K", "10-K/A"}


class BladSEC(Exception):
    pass


def cik_dla(ticker: str) -> int:
    """CIK z konfiguracja/sec-cik.yaml.

    Plik company_tickers.json z www.sec.gov odrzuca zapytania bez adresu
    kontaktowego w User-Agent, dlatego mapowanie trzymamy w konfiguracji.
    """
    mapa = yaml.safe_load((KONFIGURACJA / "sec-cik.yaml").read_text(encoding="utf-8")) or {}
    cik = mapa.get(ticker.upper())
    if cik is None:
        raise BladSEC(
            f"brak CIK dla {ticker} w konfiguracja/sec-cik.yaml; znajdź go w EDGAR (pole CIK) i dopisz"
        )
    return int(cik)


def url_companyfacts(cik: int) -> str:
    return f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"


def url_submissions(cik: int) -> str:
    return f"https://data.sec.gov/submissions/CIK{cik:010d}.json"


def pobierz_do_archiwum(cik: int, archiwum: Archiwum):
    """Pobiera companyfacts i submissions; zwraca (dok_facts, dok_submissions)."""
    wyniki = []
    for url, opis in ((url_companyfacts(cik), "XBRL companyfacts"), (url_submissions(cik), "lista raportów")):
        plik = pobierz(url)
        try:
            wyniki.append(archiwum.dodaj_plik(plik, TypDokumentu.sec_api, "SEC", adres=url, opis=opis))
        finally:
            plik.unlink(missing_ok=True)
    return tuple(wyniki)


# --- wybór wartości ---------------------------------------------------------


@dataclass
class _Wpis:
    znacznik: str
    start: Optional[date]
    koniec: date
    wartosc: float
    accn: str
    forma: str
    zlozono: date
    fy: Optional[int]
    fp: Optional[str]


def _wpisy(facts: dict, znacznik: str, jednostka_xbrl: str) -> list[_Wpis]:
    ns, _, nazwa = znacznik.rpartition(":")
    ns = ns or "us-gaap"
    try:
        surowe = facts["facts"][ns][nazwa]["units"][jednostka_xbrl]
    except KeyError:
        return []
    out = []
    for x in surowe:
        out.append(
            _Wpis(
                znacznik=f"{ns}:{nazwa}",
                start=date.fromisoformat(x["start"]) if x.get("start") else None,
                koniec=date.fromisoformat(x["end"]),
                wartosc=float(x["val"]),
                accn=x["accn"],
                forma=x.get("form", ""),
                zlozono=date.fromisoformat(x["filed"]),
                fy=x.get("fy"),
                fp=x.get("fp"),
            )
        )
    return out


@dataclass
class KalendarzFiskalny:
    """Nazwy lat i kwartałów obrotowych liczone z daty końca okresu.

    miesiac_konca: miesiąc końca roku obrotowego (np. 6 dla Microsoftu).
    przesuniecie: różnica między numerem roku, który podaje spółka, a rokiem
    kalendarzowym końca roku obrotowego (np. -1 dla sieci handlowych, które
    rok zakończony 31.01.2026 nazywają FY2025).
    Daty końca przesuwamy o 10 dni wstecz, żeby lata 52/53-tygodniowe
    (koniec np. 1 października) trafiały do właściwego miesiąca.
    """

    miesiac_konca: int
    przesuniecie: int = 0

    @staticmethod
    def _miesiac(koniec: date) -> date:
        return koniec - timedelta(days=10)

    def rok(self, koniec: date) -> int:
        d = self._miesiac(koniec)
        rok_konca = d.year if d.month <= self.miesiac_konca else d.year + 1
        return rok_konca + self.przesuniecie

    def kwartal(self, koniec: date) -> str:
        d = self._miesiac(koniec)
        return f"Q{((d.month - self.miesiac_konca - 1) % 12) // 3 + 1}"


def kalendarz(facts: dict) -> KalendarzFiskalny:
    """Kalendarz z najnowszego okresu rocznego z raportu 10-K, w którym był okresem bieżącym."""
    najlepszy = None
    for ns in facts.get("facts", {}).values():
        for tag in ns.values():
            for wartosci in tag.get("units", {}).values():
                for x in wartosci:
                    if x.get("form") not in FORMY_ROCZNE or x.get("fp") != "FY" or not x.get("start") or not x.get("fy"):
                        continue
                    k, s_ = date.fromisoformat(x["end"]), date.fromisoformat(x["start"])
                    if not 350 <= (k - s_).days <= 380:
                        continue
                    # okres bieżący: rok z pola fy pasuje do roku końca (z dokładnością do przesunięcia o 1)
                    if najlepszy is None or k > najlepszy[0]:
                        najlepszy = (k, int(x["fy"]))
    if najlepszy is None:
        raise BladSEC("brak okresów rocznych z raportów 10-K; nie da się ustalić roku obrotowego")
    koniec, fy = najlepszy
    miesiac = KalendarzFiskalny._miesiac(koniec).month
    return KalendarzFiskalny(miesiac, fy - KalendarzFiskalny._miesiac(koniec).year)


def _dni(w: _Wpis) -> int:
    return (w.koniec - w.start).days if w.start else 0


def wyciagnij_fakty(
    facts: dict,
    dok_id: str,
    mapowanie: Optional[dict] = None,
    lat: int = 10,
    kwartalow: int = 12,
) -> list[Fakt]:
    if mapowanie is None:
        mapowanie = yaml.safe_load((KONFIGURACJA / "mapowanie-us-gaap.yaml").read_text(encoding="utf-8"))
    kal = kalendarz(facts)
    wyniki: list[Fakt] = []

    for pozycja, cfg in mapowanie.items():
        jednostka = Jednostka(cfg["jednostka"])
        jedn_xbrl = cfg.get("jednostka_xbrl", "USD")
        waluta = jedn_xbrl.split("/")[0] if jednostka in (Jednostka.pieniadz, Jednostka.pieniadz_na_akcje) else None

        # klucz okresu → wpisy w kolejności priorytetu znaczników
        okresy: dict[tuple, list[_Wpis]] = {}
        for priorytet, znacznik in enumerate(cfg["znaczniki"]):
            grupy = defaultdict(list)
            for w in _wpisy(facts, znacznik, jedn_xbrl):
                if cfg["rodzaj"] == "stan":
                    if w.start is not None:
                        continue
                    klucz = ("dzien", None, w.koniec)
                else:
                    d = _dni(w)
                    if 350 <= d <= 380 and w.forma in FORMY_ROCZNE:
                        klucz = ("FY", w.start, w.koniec)
                    elif 80 <= d <= 100 and w.forma in FORMY_KWARTALNE:
                        klucz = ("Q", w.start, w.koniec)
                    else:
                        continue
                grupy[klucz].append(w)
            for klucz, wpisy in grupy.items():
                okresy.setdefault(klucz, wpisy)  # pierwszy znacznik z wartością wygrywa

        roczne = sorted([k for k in okresy if k[0] == "FY"], key=lambda k: k[2])[-lat:]
        kwartalne = sorted([k for k in okresy if k[0] == "Q"], key=lambda k: k[2])[-kwartalow:]
        stany = sorted([k for k in okresy if k[0] == "dzien"], key=lambda k: k[2])[-(lat + kwartalow):]

        for klucz in roczne + kwartalne + stany:
            wpisy = sorted(okresy[klucz], key=lambda w: (w.zlozono, w.accn))
            ostatni = wpisy[-1]
            kontrole = []
            rozne = sorted({w.wartosc for w in wpisy})
            if len(rozne) > 1:
                kontrole.append(f"zmiana_wersji:{len(rozne)}_wartosci:wybrano_najnowsza")
            typ, start, koniec = klucz
            if typ == "dzien":
                okres = Okres(typ="dzien", koniec=koniec)
                fid = f"{pozycja}.{koniec.isoformat()}"
            else:
                fy = kal.rok(koniec)
                if typ == "FY":
                    okres = Okres(typ="FY", poczatek=start, koniec=koniec)
                    fid = f"{pozycja}.FY{fy}"
                else:
                    fp = kal.kwartal(koniec)
                    okres = Okres(typ=fp, poczatek=start, koniec=koniec)
                    fid = f"{pozycja}.FY{fy}{fp}"
            wyniki.append(
                Fakt(
                    id=fid,
                    rodzaj=Rodzaj.raportowany,
                    pozycja=pozycja,
                    okres=okres,
                    wartosc=ostatni.wartosc,
                    skala=Skala.jedn,
                    jednostka=jednostka,
                    waluta=waluta,
                    metoda=Metoda.xbrl,
                    status=Status.jedno_zrodlo,
                    dokument=dok_id,
                    miejsce={
                        "xbrl": ostatni.znacznik,
                        "accn": ostatni.accn,
                        "forma": ostatni.forma,
                        "zlozono": ostatni.zlozono.isoformat(),
                    },
                    kontrole=kontrole,
                )
            )
    # Dwa różne okresy z tym samym identyfikatorem to błąd danych albo kalendarza:
    # zostawiamy późniejszy okres i oznaczamy fakt jako konflikt, zamiast cicho łączyć.
    widziane: dict[str, Fakt] = {}
    for f in wyniki:
        stary = widziane.get(f.id)
        if stary is None:
            widziane[f.id] = f
            continue
        nowszy, starszy = (f, stary) if f.okres.koniec > stary.okres.koniec else (stary, f)
        widziane[f.id] = nowszy.model_copy(update={
            "status": Status.konflikt,
            "kontrole": list(nowszy.kontrole) + [f"kolizja_okresow:{starszy.okres.koniec.isoformat()}"],
        })
    return list(widziane.values())


def wczytaj(archiwum: Archiwum, dok_id: str) -> dict:
    return json.loads(archiwum.sciezka(dok_id).read_text(encoding="utf-8"))
