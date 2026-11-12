"""obliczenia.md — tabela wskaźników generowana przez kod (bez liczb od modelu)."""

from __future__ import annotations

from datetime import date
from typing import Optional

from silnik.fakty.schemat import Fakt, Jednostka, Status

from .jakosc import PROG_M, PROG_OHLSON, STREFY_Z
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
    ("zmiana_liczby_akcji", "Zmiana liczby akcji r/r (średnia ważona)"),
    ("zmiana_liczby_akcji_koniec", "Zmiana liczby akcji r/r (koniec okresu)"),
    ("piotroski_f", "Piotroski F-score (0–9)"),
    ("beneish_m", "Beneish M-score (próg −1,78)"),
    ("altman_z2", "Altman Z'' (strefy 1,10 / 2,60)"),
    ("ohlson_p", "Prawdopodobieństwo upadłości w ciągu roku (model Ohlsona)"),
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


def _dzien_bilansu(k: Kalkulator, S: str) -> Optional[date]:
    if S.startswith("TTM"):
        return date.fromisoformat(S[3:])
    f = k.fakt(f"przychody.{S}")
    return f.okres.koniec if f else None


def komorka(k: Kalkulator, poz: str, S: str) -> str:
    """Wartość wskaźnika do tabeli. Wskaźniki długu do EBITDA przy ujemnym długu netto opisujemy
    słowami „gotówka netto”, bo liczba ujemna (albo dodatnia przy ujemnej EBITDA) myli."""
    f = k.fakt(f"{poz}.{S}")
    if poz in ("dlug_netto_do_ebitda", "dlug_netto_z_leasingiem_do_ebitda"):
        dzien = _dzien_bilansu(k, S)
        dn = k.stan("dlug_netto", dzien) if dzien else None
        if dn is not None:
            dlug = dn.wartosc_bazowa()
            if poz == "dlug_netto_z_leasingiem_do_ebitda":
                leasing = k.stan("leasing", dzien)
                dlug = dlug + leasing.wartosc_bazowa() if leasing else None
            if dlug is not None and dlug < 0:
                return "gotówka netto" + ZNAK[dn.status]
    return format_(f)


def panel_md(k: Kalkulator, wynik: dict) -> list[str]:
    """Tabela panelu wskaźników: ostatnie 5 lat i TTM."""
    ttm = wynik.get("ttm")
    lata = k.okresy_fy()[-5:]
    kolumny = [f.id.split(".", 1)[1] for f in lata]
    if ttm and k.jest(f"przychody.TTM{ttm.isoformat()}") and not any(f.okres.koniec == ttm for f in lata):
        kolumny.append(f"TTM{ttm.isoformat()}")
    naglowki = [S if not S.startswith("TTM") else f"TTM {S[8:10]}.{S[3:7]}" for S in kolumny]
    linie = ["| Wskaźnik | " + " | ".join(naglowki) + " |", "|---|" + "---:|" * len(kolumny)]
    for poz, nazwa in WIERSZE:
        linie.append(f"| {nazwa} | " + " | ".join(komorka(k, poz, S) for S in kolumny) + " |")
    linie += ["", f"Kwoty w mln {lata[-1].waluta if lata else ''}. ¹ = co najmniej jedno wejście z jednego źródła; "
              "‼ = konflikt źródeł; — = brak danych. TTM = ostatnie 12 miesięcy."]
    return linie


def obliczenia_md(k: Kalkulator, wynik: dict) -> str:
    ttm = wynik.get("ttm")
    lata = k.okresy_fy()[-5:]
    kolumny = [f.id.split(".", 1)[1] for f in lata]
    if ttm and k.jest(f"przychody.TTM{ttm.isoformat()}") and not any(f.okres.koniec == ttm for f in lata):
        kolumny.append(f"TTM{ttm.isoformat()}")
    waluta = lata[-1].waluta if lata else ""

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
        linie.append(f"| {nazwa} | " + " | ".join(komorka(k, poz, S) for S in kolumny) + " |")

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
        op = k.fakt(f"ohlson_p.{ost}")
        if op:
            # decyzja właściciela z 12.11.2026: jedna liczba w procentach, bez wartości O-score i składników
            linie.append(f"- Prawdopodobieństwo upadłości w ciągu roku (model Ohlsona): {format_(op)}"
                         + (" — sprawdź wypłacalność (dźwignia, płynność, przepływy)." if op.wartosc > PROG_OHLSON else "."))
    linie += _wycena_md(k, wynik)
    linie += ["", "## Ostrzeżenia", ""]
    linie += [f"- {o}" for o in dict.fromkeys(k.ostrzezenia)] or ["Brak."]
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


