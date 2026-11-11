"""Praca modelu z dokumentami archiwum analizy.

  python -m silnik.dokumenty url     analizy/<T>/<data> URL --opis "raport roczny 2025" [--typ raport_pdf] [--zrodlo spółka]
  python -m silnik.dokumenty wklejka analizy/<T>/<data> plik.txt --zrodlo InvestingPro [--opis "konsensus"]
  python -m silnik.dokumenty tekst   analizy/<T>/<data> doc-003 [--strona 4] [--szukaj "Przychody"]
  python -m silnik.dokumenty lista   analizy/<T>/<data>
  python -m silnik.dokumenty fragmenty-bramek analizy/<T>/<data> [--limit 4]

„tekst” wypisuje dokładnie ten tekst, w którym test cytatu szuka cytatów — cytuj tylko z niego.
„fragmenty-bramek” przeszukuje wszystkie dokumenty archiwum wzorcami z `konfiguracja/fragmenty-bramek.yaml`
i zapisuje `D/fragmenty_bramek.md`: dla każdej bramki modelu fragmenty z numerem dokumentu i strony.
Fragmenty pochodzą z tego samego tekstu co test cytatu, więc model może z nich cytować.
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

WZORCE_BRAMEK = Path(__file__).resolve().parents[1] / "konfiguracja" / "fragmenty-bramek.yaml"
POMIJANE_TYPY = {TypDokumentu.sec_api}  # dane maszynowe (JSON), nie tekst do oceny
DLUGOSC_LINII = 500


def _archiwum(katalog: Path) -> Archiwum:
    ticker = json.loads((katalog / "dokumenty.json").read_text(encoding="utf-8"))["ticker"]
    return Archiwum(ticker, katalog)


def _strony(arch: Archiwum, dok_id: str) -> tuple[str, ...]:
    sciezka = arch.sciezka(dok_id)
    if sciezka.suffix.lower() == ".pdf":
        return _strony_pdf(str(sciezka))
    return (tekst_dokumentu(sciezka, None),)


def fragmenty_bramek(arch: Archiwum, wzorce: dict[str, list[str]], limit: int = 4) -> list[str]:
    """Markdown z fragmentami dokumentów dla każdej bramki: najwyżej `limit` trafień na wzorzec i dokument."""
    teksty: dict[str, tuple[str, ...]] = {}
    pominiete: list[str] = []
    for d in arch.rejestr.dokumenty:
        if d.typ in POMIJANE_TYPY:
            continue
        try:
            teksty[d.id] = _strony(arch, d.id)
        except Exception as e:  # brak pliku w archiwum albo nieczytelny format
            pominiete.append(f"{d.id} ({type(e).__name__})")
    opisy = {d.id: d.opis for d in arch.rejestr.dokumenty}
    wynik = ["# Fragmenty do bramek modelu", "",
             "Silnik wyciągnął te fragmenty wzorcami z `konfiguracja/fragmenty-bramek.yaml`. "
             "Brak trafienia nie dowodzi braku problemu: wtedy przeczytaj dokument poleceniem `tekst`.", ""]
    if pominiete:
        wynik += [f"Pominięte dokumenty (nie da się odczytać): {', '.join(pominiete)}.", ""]
    for bramka, lista in wzorce.items():
        wynik.append(f"## {bramka}")
        trafienia = 0
        for wzorzec in lista:
            rx = re.compile(wzorzec, re.I)
            for dok_id, strony in teksty.items():
                n = 0
                for nr, strona in enumerate(strony, 1):
                    linie = strona.splitlines()
                    for i, linia in enumerate(linie):
                        if n >= limit or not rx.search(linia):
                            continue
                        n += 1
                        trafienia += 1
                        kontekst = " ".join(x.strip() for x in linie[max(i - 1, 0):i + 2])[:DLUGOSC_LINII]
                        gdzie = f"{dok_id}, strona {nr}" if len(strony) > 1 else dok_id
                        wynik.append(f"- [{gdzie}] ({opisy.get(dok_id, '')}; wzorzec „{wzorzec}”): {kontekst}")
        if not trafienia:
            wynik.append("- brak trafień")
        wynik.append("")
    return wynik


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
    f = sub.add_parser("fragmenty-bramek")
    f.add_argument("katalog", type=Path)
    f.add_argument("--limit", type=int, default=4)
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
    elif a.cmd == "fragmenty-bramek":
        import yaml

        wzorce = yaml.safe_load(WZORCE_BRAMEK.read_text(encoding="utf-8"))
        linie = fragmenty_bramek(arch, wzorce, a.limit)
        cel = a.katalog / "fragmenty_bramek.md"
        cel.write_text("\n".join(linie) + "\n", encoding="utf-8")
        bez = [b for b in wzorce if f"## {b}" in linie and linie[linie.index(f"## {b}") + 1] == "- brak trafień"]
        print(f"{cel}: {len(wzorce)} bramek, bez trafień: {', '.join(bez) or 'żadna'}")
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
