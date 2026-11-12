"""Testy poprawek braków silnika wykrytych przy analizie MU (12.11.2026), bez sieci."""

from silnik.pobieranie import sec


def _wpis(val, end="2026-09-03"):
    return {"val": val, "end": end, "accn": "0001", "form": "10-K", "fy": 2026, "fp": "FY", "filed": "2026-10-09"}


def _rok():
    # okres roczny z 10-K, żeby silnik ustalił kalendarz fiskalny
    return {"RevenueFromContractWithCustomerExcludingAssessedTax": {"units": {"USD": [
        dict(_wpis(133_188_000_000), start="2025-08-29")]}}}


def test_dlug_dlugoterminowy_z_leasingiem_finansowym():
    # MU FY2026: brak LongTermDebtNoncurrent, dług długoterminowy jest pod LongTermDebtAndCapitalLeaseObligations
    f = {"facts": {"us-gaap": {**_rok(),
        "LongTermDebtAndCapitalLeaseObligations": {"units": {"USD": [_wpis(4_688_000_000)]}},
        "DebtCurrent": {"units": {"USD": [_wpis(491_000_000)]}},
    }}}
    fakty = {x.id: x for x in sec.wyciagnij_fakty(f, "doc-001")}
    assert fakty["dlug_dlugoterminowy.2026-09-03"].wartosc == 4_688_000_000
    assert fakty["dlug_krotkoterminowy.2026-09-03"].wartosc == 491_000_000


def test_pierwszenstwo_long_term_debt_noncurrent():
    f = {"facts": {"us-gaap": {**_rok(),
        "LongTermDebtNoncurrent": {"units": {"USD": [_wpis(1_000)]}},
        "LongTermDebtAndCapitalLeaseObligations": {"units": {"USD": [_wpis(1_200)]}},
    }}}
    fakty = {x.id: x for x in sec.wyciagnij_fakty(f, "doc-001")}
    assert fakty["dlug_dlugoterminowy.2026-09-03"].wartosc == 1_000


def test_rzeczowe_aktywa_z_leasingiem_finansowym():
    # MU FY2026: brak PropertyPlantAndEquipmentNet od 2020 r.
    f = {"facts": {"us-gaap": {**_rok(),
        "PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization":
            {"units": {"USD": [_wpis(63_310_000_000)]}},
    }}}
    fakty = {x.id: x for x in sec.wyciagnij_fakty(f, "doc-001")}
    assert fakty["rzeczowe_aktywa_trwale.2026-09-03"].wartosc == 63_310_000_000
