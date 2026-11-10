"""Uruchomienie bramek na katalogu analizy: python -m silnik.bramki analizy/<TICKER>/<data>"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from silnik.fakty.rejestr import RejestrFaktow
from silnik.pobieranie.archiwum import Archiwum

from . import automaty, dowody, ocen
from .raport import bramki_md, stop_md


def uruchom_w_katalogu(katalog: Path, rynek: Optional[str] = None) -> Path:
    dok = json.loads((katalog / "dokumenty.json").read_text(encoding="utf-8"))
    ticker = dok["ticker"]
    archiwum = Archiwum(ticker, katalog)
    rejestr = RejestrFaktow.z_pliku(katalog / "fakty.json", archiwum.ids())
    if rynek is None:
        rynek = "GPW" if any(f.waluta == "PLN" for f in rejestr.fakty() if f.pozycja == "przychody") else "USA"
    wyniki = automaty.z_rejestru(rejestr)
    if rynek == "USA":
        sub = next((d for d in archiwum.rejestr.dokumenty if d.zrodlo == "SEC" and d.opis == "lista raportów"), None)
        if sub:
            cik = int(sub.adres.rsplit("CIK", 1)[1].split(".")[0])
            wyniki += automaty.z_sec(archiwum, sub.id, cik, rejestr.data_analizy)
            wyniki += automaty.kontynuacja_zlozona(rejestr, wyniki)
    else:
        nazwa = None
        strona = next((d for d in archiwum.rejestr.dokumenty if d.adres and d.adres.endswith(f"/notowania/{ticker}")), None)
        if strona:
            from silnik.pobieranie.rynek import notowania_biznesradar
            nazwa = notowania_biznesradar(archiwum.tekst(strona.id)).get("nazwa")
        wyniki += automaty.z_gpw(archiwum, ticker, nazwa)
    od_modelu, odrzucone = dowody.wczytaj(katalog / "bramki_dowody.json", archiwum)
    # dowód modelu zastępuje automatyczny wynik tej samej bramki (np. ocena przyczyny NT)
    ids_modelu = {w.id for w in od_modelu}
    wyniki = [w for w in wyniki if w.id not in ids_modelu] + od_modelu
    d = ocen(wyniki)
    (katalog / "bramki.json").write_text(d.do_json(), encoding="utf-8")
    (katalog / "bramki.md").write_text(bramki_md(ticker, rejestr.data_analizy, d, odrzucone), encoding="utf-8")
    stop = katalog / "stop.md"
    if d.decyzja == "STOP":
        stop.write_text(stop_md(ticker, rejestr.data_analizy, d), encoding="utf-8")
    elif stop.exists():
        stop.unlink()
    return katalog / "bramki.md"
