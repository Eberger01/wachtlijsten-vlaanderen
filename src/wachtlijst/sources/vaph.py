"""VAPH — wachtenden op een persoonsvolgend budget (prioriteitengroepen).

Bronnen (geverifieerd 2026-10-01):
- HTML-jaarverslag: https://extranet.vaph.be/jaarverslag/{jaar}/pages/{n}
  (2023 en 2024: "Prioriteitengroepen" = pages/25, 2025: pages/27; paginanummers verschillen per jaar -> zoek via
  ``vind_pagina`` of geef het nummer op). Halfjaar: .../jaarverslag/{jaar}-eerste-jaarhelft/pages/{n}/
- PDF "Het VAPH in cijfers {jaar}": https://publicaties.vlaanderen.be/view-file/{id}
  (2019=42019, 2021=50259, 2022=57023, 2025=85057)
- Let op: www.vaph.be blokkeert geautomatiseerde requests (403); extranet.vaph.be en
  publicaties.vlaanderen.be niet.

De zinsstructuur is al jaren stabiel:
  "Op 31 december 2024 waren 18.261 personen met in totaal 18.302 vragen geregistreerd in de
   prioriteitengroepen ... 526 vragen in prioriteitengroep 1, 8091 vragen in prioriteitengroep 2 en
   9685 vragen in prioriteitengroep 3 ... prioriteitengroep 1: 1 januari 2024, prioriteitengroep 2: ..."
``parse_prioriteitengroepen`` zet die zin om in kandidaat-bevindingen (controlestatus: ongecontroleerd).
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from bs4 import BeautifulSoup

from .. import RAW_DIR
from ..models import Bevinding, Controlestatus
from . import client

EXTRANET = "https://extranet.vaph.be/jaarverslag/{editie}/pages/{n}"

MAANDEN = {
    "januari": 1, "februari": 2, "maart": 3, "april": 4, "mei": 5, "juni": 6, "juli": 7,
    "augustus": 8, "september": 9, "oktober": 10, "november": 11, "december": 12,
}

DEFINITIE_VRAGEN = (
    "Aantal vragen naar een persoonsvolgend budget geregistreerd in de prioriteitengroepen op de peildatum; "
    "eenzelfde persoon kan in twee prioriteitengroepen voorkomen (hoofd- en deelvraag)."
)
DEFINITIE_PERSONEN = "Aantal unieke personen met minstens één vraag geregistreerd in de prioriteitengroepen."
DEFINITIE_PRIODATUM = (
    "Prioriteringsdatum (datum van aanvraag of herziening) van de eerstvolgende wachtende in de groep; "
    "maat voor de feitelijke wachttijd."
)


def _getal(s: str) -> int:
    return int(s.replace(".", "").replace(" ", ""))


def _nl_datum(s: str) -> date:
    d, m, j = s.strip().split()
    return date(int(j), MAANDEN[m.lower()], int(d))


def fetch_pagina(editie: str, n: int) -> str:
    """Haalt een jaarverslagpagina op en bewaart de HTML in data/raw/vaph/."""
    out_dir = RAW_DIR / "vaph"
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / f"jaarverslag_{editie}_p{n}.html"
    with client() as c:
        r = c.get(EXTRANET.format(editie=editie, n=n))
        r.raise_for_status()
        dest.write_text(r.text, encoding="utf-8")
    return r.text


def vind_pagina(editie: str, rond: int = 25, max_pagina: int = 80) -> int | None:
    """Zoekt de pagina met de prioriteitengroepenzin (2024: 25, 2025: 27). Probeert eerst de pagina's rond ``rond``."""
    with client() as c:
        for n in sorted(range(1, max_pagina + 1), key=lambda n: abs(n - rond)):
            r = c.get(EXTRANET.format(editie=editie, n=n))
            if r.status_code == 404:
                continue
            r.raise_for_status()
            if RX_TOTAAL.search(html_naar_tekst(r.text)):
                return n
    return None


