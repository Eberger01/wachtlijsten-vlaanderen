"""Bouwt ``data/published``: de enige map die het dashboard leest.

Het dashboard doet geen webverkeer en geen PDF-parsing; het toont uitsluitend wat hier gepubliceerd is,
met de datum van de laatste actualisering uit ``meta.json``. Zo kan het dashboard gratis gehost worden
(Streamlit Community Cloud / GitHub Pages) terwijl verzamelen en controleren lokaal gebeurt.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd

from . import PUBLISHED_DIR
from .models import TABELLEN
from .store import read_rows, validate_all


def publish(base: Path | None = None, dest: Path | None = None, force: bool = False) -> dict:
    rapport = validate_all(base)
    if not rapport.ok and not force:
        raise SystemExit("Validatie faalt; publiceren geweigerd:\n  " + "\n  ".join(rapport.fouten))

    dest = dest or PUBLISHED_DIR
    dest.mkdir(parents=True, exist_ok=True)
    meta = {
        "gepubliceerd_op": datetime.now().isoformat(timespec="seconds"),
        "aantallen": {},
        "validatie_waarschuwingen": rapport.waarschuwingen,
        "controlestatus_verdeling": {},
    }
    for tabel, model in TABELLEN.items():
        df = pd.DataFrame(read_rows(tabel, base), columns=list(model.model_fields.keys()))
        df.to_csv(dest / f"{tabel}.csv", index=False, lineterminator="\n")
        meta["aantallen"][tabel] = int(len(df))
        if "controlestatus" in df.columns and len(df):
            meta["controlestatus_verdeling"][tabel] = df["controlestatus"].value_counts().to_dict()
    (dest / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    return meta


def load_published(src: Path | None = None) -> dict[str, pd.DataFrame | dict]:
    """Leest de gepubliceerde tabellen; gebruikt door het dashboard."""
    src = src or PUBLISHED_DIR
    out: dict = {}
    for tabel, model in TABELLEN.items():
        p = src / f"{tabel}.csv"
        kolommen = list(model.model_fields.keys())
        try:
            out[tabel] = pd.read_csv(p, dtype=str, keep_default_na=False) if p.exists() else pd.DataFrame(columns=kolommen)
        except pd.errors.EmptyDataError:
            out[tabel] = pd.DataFrame(columns=kolommen)
    meta_p = src / "meta.json"
    out["meta"] = json.loads(meta_p.read_text(encoding="utf-8")) if meta_p.exists() else {}
    if len(out["bevindingen"]):
        out["bevindingen"]["waarde"] = pd.to_numeric(out["bevindingen"]["waarde"], errors="coerce")
        out["bevindingen"]["peildatum"] = pd.to_datetime(out["bevindingen"]["peildatum"], errors="coerce")
    if len(out["budgetten"]):
        out["budgetten"]["bedrag_eur"] = pd.to_numeric(out["budgetten"]["bedrag_eur"], errors="coerce")
        out["budgetten"]["begrotingsjaar"] = pd.to_numeric(out["budgetten"]["begrotingsjaar"], errors="coerce")
    if len(out["kredieten"]):
        out["kredieten"]["bedrag_keur"] = pd.to_numeric(out["kredieten"]["bedrag_keur"], errors="coerce")
        out["kredieten"]["begrotingsjaar"] = pd.to_numeric(out["kredieten"]["begrotingsjaar"], errors="coerce")
    return out
