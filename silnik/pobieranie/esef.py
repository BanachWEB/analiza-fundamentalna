"""Raporty roczne ESEF (inline XBRL) spółek z GPW → rejestr faktów, bez udziału modelu.

Pakiet ESEF to ZIP (czasem ZIP w ZIP albo plik .xbri) z raportem XHTML.
Parser czyta elementy ix:nonFraction bez wymiarów (dane skonsolidowane
z głównych zestawień), stosuje format liczby, skalę i znak z atrybutów.
"""

from __future__ import annotations

import io
import zipfile
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

import yaml
from lxml import etree

from silnik.fakty.schemat import Fakt, Jednostka, Metoda, Okres, Rodzaj, Skala, Status

KONFIGURACJA = Path(__file__).resolve().parents[2] / "konfiguracja"
NS = {
    "ix": "http://www.xbrl.org/2013/inlineXBRL",
    "xbrli": "http://www.xbrl.org/2003/instance",
    "xbrldi": "http://xbrl.org/2006/xbrldi",
}
SKALA = {0: Skala.jedn, 3: Skala.tys, 6: Skala.mln, 9: Skala.mld}


class BladESEF(Exception):
    pass


def xhtml_z_pakietu(dane: bytes, glebokosc: int = 0) -> bytes:
    """Zwraca raport XHTML z pakietu (obsługuje zagnieżdżone ZIP i .xbri)."""
    if glebokosc > 3:
        raise BladESEF("zbyt głęboko zagnieżdżony pakiet")
    if not zipfile.is_zipfile(io.BytesIO(dane)):
        if dane.lstrip()[:200].lower().find(b"<html") >= 0 or b"inlineXBRL" in dane[:5000]:
            return dane
        raise BladESEF("plik nie jest ani pakietem ZIP, ani raportem XHTML")
    z = zipfile.ZipFile(io.BytesIO(dane))
    raporty = [n for n in z.namelist() if n.lower().endswith((".xhtml", ".html")) and "/reports/" in n.replace("\\", "/")]
    if not raporty:
        raporty = [n for n in z.namelist() if n.lower().endswith(".xhtml")]
    if raporty:
        return z.read(sorted(raporty, key=lambda n: -z.getinfo(n).file_size)[0])
    for n in z.namelist():
        if n.lower().endswith((".zip", ".xbri")):
            return xhtml_z_pakietu(z.read(n), glebokosc + 1)
    raise BladESEF("w pakiecie nie ma raportu XHTML")


def liczba(tekst: str, format_: Optional[str]) -> float:
    """Zamienia wyświetlony tekst na liczbę według formatu ixt."""
    t = tekst.strip().replace(" ", " ").replace(" ", " ")
    f = (format_ or "").split(":")[-1].lower()
    if f in ("fixed-zero", "zerodash", "fixedzero") or t in ("-", "–", "—"):
        return 0.0
    t = t.replace(" ", "")
    if "comma-decimal" in f or "numcommadecimal" in f:
        t = t.replace(".", "").replace(",", ".")
    else:  # num-dot-decimal i domyślnie
        t = t.replace(",", "")
    try:
        return float(t)
    except ValueError:
        raise BladESEF(f"nie umiem odczytać liczby {tekst!r} w formacie {format_!r}") from None


@dataclass
class Wartosc:
    element: str
    kontekst: str
    start: Optional[date]
    koniec: date
    wartosc: float  # w skali z atrybutu scale
    skala: int
    waluta: Optional[str]
    na_akcje: bool
    tekst: str


