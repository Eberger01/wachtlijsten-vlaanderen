"""Beleids- en Begrotingstoelichtingen (BBT) — kredieten per ISE en per begrotingsartikel.

Register: ``config/bbt_documenten.yaml`` (WVG en Wonen, 2020–2026, BO/BA/UITV) met pfile-id's.
Download: ``download_all()`` -> ``data/raw/bbt/<domein>_<jaar>_<fase>_<pfile>.pdf`` (stdlib urllib, zodat
``scripts/harvest_bbt.py`` ook zonder extra packages op een gewone Windows-Python draait).
Parsen:   ``parse_pdf()`` -> lijst ``Krediet`` (ISE-totalen + artikelniveau), eenheid duizend euro.

Structuur van een BBT (geverifieerd op 13-V (2024-2025), pfile 2081035):
  ISE: PERSONEN MET EEN BEPERKING, MVG excl. DAB
  ... 1.7. Budgettair kader voor het begrotingsjaar
  (duizend euro)                 VAK                         VEK
                      BA 2024 evolutie BO 2025   BA 2024 evolutie BO 2025
  ESR-uitgaven (...)  331.740 -37.565 294.175    343.519 -40.728 302.791
  Toelagen (...)           25       1      26         25       1      26
  Overige (...)             0       0       0          0       0       0
  Totaal              331.765 -37.564 294.201    343.544 -40.727 302.817
  ...
  GB0-1GCF2BA-WT - BELEIDSONTWIKKELING EN -ONDERSTEUNING
  Kredietevolutie:
  (duizend euro)        VAK      VEK
  BA 2024           327.710  337.924
  Index               5.547    5.547
  Compensaties       -4.917   -4.755
  Andere bijstellingen -38.219 -39.923
  BO 2025           290.121  298.793

De parser is bewust tolerant (regex op genormaliseerde tekst) en markeert alles als ``ongecontroleerd``;
steekproefsgewijze controle tegen de PDF blijft nodig (``pagina`` staat in elke rij).
"""

from __future__ import annotations

import re
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import yaml

from .. import CONFIG_DIR, RAW_DIR
from ..models import Controlestatus, Krediet

PDF_URL = "https://docs.vlaamsparlement.be/files/pfile?id={pfile_id}"
DOC_URL = "https://www.vlaamsparlement.be/nl/parlementaire-documenten/parlementaire-initiatieven/{doc_id}"
UA = "Wachtlijst-onderzoek/0.1 (onderzoek sociale voorzieningen Vlaanderen)"


@dataclass
class BbtDoc:
    beleidsdomein: str
    begrotingsjaar: int
    fase: str
    stuk: str
    doc_id: int
    pfile_id: int
    ingediend: str
    opmerking: str = ""

    @property
    def pdf_url(self) -> str:
        return PDF_URL.format(pfile_id=self.pfile_id)

    @property
    def doc_url(self) -> str:
        return DOC_URL.format(doc_id=self.doc_id)

    @property
    def pad(self) -> Path:
        return RAW_DIR / "bbt" / f"{self.beleidsdomein}_{self.begrotingsjaar}_{self.fase}_{self.pfile_id}.pdf"


def registry(config: Path | None = None) -> tuple[list[BbtDoc], dict]:
    data = yaml.safe_load((config or CONFIG_DIR / "bbt_documenten.yaml").read_text(encoding="utf-8"))
    docs = [BbtDoc(**{k: (str(v) if k == "ingediend" else v) for k, v in d.items()}) for d in data["documenten"]]
    return docs, data["beleidsdomeinen"]


def download(doc: BbtDoc, force: bool = False) -> Path:
    doc.pad.parent.mkdir(parents=True, exist_ok=True)
    if doc.pad.exists() and doc.pad.stat().st_size > 10_000 and not force:
        return doc.pad
    req = urllib.request.Request(doc.pdf_url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=180) as r, doc.pad.open("wb") as fh:
        fh.write(r.read())
    return doc.pad