def _uwaga_beta(k: Kalkulator, fid: Optional[str]) -> str:
    f = k.fakt(fid) if fid else None
    if not f:
        return ""
    if f.pozycja != "beta_skorygowana":
        return "beta domyślna: brak bety z regresji"
    reg = k.fakt(f.wejscia[0])
    m = reg.miejsce or {}
    tekst = f"Blume; z regresji {format_(reg)}"
    if m.get("tygodni"):
        liczba = lambda x: f"{x:.2f}".replace(".", ",") if isinstance(x, (int, float)) else "—"
        tekst += (f", {m['tygodni']} tyg. od {m.get('od')}, błąd std. {liczba(m.get('blad_standardowy'))}, "
                  f"R² {liczba(m.get('r2'))}")
    return tekst


def wycena_tabela(k: Kalkulator, wynik: dict) -> list[str]:
    w = wynik.get("wycena") or {}
    if not w.get("kapitalizacja"):
        return ["Brak wyceny: brak kursu albo liczby akcji."]
    cap = k.fakt(w["kapitalizacja"])
    linie = ["| Miara | Wartość | Uwagi |", "|---|---:|---|"]
    kurs = next((x for x in cap.wejscia if x.startswith("kurs.")), None)
    linie.append(_wiersz(k, "Kurs", kurs))
    linie.append(_wiersz(k, "Kapitalizacja", w["kapitalizacja"]))
    linie.append(_wiersz(k, "EV", w.get("ev")))
    linie.append(_wiersz(k, "Beta", w.get("beta"), _uwaga_beta(k, w.get("beta"))))
    linie.append(_wiersz(k, "Koszt kapitału własnego", w.get("ke"), "stopa wolna od ryzyka + beta × premia (Damodaran)"))
    linie.append(_wiersz(k, "C/Z", w.get("c_z")))
    linie.append(_wiersz(k, "EV/EBIT", w.get("ev_ebit")))
    linie.append(_wiersz(k, "EV/EBITDA", w.get("ev_ebitda")))
    linie.append(_wiersz(k, "C/WK", w.get("c_wk")))
    cs = k.fakt(w["c_s_konsensus"]) if w.get("c_s_konsensus") else None
    linie.append(_wiersz(k, "C/S na rok naprzód", w.get("c_s_konsensus"),
                         "informacja; kapitalizacja ÷ konsensus przychodów" +
                         (f" na rok obrotowy do {cs.wejscia[1].split('.', 1)[1]}" if cs else "")))
    linie.append(_wiersz(k, "FCF yield", w.get("fcf_yield"), "FCF dla właścicieli ÷ kapitalizacja"))
    linie.append(_wiersz(k, "Udział PVGO w cenie", w.get("udzial_pvgo"), "część ceny za przyszły wzrost"))
    baza = {"finanse": "zysku netto (bank)", "deweloper": "zysku netto (deweloper)"}.get(wynik.get("sektor"), "FCF")
    linie.append(_wiersz(k, f"Implikowany wzrost {baza} (10 lat)", w.get("implikowany_wzrost_fcf"), "wariant 1"))
    linie.append(_wiersz(k, "Implikowany okres przewagi (CAP)", w.get("implikowany_cap"), "wariant 2, wzrost w tempie historycznym"))
    linie.append(_wiersz(k, "Implikowana marża FCF", w.get("implikowana_marza_fcf"), "wariant 3, wzrost w tempie historycznym"))
    linie.append(_wiersz(k, "Wzrost historyczny (CAGR przychodów)", w.get("wzrost_historyczny")))
    if w.get("metoda") == "cykliczny":
        linie.append(_wiersz(k, "Marża FCF przez cykl", w.get("marza_fcf_cykl"), "spółka cykliczna: Σ FCF ÷ Σ przychody z pełnego cyklu"))
        linie.append(_wiersz(k, "FCF znormalizowany", w.get("fcf_znormalizowany"), "marża FCF przez cykl × przychody z okresu bazowego"))
        linie.append(_wiersz(k, "FCF yield (znormalizowany)", w.get("fcf_yield_znormalizowany")))
        linie.append(_wiersz(k, "Implikowany wzrost FCF znormalizowanego (10 lat)", w.get("implikowany_wzrost_fcf_znormalizowany")))
        linie.append(_wiersz(k, "Implikowany CAP (FCF znormalizowany)", w.get("implikowany_cap_znormalizowany")))
    if w.get("metoda") == "kapitalowa":
        linie.append(_wiersz(k, "ROE średnie", w.get("roe_srednie"), "podstawa uzasadnionego C/WK"))
        linie.append(_wiersz(k, "Uzasadnione C/WK", w.get("cwk_uzasadnione"), "(ROE − g) ÷ (koszt kapitału − g)"))
        linie.append(_wiersz(k, "ROE implikowane przez kurs", w.get("roe_implikowane"), "ROE, przy którym dzisiejsze C/WK jest uzasadnione"))
        if w.get("dlug_netto_do_kapitalu"):
            linie.append(_wiersz(k, "Dług netto ÷ kapitał własny", w.get("dlug_netto_do_kapitalu"), "deweloper"))
    rsi = max((f for f in k.r.fakty() if f.pozycja == "rsi_14" and f.status != Status.odrzucony),
              key=lambda f: f.okres.koniec, default=None)
    linie.append(_wiersz(k, "RSI 14-dniowy", rsi.id if rsi else None, "informacja, nie bramka; umowne progi 70 i 30"))
    return linie


