"""Testy poprawek braków silnika wykrytych przy analizie LTRX (11.11.2026), bez sieci."""

import json
from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from silnik.bramki import automaty, konfiguracja
from silnik.fakty import cytat
from silnik.fakty.rejestr import RejestrFaktow
from silnik.fakty.schemat import Fakt
from silnik.obliczenia import raport, scenariusze, wskazniki, wycena
from silnik.obliczenia.kalkulator import Kalkulator
from silnik.pobieranie import konsensus, rynek, sec

D = date(2026, 11, 9)


def F(id, v, typ="dzien", koniec=D, poczatek=None, jedn="pieniadz", rodzaj="raportowany", status="zweryfikowany"):
    okres = {"typ": typ} if typ == "brak" else {"typ": typ, "koniec": koniec}
    if poczatek:
        okres["poczatek"] = poczatek
    kw = dict(rodzaj=rodzaj, metoda="api", dokument="doc-001", miejsce={})
    if rodzaj == "zalozenie":
        kw = dict(rodzaj=rodzaj, metoda="kod", uzasadnienie="test")
    return Fakt(id=id, pozycja=id.split(".")[0], okres=okres, wartosc=v, jednostka=jedn,
                waluta="USD" if jedn in ("pieniadz", "pieniadz_na_akcje") else None, status=status, **kw)


def FY(id, v, rok, jedn="pieniadz"):
    return F(id, v, "FY", date(rok, 6, 30), date(rok - 1, 7, 1), jedn)


# --- 1. koszt sprzedaży: znacznik, który spełnia tożsamość z zyskiem brutto -----------------------


def _wpis(val, accn="0001", start="2025-07-01", end="2026-06-30"):
    return {"val": val, "start": start, "end": end, "accn": accn, "form": "10-K", "fy": 2026, "fp": "FY",
            "filed": "2026-09-10"}


MAPA_KOSZT = {
    "przychody": {"rodzaj": "okres", "jednostka": "pieniadz", "znaczniki": ["Revenues"]},
    "koszt_sprzedazy": {"rodzaj": "okres", "jednostka": "pieniadz",
                        "znaczniki": ["CostOfRevenue", "CostOfGoodsAndServicesSold"],
                        "tozsamosc": {"plus": "przychody", "wynik": "zysk_brutto"}},
    "zysk_brutto": {"rodzaj": "okres", "jednostka": "pieniadz", "znaczniki": ["GrossProfit"]},
}


def _facts(**znaczniki):
    return {"facts": {"us-gaap": {t: {"units": {"USD": w}} for t, w in znaczniki.items()}}}


def test_koszt_sprzedazy_wg_tozsamosci():
    # LTRX FY2026: CostOfRevenue to drobna pozycja (255 tys. USD), pełny koszt jest pod CostOfGoodsAndServicesSold
    f = _facts(Revenues=[_wpis(122_000_000)], CostOfRevenue=[_wpis(255_000)],
               CostOfGoodsAndServicesSold=[_wpis(67_976_000)], GrossProfit=[_wpis(54_024_000)])
    x = {x.id: x for x in sec.wyciagnij_fakty(f, "doc-001", MAPA_KOSZT)}["koszt_sprzedazy.FY2026"]
    assert x.wartosc == 67_976_000
    assert x.miejsce["xbrl"] == "us-gaap:CostOfGoodsAndServicesSold"
    assert any(c.startswith("znacznik_wg_tozsamosci") for c in x.kontrole)


def test_koszt_sprzedazy_bez_tozsamosci_zostaje_pierwszy_znacznik():
    # żaden znacznik nie spełnia tożsamości: zostaje pierwszy z listy, konflikt pokaże weryfikacja
    f = _facts(Revenues=[_wpis(100)], CostOfRevenue=[_wpis(10)], CostOfGoodsAndServicesSold=[_wpis(20)],
               GrossProfit=[_wpis(50)])
    x = {x.id: x for x in sec.wyciagnij_fakty(f, "doc-001", MAPA_KOSZT)}["koszt_sprzedazy.FY2026"]
    assert x.wartosc == 10 and not x.kontrole
    # zysk brutto z innego raportu (accn) nie rozstrzyga wyboru
    f = _facts(Revenues=[_wpis(100)], CostOfRevenue=[_wpis(10)], CostOfGoodsAndServicesSold=[_wpis(60)],
               GrossProfit=[_wpis(40, accn="0002")])
    assert {x.id: x for x in sec.wyciagnij_fakty(f, "doc-001", MAPA_KOSZT)}["koszt_sprzedazy.FY2026"].wartosc == 10


