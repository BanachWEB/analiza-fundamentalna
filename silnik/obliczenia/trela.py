"""Cena docelowa wg Tomasza Treli: mnożnik z historii × prognoza na akcję (specyfikacja.md, punkt 7.1).

Dane wejściowe podaje właściciel w pliku `D/scrab.yaml` (odczyt z Scrab → MasterChart):

    data_odczytu: 2026-11-11
    waluta: USD
    kurs: 168.89                       # opcjonalnie; tylko kontrola, silnik liczy potencjał od własnego kursu
    rok_obrotowy_prognozy: FY2028      # opcjonalnie; którego roku obrotowego dotyczy prognoza
    eps_prognoza: 15.81                # EPS Estimates for Next Fiscal Year
    sprzedaz_na_akcje_prognoza: 28.57  # Revenue Per Share Estimates for Next Fiscal Year
    pe_forward:                        # PE Ratio (1-Year Forward)
      mediana_5l: 28.92                # linia „(5Y Median)”
      biezacy: 10.68                   # opcjonalnie; kontrola
      seria_csv: pe-forward.csv        # albo „seria: [..]”; potrzebna do percentyla (wariant optymistyczny)
    ps_forward:                        # PS Ratio (1-Year Forward)
      mediana_5l: 14.86
      biezacy: 5.91
      seria_csv: ps-forward.csv

Silnik zapisuje plik (i pliki CSV z seriami) w archiwum jako `wklejka` ze źródłem „Scrab”. Każda liczba
z pliku trafia do rejestru jako fakt z dokumentem, kluczem i dosłownym wierszem pliku (cytat), ze statusem
`jedno_zrodlo` (specyfikacja.md, punkt 3.3, „Materiały od właściciela”). Mediana i percentyl serii to
deterministyczny odczyt dokumentu przez kod; `miejsce` faktu opisuje statystykę, okno i liczbę punktów.

Wyniki (fakty wyliczone):
- cena_docelowa_trela_{pe,ps}_{kons,optym}: mnożnik × prognoza na akcję;
- cena_docelowa_trela_{kons,optym}: średnia z metody P/E i P/S (przy EPS ≤ 0 tylko P/S, jak u Treli);
- potencjal_trela_{kons,optym}: cena docelowa ÷ kurs − 1 (kurs pobrany przez silnik).
Potencjał konserwatywny to miara filaru „wycena” w karcie Treli (konfiguracja/karta-treli.yaml).
"""

from __future__ import annotations

import csv
import io
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from statistics import median
from typing import Optional

import yaml

from silnik.fakty.schemat import Fakt, Jednostka, Metoda, Okres, Rodzaj, Status, TypDokumentu

from .kalkulator import BrakSensu, Kalkulator

KONFIGURACJA = Path(__file__).resolve().parents[2] / "konfiguracja" / "cena-docelowa-trela.yaml"
PLIK = "scrab.yaml"
ZRODLO = "Scrab"
X, U, PA = Jednostka.mnoznik, Jednostka.ulamek, Jednostka.pieniadz_na_akcje
MNOZNIKI = {"pe": ("pe_forward", "P/E 1-Year Forward"), "ps": ("ps_forward", "P/S 1-Year Forward")}


class BladScrab(ValueError):
    pass


def parametry() -> dict:
    return yaml.safe_load(KONFIGURACJA.read_text(encoding="utf-8"))


# --- matematyka ------------------------------------------------------------------------


def percentyl(wartosci: list[float], p: float) -> float:
    """Percentyl z interpolacją liniową między punktami (ta sama metoda co PERCENTILE.INC w Excelu)."""
    if not wartosci:
        raise BrakSensu("pusta seria")
    if not 0 <= p <= 1:
        raise ValueError("percentyl musi być w przedziale 0–1")
    s = sorted(wartosci)
    poz = p * (len(s) - 1)
    dol = int(poz)
    gora = min(dol + 1, len(s) - 1)
    return s[dol] + (s[gora] - s[dol]) * (poz - dol)


def cena_z_mnoznika(mnoznik: float, prognoza: float) -> float:
    if prognoza <= 0:
        raise BrakSensu("prognoza na akcję ≤ 0, metoda mnożnika nie ma sensu")
    if mnoznik <= 0:
        raise BrakSensu("mnożnik ≤ 0")
    return mnoznik * prognoza


def siatka(mnoznik: float, prognoza: float, kroki_mnoznika: list[float], kroki_prognozy: list[float]) -> list[list[float]]:
    """Wiersze: przesunięcie mnożnika o krok (w punktach); kolumny: rewizja prognozy o krok (ułamek)."""
    return [[(mnoznik + dm) * prognoza * (1 + dp) for dp in kroki_prognozy] for dm in kroki_mnoznika]


# --- odczyt pliku scrab.yaml -------------------------------------------------------------