def wartosci(xhtml: bytes) -> list[Wartosc]:
    drzewo = etree.fromstring(xhtml, etree.XMLParser(huge_tree=True, recover=False))
    konteksty = {}
    for c in drzewo.iter(f"{{{NS['xbrli']}}}context"):
        if c.findall(".//xbrldi:explicitMember", NS) or c.findall(".//xbrldi:typedMember", NS):
            continue  # pomijamy dane z wymiarami (segmenty, składniki kapitału)
        p = c.find("xbrli:period", NS)
        i, s, e = (p.find(f"xbrli:{x}", NS) for x in ("instant", "startDate", "endDate"))
        if i is not None:
            konteksty[c.get("id")] = (None, date.fromisoformat(i.text.strip()[:10]))
        else:
            konteksty[c.get("id")] = (date.fromisoformat(s.text.strip()[:10]), date.fromisoformat(e.text.strip()[:10]))
    jednostki = {}
    for u in drzewo.iter(f"{{{NS['xbrli']}}}unit"):
        miary = [m.text.split(":")[-1] for m in u.iter(f"{{{NS['xbrli']}}}measure")]
        dzielenie = u.find("xbrli:divide", NS) is not None
        jednostki[u.get("id")] = (miary[0] if miary else None, dzielenie)
    wynik = []
    for n in drzewo.iter(f"{{{NS['ix']}}}nonFraction"):
        ctx = konteksty.get(n.get("contextRef"))
        if ctx is None:
            continue
        if n.get("{http://www.w3.org/2001/XMLSchema-instance}nil") == "true":
            continue
        tekst = "".join(n.itertext())
        skala = int(n.get("scale") or 0)
        v = liczba(tekst, n.get("format"))
        if n.get("sign") == "-":
            v = -v
        miara, dzielenie = jednostki.get(n.get("unitRef"), (None, False))
        waluta = miara if miara and len(miara) == 3 and miara.isupper() else None
        wynik.append(Wartosc(n.get("name"), n.get("contextRef"), ctx[0], ctx[1], v, skala, waluta, dzielenie, tekst.strip()))
    return wynik


def wyciagnij_fakty(xhtml: bytes, dok_id: str, mapowanie: Optional[dict] = None) -> list[Fakt]:
    if mapowanie is None:
        mapowanie = yaml.safe_load((KONFIGURACJA / "mapowanie-mssf.yaml").read_text(encoding="utf-8"))
    dane = wartosci(xhtml)
    roczne = [w for w in dane if w.start and 350 <= (w.koniec - w.start).days <= 380]
    if not roczne:
        raise BladESEF("w raporcie nie ma okresów rocznych")
    koniec_roku = max(w.koniec for w in roczne)
    miesiac_konca = (koniec_roku - timedelta(days=10)).month

    def rok(k: date) -> int:
        d = k - timedelta(days=10)
        return d.year if d.month <= miesiac_konca else d.year + 1

    po_elemencie: dict[str, list[Wartosc]] = {}
    for w in dane:
        po_elemencie.setdefault(w.element, []).append(w)

    fakty: dict[str, Fakt] = {}
    for pozycja, cfg in mapowanie.items():
        jednostka = Jednostka(cfg["jednostka"])
        zajete: set[tuple] = set()
        for element in cfg["znaczniki"]:
            for w in po_elemencie.get(element, []):
                if cfg["rodzaj"] == "stan":
                    if w.start is not None:
                        continue
                    klucz = (None, w.koniec)
                    okres = Okres(typ="dzien", koniec=w.koniec)
                    fid = f"{pozycja}.{w.koniec.isoformat()}"
                else:
                    if not w.start or not 350 <= (w.koniec - w.start).days <= 380:
                        continue
                    klucz = (w.start, w.koniec)
                    okres = Okres(typ="FY", poczatek=w.start, koniec=w.koniec)
                    fid = f"{pozycja}.FY{rok(w.koniec)}"
                if klucz in zajete and fid not in fakty:
                    continue
                if jednostka in (Jednostka.pieniadz, Jednostka.pieniadz_na_akcje) and not w.waluta:
                    continue
                if fid in fakty:
                    if fakty[fid].miejsce["xbrl"] != element:
                        continue  # okres ma już wartość z elementu o wyższym priorytecie
                    if abs(fakty[fid].wartosc - w.wartosc) > 1e-9:
                        stary = fakty[fid]
                        fakty[fid] = stary.model_copy(update={
                            "status": Status.konflikt,
                            "kontrole": list(stary.kontrole) + [f"rozne_wartosci_w_raporcie:{w.tekst}"],
                        })
                    continue
                zajete.add(klucz)
                fakty[fid] = Fakt(
                    id=fid,
                    rodzaj=Rodzaj.raportowany,
                    pozycja=pozycja,
                    okres=okres,
                    wartosc=w.wartosc,
                    skala=SKALA.get(w.skala, Skala.jedn) if w.skala in SKALA else Skala.jedn,
                    jednostka=jednostka,
                    waluta=w.waluta if jednostka in (Jednostka.pieniadz, Jednostka.pieniadz_na_akcje) else None,
                    metoda=Metoda.xbrl,
                    status=Status.jedno_zrodlo,
                    dokument=dok_id,
                    miejsce={"xbrl": element, "kontekst": w.kontekst, "tekst": w.tekst},
                )
                if w.skala not in SKALA:  # nietypowa skala: przeliczamy na jednostki
                    fakty[fid] = fakty[fid].model_copy(update={"wartosc": w.wartosc * 10 ** w.skala})
    return list(fakty.values())