def test_mapowanie_kosztu_sprzedazy_ma_tozsamosc():
    import yaml
    mapa = yaml.safe_load((sec.KONFIGURACJA / "mapowanie-us-gaap.yaml").read_text(encoding="utf-8"))
    assert mapa["koszt_sprzedazy"]["tozsamosc"] == {"plus": "przychody", "wynik": "zysk_brutto"}


# --- 2. dług netto ÷ EBITDA ----------------------------------------------------------------------


def _rejestr_dlugu(ebitda_zysk, gotowka):
    r = RejestrFaktow("X", D)
    B = date(2026, 6, 30)
    for fakt in (FY("przychody.FY2026", 120, 2026), FY("zysk_operacyjny.FY2026", ebitda_zysk, 2026),
                 FY("amortyzacja.FY2026", 2, 2026), F("dlug_dlugoterminowy.2026-06-30", 10, koniec=B),
                 F("gotowka.2026-06-30", gotowka, koniec=B)):
        r.dodaj(fakt)
    k = Kalkulator(r)
    wskazniki.dla_okresu(k, "FY2026", FY("x.FY2026", 0, 2026).okres, B, None)
    return k


def test_dlug_netto_do_ebitda_przy_ujemnej_ebitda_nie_ma_sensu():
    k = _rejestr_dlugu(ebitda_zysk=-8, gotowka=30)  # EBITDA −6, dług netto −20
    assert k.fakt("dlug_netto.2026-06-30").wartosc == -20
    assert k.fakt("dlug_netto_do_ebitda.FY2026") is None
    assert any("EBITDA ≤ 0" in b for b in k.braki)
    assert raport.komorka(k, "dlug_netto_do_ebitda", "FY2026") == "gotówka netto"


def test_dlug_netto_do_ebitda_gotowka_netto_przy_dodatniej_ebitda():
    k = _rejestr_dlugu(ebitda_zysk=8, gotowka=30)  # EBITDA 10, dług netto −20
    # fakt zostaje (karta Treli daje za gotówkę netto pełne punkty), raport pokazuje opis
    assert k.fakt("dlug_netto_do_ebitda.FY2026").wartosc == pytest.approx(-2.0)
    assert raport.komorka(k, "dlug_netto_do_ebitda", "FY2026") == "gotówka netto"


def test_dlug_netto_do_ebitda_przy_dlugu_netto():
    k = _rejestr_dlugu(ebitda_zysk=8, gotowka=5)  # EBITDA 10, dług netto 5
    assert k.fakt("dlug_netto_do_ebitda.FY2026").wartosc == pytest.approx(0.5)
    assert raport.komorka(k, "dlug_netto_do_ebitda", "FY2026") == "0,50"


# --- 3. scenariusze: wartość kapitału = wartość przepływów − dług netto ---------------------------


def _rejestr_scenariuszy(dlug_netto):
    r = RejestrFaktow("X", D)
    r.dodaj(F("kurs.2026-11-09", 10.0, jedn="pieniadz_na_akcje"))
    r.dodaj(F("akcje_w_obrocie.2026-11-09", 100.0, jedn="akcje"))
    r.dodaj(F("przychody.TTM2026-11-09", 1000.0, "TTM", poczatek=D - timedelta(days=364)))
    r.dodaj(F("wzrost_rezydualny.zalozenie", 0.025, "brak", jedn="ulamek", rodzaj="zalozenie"))
    r.dodaj(F("koszt_kapitalu_wlasnego.2026-11-09", 0.09, jedn="ulamek"))
    r.wylicz("kapitalizacja.2026-11-09", "kapitalizacja", "kurs × akcje", ["kurs.2026-11-09", "akcje_w_obrocie.2026-11-09"],
             lambda a, b: a * b, "pieniadz", {"typ": "dzien", "koniec": D}, "USD")
    w = {"kapitalizacja": "kapitalizacja.2026-11-09", "ke": "koszt_kapitalu_wlasnego.2026-11-09",
         "okres_bazowy": "TTM2026-11-09"}
    if dlug_netto is not None:
        r.dodaj(F("dlug_netto.2026-06-30", dlug_netto, koniec=date(2026, 6, 30)))
        r.wylicz("ev.2026-11-09", "ev", "kapitalizacja + dlug_netto", ["kapitalizacja.2026-11-09", "dlug_netto.2026-06-30"],
                 lambda c, x: c + x, "pieniadz", {"typ": "dzien", "koniec": D}, "USD")
        w["ev"] = "ev.2026-11-09"
    return r, w


def _scen(tmp_path):
    p = tmp_path / "scenariusze.json"
    p.write_text(json.dumps({"scenariusze": [
        {"nazwa": "byk", "prawdopodobienstwo": 0.5, "wzrost_przychodow": 0.08, "marza_fcf": 0.10, "uzasadnienie": "t"},
        {"nazwa": "niedzwiedz", "prawdopodobienstwo": 0.5, "wzrost_przychodow": 0.0, "marza_fcf": 0.05,
         "uzasadnienie": "t"}]}), encoding="utf-8")
    return p


