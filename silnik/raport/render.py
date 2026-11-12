"""Renderowanie raportu: tekst modelu z miejscami na liczby → Markdown z wartościami i przypisami.

Miejsca:
- {{id_faktu}}        → wartość z rejestru i przypis (okres, źródło albo wzór, status);
- {{tabela:nazwa}}    → tabela generowana przez kod (panel, wycena, cena_docelowa_trela, scenariusze, karta, bramki,
                        jakosc_danych);
- {{wykres:nazwa}}    → wykres PNG z faktów rejestru.
"""

from __future__ import annotations

import json
from pathlib import Path

from silnik.fakty.schemat import Fakt, Status
from silnik.obliczenia import uruchom as obliczenia_uruchom
from silnik.obliczenia.raport import karta_tabela, panel_md, scenariusze_tabela, trela_tabela, wycena_tabela
from silnik.pobieranie.archiwum import Archiwum

from . import formaty, lint, wykresy
from .lint import MIEJSCE

TABELE = ("panel", "wycena", "cena_docelowa_trela", "scenariusze", "karta", "bramki", "jakosc_danych")
WYKRESY = ("przychody", "marze", "fcf_zysk", "roic")


def miejsca(katalog: Path, ostatnie: int = 3) -> list[str]:
    """Zwarta lista miejsc na liczby: pozycja, liczba okresów i ostatnie okresy (bez faktów odrzuconych)."""
    fakty = json.loads((katalog / "fakty.json").read_text(encoding="utf-8"))["fakty"]
    okresy: dict[str, list[str]] = {}
    for f in fakty:
        if f.get("status") == Status.odrzucony.value:
            continue
        pozycja, okres = f["id"].split(".", 1)
        okresy.setdefault(pozycja, []).append(okres)
    wynik = [f"Tabele: {', '.join('{{tabela:' + t + '}}' for t in TABELE)}",
             f"Wykresy: {', '.join('{{wykres:' + w + '}}' for w in WYKRESY)}",
             "Fakty: pozycja (liczba okresów): ostatnie okresy → miejsce {{pozycja.okres}}"]
    for pozycja in sorted(okresy):
        lista = sorted(set(okresy[pozycja]))
        wynik.append(f"- {pozycja} ({len(lista)}): {', '.join(lista[-ostatnie:])}")
    return wynik


class BladRaportu(Exception):
    def __init__(self, bledy):
        self.bledy = bledy
        super().__init__("\n".join(f"wiersz {b.wiersz}: {b.powod} — {b.tresc}" for b in bledy))


def _przypis(f: Fakt, archiwum: Archiwum, rejestr) -> str:
    czesci = [f"{formaty.wartosc(f)}, {formaty.okres(f)}"]
    if f.rodzaj.value in ("raportowany", "prognoza") and f.dokument:
        d = archiwum[f.dokument]
        miejsce = ", ".join(f"{k}: {v}" for k, v in f.miejsce.items() if k in ("xbrl", "strona", "pole", "kolumna", "wiersz"))
        czesci.append(f"źródło: {d.zrodlo} — {d.opis} ({f.dokument}, pobrano {d.pobrano.date().isoformat()}"
                      + (f"; {miejsce}" if miejsce else "") + ")")
        if f.cytat:
            czesci.append(f"cytat: „{f.cytat[:160]}”")
    elif f.rodzaj.value == "wyliczony":
        czesci.append(f"wyliczenie: {f.wzor}")
    elif f.rodzaj.value == "zalozenie":
        czesci.append(f"założenie: {f.uzasadnienie}")
    czesci.append(f"status: {formaty.STATUS[f.status]}")
    drugie = [c for c in f.kontrole if c.startswith("drugie_zrodlo")]
    if drugie:
        czesci.append("kontrola: " + drugie[-1].split(":")[-2] + " różnicy z drugim źródłem")
    return "; ".join(czesci) + "."


