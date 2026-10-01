"""Agentschap Opgroeien — jeugdhulp NRTJ (cijferrapport, HTML) en kinderopvang (Excel 'cijfers op maat').

Geverifieerd 2026-10-01:
- NRTJ: https://www.opgroeien.be/kennis/cijfers-en-onderzoek/aanvragen-crisisjeugdhulp-en-niet-rechtstreeks-toegankelijke-jeugdhulp
  Vaste zin: "Op 31 december 2025 stonden in totaal 9.748 kinderen en jongeren op een NRTJ-wachtlijst (…). Dat zijn er 6 procent
  meer dan in 2024 (9.194)." + "aanmelding … is in 2025 gestegen naar 15.446" + "nieuwe hulpvraag … (+ 4,9%, 12.897 in 2025)".
- Kinderopvang: https://www.opgroeien.be/kennis/cijfers-en-onderzoek/kinderopvang-babys-en-peuters/cijfers-op-maat
  Excel 'b-p-aantal-plaatsen-en-locaties-naar-vergunningstype-en-inkomenstarief_<n>.xlsx' (kolommen Jaar, Gewest, Provincie,
  Zorgregio, Gemeente, Vergunningstype, IKT/Niet IKT, Totaal plaatsen, Plaatsen IKT, Plaatsen vrije prijs, Locaties).
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from bs4 import BeautifulSoup

from .. import RAW_DIR
from ..models import Bevinding, Controlestatus
from . import client

URL_NRTJ = "https://www.opgroeien.be/kennis/cijfers-en-onderzoek/aanvragen-crisisjeugdhulp-en-niet-rechtstreeks-toegankelijke-jeugdhulp"
URL_KO = "https://www.opgroeien.be/kennis/cijfers-en-onderzoek/kinderopvang-babys-en-peuters/cijfers-op-maat"

DEF_NRTJ = ("Unieke kinderen/jongeren die op 31/12 op een NRTJ-wachtlijst staan (indicatiestelling in regie, hulp niet opgestart); "
            "exclusief PAB, inclusief MFC.")

RX_WACHT = re.compile(r"Op 31 december (\d{4}) stonden in totaal ([\d.]+) kinderen en jongeren op een NRTJ-wachtlijst", re.S)
RX_VORIG = re.compile(r"(?:meer|minder) dan in (\d{4}) \(([\d.]+)\)")
RX_AANM = re.compile(r"A document is in (\d{4}) gestegen naar ([\d.]+)")
RX_HULPVRAAG = re.compile(r"nieuwe hulpvraag[^.]*?([\d.]+) in (\d{4})\)")
RX_OPSTART = re.compile(r"\(([\d.]+) in (\d{4}), ([+-]?\d+)% ten opzichte van (\d{4})\)")


def _n(s: str) -> int:
    return int(s.replace(".", ""))


def _tekst(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for t in soup(["script", "style", "nav", "header", "footer"]):
        t.decompose()
    return " ".join(soup.get_text(" ").split())


def fetch_nrtj() -> str:
    out = RAW_DIR / "opgroeien"
    out.mkdir(parents=True, exist_ok=True)
    with client() as c:
        r = c.get(URL_NRTJ)
        r.raise_for_status()
    (out / f"nrtj_{date.today().isoformat()}.html").write_text(r.text, encoding="utf-8")
    return r.text


def parse_nrtj(tekst: str, bron_id: str = "opgroeien-nrtj", pub: date | None = None) -> list[Bevinding]:
    """Kandidaat-bevindingen uit het NRTJ-cijferrapport (status ongecontroleerd)."""
    uit: list[Bevinding] = []
    basis = dict(voorziening_id="opgroeien-nrtj", bron_id=bron_id, bron_url=URL_NRTJ, documenttitel="Opgroeien — cijferrapport NRTJ",
                 pagina="sectie wachtenden/aanmeldingen", controlestatus=Controlestatus.ONGECONTROLEERD, publicatiedatum=pub,
                 opmerking="automatisch geparsed; nog te controleren")
    m = RX_WACHT.search(tekst)
    if m:
        jaar = int(m.group(1))
        passage = tekst[m.start(): m.start() + 400]
        uit.append(Bevinding(bevinding_id=f"opgroeien-nrtj:wachtenden_nrtj:{jaar}-12-31", metriek="wachtenden_nrtj", waarde=_n(m.group(2)), eenheid="personen",
                             peildatum=date(jaar, 12, 31), passage=passage, definitie=DEF_NRTJ, **basis))
        m2 = RX_VORIG.search(tekst, m.end())
        if m2 and int(m2.group(1)) == jaar - 1:
            j2 = int(m2.group(1))
            uit.append(Bevinding(bevinding_id=f"opgroeien-nrtj:wachtenden_nrtj:{j2}-12-31", metriek="wachtenden_nrtj", waarde=_n(m2.group(2)), eenheid="personen",
                                 peildatum=date(j2, 12, 31), passage=passage, definitie=DEF_NRTJ, **basis))
    m = RX_AANM.search(tekst)
    if m:
        jaar = int(m.group(1))
        uit.append(Bevinding(bevinding_id=f"opgroeien-nrtj:aanmeldingen_a_document:{jaar}-12-31", metriek="aanmeldingen_a_document", waarde=_n(m.group(2)), eenheid="personen",
                             peildatum=date(jaar, 12, 31), passage=m.group(0), definitie="Unieke kinderen/jongeren met een aanmelding (A-document) bij de toegangspoort in het jaar.", **basis))
    m = RX_HULPVRAAG.search(tekst)
    if m:
        jaar = int(m.group(2))
        uit.append(Bevinding(bevinding_id=f"opgroeien-nrtj:nieuwe_hulpvraag:{jaar}-12-31", metriek="nieuwe_hulpvraag", waarde=_n(m.group(1)), eenheid="personen",
                             peildatum=date(jaar, 12, 31), passage=m.group(0), definitie="Unieke kinderen/jongeren met een typemodule voor het eerst in regie.", **basis))
    return uit


def harvest_nrtj() -> list[Bevinding]:
    return parse_nrtj(_tekst(fetch_nrtj()))


# ---------------------------------------------------------------------------------------- kinderopvang
def vind_excel_links() -> list[str]:
    with client() as c:
        r = c.get(URL_KO)
        r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    links = [a["href"] for a in soup.find_all("a", href=True) if a["href"].lower().endswith(".xlsx")]
    return [h if h.startswith("http") else "https://www.opgroeien.be" + h for h in links]


def download_plaatsen_excel() -> Path:
    """Downloadt de Excel 'aantal plaatsen en locaties naar vergunningstype en inkomenstarief' naar data/raw/opgroeien/."""
    links = [h for h in vind_excel_links() if "plaatsen-en-locaties" in h]
    if not links:
        raise RuntimeError("Excel 'plaatsen-en-locaties' niet gevonden op de cijfers-op-maat-pagina")
    out = RAW_DIR / "opgroeien"
    out.mkdir(parents=True, exist_ok=True)
    dest = out / links[0].rsplit("/", 1)[-1]
    with client(timeout=120) as c:
        r = c.get(links[0])
        r.raise_for_status()
    dest.write_bytes(r.content)
    return dest


def plaatsen_per_jaar(xlsx: Path) -> list[Bevinding]:
    """Aggregeert de Excel naar totaal vergunde plaatsen en IKT-plaatsen per jaar (Vl. Gewest + Brussel)."""
    import pandas as pd

    df = pd.read_excel(xlsx)
    kol = {c.lower(): c for c in df.columns}
    jaar_k = next(c for k, c in kol.items() if k.startswith("jaar"))
    tot_k = next(c for k, c in kol.items() if "totaal" in k and "plaats" in k)
    ikt_k = next(c for k, c in kol.items() if "plaatsen ikt" in k)
    g = df.groupby(jaar_k)[[tot_k, ikt_k]].sum()
    uit = []
    for jaar, row in g.iterrows():
        try:
            j = int(str(jaar)[:4])
        except ValueError:
            continue
        pd_ = date(j, 12, 31)
        basis = dict(voorziening_id="opgroeien-kinderopvang", bron_id="opgroeien-kinderopvang-cijfers", bron_url=URL_KO, documenttitel=f"Opgroeien — Excel {xlsx.name}",
                     pagina=f"som rijen Jaar={jaar}", passage=f"som gemeenteniveau {jaar}: totaal {round(row[tot_k])}, IKT {round(row[ikt_k])}", peildatum=pd_,
                     controlestatus=Controlestatus.ONGECONTROLEERD, opmerking="automatisch geaggregeerd; nog te controleren")
        uit.append(Bevinding(bevinding_id=f"opgroeien-kinderopvang:vergunde_plaatsen:{pd_.isoformat()}", metriek="vergunde_plaatsen", waarde=float(round(row[tot_k])), eenheid="plaatsen",
                             definitie="Vergunde plaatsen kinderopvang baby's en peuters op 31/12 (Vl. Gewest + Brussel).", **basis))
        uit.append(Bevinding(bevinding_id=f"opgroeien-kinderopvang:plaatsen_inkomenstarief:{pd_.isoformat()}", metriek="plaatsen_inkomenstarief", waarde=float(round(row[ikt_k])), eenheid="plaatsen",
                             definitie="Vergunde plaatsen met subsidie inkomenstarief op 31/12.", **basis))
    return uit
