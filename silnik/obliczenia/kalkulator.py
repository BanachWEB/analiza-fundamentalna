"""Wspólne narzędzia obliczeń: bezpieczne pobieranie faktów i wyliczanie z zapisem braków."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Callable, Optional

from silnik.fakty.rejestr import RejestrFaktow
from silnik.fakty.schemat import Fakt, Jednostka, Okres, Status


class BrakSensu(ValueError):
    """Wskaźnik nie ma sensu dla tych danych (np. dynamika od ujemnej bazy)."""


def dodatnia_baza(a: float, b: float) -> float:
    if b <= 0:
        raise BrakSensu("ujemna albo zerowa baza, dynamika nie ma sensu")
    return a / b - 1


def cagr(a: float, b: float, lat: int) -> float:
    if a <= 0 or b <= 0:
        raise BrakSensu("wartość ujemna albo zerowa, CAGR nie ma sensu")
    return (a / b) ** (1 / lat) - 1


def podzial_akcji(a: float, b: float) -> bool:
    """True, gdy stosunek liczby akcji wygląda na podział (split) albo scalenie, np. 3:1 albo 1:10."""
    if a <= 0 or b <= 0:
        return False
    for r in (a / b, b / a):
        for n in range(2, 51):
            if abs(r - n) <= 0.06 * n:
                return True
    return False


class Kalkulator:
    def __init__(self, rejestr: RejestrFaktow):
        self.r = rejestr
        self.braki: list[str] = []

    # --- odczyt ---------------------------------------------------------------

    def fakt(self, fid: str) -> Optional[Fakt]:
        if fid not in self.r:
            return None
        f = self.r[fid]
        return None if f.status == Status.odrzucony else f

    def jest(self, fid: str) -> bool:
        return self.fakt(fid) is not None

    def okresy_fy(self, pozycja: str = "przychody") -> list[Fakt]:
        """Fakty roczne danej pozycji, od najstarszego."""
        return sorted(
            [f for f in self.r.fakty() if f.pozycja == pozycja and f.okres.typ.value == "FY" and f.status != Status.odrzucony],
            key=lambda f: f.okres.koniec,
        )

    def stan(self, pozycja: str, dzien: date, tolerancja_dni: int = 5) -> Optional[Fakt]:
        """Fakt stanu na dzień (z tolerancją na lata 52/53-tygodniowe)."""
        f = self.fakt(f"{pozycja}.{dzien.isoformat()}")
        if f:
            return f
        for d in range(1, tolerancja_dni + 1):
            for dz in (dzien - timedelta(days=d), dzien + timedelta(days=d)):
                f = self.fakt(f"{pozycja}.{dz.isoformat()}")
                if f:
                    return f
        return None

    # --- wyliczanie -----------------------------------------------------------

    def wylicz(self, fid: str, pozycja: str, wzor: str, wejscia: list[Optional[str]], fn: Callable[..., float],
               jednostka: Jednostka, okres: Okres, waluta: Optional[str] = None) -> Optional[Fakt]:
        """Wylicza fakt, gdy wszystkie wejścia istnieją; inaczej zapisuje brak i zwraca None."""
        brak = [w for w in wejscia if w is None or not self.jest(w)]
        if brak:
            self.braki.append(f"{fid}: brak {', '.join(str(b) for b in brak)}")
            return None
        try:
            return self.r.wylicz(fid, pozycja, wzor, list(wejscia), fn, jednostka, okres, waluta)
        except ZeroDivisionError:
            self.braki.append(f"{fid}: dzielenie przez zero")
            return None
        except BrakSensu as e:
            self.braki.append(f"{fid}: {e}")
            return None


def okres_fy(f: Fakt) -> Okres:
    return Okres(typ=f.okres.typ, poczatek=f.okres.poczatek, koniec=f.okres.koniec)


def sufiks(f: Fakt) -> str:
    return f.id.split(".", 1)[1]