def download_all(domeinen: list[str] | None = None, jaren: list[int] | None = None, force: bool = False) -> list[Path]:
    docs, _ = registry()
    uit = []
    for d in docs:
        if domeinen and d.beleidsdomein not in domeinen:
            continue
        if jaren and d.begrotingsjaar not in jaren:
            continue
        uit.append(download(d, force=force))
    return uit


# ------------------------------------------------------------------------------------------------ parser
RX_ISE = re.compile(r"ISE(?:\s*\d+)?\s*:\s*([A-Za-zÉÈéè][A-Za-zÉÈéè0-9 ,'&/\-]+?)(?:,\s*MVG\s*excl\.?\s*DAB)?\s*$", re.MULTILINE)
# Kop boven de synthesetabel ("1.7. Budgettair kader ..." gevolgd door "PERSONEN MET EEN BEPERKING, MVG excl. DAB")
RX_ISE2 = re.compile(r"^([A-Za-zÉÈéè][A-Za-zÉÈéè0-9 '&/\-]{3,70}?),\s*MVG\s*excl\.?\s*DAB\s*$", re.MULTILINE)


def _ise_naam(s: str) -> str:
    """Normaliseer ISE-namen: hoofdletters, tabelkop-resten weg, bekende tikfouten in de bron herstellen."""
    s = " ".join(s.upper().split())
    s = re.sub(r"^(VAK|VEK|\d+\.?)\s+", "", s)
    s = re.sub(r"^(VAK|VEK)\s+", "", s)
    s = s.replace("AANDBODZIJDE", "AANBODZIJDE").replace("GEÏNTEGREERD", "GEINTEGREERD")
    return s.strip(" ,")
RX_BELEIDSVELD = re.compile(r"BELEIDSVELD\s+[IVX]+\s*:\s*([A-ZÉÈ][A-ZÉÈ0-9 ,'&/\-]+?)\s*$", re.MULTILINE)
# Artikelkop: code, koppelteken of en-dash, omschrijving (kan op de volgende regel doorlopen)
RX_ARTIKEL = re.compile(r"^([A-Z]{2}0-[0-9A-Z][A-Z]{3}[0-9A-Z]{3}-[A-Z]{2})\s*[-–]?\s*([A-ZÉÈ].*?)\s*$", re.MULTILINE)
RX_GETAL = r"([+-]?\d{1,3}(?:\.\d{3})*|[+-]?\d+)"
# Synthese per ISE: 'Totaal' gevolgd door 6 getallen (VAK ×3, VEK ×3); getallen mogen op de volgende regel staan
RX_TOTAAL6 = re.compile(r"^Totaal\s+" + r"\s+".join([RX_GETAL] * 6) + r"\s*$", re.MULTILINE)
# Artikelrij in uitvoerings-BBT (23-x): "Uitgaven" gevolgd door 6 getallen (VAK BA/BA-JR/BU, VEK idem)
RX_UITG6 = re.compile(r"^Uitgaven\s+" + r"\s+".join([RX_GETAL] * 6) + r"\s*$", re.MULTILINE)
# Strikte kolomkop BO-stukken: 'BA 2024 evolutie BO 2025 BA 2024 evolutie BO 2025'
RX_KOP_BO = re.compile(r"(BA\s*\d{4})\s+(evolutie)\s+(BO\s*\d{4})\s+BA\s*\d{4}\s+evolutie\s+BO\s*\d{4}", re.IGNORECASE)
# Regels in 'Kredietevolutie' / 'Begrotingsuitvoering': label gevolgd door VAK en VEK (precies twee getallen)
RX_KREDIETREGEL = re.compile(
    r"^((?:BA\s*[-–]\s*JR|BA-JR|BA|BO|BU|Uitvoering|Realisatie|Vastleggingen|Vereffeningen)\s*\d{4}"
    r"|Index|Compensaties|Andere bijstellingen|Bijstellingen?|Herverdelingen?)\s+"
    + RX_GETAL + r"\s+" + RX_GETAL + r"\s*$",
    re.MULTILINE | re.IGNORECASE,
)


def _num(s: str) -> float:
    return float(s.replace(".", "").replace("+", ""))


