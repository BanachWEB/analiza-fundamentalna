"""Generuje schemat/*.schema.json z silnik/fakty/schemat.py.

Uruchom: python -m silnik.fakty.eksport_schematu
"""

import json
from pathlib import Path

from .schemat import RejestrDokumentow, RejestrFaktowPlik

KATALOG = Path(__file__).resolve().parents[2] / "schemat"


def main() -> None:
    KATALOG.mkdir(exist_ok=True)
    for nazwa, model in (("fakty", RejestrFaktowPlik), ("dokumenty", RejestrDokumentow)):
        sciezka = KATALOG / f"{nazwa}.schema.json"
        sciezka.write_text(json.dumps(model.model_json_schema(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(sciezka)


if __name__ == "__main__":
    main()
