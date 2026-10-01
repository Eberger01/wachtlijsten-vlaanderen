"""Vlaams Parlement — Document Search API + open-data XML + PDF.

Geverifieerd op 2026-10-01:
  GET https://ws.vlpar.be/api/search/query/{term}?collection=vp_collection&page=1&max=10&sort=date
  -> JSON {count, firstindex, lastindex, result:[{id,date,mimetype,index,rank,snippet,title,url,
           metatags:{metatag:[{name,value},...]}}], facet_category:[...]}
  Metatags o.a.: zittingsjaar, nummer, soort (SCHV/VI/PI/JLN), documenttype, onderwerp, aggregaat,
  aggregaattype (Schriftelijke vraag / Vraag om uitleg / Verslag van het Rekenhof / ...), displayurl,
  publicatiedatum, minister, vraagsteller, thema, document (PDF-URL), opendata (XML-URL), last_modified.

  Open data per entiteit: http://ws.vlpar.be/e/opendata/{soort}/{id}  (schv, vi, jln, vv, verg)
  PDF: https://docs.vlaamsparlement.be/files/pfile?id={pfile-id}
  Licentie: Modellicentie Gratis Hergebruik v1.0 (bronvermelding "Vlaams Parlement").

Gebruik:
  from wachtlijst.sources import vlpar
  hits = vlpar.search("wachtlijst", max_pages=3)
  vlpar.save_hits(hits, "wachtlijst")
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Iterator

from .. import RAW_DIR
from . import client

SEARCH_URL = "https://ws.vlpar.be/api/search/query/{term}"
COLLECTION = "vp_collection"

# Zoektermen die in de praktijk wachtlijst-gerelateerde documenten opleveren.
STANDAARD_TERMEN = [
    "wachtlijst",
    "wachtenden",
    "wachttijd",
    "prioriteitengroep",
    "kandidaat-huurders",
    "zorgbudget",
    "urencontingent",
]


def _flatten_metatags(hit: dict) -> dict:
    tags = {}
    for mt in hit.get("metatags", {}).get("metatag", []):
        naam, waarde = mt.get("name"), mt.get("value")
        if naam in tags:  # meervoudige waarden (bv. meerdere thema's) -> lijst
            tags[naam] = tags[naam] + [waarde] if isinstance(tags[naam], list) else [tags[naam], waarde]
        else:
            tags[naam] = waarde
    return tags


def search_page(term: str, page: int = 1, max_per_page: int = 50, sort: str = "date") -> dict:
    with client() as c:
        r = c.get(
            SEARCH_URL.format(term=term),
            params={"collection": COLLECTION, "page": page, "max": max_per_page, "sort": sort},
            headers={"Accept": "application/json"},
        )
        r.raise_for_status()
        return r.json()


def search(term: str, max_pages: int = 2, max_per_page: int = 50, sort: str = "date") -> Iterator[dict]:
    """Itereert over hits, elk afgeplat naar een dict met de metatags als gewone sleutels."""
    for page in range(1, max_pages + 1):
        data = search_page(term, page=page, max_per_page=max_per_page, sort=sort)
        results = data.get("result", [])
        if not results:
            return
        for hit in results:
            flat = {k: hit.get(k) for k in ("id", "date", "title", "url", "snippet", "rank", "mimetype")}
            flat.update(_flatten_metatags(hit))
            flat["zoekterm"] = term
            flat["opgehaald_op"] = datetime.now().isoformat(timespec="seconds")
            yield flat
        if int(data.get("lastindex", 0)) >= int(data.get("count", 0)):
            return


def save_hits(hits: Iterator[dict], naam: str) -> Path:
    """Schrijft JSONL naar data/raw/vlpar/<naam>.jsonl en een CSV-index ernaast."""
    out_dir = RAW_DIR / "vlpar"
    out_dir.mkdir(parents=True, exist_ok=True)
    jsonl = out_dir / f"{naam}.jsonl"
    rows = list(hits)
    with jsonl.open("w", encoding="utf-8") as fh:
        for h in rows:
            fh.write(json.dumps(h, ensure_ascii=False) + "\n")
    # Compacte index voor Excel/Streamlit
    import pandas as pd

    kolommen = [
        "id", "zittingsjaar", "nummer", "soort", "aggregaattype", "thema", "titel", "onderwerp",
        "vraagsteller", "minister", "publicatiedatum", "displayurl", "document", "opendata", "zoekterm",
    ]
    df = pd.DataFrame(rows)
    for k in kolommen:
        if k not in df.columns:
            df[k] = None
    df[kolommen].to_csv(out_dir / f"{naam}.csv", index=False)
    return jsonl


def fetch_pdf(pdf_url: str, dest: Path | None = None) -> Path:
    """Downloadt een parlementair PDF (docs.vlaamsparlement.be/files/pfile?id=...) naar data/raw/vlpar/pdf/."""
    out_dir = RAW_DIR / "vlpar" / "pdf"
    out_dir.mkdir(parents=True, exist_ok=True)
    pfile_id = pdf_url.rsplit("id=", 1)[-1]
    dest = dest or out_dir / f"pfile_{pfile_id}.pdf"
    if dest.exists():
        return dest
    with client(timeout=120) as c:
        r = c.get(pdf_url)
        r.raise_for_status()
        dest.write_bytes(r.content)
    return dest


def fetch_opendata_xml(opendata_url: str) -> str:
    with client() as c:
        r = c.get(opendata_url.replace("http://", "https://"))
        r.raise_for_status()
        return r.text


def pdf_text(path: Path, max_pages: int | None = None) -> list[str]:
    """Tekst per pagina (pdfplumber). Pagina-index = paginanummer - 1."""
    import pdfplumber

    pages = []
    with pdfplumber.open(path) as pdf:
        for i, p in enumerate(pdf.pages):
            if max_pages and i >= max_pages:
                break
            pages.append(p.extract_text() or "")
    return pages


def grep_pdf(path: Path, patroon: str, context: int = 200) -> list[dict]:
    """Zoekt een regex in een PDF en geeft per treffer pagina + passage terug (voor bevindingen)."""
    import re

    rx = re.compile(patroon, re.IGNORECASE)
    treffers = []
    for i, tekst in enumerate(pdf_text(path), start=1):
        for m in rx.finditer(tekst):
            s, e = max(0, m.start() - context), min(len(tekst), m.end() + context)
            treffers.append({"pagina": i, "passage": " ".join(tekst[s:e].split())})
    return treffers
