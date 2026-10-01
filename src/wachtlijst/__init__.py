"""Wachtlijst — onderzoeksbibliotheek voor wachtlijsten en budgetten van Vlaamse sociale voorzieningen.

Lagen:
- ``models``   : pydantic-datamodel (Bron, Voorziening, Bevinding, Budget) met controlestatus
- ``store``    : CSV-opslag in ``data/curated`` + validatie
- ``sources``  : connectors (Vlaams Parlement Search API, VAPH-jaarverslag, Vlaamse Codex)
- ``publish``  : bouwt ``data/published`` (wat het dashboard leest) + ``meta.json``
- ``cli``      : ``wachtlijst validate|publish|harvest ...``

Het dashboard (``dashboard/app.py``) importeert enkel ``publish.load_published`` en raakt het web nooit aan.
"""

from pathlib import Path

__version__ = "0.1.0"

# Projectroot = map boven ``src``; alle data-paden zijn hiervan afgeleid.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
STAGING_DIR = DATA_DIR / "staging"
CURATED_DIR = DATA_DIR / "curated"
PUBLISHED_DIR = DATA_DIR / "published"
CONFIG_DIR = PROJECT_ROOT / "config"
