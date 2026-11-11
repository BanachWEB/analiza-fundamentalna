"""Budowa PDF: python -m silnik.raport analizy/<TICKER>/<data>
Lista miejsc na liczby: python -m silnik.raport analizy/<TICKER>/<data> --miejsca

- decyzja bramek STOP → krótki PDF ze stop.md i tabelą bramek;
- inaczej → raport.md od modelu: lint (żadnych liczb poza miejscami), renderowanie, PDF.
Wynik: raport.pdf i raport_wyrenderowany.md (do wglądu; liczby z rejestru).
"""

import json
import sys
from pathlib import Path

from .pdf import zbuduj
from .render import BladRaportu, bramki_tabela, miejsca, renderuj


def main(katalog: Path) -> int:
    ticker = json.loads((katalog / "dokumenty.json").read_text(encoding="utf-8"))["ticker"]
    bramki = katalog / "bramki.json"
    decyzja = json.loads(bramki.read_text(encoding="utf-8"))["decyzja"] if bramki.exists() else None
    if decyzja == "STOP":
        md = (katalog / "stop.md").read_text(encoding="utf-8") + "\n## Wszystkie bramki\n\n" + "\n".join(bramki_tabela(katalog))
        zbuduj(md, katalog / "raport.pdf", f"{ticker} — STOP", katalog)
        print(f"STOP: {katalog / 'raport.pdf'}")
        return 0
    zrodlo = katalog / "raport.md"
    if not zrodlo.exists():
        print(f"Brak {zrodlo}: model musi najpierw napisać raport z miejscami na liczby.")
        return 1
    try:
        md = renderuj(katalog, zrodlo.read_text(encoding="utf-8"))
    except BladRaportu as e:
        print("Lint odrzucił raport:")
        for b in e.bledy:
            print(f"  wiersz {b.wiersz}: {b.powod} — {b.tresc}")
        return 2
    (katalog / "raport_wyrenderowany.md").write_text(md, encoding="utf-8")
    zbuduj(md, katalog / "raport.pdf", f"{ticker} — analiza fundamentalna", katalog)
    print(f"PDF: {katalog / 'raport.pdf'}")
    return 0


if __name__ == "__main__":
    if "--miejsca" in sys.argv[2:]:
        print("\n".join(miejsca(Path(sys.argv[1]))))
        sys.exit(0)
    sys.exit(main(Path(sys.argv[1])))
