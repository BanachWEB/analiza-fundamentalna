"""Lint tekstu modelu: żadnej liczby poza miejscami na liczby.

Model pisze raport.md z miejscami {{id_faktu}}, {{tabela:…}} i {{wykres:…}}.
Każda cyfra w tekście modelu jest błędem, z wyjątkiem:
- lat (1990–2049; starsze tylko z „r.” albo „roku”) i dat (dd.mm.rrrr, rrrr-mm-dd),
- etykiet okresów (FY2025, Q3, H1, M9, TTM, „I–III kw.”),
- numeracji nagłówków i list na początku wiersza („## 4.”, „1.”),
- identyfikatorów w nawiasach klamrowych i w `kodzie`.
Każde miejsce na liczbę musi wskazywać istniejący, nieodrzucony fakt.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from silnik.fakty.rejestr import RejestrFaktow
from silnik.fakty.schemat import Status

MIEJSCE = re.compile(r"\{\{([^{}]+)\}\}")
KOD = re.compile(r"`[^`]*`")
DOZWOLONE = [  # kolejność ma znaczenie: daty przed latami
    re.compile(r"\b\d{1,2}\.\d{1,2}\.\d{4}\b"),                 # dd.mm.rrrr
    re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),                       # rrrr-mm-dd
    re.compile(r"\b(19[9]\d|20[0-4]\d)\b"),                    # lata 1990–2049
    re.compile(r"\b(1[89]\d\d)\s?(r\.|roku|rok)"),                # starsze lata tylko z „r.”/„roku”
    re.compile(r"\b(FY|TTM)\d{4}(Q[1-4]|H1|M9)?\b"),            # FY2025Q3
    re.compile(r"\b(Q[1-4]|H1|M9|S&P\s?500|WIG\d*|mWIG40|sWIG80|10-K|10-Q|8-K|20-F|6-K|K-IFRS|MSSF\s?\d+|IFRS\s?\d+|"
               r"IAS\s?\d+|ASC\s?\d+|4\.0[12]|12–1|ESEF|CET1|Z''|F-score|M-score)\b"),
]
# Nazwy własne z cyframi (produkty, indeksy). Inne nazwy model zapisuje w `kodzie`.
NAZWY = re.compile(r"\b(Microsoft 365|Dynamics 365|Office 365|Windows 1[01]|Xbox 360|WIG20|WIG30|mWIG40|sWIG80|"
                   r"Russell 2000|Nasdaq[- ]100|W-8BEN|Stoxx 600|Euro Stoxx 50|FTSE 100|DAX 40|CAC 40|Web3|5G|4G)\b")
NUMERACJA = re.compile(r"^(\s*#{1,6}\s*\d+(\.\d+)*\.?|\s*\d+\.\s)")


@dataclass
class Blad:
    wiersz: int
    tresc: str
    powod: str


def sprawdz(tekst: str, rejestr: RejestrFaktow, tabele: set[str], wykresy: set[str]) -> list[Blad]:
    bledy = []
    for nr, linia in enumerate(tekst.splitlines(), 1):
        for m in MIEJSCE.finditer(linia):
            ref = m.group(1).strip()
            if ref.startswith("tabela:"):
                if ref[7:] not in tabele:
                    bledy.append(Blad(nr, ref, f"nieznana tabela (dostępne: {', '.join(sorted(tabele))})"))
            elif ref.startswith("wykres:"):
                if ref[7:] not in wykresy:
                    bledy.append(Blad(nr, ref, f"nieznany wykres (dostępne: {', '.join(sorted(wykresy))})"))
            else:
                fid = ref.split("|")[0]
                if fid not in rejestr:
                    bledy.append(Blad(nr, ref, "brak faktu w rejestrze"))
                elif rejestr[fid].status == Status.odrzucony:
                    bledy.append(Blad(nr, ref, "fakt odrzucony przez weryfikację"))
        reszta = NAZWY.sub(" ", KOD.sub(" ", MIEJSCE.sub(" ", linia)))
        reszta = NUMERACJA.sub(" ", reszta)
        for wz in DOZWOLONE:
            reszta = wz.sub(" ", reszta)
        if "%" in reszta:
            bledy.append(Blad(nr, linia.strip()[:120], "znak % poza miejscem na liczbę"))
        cyfry = re.findall(r"\d[\d\s.,]*", reszta)
        if cyfry:
            bledy.append(Blad(nr, linia.strip()[:120], f"liczba wpisana przez model: {', '.join(c.strip() for c in cyfry)}"))
    return bledy
