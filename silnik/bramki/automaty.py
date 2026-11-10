"""Bramki sprawdzane automatycznie: z rejestru faktów, z danych SEC i ze stron GPW."""

from __future__ import annotations

import json
import re
from datetime import date, timedelta
from typing import Optional

from lxml import html as lhtml

from silnik.fakty.rejestr import RejestrFaktow
from silnik.fakty.schemat import Status, TypDokumentu
from silnik.pobieranie.archiwum import Archiwum
from silnik.pobieranie.http import BladPobierania, pobierz

from . import Wynik, konfiguracja


def _pl(x: float) -> str:
    return f"{x:.2f}".replace(".", ",")


def _fy(r: RejestrFaktow, pozycja: str):
    return sorted([f for f in r.fakty() if f.pozycja == pozycja and f.okres.typ.value == "FY" and f.status != Status.odrzucony],
                  key=lambda f: f.okres.koniec)


def _ostatni_stan(r: RejestrFaktow, pozycja: str):
    s = [f for f in r.fakty() if f.pozycja == pozycja and f.okres.typ.value == "dzien" and f.status != Status.odrzucony]
    return max(s, key=lambda f: f.okres.koniec) if s else None


# --- z rejestru faktów ----------------------------------------------------------------------


def z_rejestru(r: RejestrFaktow, finansowa: bool = False, rynek: str = "USA") -> list[Wynik]:
    p = konfiguracja()["progi"]
    w: list[Wynik] = []

    # B0: pokrycie analityczne (zasady właściciela v1.6)
    an = _ostatni_stan(r, "liczba_analitykow")
    prog, duze = p["analitycy_wystarczy_ponad"], p["analitycy_duze_ponad"]
    if an is None:
        w.append(Wynik("B0.pokrycie", 0, "rynek_i_status", "informacja",
                       "Brak danych o liczbie analityków — pokrycia nie można ocenić" +
                       (" (dla GPW: wklejka z InvestingPro)" if rynek == "GPW" else "")))
    else:
        n = int(an.wartosc)
        skala = "duże" if n > duze else ("średnie" if n >= 3 else "słabe")
        if n > prog:
            w.append(Wynik("B0.pokrycie", 0, "rynek_i_status", "ok", f"Pokrycie analityczne {skala} ({n} analityków)", [an.id]))
        elif rynek == "USA":
            w.append(Wynik("B0.pokrycie", 0, "rynek_i_status", "flaga_powazna",
                           f"Pokrycie analityczne {skala} ({n} analityków) — wg twoich zasad: spółki zagranicznej "
                           "z 3 analitykami lub mniej nie kupujesz", [an.id]))
        else:
            w.append(Wynik("B0.pokrycie", 0, "rynek_i_status", "flaga",
                           f"Pokrycie analityczne małe ({n} analityków) — na GPW to tylko flaga; "
                           "nie można polegać na konsensusie", [an.id]))

    # B2: rozwodnienie
    zm = _fy(r, "zmiana_liczby_akcji")[-5:]
    ponad = [f for f in zm if f.wartosc > p["rozwodnienie_roczne"]]
    if len(ponad) >= p["rozwodnienie_seryjne_lat"]:
        w.append(Wynik("B2.rozwodnienie_seryjne", 2, "kapital", "flaga_powazna",
                       f"Liczba akcji rosła o ponad {p['rozwodnienie_roczne']:.0%} r/r w {len(ponad)} z {len(zm)} ostatnich lat; "
                       "sprawdź, czy emisje szły bez prawa poboru (wtedy STOP wymaga dowodu)", [f.id for f in ponad]))
    elif ponad:
        w.append(Wynik("B2.rozwodnienie", 2, "kapital", "flaga",
                       f"Liczba akcji wzrosła o ponad {p['rozwodnienie_roczne']:.0%} r/r", [f.id for f in ponad]))
    elif zm:
        w.append(Wynik("B2.rozwodnienie", 2, "kapital", "ok", "Brak rozwodnienia powyżej progu", [zm[-1].id]))
    else:
        w.append(Wynik("B2.rozwodnienie", 2, "kapital", "brak_danych", "Brak danych o liczbie akcji"))

    if finansowa:  # bank: przepływy operacyjne, M-score i Z'' nie mają sensu; kapitał ocenia model (CET1)
        w.append(Wynik("B3.finanse", 3, "wyplacalnosc_i_jakosc", "informacja",
                       "Spółka finansowa: przepływy ÷ zysk, M-score i Z'' pominięte; adekwatność kapitałową (CET1) ocenia model"))
        return w
    # B3: przepływy operacyjne a zysk netto (3 lata)
    cfo = {f.id.split(".", 1)[1]: f for f in _fy(r, "przeplywy_operacyjne")}
    ni = {f.id.split(".", 1)[1]: f for f in _fy(r, "zysk_netto")}
    lata = [s for s in ni if s in cfo][-3:]
    if len(lata) == 3:
        s_cfo, s_ni = sum(cfo[s].wartosc_bazowa() for s in lata), sum(ni[s].wartosc_bazowa() for s in lata)
        ids = [cfo[s].id for s in lata] + [ni[s].id for s in lata]
        if s_ni > 0 and s_cfo / s_ni < p["przeplywy_do_zysku"]:
            w.append(Wynik("B3.przeplywy_do_zysku", 3, "wyplacalnosc_i_jakosc", "flaga",
                           f"Przepływy operacyjne z 3 lat to {s_cfo / s_ni:.0%} zysku netto (próg {p['przeplywy_do_zysku']:.0%})", ids))
        else:
            w.append(Wynik("B3.przeplywy_do_zysku", 3, "wyplacalnosc_i_jakosc", "ok",
                           "Przepływy operacyjne pokrywają zysk netto" if s_ni > 0 else "Zysk netto z 3 lat ≤ 0 (patrz wskaźniki)", ids))
    m = _fy(r, "beneish_m")
    if m:
        poziom = "flaga" if m[-1].wartosc > p["beneish_m"] else "ok"
        w.append(Wynik("B3.beneish", 3, "wyplacalnosc_i_jakosc", poziom,
                       f"Beneish M-score {_pl(m[-1].wartosc)} (próg {_pl(p['beneish_m'])}): "
                       + ("sprawdź należności i memoriały" if poziom == "flaga" else "poniżej progu"), [m[-1].id]))
    z = _fy(r, "altman_z2")
    if z:
        poziom = "flaga_powazna" if z[-1].wartosc < p["altman_z2"] else "ok"
        w.append(Wynik("B3.altman", 3, "wyplacalnosc_i_jakosc", poziom,
                       f"Altman Z'' {_pl(z[-1].wartosc)} (strefa zagrożenia poniżej {_pl(p['altman_z2'])})", [z[-1].id]))
    # ujemny kapitał: tylko z aktualnego bilansu (nie starszego niż 100 dni od najnowszych aktywów)
    aktywa = _ostatni_stan(r, "aktywa")
    kandydaci = [f for f in (_ostatni_stan(r, "kapital_wlasny"), _ostatni_stan(r, "kapital_wlasny_z_udzialami_niekontrolujacymi")) if f]
    kw = max(kandydaci, key=lambda f: f.okres.koniec) if kandydaci else None
    if kw and aktywa and (aktywa.okres.koniec - kw.okres.koniec).days > 100:
        w.append(Wynik("B3.ujemny_kapital", 3, "wyplacalnosc_i_jakosc", "brak_danych",
                       f"Kapitał własny tylko z {kw.okres.koniec.isoformat()}, a aktywa z {aktywa.okres.koniec.isoformat()}: "
                       "brak aktualnego kapitału (spółka zmieniła znacznik?)", [kw.id]))
    elif kw and kw.wartosc < 0:
        skup = sum(f.wartosc_bazowa() for f in _fy(r, "skup_akcji")[-5:])
        if skup > abs(kw.wartosc_bazowa()):
            w.append(Wynik("B3.ujemny_kapital", 3, "wyplacalnosc_i_jakosc", "informacja",
                           "Ujemny kapitał własny wyjaśniony skupem akcji z 5 lat", [kw.id]))
        else:
            w.append(Wynik("B3.ujemny_kapital", 3, "wyplacalnosc_i_jakosc", "stop",
                           f"Ujemny kapitał własny na {kw.okres.koniec.isoformat()}, niewyjaśniony skupem akcji", [kw.id],
                           warunek_powrotu="kapitał własny dodatni albo wyjaśniony skupem akcji"))
    return w