def html_naar_tekst(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for t in soup(["script", "style", "nav", "header", "footer"]):
        t.decompose()
    return " ".join(soup.get_text(" ").split())


RX_TOTAAL = re.compile(
    r"Op (\d{1,2} \w+ \d{4}) waren ([\d.]+) personen met in totaal ([\d.]+) vragen geregistreerd in de prioriteitengroepen",
    re.IGNORECASE,
)
RX_PG = re.compile(r"([\d.]+) vragen in prioriteitengroep ([123])", re.IGNORECASE)
RX_PRIO = re.compile(r"prioriteitengroep ([123]):\s*(\d{1,2} \w+ \d{4})", re.IGNORECASE)


def parse_prioriteitengroepen(tekst: str, bron_id: str, bron_url: str, documenttitel: str, pagina: str = "") -> list[Bevinding]:
    """Zet de standaardzin(nen) om in kandidaat-bevindingen. Lege lijst als het patroon niet gevonden wordt."""
    m = RX_TOTAAL.search(tekst)
    if not m:
        return []
    peildatum = _nl_datum(m.group(1))
    pgs = list(RX_PG.finditer(tekst, m.start(), m.start() + 1500))
    prios = list(RX_PRIO.finditer(tekst, m.start(), m.start() + 2500))
    # Passage = van "Op <datum> waren ..." t/m de laatste gevonden prioriteringsdatum (geen menu-tekst ervoor).
    passage = tekst[m.start(): max([m.end()] + [x.end() for x in pgs + prios])].strip()
    basis = dict(
        voorziening_id="vaph-pvb", peildatum=peildatum, bron_id=bron_id, bron_url=bron_url,
        documenttitel=documenttitel, pagina=pagina, passage=passage,
        controlestatus=Controlestatus.ONGECONTROLEERD, opmerking="automatisch geparsed; nog te controleren",
    )
    pd_iso = peildatum.isoformat()
    uit: list[Bevinding] = [
        Bevinding(bevinding_id=f"vaph-pvb:wachtenden_personen:{pd_iso}", metriek="wachtenden_personen",
                  waarde=_getal(m.group(2)), eenheid="personen", definitie=DEFINITIE_PERSONEN, **basis),
        Bevinding(bevinding_id=f"vaph-pvb:wachtenden_vragen_totaal:{pd_iso}", metriek="wachtenden_vragen_totaal",
                  waarde=_getal(m.group(3)), eenheid="vragen", definitie=DEFINITIE_VRAGEN, **basis),
    ]
    for aantal, pg in (x.groups() for x in pgs):
        uit.append(Bevinding(bevinding_id=f"vaph-pvb:wachtenden_vragen_pg{pg}:{pd_iso}", metriek=f"wachtenden_vragen_pg{pg}",
                             waarde=_getal(aantal), eenheid="vragen", definitie=DEFINITIE_VRAGEN, **basis))
    for pg, datum in (x.groups() for x in prios):
        d = _nl_datum(datum)
        # Wachttijd van de eerstvolgende wachtende, uitgedrukt in dagen t.o.v. de peildatum.
        uit.append(Bevinding(bevinding_id=f"vaph-pvb:wachttijd_eerstvolgende_pg{pg}_dagen:{pd_iso}",
                             metriek=f"wachttijd_eerstvolgende_pg{pg}_dagen", waarde=(peildatum - d).days,
                             eenheid="dagen", definitie=DEFINITIE_PRIODATUM + f" Prioriteringsdatum: {d.isoformat()}.",
                             **basis))
    return uit


def harvest_jaarverslag(editie: str, pagina: int, bron_id: str, documenttitel: str) -> list[Bevinding]:
    url = EXTRANET.format(editie=editie, n=pagina)
    tekst = html_naar_tekst(fetch_pagina(editie, pagina))
    return parse_prioriteitengroepen(tekst, bron_id=bron_id, bron_url=url, documenttitel=documenttitel, pagina=f"pages/{pagina}")


def harvest_pdf(pdf_path: Path, bron_id: str, bron_url: str, documenttitel: str) -> list[Bevinding]:
    """Zelfde parser op 'Het VAPH in cijfers' (PDF)."""
    from .vlpar import pdf_text

    for i, tekst in enumerate(pdf_text(pdf_path), start=1):
        tekst = " ".join(tekst.split())
        uit = parse_prioriteitengroepen(tekst, bron_id, bron_url, documenttitel, pagina=f"p. {i}")
        if uit:
            return uit
    return []
