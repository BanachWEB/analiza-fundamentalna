"""Testy bramek stopu (krok 5), bez sieci."""

import json
from datetime import date

import pytest

from silnik.bramki import Wynik, automaty, dowody, ocen
from silnik.fakty.rejestr import RejestrFaktow
from silnik.fakty.schemat import Fakt, TypDokumentu
from silnik.pobieranie.archiwum import Archiwum


def W(id, etap, kat, poziom):
    return Wynik(id, etap, kat, poziom, "opis")


# --- decyzja ------------------------------------------------------------------------------------


def test_stop_z_najwczesniejszego_etapu():
    d = ocen([W("B3.x", 3, "wyplacalnosc_i_jakosc", "stop"), W("B0.y", 0, "rynek_i_status", "stop"),
              W("B1.z", 1, "biegly_i_regulator", "flaga_powazna")])
    assert d.decyzja == "STOP" and d.etap == 0 and d.powod.startswith("B0.y")


def test_pauza_przy_trzech_kategoriach():
    flagi = [W("a", 1, "biegly_i_regulator", "flaga_powazna"), W("b", 2, "kapital", "flaga_powazna"),
             W("c", 3, "wyplacalnosc_i_jakosc", "flaga_powazna")]
    assert ocen(flagi).decyzja == "PAUZA"
    assert ocen(flagi[:2] + [W("d", 2, "kapital", "flaga_powazna")]).decyzja == "DALEJ"  # tylko 2 kategorie


def test_flagi_zwykle_nie_zatrzymuja():
    assert ocen([W("a", 1, "x", "flaga"), W("b", 2, "y", "flaga"), W("c", 3, "z", "flaga")]).decyzja == "DALEJ"


# --- z rejestru ------------------------------------------------------------------------------------


def F(id, v, typ="FY", koniec=None, jedn="pieniadz"):
    k = koniec or date(int(id.split("FY")[1][:4]), 12, 31) if "FY" in id else koniec
    okres = {"typ": typ, "koniec": k}
    if typ == "FY":
        okres["poczatek"] = date(k.year, 1, 1)
    return Fakt(id=id, rodzaj="raportowany", pozycja=id.split(".")[0], okres=okres, wartosc=v, jednostka=jedn,
                waluta="USD" if jedn == "pieniadz" else None, metoda="xbrl", status="zweryfikowany",
                dokument="doc-001", miejsce={"xbrl": "x"})


def test_rozwodnienie_seryjne_i_przeplywy():
    r = RejestrFaktow("X", date(2026, 11, 10))
    for rok, zm in ((2021, 0.2), (2022, 0.15), (2023, 0.02), (2024, 0.3), (2025, 0.01)):
        r.dodaj(F(f"zmiana_liczby_akcji.FY{rok}", zm, jedn="ulamek"))
    for rok in (2023, 2024, 2025):
        r.dodaj(F(f"zysk_netto.FY{rok}", 100))
        r.dodaj(F(f"przeplywy_operacyjne.FY{rok}", 50))
    w = {x.id: x for x in automaty.z_rejestru(r)}
    assert w["B2.rozwodnienie_seryjne"].poziom == "flaga_powazna"
    assert w["B3.przeplywy_do_zysku"].poziom == "flaga"
    assert w["B0.pokrycie"].poziom == "informacja"  # brak danych o liczbie analityków


def test_ujemny_kapital_aktualny_przestarzaly_i_wyjasniony():
    def rej(kap_dzien, skup=0):
        r = RejestrFaktow("X", date(2026, 11, 10))
        r.dodaj(F("aktywa.2026-06-30", 100, "dzien", date(2026, 6, 30)))
        r.dodaj(F(f"kapital_wlasny.{kap_dzien.isoformat()}", -50, "dzien", kap_dzien))
        if skup:
            r.dodaj(F("skup_akcji.FY2025", skup))
        return {x.id: x for x in automaty.z_rejestru(r)}["B3.ujemny_kapital"]
    assert rej(date(2026, 6, 30)).poziom == "stop"
    assert rej(date(2022, 12, 31)).poziom == "brak_danych"
    assert rej(date(2026, 6, 30), skup=80).poziom == "informacja"


def test_kontynuacja_zlozona():
    r = RejestrFaktow("X", date(2026, 11, 10))
    r.dodaj(F("przeplywy_operacyjne.FY2025", -10))
    r.dodaj(F("aktywa_obrotowe.2026-06-30", 5, "dzien", date(2026, 6, 30)))
    r.dodaj(F("zobowiazania_krotkoterminowe.2026-06-30", 20, "dzien", date(2026, 6, 30)))
    wzm = Wynik("B3.kontynuacja_wzmianka", 3, "wyplacalnosc_i_jakosc", "flaga_powazna", "x", ["doc-002: 1 trafień"])
    assert automaty.kontynuacja_zlozona(r, [wzm])[0].poziom == "stop"
    assert automaty.kontynuacja_zlozona(r, [Wynik("B3.kontynuacja_wzmianka", 3, "w", "ok", "x")]) == []


