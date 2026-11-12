"""Dane rynkowe: kursy, obroty, rentowność obligacji USA, premie za ryzyko (Damodaran).

Źródła (sprawdzone 10.11.2026):
- USA: historia kursów z Yahoo (chart API), kontrola ostatniego kursu ze Stock Analysis;
  rentowność 10-letnich obligacji USA z Treasury.gov (CSV).
- GPW: historia kursów spółki i indeksu WIG z Biznesradaru (notowania historyczne),
  liczba akcji ze strony notowań Biznesradaru.
- Premia za ryzyko rynku akcji i spread niewypłacalności kraju: tabela Damodarana (ctryprem.html).
- Rentowność polskich obligacji 10-letnich: tabela „Rentowności obligacji wybranych państw”
  Strefy Inwestorów (publikowana w dni robocze); gdy jej brak, model albo właściciel podaje
  wartość jako założenie ze źródłem i datą (parametr --rf).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional

from lxml import html as lhtml

from silnik.fakty.schemat import Fakt, Jednostka, Metoda, Okres, Rodzaj, Status, TypDokumentu
from silnik.pobieranie.archiwum import Archiwum
from silnik.pobieranie.http import pobierz


@dataclass
class Sesja:
    dzien: date
    zamkniecie: float
    wolumen: float


class BladRynku(Exception):
    pass


def _do_archiwum(archiwum: Archiwum, url: str, zrodlo: str, opis: str, rozszerzenie: str):
    plik = pobierz(url, rozszerzenie=rozszerzenie)
    try:
        return archiwum.dodaj_plik(plik, TypDokumentu.strona, zrodlo, adres=url, opis=opis)
    finally:
        plik.unlink(missing_ok=True)


# --- historia kursów ------------------------------------------------------------


def url_yahoo(symbol: str) -> str:
    # 5 lat sesji dziennych: momentum, RSI i obroty biorą końcówkę, beta z regresji całe okno
    return f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=5y&interval=1d"


def sesje_yahoo(tresc: str) -> list[Sesja]:
    d = json.loads(tresc)["chart"]
    if d.get("error") or not d.get("result"):
        raise BladRynku(f"Yahoo: {d.get('error')}")
    r = d["result"][0]
    zamk = r["indicators"]["quote"][0]["close"]
    wol = r["indicators"]["quote"][0].get("volume") or [0] * len(zamk)
    wynik = []
    for t, c, v in zip(r["timestamp"], zamk, wol):
        if c is None:
            continue
        wynik.append(Sesja(datetime.fromtimestamp(t, tz=timezone.utc).date(), float(c), float(v or 0)))
    return wynik


def url_biznesradar_historia(symbol: str, strona: int) -> str:
    return f"https://www.biznesradar.pl/notowania-historyczne/{symbol}" + (f",{strona}" if strona > 1 else "")


def sesje_biznesradar(tresc: str) -> list[Sesja]:
    drzewo = lhtml.fromstring(tresc)
    tabele = drzewo.xpath('//table[contains(@class,"qTableFull")]')
    if not tabele:
        raise BladRynku("Biznesradar: brak tabeli notowań")
    wynik = []
    for tr in tabele[0].xpath(".//tr")[1:]:
        k = [" ".join(td.text_content().split()) for td in tr.xpath("./td")]
        if len(k) < 6:
            continue
        try:
            dz = datetime.strptime(k[0], "%d.%m.%Y").date()
            wynik.append(Sesja(dz, float(k[4].replace(" ", "")), float(k[5].replace(" ", "") or 0)))
        except ValueError:
            continue
    return wynik


def historia(archiwum: Archiwum, rynek: str, symbol: str, sesji: int = 280) -> tuple[list[Sesja], list[str]]:
    """Zwraca (sesje od najstarszej, id dokumentów)."""
    if rynek == "USA":
        dok = _do_archiwum(archiwum, url_yahoo(symbol), "Yahoo Finance", f"notowania dzienne {symbol}", ".json")
        return sorted(sesje_yahoo(archiwum.tekst(dok.id)), key=lambda s: s.dzien), [dok.id]
    sesje, ids = [], []
    for nr in range(1, 1 + (sesji // 50) + 1):
        dok = _do_archiwum(archiwum, url_biznesradar_historia(symbol, nr), "Biznesradar",
                           f"notowania historyczne {symbol}, strona {nr}", ".html")
        ids.append(dok.id)
        nowe = sesje_biznesradar(archiwum.tekst(dok.id))
        if not nowe:
            break
        sesje += nowe
        if len(sesje) >= sesji:
            break
    unik = {s.dzien: s for s in sesje}
    return sorted(unik.values(), key=lambda s: s.dzien), ids


def stopa_zwrotu_12_1(sesje: list[Sesja]) -> Optional[tuple[float, date, date]]:
    """Stopa zwrotu od ok. 12 miesięcy do ok. 1 miesiąca temu (momentum 12–1)."""
    if not sesje:
        return None
    koniec = sesje[-1].dzien
    def blisko(dni):
        cel = date.fromordinal(koniec.toordinal() - dni)
        kandydaci = [s for s in sesje if s.dzien <= cel]
        return kandydaci[-1] if kandydaci else None
    a, b = blisko(365), blisko(30)
    if a is None or b is None or (koniec - a.dzien).days < 350:
        return None
    return b.zamkniecie / a.zamkniecie - 1, a.dzien, b.dzien


def zmiana_kursu_3m(sesje: list[Sesja]) -> Optional[tuple[float, date]]:
    """Zmiana kursu od ostatniej sesji sprzed ok. 3 miesięcy (91 dni) do ostatniej sesji.

    Zasady właściciela: „pauza po rajdzie” — nie kupuje, gdy kurs jest o ponad 25% wyższy niż 3 miesiące wcześniej.
    """
    if not sesje:
        return None
    koniec = sesje[-1].dzien
    cel = date.fromordinal(koniec.toordinal() - 91)
    kandydaci = [s for s in sesje if s.dzien <= cel]
    if not kandydaci or (cel - kandydaci[-1].dzien).days > 7:
        return None
    a = kandydaci[-1]
    return sesje[-1].zamkniecie / a.zamkniecie - 1, a.dzien


def rsi(sesje: list[Sesja], okno: int = 14) -> Optional[float]:
    """RSI Wildera z cen zamknięcia (0–100). Pierwsza średnia to średnia arytmetyczna z `okno` zmian,
    kolejne wygładzamy: średnia = (poprzednia × (okno − 1) + zmiana) / okno. Informacja, nie bramka."""
    if len(sesje) < okno + 1:
        return None
    zmiany = [b.zamkniecie - a.zamkniecie for a, b in zip(sesje, sesje[1:])]
    wzrost = sum(max(z, 0) for z in zmiany[:okno]) / okno
    spadek = sum(max(-z, 0) for z in zmiany[:okno]) / okno
    for z in zmiany[okno:]:
        wzrost = (wzrost * (okno - 1) + max(z, 0)) / okno
        spadek = (spadek * (okno - 1) + max(-z, 0)) / okno
    if spadek == 0:
        return 100.0
    return 100 - 100 / (1 + wzrost / spadek)


# --- beta z regresji -----------------------------------------------------------------


def tygodniowe(sesje: list[Sesja]) -> list[tuple[date, float]]:
    """Ostatnie zamknięcie w każdym tygodniu ISO (sesje od najstarszej)."""
    tyg: dict[tuple[int, int], Sesja] = {}
    for s in sesje:
        klucz = tuple(s.dzien.isocalendar()[:2])
        if klucz not in tyg or s.dzien > tyg[klucz].dzien:
            tyg[klucz] = s
    return [(s.dzien, s.zamkniecie) for _, s in sorted(tyg.items())]


def beta_regresja(sesje: list[Sesja], indeks: list[Sesja], lat: int = 5, min_tygodni: int = 104) -> Optional[dict]:
    """Beta z regresji tygodniowych stóp zwrotu spółki na stopach zwrotu indeksu (MNK) z ostatnich `lat` lat.

    Stopy zwrotu liczy tylko dla par kolejnych tygodni, w których jest zamknięcie i spółki, i indeksu.
    Zwraca None, gdy wspólna historia ma mniej niż `min_tygodni` stóp zwrotu albo indeks się nie zmienia.
    """
    if not sesje or not indeks:
        return None
    koniec = min(sesje[-1].dzien, indeks[-1].dzien)
    poczatek = date.fromordinal(koniec.toordinal() - round(365.25 * lat))
    s_t = {tuple(d.isocalendar()[:2]): (d, c) for d, c in tygodniowe([x for x in sesje if poczatek <= x.dzien <= koniec])}
    i_t = {tuple(d.isocalendar()[:2]): (d, c) for d, c in tygodniowe([x for x in indeks if poczatek <= x.dzien <= koniec])}
    wspolne = sorted(set(s_t) & set(i_t))
    xs, ys = [], []
    for a, b in zip(wspolne, wspolne[1:]):
        (_, sa), (_, sb) = s_t[a], s_t[b]
        (_, ia), (_, ib) = i_t[a], i_t[b]
        if sa > 0 and ia > 0:
            ys.append(sb / sa - 1)
            xs.append(ib / ia - 1)
    n = len(xs)
    if n < max(min_tygodni, 3):
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return None
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    syy = sum((y - my) ** 2 for y in ys)
    b = sxy / sxx
    reszty = syy - b * sxy
    blad = (max(reszty, 0.0) / (n - 2) / sxx) ** 0.5
    r2 = (sxy * sxy) / (sxx * syy) if syy > 0 else 0.0
    return {"beta": b, "blad_standardowy": blad, "r2": r2, "tygodni": n,
            "od": s_t[wspolne[0]][0], "do": s_t[wspolne[-1]][0]}


def fakt_beta(sesje: list[Sesja], dok_ids: list[str], indeks: list[Sesja], dok_ids_indeksu: list[str],
              nazwa_indeksu: str, lat: int = 5, min_tygodni: int = 104) -> Optional[Fakt]:
    """Fakt `beta_regresja.<dzień>`; None, gdy historia notowań jest za krótka."""
    w = beta_regresja(sesje, indeks, lat, min_tygodni)
    if w is None or not dok_ids:
        return None
    metoda = Metoda.api if len(dok_ids) == 1 else Metoda.parser_strony
    return _fakt(f"beta_regresja.{w['do'].isoformat()}", "beta_regresja", Okres(typ="dzien", koniec=w["do"]), w["beta"],
                 Jednostka.liczba, dok_ids[0],
                 {"obliczenie": f"MNK: tygodniowe stopy zwrotu spółki na stopach zwrotu indeksu {nazwa_indeksu}, "
                                f"okno {lat} lat (ostatnie zamknięcie tygodnia)",
                  "od": w["od"].isoformat(), "do": w["do"].isoformat(), "tygodni": w["tygodni"],
                  "blad_standardowy": round(w["blad_standardowy"], 4), "r2": round(w["r2"], 4),
                  "dokumenty": list(dok_ids) + list(dok_ids_indeksu)}, metoda=metoda)


def parametry_bety() -> dict:
    """Okno i minimalna liczba tygodni z `konfiguracja/wycena.yaml` (jedno źródło parametrów wyceny)."""
    import yaml
    plik = Path(__file__).resolve().parents[2] / "konfiguracja" / "wycena.yaml"
    par = yaml.safe_load(plik.read_text(encoding="utf-8"))
    return {"lat": int(par["beta_okno_lat"]), "min_tygodni": int(par["beta_min_tygodni"])}


def sesji_do_bety() -> int:
    """Liczba sesji do pobrania (GPW, Biznesradar), żeby objąć okno bety: ok. 252 sesje na rok i zapas."""
    return 252 * parametry_bety()["lat"] + 30


def dodaj_bete(rejestr, sesje: list[Sesja], dok_ids: list[str], indeks: list[Sesja], dok_ids_indeksu: list[str],
               nazwa_indeksu: str) -> Optional[Fakt]:
    """Dopisuje do rejestru betę z regresji; przy za krótkiej historii zostawia ślad i nic nie dodaje."""
    par = parametry_bety()
    f = fakt_beta(sesje, dok_ids, indeks, dok_ids_indeksu, nazwa_indeksu, par["lat"], par["min_tygodni"])
    if f is None:
        print(f"Beta z regresji: za krótka wspólna historia notowań spółki i indeksu {nazwa_indeksu} "
              f"(minimum {par['min_tygodni']} tygodni); wycena użyje bety domyślnej")
        return None
    rejestr.dodaj(f, zastap=True)
    return f


# --- profil ryzyka kursu (specyfikacja 1.1, punkt 7) -----------------------------------


def _okno(sesje: list[Sesja], koniec: date, lat: int) -> list[Sesja]:
    poczatek = date.fromordinal(koniec.toordinal() - round(365.25 * lat))
    return [s for s in sesje if poczatek <= s.dzien <= koniec]


def obsuniecie(tyg: list[tuple[date, float]]) -> Optional[dict]:
    """Największy spadek od szczytu do dołka na zamknięciach tygodniowych i czas powrotu do szczytu."""
    if len(tyg) < 2:
        return None
    szczyt_d, szczyt = tyg[0]
    naj = {"wartosc": 0.0, "szczyt": tyg[0][0], "dolek": tyg[0][0], "powrot": None}
    for d, c in tyg:
        if c > szczyt:
            szczyt_d, szczyt = d, c
        spadek = c / szczyt - 1
        if spadek < naj["wartosc"]:
            naj = {"wartosc": spadek, "szczyt": szczyt_d, "dolek": d, "powrot": None, "poziom": szczyt}
    if naj["wartosc"] < 0:
        po = [d for d, c in tyg if d > naj["dolek"] and c >= naj["poziom"]]
        naj["powrot"] = po[0] if po else None
    return naj


def _zwroty(tyg: list[tuple[date, float]]) -> dict:
    klucze = [tuple(d.isocalendar()[:2]) for d, _ in tyg]
    return {klucze[i]: tyg[i][1] / tyg[i - 1][1] - 1 for i in range(1, len(tyg)) if tyg[i - 1][1] > 0}


def zmiennosc_roczna(tyg: list[tuple[date, float]]) -> Optional[float]:
    z = list(_zwroty(tyg).values())
    if len(z) < 3:
        return None
    sr = sum(z) / len(z)
    return (sum((x - sr) ** 2 for x in z) / (len(z) - 1)) ** 0.5 * 52 ** 0.5


def korelacja(tyg_a: list[tuple[date, float]], tyg_b: list[tuple[date, float]]) -> Optional[float]:
    za, zb = _zwroty(tyg_a), _zwroty(tyg_b)
    wsp = sorted(set(za) & set(zb))
    if len(wsp) < 3:
        return None
    xs, ys = [za[w] for w in wsp], [zb[w] for w in wsp]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx, syy = sum((x - mx) ** 2 for x in xs), sum((y - my) ** 2 for y in ys)
    return sxy / (sxx * syy) ** 0.5 if sxx > 0 and syy > 0 else None


def fakty_profilu(sesje: list[Sesja], dok_ids: list[str], indeks: list[Sesja], dok_ids_indeksu: list[str],
                  nazwa_indeksu: str, lat: int = 5, min_tygodni: int = 104) -> list[Fakt]:
    """Zmienność roczna, maksymalne obsunięcie z czasem powrotu i korelacja z indeksem (tygodniowo, `lat` lat)."""
    if not sesje or not dok_ids:
        return []
    koniec = sesje[-1].dzien
    tyg = tygodniowe(_okno(sesje, koniec, lat))
    if len(tyg) < min_tygodni:
        return []
    tyg_i = tygodniowe(_okno(indeks, koniec, lat)) if indeks else []
    metoda = Metoda.api if len(dok_ids) == 1 else Metoda.parser_strony
    okres = Okres(typ="dzien", koniec=koniec)
    d = koniec.isoformat()
    wspolne = {"od": tyg[0][0].isoformat(), "do": tyg[-1][0].isoformat(), "tygodni": len(tyg), "dokumenty": list(dok_ids)}
    wynik = []
    zm = zmiennosc_roczna(tyg)
    if zm is not None:
        wynik.append(_fakt(f"zmiennosc_roczna.{d}", "zmiennosc_roczna", okres, zm, Jednostka.ulamek, dok_ids[0],
                           {"obliczenie": "odchylenie standardowe tygodniowych stóp zwrotu × √52", **wspolne}, metoda=metoda))
    ob = obsuniecie(tyg)
    if ob:
        wynik.append(_fakt(f"max_obsuniecie.{d}", "max_obsuniecie", okres, ob["wartosc"], Jednostka.ulamek, dok_ids[0],
                           {"obliczenie": "największy spadek zamknięcia tygodniowego od wcześniejszego szczytu",
                            "szczyt": ob["szczyt"].isoformat(), "dolek": ob["dolek"].isoformat(),
                            "powrot": ob["powrot"].isoformat() if ob["powrot"] else None, **wspolne}, metoda=metoda))
        if ob["powrot"]:
            wynik.append(_fakt(f"czas_powrotu_tyg.{d}", "czas_powrotu_tyg", okres, (ob["powrot"] - ob["dolek"]).days / 7,
                               Jednostka.liczba, dok_ids[0],
                               {"obliczenie": "tygodnie od dołka do pierwszego zamknięcia na poziomie szczytu", **wspolne},
                               metoda=metoda))
    if tyg_i and dok_ids_indeksu:
        wsp_i = {**wspolne, "dokumenty": list(dok_ids) + list(dok_ids_indeksu)}
        kor = korelacja(tyg, tyg_i)
        if kor is not None:
            wynik.append(_fakt(f"korelacja_z_indeksem.{d}", "korelacja_z_indeksem", okres, kor, Jednostka.liczba, dok_ids[0],
                               {"obliczenie": f"korelacja tygodniowych stóp zwrotu z indeksem {nazwa_indeksu}", **wsp_i},
                               metoda=metoda))
        zi = zmiennosc_roczna(tyg_i)
        if zi is not None:
            wynik.append(_fakt(f"indeks_zmiennosc_roczna.{d}", "indeks_zmiennosc_roczna", okres, zi, Jednostka.ulamek,
                               dok_ids_indeksu[0], {"obliczenie": f"jak zmiennosc_roczna, indeks {nazwa_indeksu}", **wspolne,
                                                    "dokumenty": list(dok_ids_indeksu)}, metoda=metoda))
        oi = obsuniecie(tyg_i)
        if oi:
            wynik.append(_fakt(f"indeks_max_obsuniecie.{d}", "indeks_max_obsuniecie", okres, oi["wartosc"], Jednostka.ulamek,
                               dok_ids_indeksu[0], {"obliczenie": f"jak max_obsuniecie, indeks {nazwa_indeksu}",
                                                    "szczyt": oi["szczyt"].isoformat(), "dolek": oi["dolek"].isoformat(),
                                                    **wspolne, "dokumenty": list(dok_ids_indeksu)}, metoda=metoda))
    return wynik


def dodaj_profil_ryzyka(rejestr, sesje: list[Sesja], dok_ids: list[str], indeks: list[Sesja], dok_ids_indeksu: list[str],
                        nazwa_indeksu: str) -> list[Fakt]:
    par = parametry_bety()
    fakty = fakty_profilu(sesje, dok_ids, indeks, dok_ids_indeksu, nazwa_indeksu, par["lat"], par["min_tygodni"])
    for f in fakty:
        rejestr.dodaj(f, zastap=True)
    if not fakty:
        print(f"Profil ryzyka: za krótka historia notowań (minimum {par['min_tygodni']} tygodni)")
    return fakty


# --- beta sektorowa Damodarana (kontrola bety; specyfikacja 1.1, punkt 7) --------------------


def _norm(t: str) -> str:
    return " ".join(t.replace("\xa0", " ").split()).lower()


def beta_damodaran(tresc: str, branza: str) -> Optional[dict]:
    """Beta bez długu dla branży z tabeli Damodarana (Betas.html i odpowiedniki regionalne).

    Kolumny rozpoznaje po nagłówku: „Industry Name” i „Unlevered beta corrected for cash” (albo „Unlevered beta”).
    Zwraca None, gdy branży nie ma w tabeli. Format strony sprawdzi pierwszy przebieg z dostępem do sieci.
    """
    drzewo = lhtml.fromstring(tresc)
    naglowek, kol_b, kol_n = None, None, None
    for tr in drzewo.xpath("//tr"):
        komorki = [_norm(td.text_content()) for td in tr.xpath("./td|./th")]
        if naglowek is None:
            if komorki and "industry name" in komorki[0]:
                naglowek = komorki
                dopasowane = [i for i, k in enumerate(komorki) if "unlevered beta corrected for cash" in k]
                dopasowane = dopasowane or [i for i, k in enumerate(komorki) if k.startswith("unlevered beta")]
                if not dopasowane:
                    raise BladRynku("Damodaran: brak kolumny z betą bez długu")
                kol_b = dopasowane[0]
                kol_n = next((i for i, k in enumerate(komorki) if "number of firms" in k), None)
            continue
        if komorki and komorki[0] == _norm(branza) and len(komorki) > kol_b:
            try:
                beta = float(komorki[kol_b].replace(",", ""))
            except ValueError:
                raise BladRynku(f"Damodaran: nie odczytam bety dla {branza!r}: {komorki[kol_b]!r}")
            firm = None
            if kol_n is not None and len(komorki) > kol_n:
                try:
                    firm = int(float(komorki[kol_n].replace(",", "")))
                except ValueError:
                    firm = None
            return {"beta": beta, "kolumna": naglowek[kol_b], "firm": firm}
    if naglowek is None:
        raise BladRynku("Damodaran: brak tabeli z nagłówkiem „Industry Name”")
    return None


def dodaj_bete_sektorowa(rejestr, archiwum: Archiwum, katalog: Path, rynek: str, dzien: date) -> Optional[Fakt]:
    """Pobiera tabelę bet Damodarana dla rynku, gdy analiza.json ma pole `branza_damodaran`."""
    plik = Path(katalog) / "analiza.json"
    if not plik.exists():
        return None
    branza = json.loads(plik.read_text(encoding="utf-8")).get("branza_damodaran")
    if not branza:
        return None
    import yaml
    url = yaml.safe_load((Path(__file__).resolve().parents[2] / "konfiguracja" / "wycena.yaml").read_text(encoding="utf-8")
                         )["beta_sektorowa_url"][rynek]
    dok = archiwum.po_adresie(url) or _do_archiwum(archiwum, url, "Damodaran Online", "bety branżowe", ".html")
    rejestr.znane_dokumenty(archiwum.ids())
    w = beta_damodaran(archiwum.tekst(dok.id), branza)
    if w is None:
        print(f"Beta sektorowa: branży {branza!r} nie ma w tabeli Damodarana ({url})")
        return None
    f = _fakt(f"beta_sektorowa_bez_dlugu.{dzien.isoformat()}", "beta_sektorowa_bez_dlugu", Okres(typ="dzien", koniec=dzien),
              w["beta"], Jednostka.liczba, dok.id, {"branza": branza, "kolumna": w["kolumna"], "firm": w["firm"]},
              metoda=Metoda.parser_strony)
    rejestr.dodaj(f, zastap=True)
    return f


# --- fakty rynkowe -------------------------------------------------------------------


def _fakt(fid, pozycja, okres, wartosc, jednostka, dok, miejsce, waluta=None, metoda=Metoda.api):
    return Fakt(id=fid, rodzaj=Rodzaj.raportowany, pozycja=pozycja, okres=okres, wartosc=wartosc, jednostka=jednostka,
                waluta=waluta, metoda=metoda, status=Status.jedno_zrodlo, dokument=dok, miejsce=miejsce)


def fakty_z_historii(sesje: list[Sesja], dok_ids: list[str], waluta: str, prefiks: str = "") -> list[Fakt]:
    """Kurs ostatni, momentum 12–1, zmiana kursu z 3 miesięcy, RSI 14-dniowy i średnie dzienne obroty z 60 sesji."""
    if not sesje:
        return []
    ost = sesje[-1]
    dok = dok_ids[0]
    metoda = Metoda.api if dok_ids and len(dok_ids) == 1 else Metoda.parser_strony
    p = prefiks
    wynik = [_fakt(f"{p}kurs.{ost.dzien.isoformat()}", f"{p}kurs", Okres(typ="dzien", koniec=ost.dzien), ost.zamkniecie,
                   Jednostka.pieniadz_na_akcje if not p else Jednostka.punkty, dok,
                   {"sesja": ost.dzien.isoformat(), "pole": "zamknięcie"}, waluta if not p else None, metoda)]
    m = stopa_zwrotu_12_1(sesje)
    if m:
        wynik.append(_fakt(f"{p}momentum_12_1.{ost.dzien.isoformat()}", f"{p}momentum_12_1",
                           Okres(typ="dzien", koniec=ost.dzien), m[0], Jednostka.ulamek, dok,
                           {"od": m[1].isoformat(), "do": m[2].isoformat(), "obliczenie": "kurs(do) / kurs(od) - 1",
                            "dokumenty": dok_ids}, metoda=metoda))
    z3 = zmiana_kursu_3m(sesje)
    if z3 and not p:
        wynik.append(_fakt(f"zmiana_kursu_3m.{ost.dzien.isoformat()}", "zmiana_kursu_3m",
                           Okres(typ="dzien", koniec=ost.dzien), z3[0], Jednostka.ulamek, dok,
                           {"od": z3[1].isoformat(), "do": ost.dzien.isoformat(), "obliczenie": "kurs(do) / kurs(od) - 1",
                            "dokumenty": dok_ids}, metoda=metoda))
    r14 = rsi(sesje) if not p else None
    if r14 is not None:
        wynik.append(_fakt(f"rsi_14.{ost.dzien.isoformat()}", "rsi_14", Okres(typ="dzien", koniec=ost.dzien), r14,
                           Jednostka.liczba, dok,
                           {"obliczenie": "RSI Wildera z 14 sesji, zamknięcia", "od": sesje[0].dzien.isoformat(),
                            "dokumenty": dok_ids}, metoda=metoda))
    if not p:
        ostatnie = sesje[-60:]
        obroty = sum(s.zamkniecie * s.wolumen for s in ostatnie) / len(ostatnie)
        wynik.append(_fakt(f"obroty_dzienne_60s.{ost.dzien.isoformat()}", "obroty_dzienne_60s",
                           Okres(typ="dzien", koniec=ost.dzien), obroty, Jednostka.pieniadz, dok,
                           {"obliczenie": "średnia z 60 sesji: zamknięcie × wolumen", "od": ostatnie[0].dzien.isoformat(),
                            "dokumenty": dok_ids}, waluta, metoda))
    return wynik


# --- kontrola kursu i liczba akcji ------------------------------------------------------


def sesje_stockanalysis(tresc: str) -> list[Sesja]:
    """Historia z Stock Analysis (za darmo ok. 6 miesięcy): wariant awaryjny, gdy Yahoo nie odpowiada."""
    wynik = []
    for m in re.finditer(r"\{([^{}]*t:\"\d{4}-\d{2}-\d{2}\"[^{}]*)\}", tresc):
        pola = dict(re.findall(r"(\w+):(\"[^\"]*\"|-?[\d.]+)", m.group(1)))
        try:
            wynik.append(Sesja(date.fromisoformat(pola["t"].strip('"')), float(pola["c"]), float(pola.get("v", 0))))
        except (KeyError, ValueError):
            continue
    return sorted({s.dzien: s for s in wynik}.values(), key=lambda s: s.dzien)


def kurs_stockanalysis(tresc: str) -> Optional[tuple[date, float]]:
    m = re.search(r'data:\[\{t:"(\d{4}-\d{2}-\d{2})",o:[\d.]+,h:[\d.]+,l:[\d.]+,c:([\d.]+)', tresc)
    return (date.fromisoformat(m.group(1)), float(m.group(2))) if m else None


def notowania_biznesradar(tresc: str) -> dict:
    tekst = " ".join(lhtml.fromstring(tresc).text_content().split())
    wynik = {}
    m = re.search(r"Liczba akcji:\s*([\d ]+)", tekst)
    if m:
        wynik["liczba_akcji"] = float(m.group(1).replace(" ", ""))
    m = re.search(r"Notowania\s+\S+\s+\(([^)]+)\)", tekst)
    if m:
        wynik["nazwa"] = m.group(1).strip()
    m = re.search(r'datetime="(\d{4}-\d{2}-\d{2})', tresc)
    if m:
        wynik["dzien"] = date.fromisoformat(m.group(1))
    return wynik


# --- stopy i premie ----------------------------------------------------------------------

URL_TREASURY = ("https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/"
                "{rok}/all?type=daily_treasury_yield_curve&field_tdr_date_value={rok}&page&_format=csv")
URL_DAMODARAN = "https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/ctryprem.html"


def rentownosc_treasury(tresc: str) -> tuple[date, float]:
    linie = [l for l in tresc.strip().splitlines() if l]
    naglowek = [h.strip('"') for h in linie[0].split(",")]
    kol = naglowek.index("10 Yr")
    pierwszy = linie[1].split(",")
    return datetime.strptime(pierwszy[0], "%m/%d/%Y").date(), float(pierwszy[kol]) / 100


def damodaran_kraj(tresc: str, kraj: str) -> dict:
    """Wiersz kraju z ctryprem.html: rating, spread, premia kraju, premia rynku akcji razem."""
    tekst = re.sub(r"<[^>]+>", " ", tresc)
    tekst = re.sub(r"&nbsp;", " ", tekst)
    m = re.search(re.escape(kraj) + r"\s+([A-Za-z0-9]+)\s+([\d.]+)%\s+([\d.]+)%\s+([\d.]+)%", tekst)
    if not m:
        raise BladRynku(f"Damodaran: brak wiersza dla {kraj}")
    return {"rating": m.group(1), "spread": float(m.group(2)) / 100, "premia_kraju": float(m.group(3)) / 100,
            "premia_rynku": float(m.group(4)) / 100}


URL_STREFA = "https://strefainwestorow.pl/wiadomosci/{d}/rentownosci-obligacji-wybranych-panstw-tabela"


def rentownosc_strefa(tresc: str) -> tuple[date, float]:
    tekst = " ".join(lhtml.fromstring(tresc).text_content().split())
    m = re.search(r"Rentowności (\d\d\.\d\d\.\d{4}).*?Polska 10-letnie ([\d,]+)", tekst)
    if not m:
        raise BladRynku("Strefa Inwestorów: brak wiersza „Polska 10-letnie”")
    return datetime.strptime(m.group(1), "%d.%m.%Y").date(), float(m.group(2).replace(",", ".")) / 100


def fakt_rentownosc_pl(archiwum: Archiwum, dzien: date, dni_wstecz: int = 7) -> Fakt:
    from silnik.pobieranie.http import BladPobierania

    for i in range(dni_wstecz + 1):
        d = date.fromordinal(dzien.toordinal() - i)
        url = URL_STREFA.format(d=d.strftime("%Y%m%d"))
        try:
            dok = archiwum.po_adresie(url) or _do_archiwum(archiwum, url, "Strefa Inwestorów", "rentowności obligacji", ".html")
        except BladPobierania:
            continue
        dz, r = rentownosc_strefa(archiwum.tekst(dok.id))
        return _fakt(f"rentownosc_10l.{dz.isoformat()}", "rentownosc_10l", Okres(typ="dzien", koniec=dz), r,
                     Jednostka.ulamek, dok.id, {"wiersz": "Polska 10-letnie", "kolumna": "rentowność aktualna"},
                     metoda=Metoda.parser_strony)
    raise BladRynku(f"brak tabeli rentowności Strefy Inwestorów z ostatnich {dni_wstecz} dni")


def fakty_stop(archiwum: Archiwum, rynek: str, dzien: date) -> list[Fakt]:
    wynik = []
    dok = _do_archiwum(archiwum, URL_DAMODARAN, "Damodaran (NYU Stern)", "premie za ryzyko krajów", ".html")
    kraj = "United States" if rynek == "USA" else "Poland"
    d = damodaran_kraj(archiwum.tekst(dok.id), kraj)
    okres = Okres(typ="dzien", koniec=dzien)
    wynik.append(_fakt(f"premia_ryzyka_akcji.{dzien.isoformat()}", "premia_ryzyka_akcji", okres, d["premia_rynku"],
                       Jednostka.ulamek, dok.id, {"kraj": kraj, "kolumna": "Total Equity Risk Premium", "rating": d["rating"]},
                       metoda=Metoda.parser_strony))
    if rynek != "USA":
        wynik.append(_fakt(f"spread_kraju.{dzien.isoformat()}", "spread_kraju", okres, d["spread"], Jednostka.ulamek,
                           dok.id, {"kraj": kraj, "kolumna": "Adj. Default Spread"}, metoda=Metoda.parser_strony))
    if rynek != "USA":
        try:
            wynik.append(fakt_rentownosc_pl(archiwum, dzien))
        except BladRynku:
            pass  # wtedy model albo właściciel podaje --rf
    if rynek == "USA":
        dok_t = _do_archiwum(archiwum, URL_TREASURY.format(rok=dzien.year), "U.S. Treasury", "rentowności obligacji", ".csv")
        dz, r = rentownosc_treasury(archiwum.tekst(dok_t.id))
        wynik.append(_fakt(f"rentownosc_10l.{dz.isoformat()}", "rentownosc_10l", Okres(typ="dzien", koniec=dz), r,
                           Jednostka.ulamek, dok_t.id, {"kolumna": "10 Yr", "dzien": dz.isoformat()}))
    return wynik