def _norm(tekst: str) -> str:
    # Verwijder zachte afbreekstreepjes/NBSP en normaliseer spaties per regel; houd regeleinden.
    tekst = tekst.replace("\xa0", " ").replace("­", "")
    return "\n".join(" ".join(l.split()) for l in tekst.splitlines())


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def _kolomlabel(lab: str) -> str:
    """'BA – JR 2025' -> 'BA-JR 2025'; 'BU 2025' -> 'Uitvoering 2025'; spaties normaliseren."""
    lab = re.sub(r"\s*[-–]\s*", "-", lab.strip())
    lab = re.sub(r"^(BA|BO|BU|BA-JR|Uitvoering|Realisatie|Index|Compensaties)(\d{4})", r"\1 \2", lab)
    lab = re.sub(r"^BU\b", "Uitvoering", lab, flags=re.IGNORECASE)
    return " ".join(lab.split())


def synthese_labels(doc: BbtDoc) -> list[str]:
    """Kolommen van de synthesetabel per ISE, afhankelijk van het soort stuk (geverifieerd op 13-V en 23-V)."""
    j = doc.begrotingsjaar
    if doc.fase == "UITV":
        return [f"BA {j}", f"BA-JR {j}", f"Uitvoering {j}"]  # 23-x: BA | BA na herverdelingen (JR) | BU
    if doc.fase == "BA":
        return [f"BO {j}", "evolutie", f"BA {j}"]  # 17-A-x (2020): BO | evolutie | BA (niet geverifieerd)
    return [f"BA {j - 1}", "evolutie", f"BO {j}"]  # 13-x


def _ise_code(artikel_code: str) -> str:
    """GB0-1GGF2RX-IS -> 'GG-R' (programma + ISE-letter); GH0-AGGF2RD-WT -> 'GG-R'."""
    return f"{artikel_code[5:7]}-{artikel_code[9]}" if len(artikel_code) >= 10 else ""