def _data(tekst: str) -> Optional[date]:
    tekst = tekst.strip()
    for wzor in ("%Y-%m-%d", "%d.%m.%Y", "%m/%d/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(tekst[:10], wzor).date()
        except ValueError:
            continue
    return None


def _liczba(tekst: str) -> Optional[float]:
    t = tekst.strip().replace(" ", "").replace(" ", "").rstrip("x×")
    if not t:
        return None
    if "," in t and "." not in t:
        t = t.replace(",", ".")
    try:
        return float(t)
    except ValueError:
        return None


def seria_z_csv(tekst: str) -> list[tuple[Optional[date], float]]:
    """Wiersze CSV: data w pierwszej kolumnie (opcjonalnie), wartość w ostatniej kolumnie z liczbą.
    Wiersze bez liczby (nagłówek, puste) pomijamy."""
    try:
        dialekt = csv.Sniffer().sniff(tekst[:2048], delimiters=",;\t")
    except csv.Error:
        dialekt = csv.excel
    wynik = []
    for wiersz in csv.reader(io.StringIO(tekst), dialekt):
        if not wiersz:
            continue
        wartosc = next((_liczba(x) for x in reversed(wiersz) if _liczba(x) is not None), None)
        if wartosc is None:
            continue
        d = _data(wiersz[0]) if len(wiersz) > 1 else None
        wynik.append((d, wartosc))
    return wynik


def _wiersz_pliku(tekst: str, klucz: str) -> Optional[str]:
    """Dosłowny wiersz pliku YAML z danym kluczem („pe_forward.mediana_5l” → wiersz „  mediana_5l: 28.92”)."""
    czesci = klucz.split(".")
    rodzic = None
    for linia in tekst.splitlines():
        bez = linia.split("#", 1)[0].rstrip()
        if not bez.strip():
            continue
        wciecie = len(bez) - len(bez.lstrip())
        nazwa = bez.strip().split(":", 1)[0]
        if wciecie == 0:
            rodzic = nazwa
            if len(czesci) == 1 and nazwa == czesci[0]:
                return linia.strip()
        elif len(czesci) == 2 and rodzic == czesci[0] and nazwa == czesci[1]:
            return linia.strip()
    return None


class DaneScrab:
    """Treść `scrab.yaml` po walidacji, z dokumentami archiwum."""

    def __init__(self, tekst: str, dokument: str, serie: dict[str, tuple[str, list[tuple[Optional[date], float]]]]):
        self.tekst = tekst
        self.dokument = dokument
        self.serie = serie  # "pe" → (id dokumentu, punkty)
        try:
            d = yaml.safe_load(tekst) or {}
        except yaml.YAMLError as e:
            raise BladScrab(f"{PLIK}: niepoprawny YAML ({e})") from None
        if not isinstance(d, dict):
            raise BladScrab(f"{PLIK}: oczekuję słownika klucz: wartość")
        self.d = d
        dz = d.get("data_odczytu")
        self.data_odczytu = dz if isinstance(dz, date) else _data(str(dz or ""))
        if not self.data_odczytu:
            raise BladScrab(f"{PLIK}: brak albo zła data_odczytu (RRRR-MM-DD)")
        self.waluta = str(d.get("waluta") or "").upper()
        if not re.fullmatch(r"[A-Z]{3}", self.waluta):
            raise BladScrab(f"{PLIK}: waluta musi być kodem ISO, np. USD albo PLN")

    def wartosc(self, klucz: str) -> Optional[float]:
        biezacy = self.d
        for c in klucz.split("."):
            if not isinstance(biezacy, dict) or c not in biezacy:
                return None
            biezacy = biezacy[c]
        if biezacy is None or isinstance(biezacy, (dict, list, bool)):
            return None
        v = biezacy if isinstance(biezacy, (int, float)) else _liczba(str(biezacy))
        return float(v) if v is not None else None

    def seria(self, mnoznik: str) -> Optional[list[float]]:
        """Seria mnożnika z okna `okno_lat` przed datą odczytu (punkty bez daty: cała seria)."""
        if mnoznik not in self.serie:
            return None
        okno = parametry()["okno_lat"]
        od = self.data_odczytu - timedelta(days=round(365.25 * okno))
        punkty = self.serie[mnoznik][1]
        return [v for dz, v in punkty if dz is None or od <= dz <= self.data_odczytu]


def wczytaj(katalog: Path, ticker: str) -> Optional[DaneScrab]:
    """Zapisuje `D/scrab.yaml` (i pliki serii) w archiwum i zwraca dane. Brak pliku → None."""
    plik = katalog / PLIK
    if not plik.exists():
        return None
    from silnik.pobieranie.archiwum import Archiwum

    arch = Archiwum(ticker, katalog)
    tekst = plik.read_text(encoding="utf-8")
    dok = arch.dodaj_tekst(tekst, TypDokumentu.wklejka, ZRODLO, opis=f"{PLIK}: dane do ceny docelowej wg Treli")
    wstepne = yaml.safe_load(tekst) or {}
    serie = {}
    for skrot, (sekcja, _) in MNOZNIKI.items():
        s = wstepne.get(sekcja) if isinstance(wstepne, dict) else None
        if not isinstance(s, dict):
            continue
        if s.get("seria_csv"):
            sciezka = katalog / str(s["seria_csv"])
            if not sciezka.exists():
                raise BladScrab(f"{PLIK}: brak pliku serii {sciezka.name}")
            tekst_csv = sciezka.read_text(encoding="utf-8-sig")
            dok_csv = arch.dodaj_tekst(tekst_csv, TypDokumentu.wklejka, ZRODLO, opis=f"{sciezka.name}: seria {sekcja}")
            serie[skrot] = (dok_csv.id, seria_z_csv(tekst_csv))
        elif isinstance(s.get("seria"), list):
            punkty = [_liczba(str(x)) for x in s["seria"]]
            serie[skrot] = (dok.id, [(None, v) for v in punkty if v is not None])
    return DaneScrab(tekst, dok.id, serie)


# --- fakty -------------------------------------------------------------------------------


def _fakt_z_pliku(k: Kalkulator, dane: DaneScrab, pozycja: str, klucz: str, jednostka: Jednostka) -> Optional[str]:
    v = dane.wartosc(klucz)
    if v is None:
        return None
    cytat = _wiersz_pliku(dane.tekst, klucz)
    fid = f"{pozycja}.{dane.data_odczytu.isoformat()}"
    k.r.dodaj(Fakt(id=fid, rodzaj=Rodzaj.raportowany, pozycja=pozycja, okres=Okres(typ="dzien", koniec=dane.data_odczytu),
                   wartosc=v, jednostka=jednostka, waluta=dane.waluta if jednostka == PA else None,
                   metoda=Metoda.wklejka, status=Status.jedno_zrodlo, dokument=dane.dokument,
                   miejsce={"klucz": klucz, "plik": PLIK}, cytat=cytat), zastap=True)
    return fid


def _fakt_ze_serii(k: Kalkulator, dane: DaneScrab, skrot: str, statystyka: str, p: Optional[float]) -> Optional[str]:
    seria = dane.seria(skrot)
    par = parametry()
    sekcja = MNOZNIKI[skrot][0]
    if seria is None:
        return None
    if len(seria) < par["min_punktow_serii"]:
        k.braki.append(f"{sekcja}: seria ma {len(seria)} punktów w oknie {par['okno_lat']} lat "
                       f"(minimum {par['min_punktow_serii']}); percentyl nie policzony")
        return None
    if statystyka == "mediana":
        v, pozycja = median(seria), f"{sekcja}_mediana_seria"
    else:
        v, pozycja = percentyl(seria, p), f"{sekcja}_percentyl"
    fid = f"{pozycja}.{dane.data_odczytu.isoformat()}"
    k.r.dodaj(Fakt(id=fid, rodzaj=Rodzaj.raportowany, pozycja=pozycja, okres=Okres(typ="dzien", koniec=dane.data_odczytu),
                   wartosc=v, jednostka=X, metoda=Metoda.wklejka, status=Status.jedno_zrodlo,
                   dokument=dane.serie[skrot][0],
                   miejsce={"seria": sekcja, "statystyka": statystyka if p is None else f"percentyl {p:.2f}",
                            "okno_lat": par["okno_lat"], "punktow": len(seria)}), zastap=True)
    return fid


def _kurs(k: Kalkulator, waluta: str) -> Optional[Fakt]:
    kursy = [f for f in k.r.fakty() if f.pozycja == "kurs" and f.status != Status.odrzucony and f.waluta == waluta]
    return max(kursy, key=lambda f: f.okres.koniec) if kursy else None


def _kontrola(k: Kalkulator, fid: Optional[str], wzorzec: Optional[str], tolerancja: float, opis: str) -> None:
    """Zapisuje w kontrolach faktu `fid` rozbieżność z `wzorzec`; duża rozbieżność trafia do braków jako trop."""
    if not fid or not wzorzec:
        return
    a, b = k.fakt(fid), k.fakt(wzorzec)
    if not a or not b or b.wartosc_bazowa() == 0:
        return
    roznica = a.wartosc_bazowa() / b.wartosc_bazowa() - 1
    wpis = f"{opis}:{wzorzec}:{roznica:+.1%}"
    if wpis not in a.kontrole:
        a.kontrole.append(wpis)
    if abs(roznica) > tolerancja:
        k.braki.append(f"trop: {opis} — {fid} różni się od {wzorzec} o {roznica:+.1%} (tolerancja {tolerancja:.0%})")


def oblicz(k: Kalkulator, katalog: Optional[Path]) -> dict:
    """Zwraca słownik id faktów (wejścia i wyniki) albo pusty słownik, gdy brak `scrab.yaml`."""
    if not katalog:
        return {}
    try:
        dane = wczytaj(katalog, k.r.ticker)
    except BladScrab as e:
        k.braki.append(f"cena docelowa wg Treli: {e}")
        return {}
    if dane is None:
        return {}
    k.r.znane_dokumenty([dane.dokument] + [s[0] for s in dane.serie.values()])
    par = parametry()
    p = par["percentyl_optymistyczny"]
    d = dane.data_odczytu.isoformat()
    okres = Okres(typ="dzien", koniec=dane.data_odczytu)
    w: dict = {"data_odczytu": dane.data_odczytu, "waluta": dane.waluta, "percentyl": p,
               "rok_obrotowy_prognozy": dane.d.get("rok_obrotowy_prognozy"), "dokument": dane.dokument}

    w["eps"] = _fakt_z_pliku(k, dane, "eps_prognoza_scrab", "eps_prognoza", PA)
    w["sps"] = _fakt_z_pliku(k, dane, "sprzedaz_na_akcje_prognoza_scrab", "sprzedaz_na_akcje_prognoza", PA)
    w["kurs_scrab"] = _fakt_z_pliku(k, dane, "kurs_scrab", "kurs", PA)
    prognoza = {"pe": w["eps"], "ps": w["sps"]}
    for skrot, (sekcja, nazwa) in MNOZNIKI.items():
        w[f"{skrot}_biezacy"] = _fakt_z_pliku(k, dane, f"{sekcja}_biezacy_scrab", f"{sekcja}.biezacy", X)
        mediana_scrab = _fakt_z_pliku(k, dane, f"{sekcja}_mediana_scrab", f"{sekcja}.mediana_5l", X)
        mediana_seria = _fakt_ze_serii(k, dane, skrot, "mediana", None)
        _kontrola(k, mediana_seria, mediana_scrab, par["tolerancja_mediany"], f"mediana {nazwa} z serii a mediana 5Y ze Scrab")
        w[f"{skrot}_mediana"] = mediana_scrab or mediana_seria
        w[f"{skrot}_percentyl"] = _fakt_ze_serii(k, dane, skrot, "percentyl", p)
        if w[f"{skrot}_percentyl"] is None and skrot not in dane.serie:
            k.braki.append(f"cena docelowa wg Treli, wariant optymistyczny {nazwa}: brak serii mnożnika w {PLIK} "
                           "(potrzebna do percentyla)")
        for wariant, mnoznik in (("kons", w[f"{skrot}_mediana"]), ("optym", w[f"{skrot}_percentyl"])):
            if not mnoznik or not prognoza[skrot]:
                w[f"{skrot}_{wariant}"] = None
                continue
            f = k.wylicz(f"cena_docelowa_trela_{skrot}_{wariant}.{d}", f"cena_docelowa_trela_{skrot}_{wariant}",
                         f"{mnoznik} × {prognoza[skrot]}", [mnoznik, prognoza[skrot]], cena_z_mnoznika, PA, okres)
            w[f"{skrot}_{wariant}"] = f.id if f else None

    kurs = _kurs(k, dane.waluta)
    w["kurs"] = kurs.id if kurs else None
    if kurs is None:
        k.braki.append(f"cena docelowa wg Treli: brak kursu w walucie {dane.waluta}; potencjał nie policzony")
    _kontrola(k, w["kurs_scrab"], w["kurs"], par["tolerancja_kursu"], "kurs ze Scrab a kurs pobrany przez silnik")
    for wariant in ("kons", "optym"):
        czesci = [w[f"pe_{wariant}"], w[f"ps_{wariant}"]]
        dostepne = [c for c in czesci if c]
        fid = None
        if dostepne:
            wzor = "średnia(" + ", ".join(dostepne) + ")" if len(dostepne) == 2 else dostepne[0]
            f = k.wylicz(f"cena_docelowa_trela_{wariant}.{d}", f"cena_docelowa_trela_{wariant}", wzor, dostepne,
                         lambda *x: sum(x) / len(x), PA, okres)
            fid = f.id if f else None
        w[wariant] = fid
        w[f"potencjal_{wariant}"] = None
        if fid and kurs:
            f = k.wylicz(f"potencjal_trela_{wariant}.{d}", f"potencjal_trela_{wariant}", f"{fid} / {kurs.id} − 1",
                         [fid, kurs.id], lambda c, ku: c / ku - 1, U, okres)
            w[f"potencjal_{wariant}"] = f.id if f else None
    w["metody"] = [s for s in ("pe", "ps") if w[f"{s}_kons"]]
    return w
