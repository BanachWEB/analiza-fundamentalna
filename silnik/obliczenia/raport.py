"""obliczenia.md — tabela wskaźników generowana przez kod (bez liczb od modelu)."""

from __future__ import annotations

from datetime import date
from typing import Optional

from silnik.fakty.schemat import Fakt, Jednostka, Status

from .jakosc import PROG_M, STREFY_Z
from .kalkulator import Kalkulator
from .karta_treli import wynik_ogolny

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
    elif f.jednostka == Jednostka.lata:
        s = f"{v:,.1f} lat"
    else:
        s = f"{v:,.2f}"
    return s.replace(",", " ").replace(".", ",") + ZNAK[f.status]


def obliczenia_md(k: Kalkulator, wynik: dict) -> str:
    ttm = wynik.get("ttm")
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
    linie += _wycena_md(k, wynik)
    linie += ["", "## Braki danych", ""]
    linie += [f"- {b}" for b in sorted(set(k.braki))] or ["Brak."]
    return "\n".join(linie) + "\n"


def _wiersz(k: Kalkulator, nazwa: str, fid: Optional[str], uwaga: str = "") -> str:
    f = k.fakt(fid) if fid else None
    if f is None:
        return f"| {nazwa} | — | {uwaga} |"
    v = f.wartosc_bazowa()
    if f.jednostka == Jednostka.pieniadz_na_akcje:
        tekst = f"{v:,.2f} {f.waluta}".replace(",", " ").replace(".", ",") + ZNAK[f.status]
    elif f.jednostka == Jednostka.pieniadz:
        tekst = f"{v / 1e6:,.0f} mln {f.waluta}".replace(",", " ") + ZNAK[f.status]
    else:
        tekst = format_(f)
    return f"| {nazwa} | {tekst} | {uwaga} |"


def _wycena_md(k: Kalkulator, wynik: dict) -> list[str]:
    w = wynik.get("wycena") or {}
    if not w.get("kapitalizacja"):
        return ["", "## Wycena", "", "Brak wyceny: brak kursu albo liczby akcji (szczegóły w brakach)."]
    cap = k.fakt(w["kapitalizacja"])
    linie = ["", f"## Co jest w cenie (kurs z {cap.okres.koniec.isoformat()}, przepływy: {w.get('okres_bazowy')})", "",
             "| Miara | Wartość | Uwagi |", "|---|---:|---|"]
    kurs = next((x for x in cap.wejscia if x.startswith("kurs.")), None)
    linie.append(_wiersz(k, "Kurs", kurs))
    linie.append(_wiersz(k, "Kapitalizacja", w["kapitalizacja"]))
    linie.append(_wiersz(k, "EV", w.get("ev")))
    linie.append(_wiersz(k, "Koszt kapitału własnego", w.get("ke"), "stopa wolna od ryzyka + beta × premia (Damodaran)"))
    linie.append(_wiersz(k, "C/Z", w.get("c_z")))
    linie.append(_wiersz(k, "EV/EBIT", w.get("ev_ebit")))
    linie.append(_wiersz(k, "EV/EBITDA", w.get("ev_ebitda")))
    linie.append(_wiersz(k, "C/WK", w.get("c_wk")))
    linie.append(_wiersz(k, "FCF yield", w.get("fcf_yield"), "FCF dla właścicieli ÷ kapitalizacja"))
    linie.append(_wiersz(k, "Udział PVGO w cenie", w.get("udzial_pvgo"), "część ceny za przyszły wzrost"))
    linie.append(_wiersz(k, "Implikowany wzrost FCF (10 lat)", w.get("implikowany_wzrost_fcf"), "wariant 1"))
    linie.append(_wiersz(k, "Implikowany okres przewagi (CAP)", w.get("implikowany_cap"), "wariant 2, wzrost w tempie historycznym"))
    linie.append(_wiersz(k, "Implikowana marża FCF", w.get("implikowana_marza_fcf"), "wariant 3, wzrost w tempie historycznym"))
    linie.append(_wiersz(k, "Wzrost historyczny (CAGR przychodów)", w.get("wzrost_historyczny")))
    sc = wynik.get("scenariusze")
    if sc:
        linie += ["", "## Scenariusze", "", "| Scenariusz | Prawdopodobieństwo | Wartość na akcję |", "|---|---:|---:|"]
        for f in [x for x in k.r.fakty() if x.pozycja == "wartosc_na_akcje"]:
            nazwa = f.id.split(".", 1)[1]
            p = k.fakt(f"scenariusz_prawdopodobienstwo.{nazwa}")
            linie.append(f"| {nazwa} | {format_(p)} | {f.wartosc:,.2f} {f.waluta} |".replace(",", " ", 1))
        for nazwa, fid in sc.items():
            linie.append(_wiersz(k, nazwa.replace("_", " "), fid).replace("| ", "| **", 1).replace(" |", "** |", 1))
    karta = wynik.get("karta") or []
    if karta:
        ogolny, n = wynik_ogolny(karta)
        linie += ["", "## Karta w stylu Treli (informacja, nie bramka)", "",
                  (f"Wynik: **{ogolny:.1f} / 10** z {n} filarów z 5.".replace(".", ",", 1) if ogolny is not None
                   else "Wynik: brak danych."), "",
                  "| Filar | Waga | Punkty | Miary |", "|---|---:|---:|---|"]
        for f in karta:
            miary = "; ".join(f"{m}: " + ("brak" if v is None else f"{v[2]:.1f}".replace(".", ",")) for m, v in f.miary.items())
            pkt = "brak danych" if f.punkty is None else f"{f.punkty:.1f}".replace(".", ",")
            linie.append(f"| {f.nazwa} | {f.waga:.0%} | {pkt} | {miary} |")
        if wynik.get("analitycy") is None or wynik["analitycy"] < 3:
            linie += ["", "Filar „analitycy”: brak danych albo pokrycie poniżej 3 analityków — nie można na nim polegać."]
    return linie
