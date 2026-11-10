"""bramki.md i stop.md — generowane przez kod z wyników bramek."""

from __future__ import annotations

from datetime import date

from . import Decyzja

ETYKIETA = {"stop": "STOP", "flaga_powazna": "flaga poważna", "flaga": "flaga", "informacja": "informacja",
            "ok": "ok", "brak_danych": "brak danych"}
NAZWY_ETAPOW = {0: "Identyfikacja i status", 1: "Biegły i regulator", 2: "Kapitał", 3: "Wypłacalność i jakość zysków",
                4: "Ład korporacyjny", 5: "Biznes i przewaga"}


def bramki_md(ticker: str, dzien: date, d: Decyzja, odrzucone: list[str]) -> str:
    linie = [f"# Bramki stopu: {ticker}", "", f"Plik wygenerował silnik ({dzien.isoformat()}). Nie edytuj go ręcznie.", "",
             f"**Decyzja: {d.decyzja}**" + (f" (etap {d.etap}: {NAZWY_ETAPOW.get(d.etap, '')})" if d.etap is not None else "")
             + f" — {d.powod}.", "", "| Etap | Bramka | Wynik | Opis | Dowody | Źródło |", "|---:|---|---|---|---|---|"]
    for w in d.wyniki:
        dowody = "; ".join(w.dowody[:3]) + (" …" if len(w.dowody) > 3 else "")
        linie.append(f"| {w.etap} | {w.id} | {ETYKIETA[w.poziom]} | {w.opis} | {dowody} | {w.zrodlo} |")
    linie += ["", "## Dowody od modelu odrzucone przez silnik", ""]
    linie += [f"- {o}" for o in odrzucone] or ["Brak."]
    return "\n".join(linie) + "\n"


def stop_md(ticker: str, dzien: date, d: Decyzja) -> str:
    s = next(w for w in d.wyniki if w.poziom == "stop")
    testy = s.testy or {}
    def t(k, nazwa):
        return f"- **{nazwa}** {testy.get(k) or 'do uzupełnienia przez model'}"
    return "\n".join([
        f"# STOP: {ticker} — analiza przerwana na etapie {s.etap} ({NAZWY_ETAPOW.get(s.etap, '')})",
        "",
        f"Data: {dzien.isoformat()}. Bramka: `{s.id}`.",
        "",
        "## Powód",
        "",
        s.opis + ".",
        "",
        "Dowód: " + ("; ".join(s.dowody) if s.dowody else "brak (błąd: STOP wymaga dokumentu)") + ".",
        "",
        "## Cztery testy",
        "",
        t("strukturalny", "Czy problem jest strukturalny, a nie przejściowy?"),
        t("uczciwosc_liczb", "Czy problem dotyczy uczciwości liczb?"),
        t("zarzad_rozwiazuje", "Czy zarząd go rozwiązuje?"),
        t("termin", "Czy rozwiązanie ma termin?"),
        "",
        "## Warunek powrotu",
        "",
        (s.warunek_powrotu or "do uzupełnienia przez model") + ".",
        "",
    ])