def parse_pdf(doc: BbtDoc, pad: Path | None = None, ise_codes: dict[str, str] | None = None) -> list[Krediet]:
    """Parse één BBT naar Krediet-rijen. Vereist pdfplumber.

    ``ise_codes`` (uit config) koppelt programma+ISE-letter aan de ISE-naam; artikelregels krijgen dan die naam,
    ongeacht de (soms onvolledige) kop in de PDF. ISE-totalen behouden de naam uit de kop.
    """
    import pdfplumber

    if ise_codes is None:
        try:
            ise_codes = registry()[1][doc.beleidsdomein].get("ise_codes", {})
        except Exception:  # noqa: BLE001
            ise_codes = {}
    pad = pad or doc.pad
    rijen: list[Krediet] = []
    beleidsveld = ""
    ise = ""
    ise_totaal_gezien = False  # enkel de eerste 'Totaal' na een ISE-kop is de synthesetabel
    labels = synthese_labels(doc)
    basis = dict(
        beleidsdomein=doc.beleidsdomein, begrotingsjaar=doc.begrotingsjaar, fase=doc.fase, stuk=doc.stuk,
        pfile_id=doc.pfile_id, bron_url=doc.pdf_url, controlestatus=Controlestatus.ONGECONTROLEERD,
        opmerking="automatisch geparsed uit BBT-PDF; steekproef tegen bron nodig",
    )

    def _add(**kw):
        k = Krediet(**basis, **kw)
        k.krediet_id = f"{doc.pfile_id}:{_slug(k.ise) or 'x'}:{k.artikel_code or 'ISE'}:{_slug(k.kolom)}:{k.kredietsoort}"
        rijen.append(k)

    with pdfplumber.open(pad) as pdf:
        artikel = ("", "")
        for pnr, page in enumerate(pdf.pages, start=1):
            tekst = _norm(page.extract_text() or "")
            if not tekst:
                continue
            events: list[tuple[int, str, str]] = []
            for m in RX_BELEIDSVELD.finditer(tekst):
                events.append((m.start(), "bv", m.group(1).strip()))
            for m in RX_ISE.finditer(tekst):
                events.append((m.start(), "ise", _ise_naam(m.group(1))))
            for m in RX_ISE2.finditer(tekst):
                events.append((m.start(), "ise", _ise_naam(m.group(1))))
            for m in RX_KOP_BO.finditer(tekst):
                events.append((m.start(), "kop", "|".join(g.strip() for g in m.groups())))
            for m in RX_TOTAAL6.finditer(tekst):
                events.append((m.start(), "tot", "|".join(m.groups())))
            for m in RX_ARTIKEL.finditer(tekst):
                events.append((m.start(), "art", m.group(1) + "|" + m.group(2)))
            for m in RX_UITG6.finditer(tekst):
                events.append((m.start(), "uitg", "|".join(m.groups())))
            for m in RX_KREDIETREGEL.finditer(tekst):
                events.append((m.start(), "regel", "|".join(m.groups())))
            events.sort()

            for _, soort, val in events:
                if soort == "bv":
                    beleidsveld = val
                elif soort == "ise":
                    if val != ise:
                        ise, ise_totaal_gezien, artikel = val, False, ("", "")
                elif soort == "kop":
                    labels = [_kolomlabel(x) for x in val.split("|")]
                elif soort == "tot" and ise and not ise_totaal_gezien:
                    vals = [_num(v) for v in val.split("|")]
                    if not any(vals):
                        continue  # een lege (0-)tabel is nooit de synthesetabel van een ISE; blijf zoeken
                    ise_totaal_gezien = True
                    for i, krediet in enumerate(("VAK", "VEK")):
                        for j, lab in enumerate(labels):
                            _add(beleidsveld=beleidsveld, ise=ise, artikel_code="", label="ISE-totaal", kolom=lab,
                                 kredietsoort=krediet, bedrag_keur=vals[i * 3 + j], pagina=str(pnr))
                elif soort == "art":
                    code, label = val.split("|", 1)
                    artikel = (code, label)
                elif soort == "uitg" and artikel[0] and ise:
                    code = _ise_code(artikel[0])
                    vals = [_num(v) for v in val.split("|")]
                    for i, ks in enumerate(("VAK", "VEK")):
                        for j, lab in enumerate(labels):
                            _add(beleidsveld=beleidsveld, ise=ise_codes.get(code, ise), ise_code=code, artikel_code=artikel[0], label=artikel[1],
                                 programma=artikel[0][5:7], kolom=lab, kredietsoort=ks, bedrag_keur=vals[i * 3 + j], pagina=str(pnr))
                elif soort == "regel" and artikel[0] and ise:
                    lab, vak, vek = val.split("|")
                    code = _ise_code(artikel[0])
                    for ks, bedrag in (("VAK", vak), ("VEK", vek)):
                        _add(beleidsveld=beleidsveld, ise=ise_codes.get(code, ise), ise_code=code, artikel_code=artikel[0], label=artikel[1],
                             programma=artikel[0][5:7], kolom=_kolomlabel(lab), kredietsoort=ks, bedrag_keur=_num(bedrag), pagina=str(pnr))
    # Ontdubbelen op id: hetzelfde artikel staat vaak twee keer (departement + entiteit onder gezag) — eerste wint.
    uniek: dict[str, Krediet] = {}
    for r in rijen:
        uniek.setdefault(r.krediet_id, r)
    return list(uniek.values())


def parse_tekst(doc: BbtDoc, tekst: str, pagina: int = 1) -> list[Krediet]:
    """Zelfde parser op losse tekst (voor tests zonder PDF)."""
    import tempfile

    # Hergebruik parse_pdf-logica via een minimale nep-pdf is omslachtig; dupliceer de kern op één 'pagina'.
    class _P:
        def extract_text(self):
            return tekst

    class _PDF:
        pages = [_P()]

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    import pdfplumber  # noqa: F401  (zodat dezelfde import-fout optreedt als in parse_pdf)

    orig = pdfplumber.open
    try:
        pdfplumber.open = lambda *_a, **_k: _PDF()  # type: ignore[assignment]
        with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
            return parse_pdf(doc, Path(tmp.name))
    finally:
        pdfplumber.open = orig
