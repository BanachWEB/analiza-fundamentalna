"""Archiwum dokumentów źródłowych.

Pliki leżą poza repozytorium (są ciężkie). Do repozytorium trafia tylko
`dokumenty.json` z adresem, datą pobrania i sumą SHA-256 każdego pliku.
Plików w archiwum nikt nie zmienia: ten sam plik dodany drugi raz dostaje
ten sam wpis.
"""

from __future__ import annotations

import hashlib
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from silnik.fakty.schemat import Dokument, RejestrDokumentow, TypDokumentu

DOMYSLNY_KATALOG = Path(os.environ.get("ANALIZA_ARCHIWUM", Path.home() / ".cache" / "analiza-fundamentalna" / "archiwum"))


class BladArchiwum(Exception):
    pass


def sha256_pliku(sciezka: Path) -> str:
    h = hashlib.sha256()
    with open(sciezka, "rb") as f:
        for blok in iter(lambda: f.read(1 << 20), b""):
            h.update(blok)
    return h.hexdigest()


class Archiwum:
    def __init__(self, ticker: str, katalog_analizy: Path, katalog_plikow: Optional[Path] = None):
        self.ticker = ticker
        self.katalog_analizy = Path(katalog_analizy)
        self.katalog_plikow = Path(katalog_plikow or DOMYSLNY_KATALOG / ticker)
        self.sciezka_rejestru = self.katalog_analizy / "dokumenty.json"
        if self.sciezka_rejestru.exists():
            self.rejestr = RejestrDokumentow.model_validate_json(self.sciezka_rejestru.read_text(encoding="utf-8"))
            if self.rejestr.ticker != ticker:
                raise BladArchiwum(f"dokumenty.json dotyczy {self.rejestr.ticker}, nie {ticker}")
        else:
            self.rejestr = RejestrDokumentow(ticker=ticker)

    # --- dodawanie -------------------------------------------------------

    def dodaj_plik(
        self,
        sciezka: Path,
        typ: TypDokumentu,
        zrodlo: str,
        adres: Optional[str] = None,
        opis: str = "",
        pobrano: Optional[datetime] = None,
    ) -> Dokument:
        sciezka = Path(sciezka)
        sha = sha256_pliku(sciezka)
        istniejacy = self.po_sha(sha)
        if istniejacy:
            return istniejacy
        self.katalog_plikow.mkdir(parents=True, exist_ok=True)
        nazwa = f"{sha[:16]}{sciezka.suffix.lower()}"
        cel = self.katalog_plikow / nazwa
        if not cel.exists():
            shutil.copyfile(sciezka, cel)
            cel.chmod(0o444)
        dok = Dokument(
            id=self._nastepne_id(),
            typ=typ,
            zrodlo=zrodlo,
            adres=adres,
            opis=opis,
            pobrano=pobrano or datetime.now(timezone.utc),
            sha256=sha,
            plik=nazwa,
        )
        self.rejestr.dokumenty.append(dok)
        self._zapisz()
        return dok

    def dodaj_tekst(self, tekst: str, typ: TypDokumentu, zrodlo: str, adres: Optional[str] = None, opis: str = "") -> Dokument:
        """Np. wklejka z InvestingPro albo tekst strony skopiowany dosłownie."""
        self.katalog_plikow.mkdir(parents=True, exist_ok=True)
        tymczasowy = self.katalog_plikow / ".nowy.txt"
        tymczasowy.write_text(tekst, encoding="utf-8")
        try:
            return self.dodaj_plik(tymczasowy, typ, zrodlo, adres, opis)
        finally:
            tymczasowy.unlink(missing_ok=True)

    # --- odczyt i kontrola -----------------------------------------------

    def __getitem__(self, id: str) -> Dokument:
        for d in self.rejestr.dokumenty:
            if d.id == id:
                return d
        raise BladArchiwum(f"brak dokumentu {id}")

    def ids(self) -> list[str]:
        return [d.id for d in self.rejestr.dokumenty]

    def po_sha(self, sha: str) -> Optional[Dokument]:
        return next((d for d in self.rejestr.dokumenty if d.sha256 == sha), None)

    def sciezka(self, id: str) -> Path:
        return self.katalog_plikow / self[id].plik

    def tekst(self, id: str) -> str:
        return self.sciezka(id).read_text(encoding="utf-8")

    def sprawdz(self, id: str) -> bool:
        """True, gdy plik istnieje i ma sumę zgodną z rejestrem."""
        p = self.sciezka(id)
        return p.exists() and sha256_pliku(p) == self[id].sha256

    # --- wewnętrzne ------------------------------------------------------

    def _nastepne_id(self) -> str:
        numery = [int(d.id.split("-")[1]) for d in self.rejestr.dokumenty]
        return f"doc-{(max(numery) + 1) if numery else 1:03d}"

    def _zapisz(self) -> None:
        self.katalog_analizy.mkdir(parents=True, exist_ok=True)
        self.sciezka_rejestru.write_text(self.rejestr.model_dump_json(indent=2, exclude_defaults=False) + "\n", encoding="utf-8")
