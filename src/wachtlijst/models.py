"""Datamodel.

Ontwerpprincipe: elke *bevinding* (een cijfer) en elk *budgetbedrag* is een aparte rij met volledige
herkomst: bron, document, pagina/passage, peildatum, definitie en controlestatus. Zo blijft elk getal
in het dashboard terug te voeren op één zin in één publiek document.

Sleutels:
- ``bron_id``        : korte slug van het publicatiekanaal (bv. ``vaph-cijfers-2025``)
- ``voorziening_id`` : slug van de voorziening (bv. ``vaph-pvb``)
- ``bevinding_id``   : ``<voorziening_id>:<metriek>:<peildatum>`` (uniek)
- ``budget_id``      : ``<voorziening_id>:<begrotingsjaar>:<fase>:<niveau>:<artikel|label>`` (uniek)
"""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class Controlestatus(str, Enum):
    """Hoe ver een cijfer gecontroleerd is. Het dashboard toont dit altijd naast het cijfer."""

    ONGECONTROLEERD = "ongecontroleerd"  # overgenomen uit secundaire bron of nog niet nagelezen
    BRON_GELEZEN = "bron_gelezen"  # één onderzoeker heeft de primaire bron gelezen en de passage gekopieerd
    GECONTROLEERD = "gecontroleerd"  # tweede, onafhankelijke lezing van dezelfde primaire bron
    BETWIST = "betwist"  # bronnen spreken elkaar tegen; zie ``opmerking``


class Bevoegdheid(str, Enum):
    GEMEENSCHAP = "Vlaamse Gemeenschap"  # persoonsgebonden aangelegenheden (GW art. 128, BWHI art. 5)
    GEWEST = "Vlaams Gewest"  # o.a. huisvesting, werk, energie (GW art. 39, BWHI art. 6)


class WachtlijstType(str, Enum):
    CENTRAAL_GEPUBLICEERD = "centraal_gepubliceerd"  # Vlaamse overheid beheert en publiceert cijfers
    CENTRAAL_NIET_GEPUBLICEERD = "centraal_niet_gepubliceerd"  # cijfers enkel via parlementaire vragen
    DECENTRAAL = "decentraal"  # lijsten per voorziening/aanbieder, geen centrale registratie
    GEEN = "geen"  # geen wachtlijstmechanisme (rechtsgebonden of budgetenveloppe)
    ONBEKEND = "onbekend"


class BronType(str, Enum):
    API = "api"
    DOWNLOAD = "download"  # Excel/CSV/ZIP
    HTML = "html"
    PDF = "pdf"
    DASHBOARD = "dashboard"  # Power BI / Tableau, enkel visueel


class Budgetfase(str, Enum):
    BO = "BO"  # begrotingsopmaak (initieel)
    BA = "BA"  # begrotingsaanpassing
    UITV = "UITV"  # uitvoering / rekening
    AGENTSCHAP = "AGENTSCHAP"  # cijfer uit jaarverslag/financieel verslag van het agentschap
    BELEID = "BELEID"  # beleidsmatig bedrag (bv. uitbreidingsbeleid, meerjarenplan)


class Kredietsoort(str, Enum):
    VAK = "VAK"  # vastleggingskrediet
    VEK = "VEK"  # vereffeningskrediet
    VRK = "VRK"  # variabel krediet
    NVT = "n.v.t."  # realisatie-/beleidsbedrag zonder kredietsoort


class Bron(BaseModel):
    bron_id: str
    naam: str
    organisatie: str
    url: str
    bron_type: BronType
    licentie: str = ""
    frequentie: str = ""  # jaarlijks / halfjaarlijks / doorlopend / eenmalig
    machinaal: str = ""  # hoe te bevragen: endpoint, patroon, of 'handmatig'
    opmerking: str = ""


class Voorziening(BaseModel):
    voorziening_id: str
    naam: str
    domein: str  # handicap / jeugdhulp / ouderenzorg / wonen / onderwijs / werk / inburgering / ggz / ...
    entiteit: str  # bevoegd agentschap/departement
    bevoegdheid: Bevoegdheid
    wachtlijst_naam: str = ""
    wachtlijst_type: WachtlijstType = WachtlijstType.ONBEKEND
    publicatie_bron_id: str = ""  # bron_id van de primaire cijferpublicatie
    frequentie: str = ""
    laatste_peildatum: Optional[date] = None
    scan_status: str = "te_onderzoeken"  # te_onderzoeken / in_onderzoek / proef_uitgewerkt / afgerond
    ise_koppeling: str = ""  # ISE-naam in de BBT (bv. 'PERSONEN MET EEN BEPERKING'); meerdere met ' | '
    opmerking: str = ""