# --- SEC ----------------------------------------------------------------------------------------

URL_EFTS = ("https://efts.sec.gov/LATEST/search-index?q=%22{q}%22&forms={formy}&dateRange=custom"
            "&startdt={od}&enddt={do}&ciks={cik:010d}")


def kontynuacja_zlozona(r: RejestrFaktow, wyniki: list[Wynik]) -> list[Wynik]:
    """STOP B3.kontynuacja: wzmianka o istotnej niepewności + ujemne przepływy operacyjne
    + zobowiązania krótkoterminowe wyższe niż aktywa obrotowe (dług do spłaty bez pokrycia)."""
    wzm = next((x for x in wyniki if x.id == "B3.kontynuacja_wzmianka" and x.poziom == "flaga_powazna"), None)
    if not wzm:
        return []
    cfo = _fy(r, "przeplywy_operacyjne")
    ao, zk = _ostatni_stan(r, "aktywa_obrotowe"), _ostatni_stan(r, "zobowiazania_krotkoterminowe")
    if not (cfo and ao and zk):
        return []
    if cfo[-1].wartosc < 0 and zk.wartosc_bazowa() > ao.wartosc_bazowa():
        return [Wynik("B3.kontynuacja", 3, "wyplacalnosc_i_jakosc", "stop",
                      "Istotna niepewność kontynuacji działalności w raporcie, ujemne przepływy operacyjne i zobowiązania "
                      "krótkoterminowe wyższe niż aktywa obrotowe", wzm.dowody + [cfo[-1].id, ao.id, zk.id],
                      warunek_powrotu="raport bez zastrzeżenia o kontynuacji działalności i dodatnie przepływy operacyjne")]
    return []


