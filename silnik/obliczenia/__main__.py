"""Uruchom: python -m silnik.obliczenia analizy/<TICKER>/<data>"""

import sys
from pathlib import Path

from . import uruchom_w_katalogu

if __name__ == "__main__":
    print(uruchom_w_katalogu(Path(sys.argv[1])).read_text(encoding="utf-8"))
