"""Gewogen sectorgemiddelden van de CGG-wachttijden (aanmelding -> FTF1, FTF1 -> FTF2).

De Excel-bijlagen bij de schriftelijke vragen geven de gemiddelde wachttijd per CGG x leeftijd x geslacht, maar geen
sectorgemiddelde. Een ongewogen gemiddelde over die cellen laat een klein centrum even zwaar wegen als een groot.
Dit script weegt elke cel met het aantal actieve zorgperiodes (hoofdcliënten) van dezelfde CGG x leeftijd x geslacht:

  2019-2023: wachttijden SV 379 (pfile 2132648) x zorgperiodes SV 382 (pfile 2132652)
  2024:      wachttijd en zorgperiodes uit dezelfde bijlage SV 645 (pfile 2307491); geen FTF2-tabel

Beperking: het gewicht is een benadering. Het ideale gewicht is het aantal aanmeldingen met een FTF1 in het jaar; dat
staat niet in de bijlagen. Actieve zorgperiodes bevatten ook lopende zorg uit vorige jaren.

Draai: ``python scripts/cgg_gewogen.py`` -> tabel op scherm + data/raw/cgg/cgg_gewogen.csv. De uitkomst staat
(afgerond op 0,1 dag) in scripts/seed_aanvullingen.py.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import openpyxl
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from wachtlijst import RAW_DIR  # noqa: E402
from wachtlijst.sources import client  # noqa: E402

PF = "https://docs.vlaamsparlement.be/files/pfile?id={}"
MAP = RAW_DIR / "cgg"


def _bestand(pfile: int) -> Path:
    pad = MAP / f"pfile_{pfile}.xlsx"
    if not pad.exists():
        MAP.mkdir(parents=True, exist_ok=True)
        with client() as c:
            r = c.get(PF.format(pfile))
            r.raise_for_status()
            pad.write_bytes(r.content)
    return pad


def _leeftijd(label: str) -> str:
    s = str(label)
    for patroon, groep in (("0-17", "0-17"), ("18-59", "18-59"), ("18-64", "18-64"), ("60\\+|>59", "60+"), ("65", "65+")):
        if re.search(patroon, s):
            return groep
    raise ValueError(f"onbekende leeftijdsgroep {label!r}")


def lees_tabel(pfile: int, blad: str) -> pd.DataFrame:
    """Blad met per jaar twee kolommen (mannen, vrouwen) -> lange tabel cgg, leeftijd, jaar, geslacht, waarde."""
    ws = openpyxl.load_workbook(_bestand(pfile), data_only=True)[blad]
    rijen = list(ws.iter_rows(values_only=True))
    # Jaarkop: eerste rij met jaartallen; elk jaar beslaat de kolom zelf (M) en de volgende (V).
    kop_i = next(i for i, r in enumerate(rijen) if sum(bool(re.search(r"20\d\d", str(v))) for v in r if v is not None) >= 1
                 and not str(r[0] or "").strip().startswith("F"))
    jaren = {k: int(re.search(r"20\d\d", str(v)).group()) for k, v in enumerate(rijen[kop_i]) if v is not None and re.search(r"20\d\d", str(v))}
    uit, cgg = [], None
    for r in rijen[kop_i + 1:]:
        if r[0] is not None and str(r[0]).strip().lower().startswith("totaal"):
            break
        if r[0] is not None and str(r[0]).strip():
            cgg = str(r[0]).strip()
        if cgg is None or r[1] is None or not cgg.startswith("F"):
            continue
        for k, jaar in jaren.items():
            for geslacht, kol in (("M", k), ("V", k + 1)):
                v = r[kol]
                if isinstance(v, (int, float)):
                    uit.append({"cgg": cgg, "leeftijd": _leeftijd(r[1]), "jaar": jaar, "geslacht": geslacht, "waarde": float(v)})
    return pd.DataFrame(uit)


def gewogen(wacht: pd.DataFrame, gewicht: pd.DataFrame, maatstaf: str) -> pd.DataFrame:
    sleutel = ["cgg", "leeftijd", "jaar", "geslacht"]
    m = wacht.merge(gewicht.rename(columns={"waarde": "gewicht"}), on=sleutel, how="right")
    rijen = []
    for (jaar, leeftijd), g in m.groupby(["jaar", "leeftijd"]):
        met = g.dropna(subset=["waarde"])
        met = met[met.gewicht > 0]
        rijen.append({
            "maatstaf": maatstaf, "jaar": jaar, "leeftijd": leeftijd,
            "gewogen": (met.waarde * met.gewicht).sum() / met.gewicht.sum(),
            "ongewogen": g.waarde.mean(),
            "cellen": len(met), "dekking_pct": 100 * met.gewicht.sum() / g.gewicht.sum(), "zorgperiodes": int(g.gewicht.sum()),
        })
    return pd.DataFrame(rijen)


def main() -> None:
    zp = lees_tabel(2132652, "Zorgperiodes")
    uit = pd.concat([
        gewogen(lees_tabel(2132648, "wachtijd tot eerste FTF"), zp, "ftf1"),
        gewogen(lees_tabel(2132648, "wachttijd FTF1 en FTF2"), zp, "ftf2"),
        gewogen(lees_tabel(2307491, "wachttijd tot FTF1"), lees_tabel(2307491, "aantal zorgperiodes"), "ftf1"),
    ], ignore_index=True).sort_values(["maatstaf", "jaar", "leeftijd"])
    uit.to_csv(MAP / "cgg_gewogen.csv", index=False)
    with pd.option_context("display.width", 200, "display.float_format", "{:.1f}".format):
        print(uit.to_string(index=False))


if __name__ == "__main__":
    main()
