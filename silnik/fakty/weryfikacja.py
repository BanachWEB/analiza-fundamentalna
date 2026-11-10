"""Weryfikacja faktów: tożsamości księgowe i drugie źródło.

Wynik każdej kontroli trafia do pola „kontrole” faktu. Status:
- konflikt, gdy choć jedna kontrola wypadła źle;
- zweryfikowany, gdy fakt przeszedł co najmniej jedną kontrolę i żadnej nie oblał;
- jedno_zrodlo w pozostałych przypadkach.
Kontrola nie zmienia wartości faktu.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Optional

from .rejestr import RejestrFaktow
from .schemat import Fakt, Status

TOLERANCJA_DRUGIE_ZRODLO = 0.005  # 0,5%
TOLERANCJA_TOZSAMOSCI = 0.001  # 0,1%

# Pozycja z drugiego źródła → pozycje rejestru do porównania, w kolejności.
ALIASY = {
    "kapital_wlasny_razem": ["kapital_wlasny_z_udzialami_niekontrolujacymi", "kapital_wlasny"],
}


@dataclass
class WynikKontroli:
    nazwa: str
    okres: str
    ok: bool
    fakty: list[str]
    opis: str


@dataclass
class Raport:
    kontrole: list[WynikKontroli] = field(default_factory=list)

    def dodaj(self, w: WynikKontroli):
        self.kontrole.append(w)


def _roznica(a: float, b: float) -> float:
    mianownik = max(abs(a), abs(b))
    return 0.0 if mianownik == 0 else abs(a - b) / mianownik


def _oznacz(rejestr: RejestrFaktow, ids: list[str], wpis: str, ok: bool) -> None:
    for fid in ids:
        f = rejestr[fid]
        kontrole = list(f.kontrole) + [wpis]
        if not ok:
            status = Status.konflikt
        elif f.status == Status.konflikt:
            status = Status.konflikt
        else:
            status = Status.zweryfikowany
        rejestr.dodaj(f.model_copy(update={"kontrole": kontrole, "status": status}), zastap=True)


def _po_okresie(rejestr: RejestrFaktow) -> dict[str, dict[str, Fakt]]:
    """sufiks okresu (np. FY2026, 2026-06-30) → {pozycja: fakt}; tylko fakty raportowane."""
    wynik: dict[str, dict[str, Fakt]] = {}
    for f in rejestr.fakty():
        if f.rodzaj.value != "raportowany":
            continue
        sufiks = f.id.split(".", 1)[1]
        wynik.setdefault(sufiks, {})[f.pozycja] = f
    return wynik


def _tozsamosc(rejestr, raport, okres, nazwa, lewa: list[tuple[str, int]], prawa: str, pozycje: dict, tol: float):
    if prawa not in pozycje or not all(p in pozycje for p, _ in lewa):
        return
    suma = sum(znak * pozycje[p].wartosc for p, znak in lewa)
    wartosc_prawa = pozycje[prawa].wartosc
    r = _roznica(suma, wartosc_prawa)
    ok = r <= tol
    ids = [pozycje[p].id for p, _ in lewa] + [pozycje[prawa].id]
    wpis = f"tozsamosc:{nazwa}:{'ok' if ok else 'blad'}:{r:.4%}"
    _oznacz(rejestr, ids, wpis, ok)
    raport.dodaj(WynikKontroli(nazwa, okres, ok, ids, f"różnica {r:.4%}"))


def tozsamosci(rejestr: RejestrFaktow, raport: Optional[Raport] = None) -> Raport:
    raport = raport or Raport()
    for okres, poz in _po_okresie(rejestr).items():
        _tozsamosc(rejestr, raport, okres, "aktywa=pasywa", [("aktywa", 1)], "pasywa_razem", poz, TOLERANCJA_TOZSAMOSCI)
        kapital = "kapital_wlasny_z_udzialami_niekontrolujacymi" if "kapital_wlasny_z_udzialami_niekontrolujacymi" in poz else "kapital_wlasny"
        _tozsamosc(rejestr, raport, okres, "zobowiazania+kapital=pasywa",
                   [("zobowiazania", 1), (kapital, 1)], "pasywa_razem", poz, 0.01)
        _tozsamosc(rejestr, raport, okres, "przychody-koszt_sprzedazy=zysk_brutto",
                   [("przychody", 1), ("koszt_sprzedazy", -1)], "zysk_brutto", poz, TOLERANCJA_TOZSAMOSCI)
        _tozsamosc(rejestr, raport, okres, "przeplywy=zmiana_gotowki",
                   [("przeplywy_operacyjne", 1), ("przeplywy_inwestycyjne", 1), ("przeplywy_finansowe", 1),
                    ("wplyw_kursow_na_gotowke", 1)], "zmiana_gotowki", poz, TOLERANCJA_TOZSAMOSCI)
        if "wplyw_kursow_na_gotowke" not in poz:
            # Spółka nie podaje wpływu kursów (np. Apple). Gdy w rzeczywistości ma taką pozycję
            # pod innym znacznikiem, tożsamość nie wyjdzie i fakt dostanie konflikt — to dobrze.
            _tozsamosc(rejestr, raport, okres, "przeplywy=zmiana_gotowki(bez_kursow)",
                       [("przeplywy_operacyjne", 1), ("przeplywy_inwestycyjne", 1), ("przeplywy_finansowe", 1)],
                       "zmiana_gotowki", poz, TOLERANCJA_TOZSAMOSCI)
    return raport


def drugie_zrodlo(
    rejestr: RejestrFaktow,
    dane: dict[tuple[str, date], tuple[float, str]],
    raport: Optional[Raport] = None,
    tol: float = TOLERANCJA_DRUGIE_ZRODLO,
) -> Raport:
    """Porównuje fakty roczne i stany na koniec roku z danymi z drugiego źródła."""
    raport = raport or Raport()
    fakty = {
        (f.pozycja, f.okres.koniec): f
        for f in rejestr.fakty()
        if f.rodzaj.value == "raportowany" and f.okres.typ.value in ("FY", "dzien")
    }
    for (pozycja2, koniec), (wartosc2, dok2) in sorted(dane.items(), key=lambda x: (x[0][0], x[0][1])):
        f = next((fakty[(p, koniec)] for p in ALIASY.get(pozycja2, [pozycja2]) if (p, koniec) in fakty), None)
        if f is None:
            continue
        r = _roznica(f.wartosc, wartosc2)
        ok = r <= tol
        wpis = f"drugie_zrodlo:{dok2}:{wartosc2:g}:{r:.2%}:{'ok' if ok else 'blad'}"
        _oznacz(rejestr, [f.id], wpis, ok)
        raport.dodaj(WynikKontroli("drugie_zrodlo", f.id.split(".", 1)[1], ok, [f.id], f"{dok2}: różnica {r:.2%}"))
    return raport


def pozycje_przestarzale(rejestr: RejestrFaktow) -> list[str]:
    """Pozycje okresowe, których ostatni rok obrotowy jest starszy niż ostatni rok w rejestrze."""
    ostatni: dict[str, date] = {}
    for f in rejestr.fakty():
        if f.rodzaj.value == "raportowany" and f.okres.typ.value == "FY":
            if f.pozycja not in ostatni or f.okres.koniec > ostatni[f.pozycja]:
                ostatni[f.pozycja] = f.okres.koniec
    if not ostatni:
        return []
    najnowszy = max(ostatni.values())
    return sorted(p for p, k in ostatni.items() if k < najnowszy)


def podsumowanie_md(rejestr: RejestrFaktow, raport: Raport) -> str:
    """Raport z weryfikacji w Markdown (generowany przez kod; bez liczb od modelu)."""
    licznik = {s: len(rejestr.ze_statusem(s)) for s in Status}
    linie = [
        f"# Weryfikacja faktów: {rejestr.ticker}",
        "",
        f"Plik wygenerował silnik ({rejestr.data_analizy.isoformat()}). Nie edytuj go ręcznie.",
        "",
        "| Status | Liczba faktów |",
        "|---|---:|",
    ] + [f"| {s.value} | {n} |" for s, n in licznik.items()]
    nazwy = sorted({k.nazwa for k in raport.kontrole})
    linie += ["", "## Kontrole", "", "| Kontrola | Zaliczone | Niezaliczone |", "|---|---:|---:|"]
    for n in nazwy:
        ok = sum(1 for k in raport.kontrole if k.nazwa == n and k.ok)
        zle = sum(1 for k in raport.kontrole if k.nazwa == n and not k.ok)
        linie.append(f"| {n} | {ok} | {zle} |")
    bledy = [k for k in raport.kontrole if not k.ok]
    linie += ["", "## Konflikty", ""]
    if not bledy:
        linie.append("Brak konfliktów.")
    else:
        linie += ["| Kontrola | Okres | Fakty | Opis |", "|---|---|---|---|"]
        for k in bledy:
            linie.append(f"| {k.nazwa} | {k.okres} | {', '.join(k.fakty)} | {k.opis} |")
    linie += ["", "## Pozycje bez danych za ostatni rok obrotowy", ""]
    przestarzale = pozycje_przestarzale(rejestr)
    linie.append(
        "Spółka mogła zmienić znacznik XBRL; sprawdź mapowanie: " + ", ".join(przestarzale) if przestarzale else "Brak."
    )
    zmiany = [f.id for f in rejestr.fakty() if any(c.startswith("zmiana_wersji") for c in f.kontrole)]
    linie += ["", "## Fakty zmienione w kolejnych raportach spółki", ""]
    linie.append(", ".join(sorted(zmiany)) if zmiany else "Brak.")
    return "\n".join(linie) + "\n"
