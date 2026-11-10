"""Wskaźniki jakości zysków i ryzyka: Piotroski F-score, Beneish M-score, Altman Z''.

To diagnostyka, nie wyrok (specyfikacja, część 4): wynik poza progiem daje
flagę do sprawdzenia, a nie stop. Wskaźniki nie mają sensu dla banków
i ubezpieczycieli; dla nich silnik ich nie liczy (sektor ustala krok 5).

Źródła wzorów:
- Piotroski (2000), 9 sygnałów binarnych.
- Beneish (1999), model 8-zmiennowy; próg −1,78.
- Altman Z'' (1995) dla spółek nieprodukcyjnych i rynków wschodzących:
  6,56·X1 + 3,26·X2 + 6,72·X3 + 1,05·X4; strefy: > 2,60 bezpieczna, < 1,10 zagrożenia.
"""

from __future__ import annotations

from silnik.fakty.schemat import Jednostka, Okres

from .kalkulator import Kalkulator

PROG_M = -1.78
STREFY_Z = (1.10, 2.60)


def _ids(k: Kalkulator, pary: list[tuple[str, str]]) -> list[str] | None:
    """Zwraca listę id albo None (i zapis braku), gdy któregoś brakuje."""
    ids = [f"{p}.{s}" for p, s in pary]
    return ids


def piotroski(k: Kalkulator, lata: list) -> None:
    for n in range(2, len(lata)):
        t, t1, t2 = lata[n], lata[n - 1], lata[n - 2]
        S, S1 = t.id.split(".", 1)[1], t1.id.split(".", 1)[1]
        B, B1, B2 = t.okres.koniec.isoformat(), t1.okres.koniec.isoformat(), t2.okres.koniec.isoformat()
        f = lambda p, s: f"{p}.{s}"  # noqa: E731
        wej = [
            f("zysk_netto", S), f("aktywa", B1),            # 0,1 ROA t
            f("przeplywy_operacyjne", S),                     # 2 CFO
            f("zysk_netto", S1), f("aktywa", B2),           # 3,4 ROA t-1
            f("dlug_dlugoterminowy_f", B), f("aktywa", B),   # 5,6 dźwignia t (dług długoterminowy / aktywa)
            f("dlug_dlugoterminowy_f", B1),                  # 7 dźwignia t-1 (/ aktywa B1 = 1)
            f("aktywa_obrotowe", B), f("zobowiazania_krotkoterminowe", B),    # 8,9
            f("aktywa_obrotowe", B1), f("zobowiazania_krotkoterminowe", B1),  # 10,11
            f("liczba_akcji_rozwodniona", S), f("liczba_akcji_rozwodniona", S1),  # 12,13
            f("marza_brutto", S), f("marza_brutto", S1),    # 14,15
            f("przychody", S), f("przychody", S1),          # 16,17
        ]

        def fn(ni, a1, cfo, ni1, a2, ld, a, ld1, ca, cl, ca1, cl1, sh, sh1, gm, gm1, rev, rev1):
            roa, roa1 = ni / a1, ni1 / a2
            sygnaly = [
                roa > 0, cfo > 0, roa > roa1, cfo / a1 > roa,
                ld / a < ld1 / a1, ca / cl > ca1 / cl1, sh <= sh1 * 1.005,
                gm > gm1, rev / a1 > rev1 / a2,
            ]
            return float(sum(sygnaly))

        k.wylicz(f"piotroski_f.{S}", "piotroski_f",
                 "9 sygnałów Piotroskiego (ROA>0, CFO>0, ΔROA>0, CFO>ROA, Δdźwignia<0, Δpłynność>0, "
                 "brak emisji, Δmarża brutto>0, Δrotacja aktywów>0)",
                 wej, fn, Jednostka.punkty, Okres(typ="FY", poczatek=t.okres.poczatek, koniec=t.okres.koniec))