# --- SEC i GPW --------------------------------------------------------------------------------------


def test_z_sec(tmp_path, monkeypatch):
    a = Archiwum("X", tmp_path / "a", tmp_path / "p")
    sub = {"filings": {"recent": {
        "form": ["8-K", "NT 10-K", "10-K", "8-K", "8-K"],
        "filingDate": ["2026-05-01", "2026-03-31", "2026-04-10", "2025-01-10", "2019-01-01"],
        "items": ["4.02,9.01", "", "", "4.01", "4.02"],
        "accessionNumber": ["a1", "a2", "a3", "a4", "a5"]}}}
    d = a.dodaj_tekst(json.dumps(sub), TypDokumentu.sec_api, "SEC", opis="lista raportów")
    efts = tmp_path / "efts.json"
    efts.write_text(json.dumps({"hits": {"total": {"value": 0}}}), encoding="utf-8")

    def falszywe_pobierz(url, **kw):
        p = tmp_path / f"e{abs(hash(url))}.json"
        p.write_text(efts.read_text(), encoding="utf-8")
        return p
    monkeypatch.setattr(automaty, "pobierz", falszywe_pobierz)
    w = {x.id: x for x in automaty.z_sec(a, d.id, 1, date(2026, 11, 10))}
    assert w["B1.korekta_sprawozdan"].poziom == "stop"  # 4.02 w oknie 3 lat
    assert len(w["B1.korekta_sprawozdan"].dowody) == 1  # 4.02 z 2019 poza oknem
    assert w["B1.opoznione_raporty"].poziom == "flaga_powazna"
    assert w["B1.zmiana_bieglego"].poziom == "flaga"
    assert w["B3.kontynuacja_wzmianka"].poziom == "ok"


def test_tabela_gpw():
    html = ("<table><tr><th>Op. na pap.</th><th>Nazwa</th><th>Skrót</th><th>Waluta</th></tr>"
            "<tr><td></td><td>PBG /Z /6,/7</td><td>PBG</td><td>PLN</td></tr>"
            "<tr><td></td><td>REDAN /Z</td><td>RDN</td><td>PLN</td></tr></table>")
    assert automaty.spolki_z_tabeli(html) == [("PBG /Z /6,/7", "PBG"), ("REDAN /Z", "RDN")]


# --- dowody od modelu ---------------------------------------------------------------------------------


def test_dowody_modelu(tmp_path):
    a = Archiwum("X", tmp_path / "a", tmp_path / "p")
    d = a.dodaj_tekst("Akcjonariusz XYZ posiada 93,5% głosów na walnym zgromadzeniu.", TypDokumentu.inny, "spółka")
    testy = {"strukturalny": "tak", "uczciwosc_liczb": "nie", "zarzad_rozwiazuje": "nie dotyczy", "termin": "brak"}
    plik = tmp_path / "bramki_dowody.json"
    plik.write_text(json.dumps({"dowody": [
        {"bramka": "B4.akcjonariusz_90", "poziom": "stop", "dokument": d.id, "cytat": "posiada 93,5% głosów",
         "testy": testy, "warunek_powrotu": "udział poniżej 90%"},
        {"bramka": "B4.oszustwo", "poziom": "stop", "dokument": d.id, "cytat": "spółka fałszowała przychody",
         "testy": testy, "warunek_powrotu": "x"},
        {"bramka": "B5.decyzja_organu", "poziom": "stop", "dokument": d.id, "cytat": "posiada 93,5% głosów"},
        {"bramka": "B9.nieznana", "poziom": "flaga"},
    ]}), encoding="utf-8")
    przyjete, odrzucone = dowody.wczytaj(plik, a)
    assert [w.id for w in przyjete] == ["B4.akcjonariusz_90"]
    assert przyjete[0].zrodlo == "model" and przyjete[0].etap == 4
    assert any("cytatu nie ma" in o for o in odrzucone)
    assert any("czterech testów" in o for o in odrzucone)
    assert any("nieznana bramka" in o for o in odrzucone)


@pytest.mark.parametrize("rynek,n,poziom", [("USA", 58, "ok"), ("USA", 3, "flaga_powazna"), ("GPW", 3, "flaga"),
                                           ("GPW", 7, "ok")])
def test_pokrycie_wg_zasad(rynek, n, poziom):
    r = RejestrFaktow("X", date(2026, 11, 10))
    r.dodaj(Fakt(id="liczba_analitykow.2026-11-10", rodzaj="raportowany", pozycja="liczba_analitykow",
                 okres={"typ": "dzien", "koniec": date(2026, 11, 10)}, wartosc=n, jednostka="liczba",
                 metoda="parser_strony", status="jedno_zrodlo", dokument="doc-001", miejsce={}))
    w = {x.id: x for x in automaty.z_rejestru(r, rynek=rynek)}
    assert w["B0.pokrycie"].poziom == poziom
