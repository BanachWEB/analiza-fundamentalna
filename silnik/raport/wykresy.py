"""Wykresy do raportu z faktów rejestru (matplotlib, PNG).

Zasady (wytyczne dataviz): jedna oś Y, cienkie znaczniki, stała kolejność kolorów
(niebieski, pomarańczowy, morski), legenda przy co najmniej 2 seriach i etykiety na końcach linii,
stonowana siatka. Tekst w kolorze tekstu, nie serii. Każdy wykres ma obok tabelę z liczbami
(panel w raporcie), bo kolor morski ma kontrast poniżej 3:1.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402

from silnik.obliczenia.kalkulator import Kalkulator  # noqa: E402

SERIA = ["#2a78d6", "#eb6834", "#1baf7a"]
TEKST, TEKST2, SIATKA, TLO = "#0b0b0b", "#52514e", "#e4e3df", "#ffffff"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": SIATKA, "axes.labelcolor": TEKST2,
    "xtick.color": TEKST2, "ytick.color": TEKST2, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": SIATKA, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "figure.facecolor": TLO, "axes.facecolor": TLO, "legend.frameon": False,
})


def _seria(k: Kalkulator, pozycja: str, lat: int = 10) -> list[tuple[str, float, str]]:
    fy = k.okresy_fy(pozycja)[-lat:]
    return [(f.id.split(".", 1)[1].replace("FY", ""), f.wartosc_bazowa(), f.status.value) for f in fy]


def _skala(wartosci: list[float]) -> tuple[float, str]:
    m = max((abs(v) for v in wartosci), default=1)
    return (1e9, "mld") if m >= 1e9 else (1e6, "mln") if m >= 1e6 else (1e3, "tys.")


def _zapisz(fig, sciezka: Path) -> Path:
    fig.tight_layout()
    fig.savefig(sciezka, dpi=200)
    plt.close(fig)
    return sciezka


def slupki(k: Kalkulator, pozycja: str, tytul: str, katalog: Path, waluta: str) -> Optional[Path]:
    s = _seria(k, pozycja)
    if len(s) < 2:
        return None
    dziel, jedn = _skala([v for _, v, _ in s])
    fig, ax = plt.subplots(figsize=(6.4, 2.6))
    ax.bar([e for e, _, _ in s], [v / dziel for _, v, _ in s], color=SERIA[0], width=0.6)
    ax.set_title(f"{tytul} ({jedn} {waluta})", loc="left", color=TEKST, fontsize=10)
    ax.grid(axis="x", visible=False)
    ost = s[-1]
    ax.annotate(f"{ost[1] / dziel:,.1f}".replace(",", " ").replace(".", ","), (len(s) - 1, ost[1] / dziel),
                ha="center", va="bottom", fontsize=8, color=TEKST, xytext=(0, 2), textcoords="offset points")
    return _zapisz(fig, katalog / f"wykres_{pozycja}.png")


def linie_procent(k: Kalkulator, pozycje: list[tuple[str, str]], tytul: str, katalog: Path, nazwa: str) -> Optional[Path]:
    serie = [(etyk, _seria(k, poz)) for poz, etyk in pozycje]
    serie = [(e, s) for e, s in serie if len(s) >= 2][:3]
    if not serie:
        return None
    fig, ax = plt.subplots(figsize=(6.4, 2.8))
    for i, (etyk, s) in enumerate(serie):
        x, y = [e for e, _, _ in s], [v * 100 for _, v, _ in s]
        ax.plot(x, y, color=SERIA[i], linewidth=2, marker="o", markersize=3.5, label=etyk)
        ax.annotate(f"{etyk} {y[-1]:.1f}%".replace(".", ","), (len(x) - 1, y[-1]), xytext=(4, 0),
                    textcoords="offset points", fontsize=7.5, color=TEKST, va="center")
    ax.set_title(f"{tytul} (%)", loc="left", color=TEKST, fontsize=10)
    ax.axhline(0, color=TEKST2, linewidth=0.6)
    if len(serie) >= 2:  # legenda pod osią, żeby nie zasłaniała linii
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), fontsize=7.5, ncol=len(serie))
    ax.margins(x=0.12)
    return _zapisz(fig, katalog / f"wykres_{nazwa}.png")


def slupki_pary(k: Kalkulator, pozycje: list[tuple[str, str]], tytul: str, katalog: Path, nazwa: str,
                waluta: str) -> Optional[Path]:
    a, b = (_seria(k, p) for p, _ in pozycje)
    lata = [e for e, _, _ in a if e in {x for x, _, _ in b}]
    if len(lata) < 2:
        return None
    da, db = dict((e, v) for e, v, _ in a), dict((e, v) for e, v, _ in b)
    dziel, jedn = _skala(list(da.values()) + list(db.values()))
    fig, ax = plt.subplots(figsize=(6.4, 2.7))
    x = range(len(lata))
    w = 0.38
    ax.bar([i - w / 2 - 0.01 for i in x], [da[e] / dziel for e in lata], width=w, color=SERIA[0], label=pozycje[0][1])
    ax.bar([i + w / 2 + 0.01 for i in x], [db[e] / dziel for e in lata], width=w, color=SERIA[1], label=pozycje[1][1])
    ax.set_xticks(list(x), lata)
    ax.axhline(0, color=TEKST2, linewidth=0.6)
    ax.grid(axis="x", visible=False)
    ax.set_title(f"{tytul} ({jedn} {waluta})", loc="left", color=TEKST, fontsize=10)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), fontsize=7.5, ncol=2)
    return _zapisz(fig, katalog / f"wykres_{nazwa}.png")


def wszystkie(k: Kalkulator, katalog: Path) -> dict[str, Path]:
    fy = k.okresy_fy()
    waluta = fy[-1].waluta if fy else ""
    wynik = {}
    for nazwa, fn in (
        ("przychody", lambda: slupki(k, "przychody", "Przychody", katalog, waluta)),
        ("marze", lambda: linie_procent(k, [("marza_brutto", "brutto"), ("marza_operacyjna", "operacyjna"),
                                            ("marza_fcf", "FCF")], "Marże", katalog, "marze")),
        ("fcf_zysk", lambda: slupki_pary(k, [("zysk_netto", "zysk netto"), ("fcf_wlascicieli", "FCF dla właścicieli")],
                                         "Zysk netto a FCF dla właścicieli", katalog, "fcf_zysk", waluta)),
        ("roic", lambda: linie_procent(k, [("roic", "ROIC"), ("roe", "ROE")], "Rentowność kapitału", katalog, "roic")),
    ):
        p = fn()
        if p:
            wynik[nazwa] = p
    return wynik