def z_sec(archiwum: Archiwum, dok_submissions: str, cik: int, dzien: date) -> list[Wynik]:
    p = konfiguracja()["progi"]
    d = json.loads(archiwum.tekst(dok_submissions))["filings"]["recent"]
    granica = dzien - timedelta(days=365 * p["lata_sec"])
    zgl = [(d["form"][i], date.fromisoformat(d["filingDate"][i]), d.get("items", [""] * len(d["form"]))[i] or "",
            d["accessionNumber"][i]) for i in range(len(d["form"]))]
    zgl = [z for z in zgl if z[1] >= granica]
    w: list[Wynik] = []

    nt = [z for z in zgl if z[0] in ("NT 10-K", "NT 10-Q")]
    w.append(Wynik("B1.opoznione_raporty", 1, "biegly_i_regulator", "flaga_powazna" if nt else "ok",
                   (f"{len(nt)} zawiadomień o opóźnieniu raportu (NT) w {p['lata_sec']} latach; przyczynę sprawdza model "
                    "(przyczyny księgowe = STOP)") if nt else "Brak zawiadomień NT 10-K/NT 10-Q",
                   [f"{dok_submissions}: {z[0]} {z[1]} {z[3]}" for z in nt]))
    korekty = [z for z in zgl if z[0].startswith("8-K") and "4.02" in z[2]]
    w.append(Wynik("B1.korekta_sprawozdan", 1, "biegly_i_regulator", "stop" if korekty else "ok",
                   "Spółka ogłosiła, że wcześniejszym sprawozdaniom nie można ufać (8-K, pozycja 4.02)" if korekty
                   else "Brak 8-K z pozycją 4.02 (korekta sprawozdań)",
                   [f"{dok_submissions}: 8-K 4.02 {z[1]} {z[3]}" for z in korekty],
                   warunek_powrotu="pełny rok raportów bez nowych korekt i z czystą opinią biegłego" if korekty else None))
    zmiany = [z for z in zgl if z[0].startswith("8-K") and "4.01" in z[2]]
    w.append(Wynik("B1.zmiana_bieglego", 1, "biegly_i_regulator", "flaga" if zmiany else "ok",
                   "Zmiana biegłego rewidenta (8-K, pozycja 4.01); model sprawdza, czy były spory" if zmiany
                   else "Brak zmiany biegłego rewidenta", [f"{dok_submissions}: 8-K 4.01 {z[1]} {z[3]}" for z in zmiany]))

    # pełnotekstowe wyszukiwanie w ostatnich raportach okresowych
    roczne = [z for z in zgl if z[0] in ("10-K", "10-K/A")]
    od = (max(z[1] for z in roczne) - timedelta(days=1)) if roczne else granica
    for q, bid, opis_t, poziom_t in (
        ("substantial doubt", "B3.kontynuacja_wzmianka", "Raport okresowy wspomina o istotnej niepewności kontynuacji działalności "
         "(„substantial doubt”); STOP, jeśli do tego ujemne przepływy i dług do spłaty bez finansowania", "flaga_powazna"),
        ("material weakness", "B1.slabosc_kontroli_wzmianka", "Raport roczny wspomina o istotnej słabości kontroli wewnętrznej "
         "(„material weakness”); często to ogólny opis ryzyka — model sprawdza; STOP, jeśli słabość jest nieusunięta", "flaga"),
    ):
        formy = "10-K,10-Q" if q == "substantial doubt" else "10-K"
        url = URL_EFTS.format(q=q.replace(" ", "%20"), formy=formy, od=od.isoformat(), do=dzien.isoformat(), cik=cik)
        try:
            dok = archiwum.po_adresie(url) or _do_archiwum(archiwum, url, "SEC EDGAR (wyszukiwanie)", f"wyszukiwanie: {q}", ".json")
            trafienia = json.loads(archiwum.tekst(dok.id))["hits"]["total"]["value"]
        except (BladPobierania, KeyError, ValueError):
            w.append(Wynik(bid, 1 if "B1" in bid else 3, "biegly_i_regulator" if "B1" in bid else "wyplacalnosc_i_jakosc",
                           "brak_danych", f"Wyszukiwanie „{q}” niedostępne"))
            continue
        etap = 1 if "B1" in bid else 3
        kat = "biegly_i_regulator" if etap == 1 else "wyplacalnosc_i_jakosc"
        w.append(Wynik(bid, etap, kat, poziom_t if trafienia else "ok",
                       opis_t if trafienia else f"Brak wzmianki „{q}” w raportach od {od.isoformat()}",
                       [f"{dok.id}: {trafienia} trafień od {od.isoformat()}"]))
    return w


