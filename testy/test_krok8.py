"""Krok 8: narzędzia, które oszczędzają tury modelu (fragmenty do bramek, lista miejsc na liczby)."""

import json

import yaml

from silnik.dokumenty import WZORCE_BRAMEK, fragmenty_bramek
from silnik.fakty.schemat import TypDokumentu
from silnik.pobieranie.archiwum import Archiwum
from silnik.raport.render import miejsca


def test_fragmenty_bramek_znajduja_wzorce_i_pomijaja_api(tmp_path):
    a = Archiwum("X", tmp_path / "analiza", tmp_path / "pliki")
    src = tmp_path / "10k.txt"
    src.write_text("Item 9A.\nManagement identified a material weakness in revenue controls.\nNext line.", encoding="utf-8")
    a.dodaj_plik(src, TypDokumentu.raport_10k, "SEC", opis="10-K 2026")
    api = tmp_path / "facts.txt"
    api.write_text("material weakness", encoding="utf-8")
    a.dodaj_plik(api, TypDokumentu.sec_api, "SEC", opis="companyfacts")
    linie = fragmenty_bramek(a, {"B1.slabosc_kontroli": ["material weakness"], "B3.kontynuacja": ["going concern"]})
    trafienia = [x for x in linie if x.startswith("- [")]
    assert len(trafienia) == 1  # dokument sec_api pominięty
    assert "doc-001" in trafienia[0] and "Item 9A." in trafienia[0] and "Next line." in trafienia[0]
    i = linie.index("## B3.kontynuacja")
    assert linie[i + 1] == "- brak trafień"


def test_fragmenty_bramek_limit_na_dokument(tmp_path):
    a = Archiwum("X", tmp_path / "analiza", tmp_path / "pliki")
    src = tmp_path / "proxy.txt"
    src.write_text("\n".join(["10b5-1 plan"] * 10), encoding="utf-8")
    a.dodaj_plik(src, TypDokumentu.inny, "SEC")
    linie = fragmenty_bramek(a, {"B4.insiderzy": ["10b5-1"]}, limit=2)
    assert len([x for x in linie if x.startswith("- [")]) == 2


def test_wzorce_bramek_to_bramki_modelu():
    wzorce = yaml.safe_load(WZORCE_BRAMEK.read_text(encoding="utf-8"))
    bramki = yaml.safe_load((WZORCE_BRAMEK.parent / "bramki.yaml").read_text(encoding="utf-8"))["bramki_modelu"]
    assert set(wzorce) <= set(bramki)


def test_miejsca_grupuja_okresy_i_pomijaja_odrzucone(tmp_path):
    fakty = [{"id": f"przychody.FY{r}", "status": "zweryfikowany"} for r in range(2020, 2026)]
    fakty.append({"id": "kurs.2026-11-10", "status": "jedno_zrodlo"})
    fakty.append({"id": "zysk_netto.FY2025", "status": "odrzucony"})
    (tmp_path / "fakty.json").write_text(json.dumps({"fakty": fakty}), encoding="utf-8")
    linie = miejsca(tmp_path)
    assert "- przychody (6): FY2023, FY2024, FY2025" in linie
    assert "- kurs (1): 2026-11-10" in linie
    assert not any(x.startswith("- zysk_netto") for x in linie)
    assert linie[0].startswith("Tabele: {{tabela:panel}}")