def beneish(k: Kalkulator, lata: list) -> None:
    for n in range(1, len(lata)):
        t, t1 = lata[n], lata[n - 1]
        S, S1 = t.id.split(".", 1)[1], t1.id.split(".", 1)[1]
        B, B1 = t.okres.koniec.isoformat(), t1.okres.koniec.isoformat()
        wej = [
            f"naleznosci_handlowe.{B}", f"przychody.{S}", f"naleznosci_handlowe.{B1}", f"przychody.{S1}",  # 0-3
            f"marza_brutto.{S}", f"marza_brutto.{S1}",                                                    # 4,5
            f"aktywa_obrotowe.{B}", f"rzeczowe_aktywa_trwale.{B}", f"aktywa.{B}",                        # 6-8
            f"aktywa_obrotowe.{B1}", f"rzeczowe_aktywa_trwale.{B1}", f"aktywa.{B1}",                     # 9-11
            f"amortyzacja.{S}", f"amortyzacja.{S1}",                                                      # 12,13
            f"koszty_sprzedazy_i_zarzadu.{S}", f"koszty_sprzedazy_i_zarzadu.{S1}",                        # 14,15
            f"zobowiazania_krotkoterminowe.{B}", f"dlug_dlugoterminowy_f.{B}",                            # 16,17
            f"zobowiazania_krotkoterminowe.{B1}", f"dlug_dlugoterminowy_f.{B1}",                          # 18,19
            f"zysk_netto.{S}", f"przeplywy_operacyjne.{S}",                                               # 20,21
        ]

        def fn(ar, s, ar1, s1, gm, gm1, ca, ppe, ta, ca1, ppe1, ta1, dep, dep1, sga, sga1, cl, ltd, cl1, ltd1, ni, cfo):
            dsri = (ar / s) / (ar1 / s1)
            gmi = gm1 / gm
            aqi = (1 - (ca + ppe) / ta) / (1 - (ca1 + ppe1) / ta1)
            sgi = s / s1
            depi = (dep1 / (dep1 + ppe1)) / (dep / (dep + ppe))
            sgai = (sga / s) / (sga1 / s1)
            lvgi = ((cl + ltd) / ta) / ((cl1 + ltd1) / ta1)
            tata = (ni - cfo) / ta
            return (-4.84 + 0.92 * dsri + 0.528 * gmi + 0.404 * aqi + 0.892 * sgi + 0.115 * depi
                    - 0.172 * sgai + 4.679 * tata - 0.327 * lvgi)

        k.wylicz(f"beneish_m.{S}", "beneish_m", "Beneish M-score, model 8-zmiennowy (1999); próg −1,78",
                 wej, fn, Jednostka.punkty, Okres(typ="FY", poczatek=t.okres.poczatek, koniec=t.okres.koniec))


def altman(k: Kalkulator, lata: list) -> None:
    for t in lata:
        S, B = t.id.split(".", 1)[1], t.okres.koniec.isoformat()
        kapital = f"kapital_wlasny_z_udzialami_niekontrolujacymi.{B}" if k.jest(
            f"kapital_wlasny_z_udzialami_niekontrolujacymi.{B}") else f"kapital_wlasny.{B}"
        wej = [f"aktywa_obrotowe.{B}", f"zobowiazania_krotkoterminowe.{B}", f"zyski_zatrzymane.{B}",
               f"zysk_operacyjny.{S}", kapital, f"zobowiazania.{B}", f"aktywa.{B}"]

        def fn(ca, cl, re, ebit, eq, tl, ta):
            return 6.56 * (ca - cl) / ta + 3.26 * re / ta + 6.72 * ebit / ta + 1.05 * eq / tl

        k.wylicz(f"altman_z2.{S}", "altman_z2", "Altman Z'' = 6,56·KO/A + 3,26·ZZ/A + 6,72·EBIT/A + 1,05·KW/Z",
                 wej, fn, Jednostka.punkty, Okres(typ="FY", poczatek=t.okres.poczatek, koniec=t.okres.koniec))


def dlug_dlugoterminowy_f(k: Kalkulator, lata: list) -> None:
    """Pomocniczo: dług długoterminowy (zbiorczy albo z kredytów i obligacji) jako jeden fakt."""
    for t in lata:
        B = t.okres.koniec
        d = B.isoformat()
        zbiorczy = [f"dlug_dlugoterminowy.{d}"] if k.jest(f"dlug_dlugoterminowy.{d}") else []
        skladniki = [x for x in (f"kredyty_dlugoterminowe.{d}", f"obligacje_dlugoterminowe.{d}") if k.jest(x)]
        wej = zbiorczy or skladniki
        if wej:
            k.wylicz(f"dlug_dlugoterminowy_f.{d}", "dlug_dlugoterminowy_f", " + ".join(wej), wej, lambda *a: sum(a),
                     Jednostka.pieniadz, Okres(typ="dzien", koniec=B))
        else:
            k.braki.append(f"dlug_dlugoterminowy_f.{d}: brak długu długoterminowego")


def oblicz(k: Kalkulator) -> None:
    lata = k.okresy_fy()
    dlug_dlugoterminowy_f(k, lata)
    piotroski(k, lata)
    beneish(k, lata)
    altman(k, lata)
