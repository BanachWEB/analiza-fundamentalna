"""Aktualność materiałów od właściciela (specyfikacja 1.1, punkt 3.3, zasada 6; decyzja z 12.11.2026).

Silnik nie poprawia materiału. Porównuje go z własnymi danymi i zapisuje ostrzeżenie, gdy różnica
przekracza próg z `konfiguracja/wycena.yaml` (sekcja `aktualnosc`):
- kurs w arkuszu ceny docelowej a dzisiejszy kurs;
- prognoza EPS w arkuszu a EPS rozwodniony TTM (albo z ostatniego roku) i konsensus EPS;
- wiek danych z wklejek (data prognozy albo koniec okresu) wobec daty analizy;
- konsensus z wklejki a konsensus pobrany przez silnik (ta sama pozycja, inne źródło).
Rozbieżność to trop: często ujawnia błąd danych po jednej ze stron.
"""

from __future__ import annotations

from typing import Optional

from silnik.fakty.schemat import Fakt, Jednostka, Metoda, Okres, Status

from .kalkulator import BrakSensu, Kalkulator
from .wycena import ostatni, parametry

KONSENSUS = ("cena_docelowa_srednia", "wzrost_eps_konsensus", "eps_konsensus", "przychody_konsensus", "liczba_analitykow")


def _wzgledna(a: float, b: float) -> float:
    if b <= 0:
        raise BrakSensu("podstawa porównania ≤ 0")
    return a / b - 1


def _proc(x: float) -> str:
    return f"{x * 100:+.0f}%".replace("-", "−")


def _ostatni_dowolny(k: Kalkulator, pozycja: str, warunek=lambda f: True) -> Optional[Fakt]:
    fs = [f for f in k.r.fakty() if f.pozycja == pozycja and f.status != Status.odrzucony and warunek(f)]
    return max(fs, key=lambda f: (f.okres.koniec or k.r.data_analizy, f.id)) if fs else None


def _eps_raportowany(k: Kalkulator) -> Optional[Fakt]:
    ttm = [f for f in k.r.fakty() if f.pozycja == "eps_rozwodniony" and f.okres.typ.value == "TTM" and f.status != Status.odrzucony]
    if ttm:
        return max(ttm, key=lambda f: f.okres.koniec)
    fy = k.okresy_fy("eps_rozwodniony")
    return fy[-1] if fy else None


def sprawdz(k: Kalkulator, trela: dict, wycena: dict) -> list[str]:
    """Dopisuje ostrzeżenia do k.ostrzezenia i zwraca je."""
    progi = parametry()["aktualnosc"]
    D = k.r.data_analizy
    okres_d = Okres(typ="dzien", koniec=D)
    nowe: list[str] = []

    # 1. arkusz ceny docelowej
    kurs = ostatni(k, "kurs")
    if trela.get("kurs_arkusz") and kurs:
        f = k.wylicz(f"rozbieznosc_kursu_arkusza.{D.isoformat()}", "rozbieznosc_kursu_arkusza", "kurs_arkusz / kurs − 1",
                     [trela["kurs_arkusz"], kurs.id], lambda a, b: a / b - 1, Jednostka.ulamek, okres_d)
        if f and abs(f.wartosc) > progi["kurs"]:
            nowe.append(f"Arkusz ceny docelowej: kurs w arkuszu różni się od kursu z {kurs.okres.koniec.isoformat()} o "
                        f"{_proc(f.wartosc)} (próg ±{progi['kurs']:.0%}) — arkusz może być nieaktualny.")
    eps = _eps_raportowany(k)
    if trela.get("eps_prognoza_arkusz") and eps:
        f = k.wylicz(f"rozbieznosc_eps_arkusza.{D.isoformat()}", "rozbieznosc_eps_arkusza",
                     f"eps_prognoza_arkusz / {eps.id} − 1", [trela["eps_prognoza_arkusz"], eps.id],
                     _wzgledna, Jednostka.ulamek, okres_d)
        if f and abs(f.wartosc) > progi["eps"]:
            nowe.append(f"Arkusz ceny docelowej: prognoza EPS różni się od EPS rozwodnionego ({eps.id}) o "
                        f"{_proc(f.wartosc)} (próg ±{progi['eps']:.0%}) — sprawdź, czy dane ze Scrab są aktualne.")
    kons = _ostatni_dowolny(k, "eps_konsensus", lambda f: f.metoda != Metoda.wklejka)
    if trela.get("eps_prognoza_arkusz") and kons:
        f = k.wylicz(f"rozbieznosc_eps_arkusza_konsensus.{D.isoformat()}", "rozbieznosc_eps_arkusza_konsensus",
                     f"eps_prognoza_arkusz / {kons.id} − 1", [trela["eps_prognoza_arkusz"], kons.id],
                     _wzgledna, Jednostka.ulamek, okres_d)
        if f and abs(f.wartosc) > progi["eps"]:
            nowe.append(f"Arkusz ceny docelowej: prognoza EPS różni się od konsensusu EPS ({kons.id}) o {_proc(f.wartosc)} "
                        f"(próg ±{progi['eps']:.0%}).")

    # 2. wiek danych z wklejek (bez arkusza: jego datą jest zawsze data analizy)
    arkusz_dok = trela.get("dokument")
    stare = []
    for f in k.r.fakty():
        if f.metoda != Metoda.wklejka or f.status == Status.odrzucony or f.dokument == arkusz_dok:
            continue
        data = f.data_prognozy or (f.okres.koniec if f.okres.typ.value == "dzien" else None)
        if data and (D - data).days > progi["dni"]:
            stare.append(f"{f.id} ({data.isoformat()})")
    if stare:
        nowe.append(f"Wklejka: dane starsze niż {progi['dni']} dni przed datą analizy: {', '.join(sorted(stare)[:8])}"
                    + (" i inne" if len(stare) > 8 else "") + ".")

    # 3. konsensus z wklejki a konsensus silnika
    for poz in KONSENSUS:
        z_wklejki = _ostatni_dowolny(k, poz, lambda f: f.metoda == Metoda.wklejka)
        z_silnika = _ostatni_dowolny(k, poz, lambda f: f.metoda != Metoda.wklejka)
        if not (z_wklejki and z_silnika) or not z_silnika.wartosc:
            continue
        if poz == "przychody_konsensus" and z_wklejki.okres.koniec != z_silnika.okres.koniec:
            continue  # różne lata obrotowe
        roznica = z_wklejki.wartosc_bazowa() / z_silnika.wartosc_bazowa() - 1
        if abs(roznica) > progi["konsensus"]:
            nowe.append(f"Konsensus: {z_wklejki.id} z wklejki różni się od {z_silnika.id} ({z_silnika.dostawca or 'silnik'}) o "
                        f"{_proc(roznica)} (próg ±{progi['konsensus']:.0%}).")
    k.ostrzezenia += nowe
    return nowe