def test_scenariusze_dodaja_gotowke_netto(tmp_path):
    r0, w0 = _rejestr_scenariuszy(None)
    scenariusze.oblicz(Kalkulator(r0), _scen(tmp_path), w0)
    r, w = _rejestr_scenariuszy(-300.0)  # gotówka netto 300 USD = 3 USD na akcję
    scenariusze.oblicz(Kalkulator(r), _scen(tmp_path), w)
    for n in ("byk", "niedzwiedz"):
        f = r[f"wartosc_na_akcje.{n}"]
        assert "dlug_netto.2026-06-30" in f.wejscia
        assert "− dlug_netto" in f.wzor
        assert f.wartosc == pytest.approx(r0[f"wartosc_na_akcje.{n}"].wartosc + 3.0)
        # stopa implikowana: przy niej wartość kapitału na akcję równa się kursowi
        st = r[f"stopa_zwrotu_implikowana.{n}"]
        assert "dlug_netto.2026-06-30" in st.wejscia
        v = scenariusze.wartosc_kapitalu(1000.0, r[f"scenariusz_wzrost_przychodow.{n}"].wartosc, 10, 0.025, st.wartosc,
                                         r[f"scenariusz_marza_fcf.{n}"].wartosc, -300.0) / 100
        assert v == pytest.approx(10.0, rel=1e-4)


def test_scenariusze_odejmuja_dlug_netto(tmp_path):
    r0, w0 = _rejestr_scenariuszy(None)
    scenariusze.oblicz(Kalkulator(r0), _scen(tmp_path), w0)
    r, w = _rejestr_scenariuszy(200.0)
    scenariusze.oblicz(Kalkulator(r), _scen(tmp_path), w)
    assert r["wartosc_na_akcje.byk"].wartosc == pytest.approx(r0["wartosc_na_akcje.byk"].wartosc - 2.0)


def test_scenariusze_bez_dlugu_netto_zapisuja_brak(tmp_path):
    r, w = _rejestr_scenariuszy(None)
    k = Kalkulator(r)
    scenariusze.oblicz(k, _scen(tmp_path), w)
    assert "bez długu netto" in r["wartosc_na_akcje.byk"].wzor
    assert any(b.startswith("scenariusze: brak długu netto") for b in k.braki)


# --- 4. rozwodnienie: liczba akcji na koniec okresu ----------------------------------------------


def test_zmiana_liczby_akcji_na_koniec_okresu_i_bramka():
    # LTRX FY2026: średnia ważona +4,0%, liczba akcji na koniec okresu z 39,1 mln do 46,6 mln (+19%)
    r = RejestrFaktow("X", D)
    for rok, prz in ((2025, 120), (2026, 122)):
        r.dodaj(FY(f"przychody.FY{rok}", prz, rok))
    r.dodaj(FY("liczba_akcji_rozwodniona.FY2025", 38_500_000, 2025, "akcje"))
    r.dodaj(FY("liczba_akcji_rozwodniona.FY2026", 40_040_000, 2026, "akcje"))
    r.dodaj(F("akcje_koniec_okresu.2025-06-30", 39_102_563, koniec=date(2025, 6, 30), jedn="akcje"))
    r.dodaj(F("akcje_koniec_okresu.2026-06-30", 46_594_283, koniec=date(2026, 6, 30), jedn="akcje"))
    k = Kalkulator(r)
    wskazniki.dynamika(k)
    assert r["zmiana_liczby_akcji.FY2026"].wartosc == pytest.approx(0.04)
    koniec = r["zmiana_liczby_akcji_koniec.FY2026"]
    assert koniec.wartosc == pytest.approx(46_594_283 / 39_102_563 - 1)
    assert koniec.wejscia == ["akcje_koniec_okresu.2026-06-30", "akcje_koniec_okresu.2025-06-30"]

    assert konfiguracja()["progi"]["rozwodnienie_roczne"] == 0.10  # próg bez zmian
    w = {x.id: x for x in automaty.z_rejestru(r)}
    assert w["B2.rozwodnienie"].poziom == "flaga"
    assert "zmiana_liczby_akcji_koniec.FY2026" in w["B2.rozwodnienie"].dowody
    assert "na koniec okresu" in w["B2.rozwodnienie"].opis


