"""Pobieranie plików z sieci do archiwum.

Jeden, jawny nagłówek User-Agent (zmienna ANALIZA_USER_AGENT). SEC prosi
w zasadach dostępu o nazwę narzędzia i adres kontaktowy, więc właściciel
powinien ustawić tę zmienną z własnym adresem. Silnik nie podmienia nagłówków
i nie omija blokad: gdy serwis odmawia (403), zwraca błąd.
"""

from __future__ import annotations

import os
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

USER_AGENT = os.environ.get("ANALIZA_USER_AGENT", "analiza-fundamentalna/0.1 (narzedzie badawcze)")

# SEC pozwala na 10 zapytań na sekundę; trzymamy się wyraźnie poniżej.
_ODSTEP = {"data.sec.gov": 0.2, "www.sec.gov": 0.2}
_ostatnie: dict[str, float] = {}


class BladPobierania(Exception):
    pass


def pobierz(url: str, limit_s: int = 60) -> Path:
    """Pobiera URL do pliku tymczasowego i zwraca jego ścieżkę."""
    host = urlparse(url).netloc
    odstep = _ODSTEP.get(host, 0.5)
    czekaj = _ostatnie.get(host, 0) + odstep - time.monotonic()
    if czekaj > 0:
        time.sleep(czekaj)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept-Encoding": "identity"})
    try:
        with urllib.request.urlopen(req, timeout=limit_s) as odp:
            dane = odp.read()
    except urllib.error.HTTPError as e:
        raise BladPobierania(f"{url}: HTTP {e.code}") from None
    except urllib.error.URLError as e:
        raise BladPobierania(f"{url}: {e.reason}") from None
    finally:
        _ostatnie[host] = time.monotonic()
    rozszerzenie = Path(urlparse(url).path).suffix or ".bin"
    if url.rstrip("/").endswith(("/financials", "/income-statement", "/balance-sheet", "/cash-flow-statement")):
        rozszerzenie = ".html"
    fd, sciezka = tempfile.mkstemp(suffix=rozszerzenie, prefix="pobrane-")
    with os.fdopen(fd, "wb") as f:
        f.write(dane)
    return Path(sciezka)