def jakosc_danych(rejestr, archiwum: Archiwum, katalog: Path, ostrzezenia: list[str] | None = None) -> list[str]:
    fakty = [f for f in rejestr.fakty() if f.rodzaj.value == "raportowany"]
    licz = {s: sum(1 for f in fakty if f.status == s) for s in Status}
    linie = ["| Status faktów z dokumentów | Liczba |", "|---|---:|"]
    linie += [f"| {formaty.STATUS[s]} | {n} |" for s, n in licz.items()]
    konflikty = [f for f in rejestr.fakty() if f.status == Status.konflikt and f.rodzaj.value == "raportowany"]
    def powod(f):
        bledy = [c for c in f.kontrole if ":blad" in c]
        return bledy[-1].split(":")[1] if bledy else "konflikt"
    linie += ["", "**Konflikty źródeł:** " + ("; ".join(f"{f.id} ({powod(f)})" for f in konflikty[:10]) if konflikty else "brak.")]
    uzup = sorted({f.okres.koniec.year for f in fakty if f.metoda.value == "parser_strony" and f.okres.typ.value == "FY"})
    if uzup:
        linie.append(f"**Lata z serwisu danych (bez raportu spółki):** {', '.join(map(str, uzup))}.")
    odrz = [f for f in rejestr.fakty() if f.status == Status.odrzucony]
    if odrz:
        linie.append(f"**Propozycje odrzucone przez test cytatu:** {', '.join(f.id for f in odrz)}.")
    zrodla = sorted({d.zrodlo for d in archiwum.rejestr.dokumenty})
    linie.append(f"**Źródła w archiwum:** {', '.join(zrodla)} ({len(archiwum.rejestr.dokumenty)} dokumentów).")
    if ostrzezenia:
        linie += ["", "**Ostrzeżenia silnika:**"] + [f"- {o}" for o in dict.fromkeys(ostrzezenia)]
    return linie


def bramki_tabela(katalog: Path) -> list[str]:
    p = katalog / "bramki.json"
    if not p.exists():
        return ["Brak wyniku bramek."]
    d = json.loads(p.read_text(encoding="utf-8"))
    linie = [f"**Decyzja bramek: {d['decyzja']}** — {d['powod']}.", "", "| Etap | Bramka | Wynik | Opis |", "|---:|---|---|---|"]
    for w in d["wyniki"]:
        if w["poziom"] in ("ok",):
            continue
        linie.append(f"| {w['etap']} | {w['id']} | {w['poziom'].replace('_', ' ')} | {w['opis']} |")
    return linie


def renderuj(katalog: Path, tekst: str) -> str:
    dok = json.loads((katalog / "dokumenty.json").read_text(encoding="utf-8"))
    archiwum = Archiwum(dok["ticker"], katalog)
    from silnik.fakty.rejestr import RejestrFaktow

    rejestr = RejestrFaktow.z_pliku(katalog / "fakty.json", archiwum.ids())
    k, wynik = obliczenia_uruchom(rejestr, katalog)
    obrazy = wykresy.wszystkie(k, katalog)
    bledy = lint.sprawdz(tekst, rejestr, set(TABELE), set(obrazy))
    if bledy:
        raise BladRaportu(bledy)
    tabele = {
        "panel": panel_md(k, wynik), "wycena": wycena_tabela(k, wynik), "cena_docelowa_trela": trela_tabela(k, wynik),
        "scenariusze": scenariusze_tabela(k, wynik),
        "karta": karta_tabela(k, wynik), "bramki": bramki_tabela(katalog), "jakosc_danych": jakosc_danych(rejestr, archiwum, katalog, k.ostrzezenia),
    }
    przypisy: dict[str, int] = {}

    def zamien(m):
        ref = m.group(1).strip()
        if ref.startswith("tabela:"):
            return "\n" + "\n".join(tabele[ref[7:]]) + "\n"
        if ref.startswith("wykres:"):
            return f"![{ref[7:]}]({obrazy[ref[7:]].name})"
        fid = ref.split("|")[0]
        f = rejestr[fid]
        if fid not in przypisy:
            przypisy[fid] = len(przypisy) + 1
        znak = "‼" if f.status == Status.konflikt else ""
        return f"{formaty.wartosc(f)}{znak}[^{przypisy[fid]}]"

    wynik_md = MIEJSCE.sub(zamien, tekst)
    if przypisy:
        wynik_md += "\n\n## Przypisy: źródła liczb\n\n"
        for fid, n in przypisy.items():
            wynik_md += f"[^{n}]: {_przypis(rejestr[fid], archiwum, rejestr)}\n"
    return wynik_md
