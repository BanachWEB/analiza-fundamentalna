"""Cena docelowa wg arkusza właściciela (arkusz Tomasza Treli „Cena-docelowa.xlsx”; specyfikacja.md, punkt 7.1).

Silnik niczego tu nie liczy. Odczytuje wartości, które policzył arkusz właściciela (zakładka „Cena docelowa”),
i dodaje je do rejestru jako fakty z dokumentu `wklejka` (źródło: „arkusz właściciela”), z adresem komórki.
Wycena jest wyceną właściciela według jego założeń; raport podaje ją jako „wg twojego arkusza”.

Plik jest opcjonalny. Skill kopiuje plik dołączony przez właściciela do `D/cena-docelowa.xlsx`.
Brak pliku → silnik pomija tę część (pusty wynik, bez wpisu w brakach danych).
Ticker w arkuszu musi zgadzać się z analizowaną spółką; inaczej silnik nie wstawia żadnej liczby.

Komórki silnik znajduje po etykietach (nie po adresach), więc przesunięcie wierszy w arkuszu nie psuje odczytu:
- dane wejściowe: pierwsza niepusta komórka na prawo od etykiety;
- wiersze wyników: cztery komórki na prawo (konserwatywna, optymistyczna, potencjał kons., potencjał optym.).
Arkusz musi mieć zapisane wartości formuł (plik zapisany w Excelu albo Arkuszach Google).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Optional

from silnik.fakty.schemat import Fakt, Jednostka, Metoda, Okres, Rodzaj, Status, TypDokumentu

from .kalkulator import Kalkulator

PLIK = "cena-docelowa.xlsx"
ZAKLADKA = "Cena docelowa"
ZRODLO = "arkusz właściciela (metoda Treli)"
X, U, PA = Jednostka.mnoznik, Jednostka.ulamek, Jednostka.pieniadz_na_akcje

# etykieta (początek tekstu komórki, małe litery) → (pozycja, jednostka)
WEJSCIA = {
    "aktualny kurs akcji": ("kurs_arkusz", PA),
    "prognoza zysku na akcję": ("eps_prognoza_arkusz", PA),
    "prognoza sprzedaży na akcję": ("sprzedaz_na_akcje_prognoza_arkusz", PA),
    "mediana p/e": ("pe_forward_mediana_arkusz", X),
    "maksimum historycznego p/e": ("pe_forward_maksimum_arkusz", X),
    "mediana p/s": ("ps_forward_mediana_arkusz", X),
    "maksimum historycznego p/s": ("ps_forward_maksimum_arkusz", X),
}
# etykieta wiersza wyników → przedrostek pozycji
WYNIKI = {
    "cena docelowa z p/e": "pe",
    "cena docelowa z p/s": "ps",
    "cena docelowa na 12": "srednia",
}
ETYKIETA_TICKERA = "spółka (ticker)"


def _tekst(v: Any) -> str:
    return re.sub(r"\s+", " ", str(v)).strip().lower() if v is not None else ""


def _liczba(v: Any) -> Optional[float]:
    if isinstance(v, bool) or v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    return None


def normalny_ticker(t: str) -> str:
    """NVDA, NVDA.US, XTB.WA, XTB.PL → NVDA, NVDA, XTB, XTB."""
    t = str(t or "").strip().upper()
    return re.sub(r"\.(US|WA|PL)$", "", t)


class Arkusz:
    """Odczyt zakładki „Cena docelowa”: komórka z etykietą → komórki na prawo."""

    def __init__(self, sciezka: Path):
        import openpyxl

        wb = openpyxl.load_workbook(sciezka, data_only=True, read_only=False)
        if ZAKLADKA not in wb.sheetnames:
            raise ValueError(f"brak zakładki „{ZAKLADKA}”")
        self.ws = wb[ZAKLADKA]

    def _znajdz(self, etykieta: str):
        for wiersz in self.ws.iter_rows():
            for c in wiersz:
                if isinstance(c.value, str) and _tekst(c.value).startswith(etykieta):
                    return c
        return None

    def wartosc(self, etykieta: str):
        """(wartość, adres komórki) z pierwszej niepustej komórki na prawo od etykiety."""
        c = self._znajdz(etykieta)
        if c is None:
            return None, None
        for kol in range(c.column + 1, c.column + 6):
            k = self.ws.cell(row=c.row, column=kol)
            if k.value not in (None, ""):
                return k.value, k.coordinate
        return None, None

    def wiersz(self, etykieta: str, n: int = 4):
        """n komórek na prawo od etykiety: [(wartość, adres), …]."""
        c = self._znajdz(etykieta)
        if c is None:
            return []
        return [(self.ws.cell(row=c.row, column=kol).value, self.ws.cell(row=c.row, column=kol).coordinate)
                for kol in range(c.column + 1, c.column + 1 + n)]


def _waluta(k: Kalkulator, rynek: str) -> str:
    kursy = [f for f in k.r.fakty() if f.pozycja == "kurs" and f.status != Status.odrzucony and f.waluta]
    if kursy:
        return max(kursy, key=lambda f: f.okres.koniec).waluta
    return "PLN" if rynek == "GPW" else "USD"


def oblicz(k: Kalkulator, katalog: Optional[Path], rynek: str = "USA") -> dict:
    """Zwraca słownik id faktów odczytanych z arkusza; pusty, gdy pliku brak albo ticker się nie zgadza."""
    if not katalog or not (katalog / PLIK).exists():
        return {}
    from silnik.pobieranie.archiwum import Archiwum

    sciezka = katalog / PLIK
    try:
        ark = Arkusz(sciezka)
    except Exception as e:  # uszkodzony plik albo inny arkusz: pomijamy z wpisem w brakach
        k.braki.append(f"cena docelowa wg arkusza właściciela: nie odczytam {PLIK} ({e})")
        return {}
    ticker, _ = ark.wartosc(ETYKIETA_TICKERA)
    if normalny_ticker(ticker) != normalny_ticker(k.r.ticker):
        k.braki.append(f"cena docelowa wg arkusza właściciela: arkusz dotyczy {ticker!r}, a analiza {k.r.ticker}; pomijam")
        return {}
    dok = Archiwum(k.r.ticker, katalog).dodaj_plik(sciezka, TypDokumentu.wklejka, ZRODLO,
                                                   opis=f"{PLIK}: cena docelowa wg arkusza właściciela")
    k.r.znane_dokumenty([dok.id])
    D = k.r.data_analizy
    waluta = _waluta(k, rynek)
    w: dict = {"dokument": dok.id, "data": D, "waluta": waluta, "ticker": str(ticker)}

    def dodaj(pozycja: str, wartosc: Any, adres: Optional[str], jednostka: Jednostka, etykieta: str) -> Optional[str]:
        v = _liczba(wartosc)
        if v is None:
            k.braki.append(f"cena docelowa wg arkusza właściciela: brak liczby przy „{etykieta}”"
                           + (f" ({adres})" if adres else ""))
            return None
        fid = f"{pozycja}.{D.isoformat()}"
        k.r.dodaj(Fakt(id=fid, rodzaj=Rodzaj.raportowany, pozycja=pozycja, okres=Okres(typ="dzien", koniec=D),
                       wartosc=v, jednostka=jednostka, waluta=waluta if jednostka == PA else None,
                       metoda=Metoda.wklejka, status=Status.jedno_zrodlo, dokument=dok.id,
                       miejsce={"zakladka": ZAKLADKA, "komorka": adres, "etykieta": etykieta}), zastap=True)
        return fid

    for etykieta, (pozycja, jednostka) in WEJSCIA.items():
        wartosc, adres = ark.wartosc(etykieta)
        w[pozycja] = dodaj(pozycja, wartosc, adres, jednostka, etykieta)
    for etykieta, przedrostek in WYNIKI.items():
        komorki = ark.wiersz(etykieta)
        if len(komorki) < 4:
            k.braki.append(f"cena docelowa wg arkusza właściciela: brak wiersza „{etykieta}”")
            continue
        nazwy = [("cena_docelowa_trela", "kons", PA), ("cena_docelowa_trela", "optym", PA),
                 ("potencjal_trela", "kons", U), ("potencjal_trela", "optym", U)]
        for (rdzen, wariant, jednostka), (wartosc, adres) in zip(nazwy, komorki):
            sredni = przedrostek == "srednia"
            pozycja = f"{rdzen}_{wariant}" if sredni else f"{rdzen}_{przedrostek}_{wariant}"
            klucz = f"{'' if sredni else przedrostek + '_'}{'potencjal_' if rdzen == 'potencjal_trela' else ''}{wariant}"
            w[klucz] = dodaj(pozycja, wartosc, adres, jednostka, etykieta)
    return w
