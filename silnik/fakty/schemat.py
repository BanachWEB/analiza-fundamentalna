"""Schemat rejestru faktów i rejestru dokumentów.

Każda liczba w analizie jest faktem. Fakt wskazuje dokument z archiwum
(albo wzór i dane wejściowe, gdy kod go wyliczył) i ma status weryfikacji.
"""

from __future__ import annotations

import re
from datetime import date, datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

WERSJA_SCHEMATU = "1"

ID_DOKUMENTU = re.compile(r"^doc-\d{3,}$")
# pozycja.okres, np. "przychody.FY2025", "dlug_netto.2026-09-30", "wacc.zalozenie"
ID_FAKTU = re.compile(r"^[a-z0-9_]+(\.[A-Za-z0-9_\-]+)+$")


class TypDokumentu(str, Enum):
    sec_api = "sec_api"
    raport_10k = "10-K"
    raport_10q = "10-Q"
    raport_8k = "8-K"
    raport_20f = "20-F"
    raport_6k = "6-K"
    esef = "esef"
    raport_pdf = "raport_pdf"
    espi = "espi"
    strona = "strona"
    wklejka = "wklejka"
    inny = "inny"


class Dokument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    typ: TypDokumentu
    zrodlo: str = Field(description="Kto opublikował dane, np. SEC, spółka, Biznesradar, InvestingPro")
    adres: Optional[str] = Field(None, description="URL; dla wklejki None")
    opis: str = ""
    pobrano: datetime
    sha256: str
    plik: str = Field(description="Nazwa pliku w archiwum (poza repozytorium)")

    @field_validator("id")
    @classmethod
    def _id(cls, v: str) -> str:
        if not ID_DOKUMENTU.match(v):
            raise ValueError(f"id dokumentu musi mieć postać doc-NNN, jest {v!r}")
        return v

    @field_validator("sha256")
    @classmethod
    def _sha(cls, v: str) -> str:
        if not re.fullmatch(r"[0-9a-f]{64}", v):
            raise ValueError("sha256 musi mieć 64 znaki szesnastkowe")
        return v


class RejestrDokumentow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    wersja_schematu: str = WERSJA_SCHEMATU
    ticker: str
    dokumenty: list[Dokument] = []


class Rodzaj(str, Enum):
    raportowany = "raportowany"
    wyliczony = "wyliczony"
    zalozenie = "zalozenie"
    prognoza = "prognoza"


class Metoda(str, Enum):
    api = "api"
    xbrl = "xbrl"
    tabela_pdf = "tabela_pdf"
    wklejka = "wklejka"
    parser_strony = "parser_strony"  # deterministyczny odczyt tabeli ze strony WWW (np. Biznesradar)
    model = "model"  # model przypisał wiersz i podał cytat; wymaga testu cytatu
    kod = "kod"  # wyliczone przez silnik
    uzytkownik = "uzytkownik"  # założenie podane przez właściciela


class Status(str, Enum):
    zweryfikowany = "zweryfikowany"
    jedno_zrodlo = "jedno_zrodlo"
    konflikt = "konflikt"
    odrzucony = "odrzucony"


# Im wyżej, tym mocniejszy status. Fakt wyliczony dziedziczy najsłabszy status wejść.
SILA_STATUSU = {
    Status.zweryfikowany: 3,
    Status.jedno_zrodlo: 2,
    Status.konflikt: 1,
    Status.odrzucony: 0,
}


class Skala(str, Enum):
    jedn = "jedn"
    tys = "tys"
    mln = "mln"
    mld = "mld"


MNOZNIK_SKALI = {Skala.jedn: 1, Skala.tys: 1e3, Skala.mln: 1e6, Skala.mld: 1e9}


class Jednostka(str, Enum):
    pieniadz = "pieniadz"  # wymaga waluty
    pieniadz_na_akcje = "pieniadz_na_akcje"  # np. EPS, DPS; wymaga waluty
    ulamek = "ulamek"  # 0,456 = 45,6%
    mnoznik = "mnoznik"  # np. EV/EBIT
    akcje = "akcje"
    dni = "dni"
    lata = "lata"
    punkty = "punkty"
    liczba = "liczba"


class TypOkresu(str, Enum):
    FY = "FY"
    H1 = "H1"  # narastająco 6 miesięcy
    M9 = "M9"  # narastająco 9 miesięcy
    Q1 = "Q1"
    Q2 = "Q2"
    Q3 = "Q3"
    Q4 = "Q4"
    TTM = "TTM"
    dzien = "dzien"  # stan na dzień (bilans, kurs, liczba akcji)
    brak = "brak"  # założenie bez okresu, np. koszt kapitału


