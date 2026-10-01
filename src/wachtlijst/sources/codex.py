"""Vlaamse Codex Open Data API — regelgeving (decreten, BVR's, MB's).

Geverifieerd 2026-10-01: https://codex.opendata.api.vlaanderen.be/
  GET /api/WetgevingDocument/Zoeken?Zoekterm=wachtlijst   -> documenten + artikelen
  GET /api/WetgevingDocument/{id}                           (1004736 = BWHI 8-8-1980)
  GET /api/WetgevingDocument/{id}/Structuur
  GET /api/WetgevingArtikel/{id}
Nuttig om de juridische grondslag (toewijzingsregels, prioriteitencriteria) per voorziening te koppelen.
"""

from __future__ import annotations

from . import client

BASE = "https://codex.opendata.api.vlaanderen.be/api"


def zoek(zoekterm: str) -> dict:
    with client() as c:
        r = c.get(f"{BASE}/WetgevingDocument/Zoeken", params={"Zoekterm": zoekterm})
        r.raise_for_status()
        return r.json()


def document(doc_id: int) -> dict:
    with client() as c:
        r = c.get(f"{BASE}/WetgevingDocument/{doc_id}")
        r.raise_for_status()
        return r.json()


def structuur(doc_id: int) -> dict:
    with client() as c:
        r = c.get(f"{BASE}/WetgevingDocument/{doc_id}/Structuur")
        r.raise_for_status()
        return r.json()