# --- GPW ------------------------------------------------------------------------------------------

STRONY_GPW = {
    "lista_alertow": "https://www.gpw.pl/lista-alertow-notowania",
    "oznaczenie_ciagle": "https://www.gpw.pl/spolki-ze-szczegolnym-oznaczeniem-notowania-ciagle",
    "oznaczenie_jednolite": "https://www.gpw.pl/spolki-ze-szczegolnym-oznaczeniem-notowania-jednolite",
    "zawieszenia": "https://www.gpw.pl/zawieszenia-i-wykluczenia",
}


def _do_archiwum(archiwum: Archiwum, url: str, zrodlo: str, opis: str, rozszerzenie: str):
    plik = pobierz(url, rozszerzenie=rozszerzenie)
    try:
        return archiwum.dodaj_plik(plik, TypDokumentu.strona, zrodlo, adres=url, opis=opis)
    finally:
        plik.unlink(missing_ok=True)


def spolki_z_tabeli(tresc: str) -> list[tuple[str, str]]:
    """(nazwa z oznaczeniem, skrót) z tabel notowań GPW."""
    wynik = []
    for tb in lhtml.fromstring(tresc).xpath("//table"):
        naglowki = [" ".join(th.text_content().split()) for th in tb.xpath(".//tr[1]/th|.//tr[1]/td")]
        if "Skrót" not in naglowki or "Nazwa" not in naglowki:
            continue
        i_n, i_s = naglowki.index("Nazwa"), naglowki.index("Skrót")
        for tr in tb.xpath(".//tr")[1:]:
            k = [" ".join(td.text_content().split()) for td in tr.xpath("./td|./th")]
            if len(k) > max(i_n, i_s) and k[i_s]:
                wynik.append((k[i_n], k[i_s]))
    return wynik


def z_gpw(archiwum: Archiwum, ticker: str, nazwa: Optional[str] = None) -> list[Wynik]:
    w: list[Wynik] = []
    ticker = ticker.upper()
    for klucz, url in STRONY_GPW.items():
        try:
            dok = _do_archiwum(archiwum, url, "GPW", klucz.replace("_", " "), ".html")
        except BladPobierania as e:
            w.append(Wynik(f"B0.{klucz}", 0, "rynek_i_status", "brak_danych", f"Strona GPW niedostępna: {e}"))
            continue
        tresc = archiwum.tekst(dok.id)
        if klucz == "zawieszenia":
            tekst = " ".join(lhtml.fromstring(tresc).text_content().split())
            szukane = [s for s in {ticker, (nazwa or "").upper()} if s]
            trafienia = [s for s in szukane if re.search(rf"\b{re.escape(s)}\b", tekst)]
            w.append(Wynik("B0.zawieszenie", 0, "rynek_i_status", "flaga_powazna" if trafienia else "ok",
                           ("Spółka występuje w komunikatach GPW o zawieszeniach i wykluczeniach; model sprawdza, czy obrót "
                            "jest zawieszony (wtedy STOP)") if trafienia else "Brak spółki w komunikatach o zawieszeniach",
                           [f"{dok.id}: {', '.join(trafienia)}"] if trafienia else [dok.id]))
            continue
        spolki = spolki_z_tabeli(tresc)
        moja = [(n, s) for n, s in spolki if s.upper() == ticker]
        if klucz == "lista_alertow":
            w.append(Wynik("B0.lista_alertow", 0, "rynek_i_status", "stop" if moja else "ok",
                           "Spółka jest na Liście Alertów GPW" if moja else "Spółki nie ma na Liście Alertów GPW",
                           [f"{dok.id}: {moja[0][0]}"] if moja else [dok.id],
                           warunek_powrotu="spółka zdjęta z Listy Alertów" if moja else None))
        else:
            w.append(Wynik(f"B0.{klucz}", 0, "rynek_i_status", "flaga_powazna" if moja else "ok",
                           (f"Spółka ma szczególne oznaczenie GPW ({moja[0][0]}); model sprawdza przyczynę: upadłość, "
                            "restrukturyzacja albo likwidacja = STOP") if moja else "Brak szczególnego oznaczenia GPW",
                           [f"{dok.id}: {moja[0][0]}"] if moja else [dok.id]))
    return w
