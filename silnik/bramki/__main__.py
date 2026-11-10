import sys
from pathlib import Path

from .uruchom import uruchom_w_katalogu

if __name__ == "__main__":
    print(uruchom_w_katalogu(Path(sys.argv[1])).read_text(encoding="utf-8"))
