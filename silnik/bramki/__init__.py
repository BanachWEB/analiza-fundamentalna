"""Bramki stopu: automatyczne sprawdzenia + dowody od modelu → decyzja STOP / PAUZA / DALEJ."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

import yaml

KONFIGURACJA = Path(__file__).resolve().parents[2] / "konfiguracja" / "bramki.yaml"
POZIOMY = ("stop", "flaga_powazna", "flaga", "informacja", "ok", "brak_danych")


@dataclass
class Wynik:
    id: str
    etap: int
    kategoria: str
    poziom: str
    opis: str
    dowody: list[str] = field(default_factory=list)  # id faktów albo „doc-NNN: fragment”
    zrodlo: str = "kod"  # kod | model
    testy: Optional[dict] = None  # cztery testy (dla stopu od modelu)
    warunek_powrotu: Optional[str] = None

    def __post_init__(self):
        if self.poziom not in POZIOMY:
            raise ValueError(f"nieznany poziom {self.poziom}")


def konfiguracja() -> dict:
    return yaml.safe_load(KONFIGURACJA.read_text(encoding="utf-8"))


@dataclass
class Decyzja:
    decyzja: str  # STOP | PAUZA | DALEJ
    etap: Optional[int]
    powod: str
    wyniki: list[Wynik]

    def do_json(self) -> str:
        return json.dumps({"decyzja": self.decyzja, "etap": self.etap, "powod": self.powod,
                           "wyniki": [asdict(w) for w in self.wyniki]}, ensure_ascii=False, indent=2) + "\n"


def ocen(wyniki: list[Wynik]) -> Decyzja:
    wyniki = sorted(wyniki, key=lambda w: (w.etap, POZIOMY.index(w.poziom), w.id))
    stopy = [w for w in wyniki if w.poziom == "stop"]
    if stopy:
        s = stopy[0]
        return Decyzja("STOP", s.etap, f"{s.id}: {s.opis}", wyniki)
    powazne = [w for w in wyniki if w.poziom == "flaga_powazna"]
    kategorie = sorted({w.kategoria for w in powazne})
    if len(kategorie) >= 3:
        return Decyzja("PAUZA", None, f"flagi poważne w {len(kategorie)} kategoriach: {', '.join(kategorie)}", wyniki)
    return Decyzja("DALEJ", None, "brak twardej flagi", wyniki)
