"""Praca modelu z dokumentami archiwum analizy.

  python -m silnik.dokumenty url     analizy/<T>/<data> URL --opis "raport roczny 2025" [--typ raport_pdf] [--zrodlo spółka]
  python -m silnik.dokumenty wklejka analizy/<T>/<data> plik.txt --zrodlo InvestingPro [--opis "konsensus"]
  python -m silnik.dokumenty tekst   analizy/<T>/<data> doc-003 [--strona 4] [--szukaj "Przychody"]
  python -m silnik.dokumenty lista   analizy/<T>/<data>

„tekst” wypisuje dokładnie ten tekst, w którym test cytatu szuka cytatów — cytuj tylko z niego.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from silnik.fakty.cytat import _strony_pdf, tekst_dokumentu
from silnik.fakty.schemat import TypDokumentu
from silnik.pobieranie.archiwum import Archiwum
from silnik.pobieranie.http import pobierz


def _archiwum(katalog: Path) -> Archiwum:
    ticker = json.loads((katalog / "dokumenty.json").read_text(encoding="utf-8"))["ticker"]
    return Archiwum(ticker, katalog)


def main() -> None:
    import signal

    signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # bez błędu przy „| head”
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    u = sub.add_parser("url")
    u.add_argument("katalog", type=Path)
    u.add_argument("adres")
    u.add_argument("--opis", required=True)
    u.add_argument("--typ", default="raport_pdf", choices=[t.value for t in TypDokumentu])
    u.add_argument("--zrodlo", default="spółka")
    w = sub.add_parser("wklejka")
    w.add_argument("katalog", type=Path)
    w.add_argument("plik", type=Path)
    w.add_argument("--zrodlo", required=True)
    w.add_argument("--opis", default="wklejka od właściciela")
    t = sub.add_parser("tekst")
    t.add_argument("katalog", type=Path)
    t.add_argument("dok")
    t.add_argument("--strona", type=int)
    t.add_argument("--szukaj")
    l_ = sub.add_parser("lista")
    l_.add_argument("katalog", type=Path)
    a = p.parse_args()

    arch = _archiwum(a.katalog)
    if a.cmd == "url":
        d = arch.po_adresie(a.adres)
        if d is None:
            sufiks = Path(a.adres.split("?")[0]).suffix.lower()
            plik = pobierz(a.adres, limit_s=180, rozszerzenie=sufiks if sufiks in (".pdf", ".htm", ".html", ".zip", ".txt") else ".html")
            try:
                d = arch.dodaj_plik(plik, TypDokumentu(a.typ), a.zrodlo, adres=a.adres, opis=a.opis)
            finally:
                plik.unlink(missing_ok=True)
        info = f" ({len(_strony_pdf(str(arch.sciezka(d.id))))} stron)" if arch.sciezka(d.id).suffix == ".pdf" else ""
        print(f"{d.id}{info}: {d.opis} — {d.adres}")
    elif a.cmd == "wklejka":
        d = arch.dodaj_tekst(a.plik.read_text(encoding="utf-8"), TypDokumentu.wklejka, a.zrodlo, opis=a.opis)
        print(f"{d.id}: {d.opis} ({d.zrodlo})")
    elif a.cmd == "lista":
        for d in arch.rejestr.dokumenty:
            print(f"{d.id}  {d.typ.value:10} {d.zrodlo:22} {d.opis}")
    else:
        tekst = tekst_dokumentu(arch.sciezka(a.dok), a.strona)
        if a.szukaj:
            sciezka = arch.sciezka(a.dok)
            strony = _strony_pdf(str(sciezka)) if sciezka.suffix == ".pdf" else (tekst,)
            for nr, s in enumerate(strony, 1):
                for linia in s.splitlines():
                    if re.search(a.szukaj, linia, re.I):
                        print(f"[strona {nr}] {linia}" if sciezka.suffix == ".pdf" else linia)
        else:
            print(tekst)


if __name__ == "__main__":
    main()
