"""CSV-opslag en validatie van de gecureerde data (``data/curated``).

CSV is bewust gekozen: leesbaar in Excel, diff-baar in git, geen database nodig. Elke tabel heeft een
pydantic-model; ``validate_all`` controleert typen, unieke sleutels en referentiële integriteit
(bevinding -> voorziening, bevinding -> bron, budget -> voorziening/bron).
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from pydantic import BaseModel, ValidationError

from . import CURATED_DIR
from .models import SLEUTELS, TABELLEN


def _csv_path(tabel: str, base: Path | None = None) -> Path:
    return (base or CURATED_DIR) / f"{tabel}.csv"


def read_rows(tabel: str, base: Path | None = None) -> list[dict]:
    path = _csv_path(tabel, base)
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    # Lege strings -> None, maar alleen voor Optional-velden (default None); tekstvelden blijven "".
    model = TABELLEN[tabel]
    optioneel = {k for k, f in model.model_fields.items() if f.default is None}
    return [{k: (None if (v == "" and k in optioneel) else v) for k, v in r.items()} for r in rows]


def load(tabel: str, base: Path | None = None) -> list[BaseModel]:
    model = TABELLEN[tabel]
    return [model.model_validate(r) for r in read_rows(tabel, base)]


def write_rows(tabel: str, items: Iterable[BaseModel], base: Path | None = None) -> Path:
    model = TABELLEN[tabel]
    path = _csv_path(tabel, base)
    path.parent.mkdir(parents=True, exist_ok=True)
    kolommen = list(model.model_fields.keys())
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=kolommen)
        w.writeheader()
        for it in items:
            d = it.model_dump(mode="json")
            w.writerow({k: ("" if d.get(k) is None else d.get(k)) for k in kolommen})
    return path


def upsert(tabel: str, nieuwe: Iterable[BaseModel], base: Path | None = None) -> int:
    """Voeg toe of vervang op sleutel. Geeft aantal gewijzigde/toegevoegde rijen terug."""
    sleutel = SLEUTELS[tabel]
    bestaand = {getattr(x, sleutel): x for x in load(tabel, base)}
    n = 0
    for item in nieuwe:
        bestaand[getattr(item, sleutel)] = item
        n += 1
    write_rows(tabel, bestaand.values(), base)
    return n


@dataclass
class ValidatieRapport:
    fouten: list[str] = field(default_factory=list)
    waarschuwingen: list[str] = field(default_factory=list)
    aantallen: dict[str, int] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.fouten


def validate_all(base: Path | None = None) -> ValidatieRapport:
    rapport = ValidatieRapport()
    data: dict[str, list[BaseModel]] = {}

    for tabel, model in TABELLEN.items():
        rows = read_rows(tabel, base)
        items = []
        for i, r in enumerate(rows, start=2):  # rij 1 = header
            try:
                items.append(model.model_validate(r))
            except ValidationError as e:
                rapport.fouten.append(f"{tabel}.csv rij {i}: {e.errors()[0]['loc']} -> {e.errors()[0]['msg']}")
        data[tabel] = items
        rapport.aantallen[tabel] = len(items)

        sleutel = SLEUTELS[tabel]
        gezien: set[str] = set()
        for it in items:
            k = getattr(it, sleutel)
            if k in gezien:
                rapport.fouten.append(f"{tabel}.csv: dubbele sleutel {k!r}")
            gezien.add(k)

    bron_ids = {b.bron_id for b in data["bronnen"]}
    voorz_ids = {v.voorziening_id for v in data["voorzieningen"]}

    for b in data["bevindingen"]:
        if b.voorziening_id not in voorz_ids:
            rapport.fouten.append(f"bevinding {b.bevinding_id}: onbekende voorziening {b.voorziening_id!r}")
        if b.bron_id not in bron_ids:
            rapport.fouten.append(f"bevinding {b.bevinding_id}: onbekende bron {b.bron_id!r}")
        if not b.passage and b.controlestatus != "ongecontroleerd":
            rapport.waarschuwingen.append(f"bevinding {b.bevinding_id}: status {b.controlestatus} zonder passage")
        verwacht = f"{b.voorziening_id}:{b.metriek}:{b.peildatum.isoformat()}"
        if b.bevinding_id != verwacht:
            rapport.fouten.append(f"bevinding {b.bevinding_id}: id wijkt af van {verwacht!r}")

    for bu in data["budgetten"]:
        if bu.voorziening_id not in voorz_ids:
            rapport.fouten.append(f"budget {bu.budget_id}: onbekende voorziening {bu.voorziening_id!r}")
        if bu.bron_id not in bron_ids:
            rapport.fouten.append(f"budget {bu.budget_id}: onbekende bron {bu.bron_id!r}")

    for v in data["voorzieningen"]:
        if v.publicatie_bron_id and v.publicatie_bron_id not in bron_ids:
            rapport.waarschuwingen.append(f"voorziening {v.voorziening_id}: publicatie_bron_id {v.publicatie_bron_id!r} niet in bronnen")

    return rapport