class Bevinding(BaseModel):
    """Eén waargenomen cijfer, met volledige herkomst."""

    bevinding_id: str
    voorziening_id: str
    metriek: str  # bv. wachtenden_vragen_pg1
    waarde: float
    eenheid: str  # personen / vragen / budgetten / dagen / euro
    peildatum: date
    bron_id: str
    bron_url: str
    documenttitel: str
    pagina: str = ""  # paginanummer, sectie of HTML-pagina
    passage: str = ""  # letterlijk citaat
    definitie: str = ""
    publicatiedatum: Optional[date] = None
    controlestatus: Controlestatus = Controlestatus.ONGECONTROLEERD
    gecontroleerd_door: str = ""
    gecontroleerd_op: Optional[date] = None
    opmerking: str = ""

    @field_validator("bevinding_id")
    @classmethod
    def _id_shape(cls, v: str) -> str:
        if v.count(":") != 2:
            raise ValueError("bevinding_id moet de vorm <voorziening_id>:<metriek>:<peildatum> hebben")
        return v


class Budget(BaseModel):
    """Eén budgetbedrag voor een voorziening in een begrotingsjaar.

    ``niveau`` zegt waar het bedrag vandaan komt:
    - ``dept_artikel``      : begrotingsartikel bij het departement (bv. dotatie aan het VAPH)
    - ``entiteit_begroting``: eigen begroting van de rechtspersoon (Bijlage 2 bij de uitgavenbegroting)
    - ``uitbreidingsbeleid``: beleidsmatige enveloppe (groeipad) uit jaarverslag/meerjarenplan
    - ``realisatie``        : effectieve uitgave uit financieel verslag/rekening
    """

    budget_id: str
    voorziening_id: str
    begrotingsjaar: int = Field(ge=2000, le=2100)
    fase: Budgetfase
    niveau: str
    bedrag_eur: float
    kredietsoort: Kredietsoort = Kredietsoort.NVT
    artikel_code: str = ""  # bv. GB0-1GGF2RX-IS
    programma: str = ""
    ise: str = ""  # inhoudelijk structuurelement
    label: str = ""
    bron_id: str
    bron_url: str
    documenttitel: str
    pagina: str = ""
    passage: str = ""
    controlestatus: Controlestatus = Controlestatus.ONGECONTROLEERD
    gecontroleerd_door: str = ""
    gecontroleerd_op: Optional[date] = None
    opmerking: str = ""


class Krediet(BaseModel):
    """Eén bedrag uit een Beleids- en Begrotingstoelichting (BBT), per ISE of per begrotingsartikel.

    Eenheid: duizend euro (zoals in de BBT). ``kolom`` is de kolomkop uit het document ("BA 2024", "BO 2025",
    "Index", "Compensaties", "Andere bijstellingen", "Uitvoering 2024", ...). ``artikel_code`` leeg = ISE-totaal.
    Koppeling naar voorzieningen loopt via ``Voorziening.ise_koppeling`` (tekstmatch op ``ise``).
    """

    krediet_id: str = ""
    beleidsdomein: str  # WVG / WONEN
    begrotingsjaar: int = Field(ge=2000, le=2100)
    fase: Budgetfase
    stuk: str
    pfile_id: int
    beleidsveld: str = ""
    ise: str = ""
    ise_code: str = ""  # programma + ISE-letter uit de artikelcode, bv. GG-R
    programma: str = ""
    artikel_code: str = ""
    label: str = ""
    kolom: str
    kredietsoort: Kredietsoort
    bedrag_keur: float
    pagina: str = ""
    bron_url: str
    controlestatus: Controlestatus = Controlestatus.ONGECONTROLEERD
    opmerking: str = ""


# Mapping tabelnaam -> model, gebruikt door store en publish.
TABELLEN = {
    "bronnen": Bron,
    "voorzieningen": Voorziening,
    "bevindingen": Bevinding,
    "budgetten": Budget,
    "kredieten": Krediet,
}
SLEUTELS = {
    "bronnen": "bron_id",
    "voorzieningen": "voorziening_id",
    "bevindingen": "bevinding_id",
    "budgetten": "budget_id",
    "kredieten": "krediet_id",
}