def scenariusze_tabela(k: Kalkulator, wynik: dict) -> list[str]:
    linie = []
    sc = wynik.get("scenariusze")
    if sc:
        linie += ["| Scenariusz | Prawdopodobieństwo | Wartość na akcję | Stopa zwrotu przy obecnym kursie |",
                  "|---|---:|---:|---:|"]
        for f in [x for x in k.r.fakty() if x.pozycja == "wartosc_na_akcje"]:
            nazwa = f.id.split(".", 1)[1]
            p = k.fakt(f"scenariusz_prawdopodobienstwo.{nazwa}")
            st = k.fakt(f"stopa_zwrotu_implikowana.{nazwa}")
            wartosc = f"{f.wartosc:,.2f}".replace(",", " ").replace(".", ",")
            linie.append(f"| {nazwa} | {format_(p)} | {wartosc} {f.waluta} | {format_(st)} |")
        for nazwa, fid in sc.items():
            nazwy = {"wartosc_oczekiwana_na_akcje": "Wartość oczekiwana na akcję", "potencjal_oczekiwany": "Potencjał oczekiwany",
                     "prawdopodobienstwo_straty": "Prawdopodobieństwo straty", "asymetria": "Asymetria (zysk ÷ strata)"}
            linie.append(_wiersz(k, nazwy.get(nazwa, nazwa), fid) + " |")
    return linie or ["Brak scenariuszy (plik scenariusze.json)."]


def karta_tabela(k: Kalkulator, wynik: dict) -> list[str]:
    linie = []
    karta = wynik.get("karta") or []
    if karta:
        ogolny, n = wynik_ogolny(karta)
        linie += [
                  (f"Wynik: **{ogolny:.1f} / 10** z {n} filarów z 5.".replace(".", ",", 1) if ogolny is not None
                   else f"Wynik: nie liczę — dane tylko dla {n} filarów z 5 (minimum 3)."), "",
                  "| Filar | Waga | Punkty | Miary |", "|---|---:|---:|---|"]
        for f in karta:
            miary = "; ".join(f"{m}: " + ("brak" if v is None else f"{v[2]:.1f}".replace(".", ",")) for m, v in f.miary.items())
            pkt = "brak danych" if f.punkty is None else f"{f.punkty:.1f}".replace(".", ",")
            linie.append(f"| {f.nazwa} | {f.waga:.0%} | {pkt} | {miary} |")
        if wynik.get("analitycy") is None or wynik["analitycy"] <= 3:
            linie += ["", "Filar „analitycy”: brak danych albo 3 analityków lub mniej — nie można na nim polegać."]
        sc = wynik.get("scrab")
        if sc:
            liczba = lambda x: f"{x:.0f}"
            linie += ["", f"Porównanie z wynikiem Scrab (skala 0–100): karta {liczba(sc['karta'])}, Scrab {liczba(sc['scrab'])}, "
                      + (f"różnica powyżej progu {liczba(sc['prog'])} pkt — ROZBIEŻNOŚĆ: sprawdź dane po obu stronach."
                         if sc["rozbiezny"] else f"różnica w granicach progu {liczba(sc['prog'])} pkt.")]
    return linie or ["Brak karty (brak wyceny)."]


def _kwota(v: float, waluta: str) -> str:
    return f"{v:,.2f} {waluta}".replace(",", " ").replace(".", ",")


def _komorka(k: Kalkulator, fid: Optional[str]) -> str:
    f = k.fakt(fid) if fid else None
    if f is None:
        return "—"
    if f.jednostka == Jednostka.pieniadz_na_akcje:
        return _kwota(f.wartosc_bazowa(), f.waluta) + ZNAK[f.status]
    if f.jednostka == Jednostka.mnoznik:
        return f"{f.wartosc_bazowa():,.2f}×".replace(",", " ").replace(".", ",") + ZNAK[f.status]
    if f.jednostka == Jednostka.ulamek:
        return f"{f.wartosc_bazowa() * 100:+,.1f}%".replace(",", " ").replace(".", ",") + ZNAK[f.status]
    return format_(f)