class Okres(BaseModel):
    model_config = ConfigDict(extra="forbid")

    typ: TypOkresu
    koniec: Optional[date] = None
    poczatek: Optional[date] = None

    @model_validator(mode="after")
    def _koniec(self) -> "Okres":
        if self.typ != TypOkresu.brak and self.koniec is None:
            raise ValueError("okres musi mieć datę końca (poza typem 'brak')")
        if self.poczatek and self.koniec and self.poczatek > self.koniec:
            raise ValueError("początek okresu jest po końcu")
        return self


class Fakt(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    rodzaj: Rodzaj
    pozycja: str = Field(description="Kanoniczna nazwa pozycji, np. przychody, ebit, dlug_netto")
    okres: Okres
    wartosc: float
    skala: Skala = Skala.jedn
    jednostka: Jednostka
    waluta: Optional[str] = None
    metoda: Metoda
    status: Status
    # źródło
    dokument: Optional[str] = None
    miejsce: dict[str, Any] = {}
    cytat: Optional[str] = None
    # fakty wyliczone
    wzor: Optional[str] = None
    wejscia: list[str] = []
    # założenia
    uzasadnienie: Optional[str] = None
    # prognozy
    dostawca: Optional[str] = None
    data_prognozy: Optional[date] = None
    liczba_analitykow: Optional[int] = None
    # wyniki kontroli, np. "drugie_zrodlo:doc-007:0.0%"
    kontrole: list[str] = []

    @field_validator("id")
    @classmethod
    def _id(cls, v: str) -> str:
        if not ID_FAKTU.match(v):
            raise ValueError(f"id faktu musi mieć postać pozycja.okres, jest {v!r}")
        return v

    @field_validator("waluta")
    @classmethod
    def _waluta(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not re.fullmatch(r"[A-Z]{3}", v):
            raise ValueError(f"waluta musi być kodem ISO 4217, jest {v!r}")
        return v

    @model_validator(mode="after")
    def _spojnosc(self) -> "Fakt":
        if self.jednostka in (Jednostka.pieniadz, Jednostka.pieniadz_na_akcje) and not self.waluta:
            raise ValueError(f"{self.id}: kwota pieniężna musi mieć walutę")
        if self.jednostka not in (Jednostka.pieniadz, Jednostka.pieniadz_na_akcje) and self.waluta:
            raise ValueError(f"{self.id}: waluta tylko przy kwotach pieniężnych")

        r = self.rodzaj
        if r == Rodzaj.raportowany:
            if not self.dokument:
                raise ValueError(f"{self.id}: fakt raportowany musi wskazywać dokument")
            if self.metoda not in (Metoda.api, Metoda.xbrl, Metoda.tabela_pdf, Metoda.wklejka, Metoda.parser_strony, Metoda.model):
                raise ValueError(f"{self.id}: niedozwolona metoda dla faktu raportowanego")
            if self.metoda in (Metoda.model, Metoda.tabela_pdf) and not self.cytat:
                raise ValueError(f"{self.id}: fakt z dokumentu tekstowego musi mieć cytat dosłowny")
            if self.wzor or self.wejscia:
                raise ValueError(f"{self.id}: fakt raportowany nie ma wzoru")
        elif r == Rodzaj.wyliczony:
            if self.metoda != Metoda.kod:
                raise ValueError(f"{self.id}: fakt wyliczony tworzy tylko kod")
            if not self.wzor or not self.wejscia:
                raise ValueError(f"{self.id}: fakt wyliczony musi mieć wzór i dane wejściowe")
            if self.dokument:
                raise ValueError(f"{self.id}: fakt wyliczony nie wskazuje dokumentu")
        elif r == Rodzaj.zalozenie:
            if not self.uzasadnienie:
                raise ValueError(f"{self.id}: założenie musi mieć uzasadnienie")
            if self.metoda not in (Metoda.model, Metoda.uzytkownik, Metoda.kod):
                raise ValueError(f"{self.id}: założenie podaje model, użytkownik albo kod (wartość domyślna)")
        elif r == Rodzaj.prognoza:
            if not (self.dokument and self.dostawca and self.data_prognozy and self.liczba_analitykow is not None):
                raise ValueError(
                    f"{self.id}: prognoza musi mieć dokument, dostawcę, datę i liczbę analityków"
                )
        return self

    def wartosc_bazowa(self) -> float:
        """Wartość w jednostkach podstawowych (bez skali tys/mln/mld)."""
        return self.wartosc * MNOZNIK_SKALI[self.skala]


class RejestrFaktowPlik(BaseModel):
    model_config = ConfigDict(extra="forbid")

    wersja_schematu: str = WERSJA_SCHEMATU
    ticker: str
    data_analizy: date
    fakty: list[Fakt] = []
