"""Download alle BBT-PDF's (WVG + Wonen, 2020–2026) naar data/raw/bbt/ — alleen standaardbibliotheek.

Draai op een werkpost MET internettoegang (docs.vlaamsparlement.be):
    python scripts\\harvest_bbt.py            # alles
    python scripts\\harvest_bbt.py WVG 2025   # één domein / jaar

Daarna (vereist pip install -e .):
    wachtlijst harvest bbt-parse
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from wachtlijst.sources.bbt import registry, download  # noqa: E402


def main(argv: list[str]) -> None:
    domein = argv[0].upper() if argv else None
    jaar = int(argv[1]) if len(argv) > 1 else None
    docs, _ = registry()
    n = 0
    for d in docs:
        if (domein and d.beleidsdomein != domein) or (jaar and d.begrotingsjaar != jaar):
            continue
        try:
            p = download(d)
            print(f"OK  {p.name:40s} {p.stat().st_size // 1024:6d} kB  {d.stuk}")
            n += 1
        except Exception as e:  # noqa: BLE001
            print(f"FOUT {d.stuk}: {e}")
    print(f"{n} bestanden in data/raw/bbt/")


if __name__ == "__main__":
    main(sys.argv[1:])