def trela_tabela(k: Kalkulator, wynik: dict) -> list[str]:
    """Część 8 raportu: cena docelowa wg arkusza właściciela (metoda Treli). Brak arkusza → pusta lista (pomijamy)."""
    t = wynik.get("trela") or {}
    if not t:
        return []
    kurs = max((f for f in k.r.fakty() if f.pozycja == "kurs" and f.status != Status.odrzucony),
               key=lambda f: f.okres.koniec, default=None)
    return [
        f"Wycena właściciela z arkusza „Cena docelowa” (metoda Tomasza Treli, dane ze Scrab; {t['dokument']}, "
        f"ticker w arkuszu: {t['ticker']}). Silnik przepisuje wyniki arkusza i niczego nie przelicza.", "",
        "| Dane wejściowe z arkusza | P/E 1-Year Forward | P/S 1-Year Forward |", "|---|---:|---:|",
        f"| Prognoza na akcję na 12 miesięcy | EPS {_komorka(k, t.get('eps_prognoza_arkusz'))} | "
        f"sprzedaż {_komorka(k, t.get('sprzedaz_na_akcje_prognoza_arkusz'))} |",
        f"| Mediana mnożnika (wariant konserwatywny) | {_komorka(k, t.get('pe_forward_mediana_arkusz'))} | "
        f"{_komorka(k, t.get('ps_forward_mediana_arkusz'))} |",
        f"| Maksimum mnożnika (wariant optymistyczny) | {_komorka(k, t.get('pe_forward_maksimum_arkusz'))} | "
        f"{_komorka(k, t.get('ps_forward_maksimum_arkusz'))} |",
        "",
        "| Cena docelowa na 12 miesięcy | Konserwatywna | Optymistyczna | Potencjał kons. | Potencjał optym. |",
        "|---|---:|---:|---:|---:|",
        *[f"| {nazwa} | {_komorka(k, t.get(p + 'kons'))} | {_komorka(k, t.get(p + 'optym'))} | "
          f"{_komorka(k, t.get(p + 'potencjal_kons'))} | {_komorka(k, t.get(p + 'potencjal_optym'))} |"
          for nazwa, p in (("Z P/E (mediana albo maksimum P/E × prognoza EPS)", "pe_"),
                           ("Z P/S (mediana albo maksimum P/S × prognoza sprzedaży na akcję)", "ps_"),
                           ("**Cena docelowa** (średnia z P/E i P/S)", ""))],
        "",
        f"Potencjał liczy arkusz od kursu z arkusza: {_komorka(k, t.get('kurs_arkusz'))}. "
        + (f"Kurs pobrany przez silnik z {kurs.okres.koniec.strftime('%d.%m.%Y')}: {_komorka(k, kurs.id)}." if kurs else ""),
        "",
        "Założenia arkusza (ustawia je właściciel):", "",
        "- Wariant konserwatywny: mnożnik wraca do mediany historycznego P/E i P/S 1-Year Forward.",
        "- Wariant optymistyczny: mnożnik wraca do maksimum z historii, czyli do poziomu z „dobrych czasów” spółki.",
        "- Konsensus EPS i konsensus sprzedaży na akcję na kolejne 12 miesięcy się sprawdzą.",
        "- Horyzont wynosi 12 miesięcy: za rok dzisiejsza prognoza stanie się wynikiem raportowanym.",
        "- Cena docelowa to średnia z metody P/E i metody P/S; przy EPS = 0 liczy się tylko metoda P/S.",
        "- Dane pochodzą z jednego źródła (¹): ze Scrab, przez arkusz właściciela, a nie ze sprawozdań spółki.",
        "",
        "To wycena przy założeniach właściciela, a nie prognoza kursu ani rekomendacja.",
    ]


def _wycena_md(k: Kalkulator, wynik: dict) -> list[str]:
    w = wynik.get("wycena") or {}
    naglowek = "## Co jest w cenie"
    if w.get("kapitalizacja"):
        cap = k.fakt(w["kapitalizacja"])
        naglowek += f" (kurs z {cap.okres.koniec.isoformat()}, przepływy: {w.get('okres_bazowy')})"
    return (["", naglowek, ""] + wycena_tabela(k, wynik) + ["", "## Scenariusze", ""] + scenariusze_tabela(k, wynik)
            + (["", "## Cena docelowa wg arkusza właściciela", ""] + trela_tabela(k, wynik) if wynik.get("trela") else [])
            + ["", "## Karta w stylu Treli (informacja, nie bramka)", ""] + karta_tabela(k, wynik))