def test_akcje_na_koniec_z_akcji_w_obrocie():
    # GPW: brak liczby akcji z bilansu, jest liczba akcji w obrocie z dnia bilansowego (±5 dni)
    r = RejestrFaktow("X", D)
    for rok in (2025, 2026):
        r.dodaj(FY(f"przychody.FY{rok}", 100, rok))
    r.dodaj(F("akcje_w_obrocie.2025-07-02", 100, koniec=date(2025, 7, 2), jedn="akcje"))
    r.dodaj(F("akcje_w_obrocie.2026-06-30", 105, koniec=date(2026, 6, 30), jedn="akcje"))
    wskazniki.dynamika(Kalkulator(r))
    assert r["zmiana_liczby_akcji_koniec.FY2026"].wartosc == pytest.approx(0.05)


# --- 5. test cytatu: zera końcowe ----------------------------------------------------------------


def test_cytat_z_zerami_koncowymi():
    assert cytat.liczba_w_cytacie(7.2, "public offering at a price of $7.20 per share")
    assert cytat.liczba_w_cytacie(7.2, "cena emisyjna 7,20 zł")
    assert cytat.liczba_w_cytacie(0.5, "wzrost o 0.500 pkt")
    assert not cytat.liczba_w_cytacie(7.2, "price of $7.21 per share")
    assert not cytat.liczba_w_cytacie(7.2, "price of $17.20 per share")
    assert not cytat.liczba_w_cytacie(7.2, "price of $7.205 per share")


# --- 6. schemat: skala „jedn” dla ułamka i liczby ------------------------------------------------


@pytest.mark.parametrize("jedn", ["ulamek", "liczba"])
def test_schemat_odrzuca_skale_dla_ulamka_i_liczby(jedn):
    kw = dict(id="pracownicy.2026-06-30", rodzaj="raportowany", pozycja="pracownicy",
              okres={"typ": "dzien", "koniec": date(2026, 6, 30)}, wartosc=443, jednostka=jedn,
              metoda="api", status="jedno_zrodlo", dokument="doc-001")
    with pytest.raises(ValidationError, match="skali „jedn”"):
        Fakt(skala="tys", **kw)
    assert Fakt(skala="jedn", **kw).wartosc == 443
    # kwoty pieniężne skalę mają
    assert Fakt(**{**kw, "jednostka": "pieniadz", "waluta": "USD", "skala": "tys"}).wartosc_bazowa() == 443_000


# --- 7. RSI 14-dniowy i cena ÷ sprzedaż na rok naprzód (informacja) -------------------------------


def _sesje(ceny):
    return [rynek.Sesja(date(2026, 1, 1) + timedelta(days=i), c, 1000) for i, c in enumerate(ceny)]


def test_rsi():
    assert rynek.rsi(_sesje(range(10))) is None  # za krótka historia
    assert rynek.rsi(_sesje([100 + i for i in range(30)])) == 100.0  # same wzrosty
    assert rynek.rsi(_sesje([100 - i for i in range(30)])) == pytest.approx(0.0)
    # naprzemiennie +1 / −1: wzrosty i spadki równe → RSI blisko 50
    assert rynek.rsi(_sesje([100 + (i % 2) for i in range(201)])) == pytest.approx(50, abs=2)
    ids = {f.pozycja for f in rynek.fakty_z_historii(_sesje([100 + (i % 3) for i in range(100)]), ["doc-001"], "USD")}
    assert "rsi_14" in ids


def test_konsensus_przychodow_i_c_s():
    html = ('According to 6 analysts polled by S&amp;P Global, X has an average price target of $10.58 '
            'epsThis:{last:.15,this:.2275,growth:51.6} revenue:{"2027-06-30":{no:6,avg:137782330,low:1,high:2}')
    d = konsensus.parsuj(html)
    assert d["przychody_konsensus"] == (date(2027, 6, 30), 6, 137782330.0)

    r = RejestrFaktow("X", D)
    r.dodaj(F("kurs.2026-11-09", 5.0, jedn="pieniadz_na_akcje"))
    r.dodaj(F("akcje_w_obrocie.2026-11-09", 40_000_000, jedn="akcje"))
    r.dodaj(Fakt(id="przychody_konsensus.2027-06-30", rodzaj="prognoza", pozycja="przychody_konsensus",
                 okres={"typ": "FY", "koniec": date(2027, 6, 30)}, wartosc=137_782_330, jednostka="pieniadz",
                 waluta="USD", metoda="parser_strony", status="jedno_zrodlo", dokument="doc-001",
                 dostawca="S&P Global", data_prognozy=D, liczba_analitykow=6))
    k = Kalkulator(r)
    w = wycena.oblicz(k, None, "USA")
    assert r[w["c_s_konsensus"]].wartosc == pytest.approx(200_000_000 / 137_782_330)
    assert "przychody_konsensus.2027-06-30" in r[w["c_s_konsensus"]].wejscia
