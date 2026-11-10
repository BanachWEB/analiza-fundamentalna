"""Rejestr faktów: jedyne miejsce, z którego raport bierze liczby."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Callable, Iterable, Optional

from .schemat import (
    SILA_STATUSU,
    Fakt,
    Jednostka,
    Metoda,
    Okres,
    RejestrFaktowPlik,
    Rodzaj,
    Skala,
    Status,
)


class BladRejestru(Exception):
    pass


class RejestrFaktow:
    def __init__(self, ticker: str, data_analizy: date, dokumenty: Optional[Iterable[str]] = None):
        self.ticker = ticker
        self.data_analizy = data_analizy
        self._fakty: dict[str, Fakt] = {}
        # gdy podano listę id dokumentów, rejestr pilnuje, żeby fakty wskazywały istniejące dokumenty
        self._dokumenty = set(dokumenty) if dokumenty is not None else None

    # --- dodawanie -------------------------------------------------------

    def znane_dokumenty(self, ids: Iterable[str]) -> None:
        """Dopisuje id dokumentów, które pojawiły się w archiwum po utworzeniu rejestru."""
        if self._dokumenty is not None:
            self._dokumenty.update(ids)

    def dodaj(self, fakt: Fakt, zastap: bool = False) -> Fakt:
        if fakt.id in self._fakty and not zastap:
            raise BladRejestru(f"fakt {fakt.id} już istnieje; użyj zastap=True, jeśli to świadoma zmiana")
        if fakt.dokument and self._dokumenty is not None and fakt.dokument not in self._dokumenty:
            raise BladRejestru(f"{fakt.id}: dokument {fakt.dokument} nie istnieje w archiwum")
        for w in fakt.wejscia:
            if w not in self._fakty:
                raise BladRejestru(f"{fakt.id}: brak faktu wejściowego {w}")
        self._fakty[fakt.id] = fakt
        return fakt

    def wylicz(
        self,
        id: str,
        pozycja: str,
        wzor: str,
        wejscia: list[str],
        funkcja: Callable[..., float],
        jednostka: Jednostka,
        okres: Okres,
        waluta: Optional[str] = None,
    ) -> Fakt:
        """Dodaje fakt wyliczony przez kod.

        `funkcja` dostaje wartości wejść w jednostkach podstawowych, w kolejności `wejscia`.
        Wynik zapisujemy w skali `jedn`. Status to najsłabszy status wejść.
        """
        brak = [w for w in wejscia if w not in self._fakty]
        if brak:
            raise BladRejestru(f"{id}: brak faktów wejściowych {brak}")
        fakty_wej = [self._fakty[w] for w in wejscia]
        odrzucone = [f.id for f in fakty_wej if f.status == Status.odrzucony]
        if odrzucone:
            raise BladRejestru(f"{id}: wejścia odrzucone {odrzucone}; nie liczę")
        if jednostka in (Jednostka.pieniadz, Jednostka.pieniadz_na_akcje):
            waluty = {f.waluta for f in fakty_wej if f.waluta}
            if waluta is None and len(waluty) == 1:
                waluta = waluty.pop()
        wynik = float(funkcja(*[f.wartosc_bazowa() for f in fakty_wej]))
        status = min((f.status for f in fakty_wej), key=lambda s: SILA_STATUSU[s])
        fakt = Fakt(
            id=id,
            rodzaj=Rodzaj.wyliczony,
            pozycja=pozycja,
            okres=okres,
            wartosc=wynik,
            skala=Skala.jedn,
            jednostka=jednostka,
            waluta=waluta,
            metoda=Metoda.kod,
            status=status,
            wzor=wzor,
            wejscia=list(wejscia),
        )
        return self.dodaj(fakt, zastap=id in self._fakty)

    # --- odczyt ----------------------------------------------------------

    def __getitem__(self, id: str) -> Fakt:
        try:
            return self._fakty[id]
        except KeyError:
            raise BladRejestru(f"brak faktu {id}") from None

    def __contains__(self, id: str) -> bool:
        return id in self._fakty

    def __len__(self) -> int:
        return len(self._fakty)

    def fakty(self) -> list[Fakt]:
        return list(self._fakty.values())

    def ze_statusem(self, *statusy: Status) -> list[Fakt]:
        return [f for f in self._fakty.values() if f.status in statusy]

    def rodowod(self, id: str) -> list[str]:
        """Wszystkie fakty, z których powstał dany fakt (łącznie z nim), w kolejności przeszukiwania."""
        wynik, kolejka = [], [id]
        while kolejka:
            biezacy = kolejka.pop(0)
            if biezacy in wynik:
                continue
            wynik.append(biezacy)
            kolejka.extend(self[biezacy].wejscia)
        return wynik

    # --- zapis -----------------------------------------------------------

    def do_pliku(self, sciezka: Path) -> None:
        plik = RejestrFaktowPlik(
            ticker=self.ticker,
            data_analizy=self.data_analizy,
            fakty=sorted(self._fakty.values(), key=lambda f: f.id),
        )
        sciezka.parent.mkdir(parents=True, exist_ok=True)
        sciezka.write_text(
            json.dumps(plik.model_dump(mode="json", exclude_defaults=True), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    @classmethod
    def z_pliku(cls, sciezka: Path, dokumenty: Optional[Iterable[str]] = None) -> "RejestrFaktow":
        plik = RejestrFaktowPlik.model_validate_json(sciezka.read_text(encoding="utf-8"))
        rejestr = cls(plik.ticker, plik.data_analizy, dokumenty)
        # wejścia muszą być dodane przed faktami wyliczonymi
        oczekujace = list(plik.fakty)
        while oczekujace:
            gotowe = [f for f in oczekujace if all(w in rejestr for w in f.wejscia)]
            if not gotowe:
                raise BladRejestru(f"nierozwiązane wejścia: {[f.id for f in oczekujace]}")
            for f in gotowe:
                rejestr.dodaj(f)
                oczekujace.remove(f)
        return rejestr
