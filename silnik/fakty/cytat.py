"""Test cytatu: liczby, które model odczytał z PDF albo z tekstu, przechodzą tylko z dowodem.

Model składa propozycje faktów (plik JSON) z dosłownym cytatem i numerem strony.
Silnik sprawdza dwie rzeczy:
1. cytat występuje w tekście wskazanej strony dokumentu z archiwum
   (po ujednoliceniu odstępów);
2. wartość faktu występuje w cytacie jako liczba (w zapisie polskim albo
   angielskim, z minusem albo w nawiasie dla wartości ujemnych).
Propozycja, która nie przejdzie testu, trafia do rejestru ze statusem
„odrzucony” i z powodem w kontrolach, żeby było widać, co model próbował wpisać.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

from .rejestr import RejestrFaktow
from .schemat import Fakt, Metoda, Rodzaj, Status

_ODSTEPY = re.compile(r"[\s   ]+")
_KROPKI = re.compile(r"\.{3,}|…+")


def ujednolic(tekst: str) -> str:
    t = _KROPKI.sub(" ", tekst)
    t = t.replace("−", "-").replace("–", "-")
    return _ODSTEPY.sub(" ", t).strip()


_LICZBA_SLOWO = re.compile(r"^\(?-?[\d.,]+\)?$")
ODSTEP_W_LICZBIE_PT = 6.0  # grupy cyfr jednej liczby dzieli ok. 2 pt, kolumny — kilkanaście pt


@lru_cache(maxsize=32)
def _wiersze_pdf(sciezka: str) -> tuple[tuple[tuple[str, tuple[float, ...]], ...], ...]:
    """Dla każdej strony: wiersze jako (tekst wiersza, liczby z kolumn).

    Liczby składamy ze słów na podstawie odstępów w PDF, więc „27 679 127 24 738 104”
    to dwie liczby, a nie jedna albo sześć.
    """
    import pdfplumber

    strony = []
    with pdfplumber.open(sciezka) as pdf:
        for p in pdf.pages:
            slowa = sorted(p.extract_words(x_tolerance=1.5, keep_blank_chars=False), key=lambda w: (round(w["top"]), w["x0"]))
            wiersze: list[list[dict]] = []
            for w in slowa:
                if wiersze and abs(wiersze[-1][0]["top"] - w["top"]) < 2.5:
                    wiersze[-1].append(w)
                else:
                    wiersze.append([w])
            wynik = []
            for wiersz in wiersze:
                wiersz.sort(key=lambda w: w["x0"])
                tekst = " ".join(w["text"] for w in wiersz)
                liczby, biezaca, koniec = [], [], None
                for w in wiersz:
                    if _LICZBA_SLOWO.match(w["text"]) and any(ch.isdigit() for ch in w["text"]):
                        if biezaca and koniec is not None and w["x0"] - koniec < ODSTEP_W_LICZBIE_PT:
                            biezaca.append(w["text"])
                        else:
                            if biezaca:
                                liczby.append("".join(biezaca))
                            biezaca = [w["text"]]
                        koniec = w["x1"]
                    else:
                        if biezaca:
                            liczby.append("".join(biezaca))
                        biezaca, koniec = [], None
                if biezaca:
                    liczby.append("".join(biezaca))
                wynik.append((tekst, tuple(v for v in (_na_liczbe(x) for x in liczby) if v is not None)))
            strony.append(tuple(wynik))
    return tuple(strony)


def _na_liczbe(tekst: str) -> float | None:
    ujemna = tekst.startswith("(") and tekst.endswith(")") or tekst.startswith("-")
    t = tekst.strip("()-")
    if "," in t and "." not in t:
        t = t.replace(",", ".") if re.fullmatch(r"\d+,\d{1,4}", t) else t.replace(",", "")
    else:
        t = t.replace(",", "")
    try:
        v = float(t)
    except ValueError:
        return None
    return -v if ujemna else v


@lru_cache(maxsize=32)
def _strony_pdf(sciezka: str) -> tuple[str, ...]:
    import pdfplumber

    with pdfplumber.open(sciezka) as pdf:
        return tuple((p.extract_text() or "") for p in pdf.pages)


def tekst_dokumentu(sciezka: Path, strona: int | None) -> str:
    if sciezka.suffix.lower() == ".pdf":
        strony = _strony_pdf(str(sciezka))
        if strona is None:
            return "\n".join(strony)
        if not 1 <= strona <= len(strony):
            raise ValueError(f"strona {strona} poza zakresem 1–{len(strony)}")
        return strony[strona - 1]
    tresc = sciezka.read_text(encoding="utf-8", errors="replace")
    if sciezka.suffix.lower() in (".htm", ".html", ".xhtml"):
        return _tekst_html(tresc)
    return tresc


@lru_cache(maxsize=16)
def _tekst_html(tresc: str) -> str:
    """Tekst strony HTML (bez znaczników, skryptów i stylów), wiersz na blok — tego używa test cytatu."""
    from lxml import html as lhtml

    drzewo = lhtml.fromstring(tresc)
    for el in drzewo.xpath("//script|//style|//noscript"):
        el.drop_tree()
    for el in drzewo.xpath("//br|//p|//div|//tr|//li|//h1|//h2|//h3|//h4|//td"):
        el.tail = ("\n" + el.tail) if el.tail else "\n"
    return "\n".join(l.strip() for l in drzewo.text_content().splitlines() if l.strip())


def zapisy_liczby(wartosc: float) -> list[str]:
    """Możliwe zapisy liczby w raportach: 1 234 567 / 1234567 / 1,234,567 / 1 234,5 / (1 234) / -1 234."""
    ujemna = wartosc < 0
    a = abs(wartosc)
    calkowita = abs(a - round(a)) < 1e-9
    if calkowita:
        n = int(round(a))
        podstawy = {f"{n:,}".replace(",", " "), str(n), f"{n:,}"}
        for zera in ("0", "00"):  # „5.0 billion”, „1 234,00”
            podstawy |= {f"{n}.{zera}", f"{n},{zera}", f"{n:,}.{zera}", f"{n:,}".replace(",", " ") + f",{zera}"}
    else:
        podstawy = set()
        for miejsca in (1, 2, 3, 4):
            if abs(round(a, miejsca) - a) < 1e-9:
                s = f"{a:,.{miejsca}f}"
                podstawy |= {s.replace(",", " ").replace(".", ","), s.replace(",", ""), s,
                             s.replace(",", "").replace(".", ",")}
                break
    if not ujemna:
        return sorted(podstawy, key=len, reverse=True)
    wynik = set()
    for p in podstawy:
        wynik |= {f"({p})", f"-{p}", f"- {p}"}
    return sorted(wynik, key=len, reverse=True)


def liczba_w_cytacie(wartosc: float, cytat: str) -> bool:
    c = ujednolic(cytat)
    for zapis in zapisy_liczby(wartosc):
        for m in re.finditer(re.escape(zapis), c):
            przed = c[m.start() - 1] if m.start() > 0 else " "
            po = c[m.end()] if m.end() < len(c) else " "
            # liczba nie może być fragmentem dłuższej liczby
            if przed.isdigit() or po.isdigit() or (po in ",." and m.end() + 1 < len(c) and c[m.end() + 1].isdigit()):
                continue
            if wartosc >= 0 and przed in "-(":
                continue
            return True
    return False


def sprawdz(sciezka: Path, strona: int | None, cytat: str, wartosc: float, procent: bool = False) -> tuple[bool, str]:
    """procent=True: wartość jest ułamkiem (0,41), a dokument może pisać „41%”."""
    try:
        tekst = tekst_dokumentu(sciezka, strona)
    except ValueError as e:
        return False, str(e)
    if ujednolic(cytat) not in ujednolic(tekst):
        return False, "cytatu nie ma na wskazanej stronie"
    kandydaci = [wartosc] + ([round(wartosc * 100, 6)] if procent else [])
    if not any(liczba_w_cytacie(v, cytat) for v in kandydaci):
        return False, "wartości nie ma w cytacie"
    if sciezka.suffix.lower() == ".pdf" and strona is not None:
        # W PDF sprawdzamy całe liczby z kolumn wierszy, które tworzą cytat.
        c = ujednolic(cytat)
        liczby = [v for t, vs in _wiersze_pdf(str(sciezka))[strona - 1] if ujednolic(t) and ujednolic(t) in c for v in vs]
        if liczby and not any(abs(v - w) < 1e-6 for v in liczby for w in kandydaci):
            return False, "wartość jest tylko fragmentem liczby z kolumny"
    return True, "ok"


def dodaj_propozycje(rejestr: RejestrFaktow, sciezka_dokumentu, propozycje: list[dict]) -> list[Fakt]:
    """Dodaje propozycje modelu po teście cytatu.

    `sciezka_dokumentu`: funkcja id dokumentu → ścieżka pliku w archiwum.
    """
    dodane = []
    for p in propozycje:
        dane = dict(p)
        dane.setdefault("rodzaj", Rodzaj.raportowany.value)
        dane.setdefault("metoda", Metoda.tabela_pdf.value)
        dane["status"] = Status.jedno_zrodlo.value
        strona = (dane.get("miejsce") or {}).get("strona")
        ok, powod = sprawdz(Path(sciezka_dokumentu(dane["dokument"])), strona, dane.get("cytat") or "", dane["wartosc"],
                            procent=dane.get("jednostka") == "ulamek")
        dane["kontrole"] = list(dane.get("kontrole", [])) + [f"test_cytatu:{'ok' if ok else 'blad'}:{powod}"]
        if not ok:
            dane["status"] = Status.odrzucony.value
        fakt = Fakt(**dane)
        dodane.append(rejestr.dodaj(fakt, zastap=fakt.id in rejestr))
    return dodane


def wczytaj_propozycje(plik: Path) -> list[dict]:
    dane = json.loads(Path(plik).read_text(encoding="utf-8"))
    return dane["fakty"] if isinstance(dane, dict) else dane
