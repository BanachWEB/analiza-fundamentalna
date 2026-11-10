"""Dowody od modelu: flagi wymagające oceny (oszustwo, decyzja organu, akcjonariusz > 90% …).

Model zapisuje analizy/<TICKER>/<data>/bramki_dowody.json:
{"dowody": [{"bramka": "B4.akcjonariusz_90", "poziom": "stop", "opis": "…",
             "dokument": "doc-012", "strona": 5, "cytat": "…dosłowny fragment…",
             "testy": {"strukturalny": "…", "uczciwosc_liczb": "…", "zarzad_rozwiazuje": "…", "termin": "…"},
             "warunek_powrotu": "…"}]}
Silnik przyjmuje dowód tylko wtedy, gdy bramka jest w konfiguracji, a cytat występuje w dokumencie
z archiwum (test cytatu bez liczby). STOP wymaga też czterech testów i warunku powrotu.
Odrzucony dowód nie zmienia decyzji, ale trafia do raportu bramek.
"""

from __future__ import annotations

import json
from pathlib import Path

from silnik.fakty.cytat import tekst_dokumentu, ujednolic
from silnik.pobieranie.archiwum import Archiwum

from . import Wynik, konfiguracja

TESTY = ("strukturalny", "uczciwosc_liczb", "zarzad_rozwiazuje", "termin")


def wczytaj(plik: Path, archiwum: Archiwum) -> tuple[list[Wynik], list[str]]:
    if not plik.exists():
        return [], []
    cfg = konfiguracja()["bramki_modelu"]
    przyjete, odrzucone = [], []
    for d in json.loads(plik.read_text(encoding="utf-8"))["dowody"]:
        bid = d.get("bramka")
        if bid not in cfg:
            odrzucone.append(f"{bid}: nieznana bramka")
            continue
        poziom = d.get("poziom")
        if poziom not in ("stop", "flaga_powazna", "flaga", "informacja", "ok"):
            odrzucone.append(f"{bid}: nieznany poziom {poziom}")
            continue
        if poziom != "ok":
            try:
                tekst = tekst_dokumentu(archiwum.sciezka(d["dokument"]), d.get("strona"))
            except Exception as e:  # brak dokumentu, zła strona
                odrzucone.append(f"{bid}: dokument {d.get('dokument')} niedostępny ({e})")
                continue
            if not d.get("cytat") or ujednolic(d["cytat"]) not in ujednolic(tekst):
                odrzucone.append(f"{bid}: cytatu nie ma we wskazanym dokumencie")
                continue
        if poziom == "stop":
            brak = [t for t in TESTY if not (d.get("testy") or {}).get(t)]
            if brak or not d.get("warunek_powrotu"):
                odrzucone.append(f"{bid}: STOP bez czterech testów albo bez warunku powrotu (brak: {', '.join(brak) or 'warunek'})")
                continue
        c = cfg[bid]
        przyjete.append(Wynik(bid, c["etap"], c["kategoria"], poziom, d.get("opis") or c["opis"],
                              [f"{d.get('dokument')}: „{d.get('cytat', '')[:200]}”"] if d.get("dokument") else [],
                              zrodlo="model", testy=d.get("testy"), warunek_powrotu=d.get("warunek_powrotu")))
    return przyjete, odrzucone
