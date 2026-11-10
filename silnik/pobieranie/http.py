"""Pobieranie plików z sieci do archiwum.

Jeden, jawny nagłówek User-Agent (zmienna ANALIZA_USER_AGENT). SEC prosi
w zasadach dostępu o nazwę narzędzia i adres kontaktowy, więc właściciel
powinien ustawić tę zmienną z własnym adresem. Silnik nie podmienia nagłówków
i nie omija blokad: gdy serwis odmawia (403), zwraca błąd.
"""

from __future__ import annotations

import http.client
import os
import re
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

USER_AGENT = os.environ.get("ANALIZA_USER_AGENT", "analiza-fundamentalna/0.1 (narzedzie badawcze)")

# SEC pozwala na 10 zapytań na sekundę; trzymamy się wyraźnie poniżej.
_ODSTEP = {"data.sec.gov": 0.2, "www.sec.gov": 0.2, "query1.finance.yahoo.com": 1.5}
_ostatnie: dict[str, float] = {}


class BladPobierania(Exception):
    pass


def pobierz(url: str, limit_s: int = 60, rozszerzenie: str | None = None) -> Path:
    """Pobiera URL do pliku tymczasowego i zwraca jego ścieżkę."""
    host = urlparse(url).netloc
    odstep = _ODSTEP.get(host, 0.5)
    czekaj = _ostatnie.get(host, 0) + odstep - time.monotonic()
    if czekaj > 0:
        time.sleep(czekaj)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept-Encoding": "identity"})
    for proba in range(3):
        try:
            with urllib.request.urlopen(req, timeout=limit_s) as odp:
                dane = odp.read()
            break
        except urllib.error.HTTPError as e:
            # 429 = serwis prosi o wolniejsze zapytania: czekamy tyle, ile podaje (Retry-After), najwyżej 2 razy
            if e.code == 429 and proba < 2:
                try:
                    czekaj = min(float(e.headers.get("Retry-After", 15)), 60)
                except ValueError:
                    czekaj = 15
                time.sleep(czekaj)
                continue
            raise BladPobierania(f"{url}: HTTP {e.code}") from None
        except urllib.error.URLError as e:
            raise BladPobierania(f"{url}: {e.reason}") from None
        except (http.client.HTTPException, ValueError, ConnectionError, TimeoutError) as e:
            # zerwana transmisja (np. uszkodzone kodowanie chunked): jedno ponowienie, potem błąd pobierania
            if proba < 2:
                time.sleep(3)
                continue
            raise BladPobierania(f"{url}: przerwana transmisja ({type(e).__name__})") from None
        finally:
            _ostatnie[host] = time.monotonic()
    if rozszerzenie is None:
        sufiks = Path(urlparse(url).path).suffix.lower()
        rozszerzenie = sufiks if re.fullmatch(r"\.[a-z0-9]{1,5}", sufiks) else ".bin"
    fd, sciezka = tempfile.mkstemp(suffix=rozszerzenie, prefix="pobrane-")
    with os.fdopen(fd, "wb") as f:
        f.write(dane)
    return Path(sciezka)
