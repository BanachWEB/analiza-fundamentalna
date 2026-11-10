"""obliczenia.md — tabela wskaźników generowana przez kod (bez liczb od modelu)."""

from __future__ import annotations

from datetime import date
from typing import Optional

from silnik.fakty.schemat import Fakt, Jednostka, Status

from .jakosc import PROG_M, STREFY_Z
from .kalkulator import Kalkulator

ZNAK = {Status.zweryfikowany: "", Status.jedno_zrodlo: "¹", Status.konflikt: "‼", Status.odrzucony: "✗"}

WIERSZE = [
    ("przychody", "Przychody"),
    ("wzrost_przychody", "Wzrost przychodów r/r"),
    ("marza_brutto", "Marża brutto"),
    ("marza_operacyjna", "Marża operacyjna"),
    ("marza_netto", "Marża netto"),
    ("zysk_netto", "Zysk netto"),
    ("ebitda", "EBITDA"),
    ("fcf_wlascicieli", "FCF dla właścicieli"),
    ("konwersja_fcf", "FCF dla właścicieli ÷ zysk netto"),
    ("marza_fcf", "Marża FCF"),
    ("capex_do_amortyzacji", "Capex ÷ amortyzacja"),
    ("roe", "ROE"),
    ("roic", "ROIC"),
    ("dlug_netto_do_ebitda", "Dług netto ÷ EBITDA"),
    ("dlug_netto_z_leasingiem_do_ebitda", "Dług netto z leasingiem ÷ EBITDA"),
    ("pokrycie_odsetek", "Pokrycie odsetek (EBIT ÷ odsetki)"),
    ("zmiana_liczby_akcji", "Zmiana liczby akcji r/r"),
    ("piotroski_f", "Piotroski F-score (0–9)"),
    ("beneish_m", "Beneish M-score (próg −1,78)"),
    ("altman_z2", "Altman Z'' (strefy 1,10 / 2,60)"),
]


def format_(f: Optional[Fakt]) -> str:
    if f is None:
        return "—"
    v = f.wartosc_bazowa()
    if f.jednostka == Jednostka.ulamek:
        s = f"{v * 100:,.1f}%"
    elif f.jednostka in (Jednostka.mnoznik, Jednostka.punkty):
        s = f"{v:,.2f}"
    elif f.jednostka == Jednostka.pieniadz:
        s = f"{v / 1e6:,.0f}"
    else:
        s = f"{v:,.2f}"
    return s.replace(",", " ").replace(".", ",") + ZNAK[f.status]


def obliczenia_md(k: Kalkulator, ttm: Optional[date]) -> str:
    lata = k.okresy_fy()[-5:]
    kolumny = [f.id.split(".", 1)[1] for f in lata]
    if ttm and k.jest(f"przychody.TTM{ttm.isoformat()}") and not any(f.okres.koniec == ttm for f in lata):
        kolumny.append(f"TTM{ttm.isoformat()}")
    waluta = lata[-1].waluta if lata else ""

    def komorka(poz: str, S: str) -> str:
        f = k.fakt(f"{poz}.{S}")
        if f is None and poz.startswith(("dlug_netto_do", "dlug_netto_z")):
            return "—"
        return format_(f)

    linie = [
        f"# Obliczenia: {k.r.ticker}",
        "",
        f"Plik wygenerował silnik ({k.r.data_analizy.isoformat()}). Kwoty w mln {waluta}. "
        "¹ = co najmniej jedno wejście z jednego źródła, ‼ = konflikt w danych wejściowych, — = brak danych.",
        "",
        "| Wskaźnik | " + " | ".join(kolumny) + " |",
        "|---|" + "---:|" * len(kolumny),
    ]
    for poz, nazwa in WIERSZE:
        linie.append(f"| {nazwa} | " + " | ".join(komorka(poz, S) for S in kolumny) + " |")

    # CAGR z ostatniego roku
    ost = kolumny[len(lata) - 1] if lata else None
    if ost:
        linie += ["", f"## Dynamika wieloletnia (do {ost})", ""]
        for poz in ("przychody", "zysk_netto", "eps_rozwodniony", "fcf_wlascicieli"):
            linie.append(f"- CAGR {poz}: 3 lata {format_(k.fakt(f'cagr_{poz}_3l.{ost}'))}, "
                         f"5 lat {format_(k.fakt(f'cagr_{poz}_5l.{ost}'))}")
        m = k.fakt(f"beneish_m.{ost}")
        z = k.fakt(f"altman_z2.{ost}")
        linie += ["", "## Sygnały do sprawdzenia (diagnostyka, nie stop)", ""]
        if m:
            linie.append(f"- Beneish M-score {format_(m)}: " + ("powyżej progu −1,78 — sprawdź jakość zysków (należności, memoriały)."
                                                             if m.wartosc > PROG_M else "poniżej progu."))
        if z:
            strefa = "zagrożenia" if z.wartosc < STREFY_Z[0] else ("szara" if z.wartosc < STREFY_Z[1] else "bezpieczna")
            linie.append(f"- Altman Z'' {format_(z)}: strefa {strefa}.")
    linie += ["", "## Braki danych", ""]
    linie += [f"- {b}" for b in sorted(set(k.braki))] or ["Brak."]
    return "\n".join(linie) + "\n"
