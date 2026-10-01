"""Connectors naar publieke bronnen. Elke connector haalt ruwe data op naar ``data/raw/<bron>/`` en levert
kandidaat-bevindingen af in ``data/staging/`` voor handmatige controle. Niets gaat rechtstreeks naar
``data/curated`` — dat is een bewuste, menselijke stap (``controlestatus``).
"""

from __future__ import annotations

import httpx

USER_AGENT = "Wachtlijst-onderzoek/0.1 (+https://github.com/; onderzoek sociale voorzieningen Vlaanderen)"


def client(timeout: float = 60.0) -> httpx.Client:
    return httpx.Client(
        timeout=timeout,
        follow_redirects=True,
        headers={"User-Agent": USER_AGENT, "Accept-Language": "nl-BE,nl;q=0.9"},
    )
