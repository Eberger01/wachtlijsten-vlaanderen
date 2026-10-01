"""Seed van data/curated met de bronnenkaart, de inventaris en de proefvoorziening (VAPH-PVB).

Draai: ``python scripts/seed_proef.py``  (overschrijft data/curated/*.csv)

Alle cijfers hieronder zijn op 2026-10-01 uit de genoemde publieke documenten gelezen. De controlestatus
geeft aan hoe ver de controle staat:
  gecontroleerd   = twee onafhankelijke lezingen van de primaire bron (passage letterlijk geciteerd)
  bron_gelezen    = één lezing van de primaire bron
  ongecontroleerd = secundaire bron (pers, belangenorganisatie) of jaarreekstabel met afwijkingen
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from wachtlijst.models import (  # noqa: E402
    Bevinding, Bevoegdheid, Bron, BronType, Budget, Budgetfase, Controlestatus, Kredietsoort, Voorziening, WachtlijstType,
)
from wachtlijst.store import write_rows  # noqa: E402

VANDAAG = date(2026, 10, 1)
GEM, GEW = Bevoegdheid.GEMEENSCHAP, Bevoegdheid.GEWEST
GEC, GEL, ONG, BET = (Controlestatus.GECONTROLEERD, Controlestatus.BRON_GELEZEN,
                      Controlestatus.ONGECONTROLEERD, Controlestatus.BETWIST)

# --------------------------------------------------------------------------------------------- bronnen
BRONNEN = [
    Bron(bron_id="vlpar-search-api", naam="Vlaams Parlement — Document Search API", organisatie="Vlaams Parlement",
         url="https://ws.vlpar.be/api/search/query/{term}?collection=vp_collection&page=1&max=50&sort=date",
         bron_type=BronType.API, licentie="Modellicentie Gratis Hergebruik v1.0", frequentie="doorlopend",
         machinaal="JSON; metatags per hit: aggregaattype, thema, zittingsjaar, document (PDF), opendata (XML). Swagger: https://ws.vlpar.be/v3/api-docs",
         opmerking="Primaire machinale ingang: schriftelijke vragen, vragen om uitleg, Rekenhof-verslagen, BBT's en begrotingsstukken. 'wachtlijst' -> 12.552 hits (2026-10-01)."),
    Bron(bron_id="vlpar-opendata", naam="Vlaams Parlement — open data XML per entiteit", organisatie="Vlaams Parlement",
         url="http://ws.vlpar.be/e/opendata/{soort}/{id}", bron_type=BronType.API, licentie="Modellicentie Gratis Hergebruik v1.0",
         frequentie="doorlopend", machinaal="soort = schv (schriftelijke vraag), vi, jln, vv, verg; XML met PDF-link",
         opmerking="Documentatie: https://www.vlaamsparlement.be/nl/parlementair-werk/dossiers/dossiers/open-data"),
    Bron(bron_id="vlpar-docs", naam="Vlaams Parlement — parlementaire documenten (PDF)", organisatie="Vlaams Parlement",
         url="https://docs.vlaamsparlement.be/files/pfile?id={pfile-id}", bron_type=BronType.PDF,
         licentie="Modellicentie Gratis Hergebruik v1.0", frequentie="doorlopend",
         machinaal="pfile-id uit metatag 'document'; tekst via pdfplumber", opmerking="Antwoorden op schriftelijke vragen, BBT's, uitgavenbegroting (stuk 15), Rekenhof (stuk 16/36)."),
    Bron(bron_id="vlpar-begroting-dossier", naam="Vlaams Parlement — dossier Begroting {jaar}", organisatie="Vlaams Parlement",
         url="https://www.vlaamsparlement.be/nl/parlementair-werk/dossiers/dossiers/begroting-2026", bron_type=BronType.HTML,
         frequentie="jaarlijks (BO okt, BA apr)", machinaal="HTML-scrape -> PDF's; stuk 13-x = BBT, 15 = uitgavenbegroting (+Bijlage 2 rechtspersonen), 16 = Rekenhof, 19 = aanpassing, 23-x = BBT uitvoering",
         opmerking="Geen open data per begrotingsartikel; enkel PDF. ISE-tabellen in BBT's zijn regelmatig genoeg voor tabelextractie."),
    Bron(bron_id="themis", naam="Themis — besluitvorming Vlaamse Regering (open data)", organisatie="Departement Kanselarij en Buitenlandse Zaken",
         url="https://themis.vlaanderen.be/", bron_type=BronType.API, frequentie="per ministerraad",
         machinaal="JSON:API /catalogs -> /datasets -> /distributions (Turtle); PDF via /files/{id}/download",
         opmerking="Bevat BBT's als mededeling aan de VR (bv. BBT WVG BO 2026 = VR 2025 2410 MED.0443-1)."),
    Bron(bron_id="codex-api", naam="Vlaamse Codex Open Data API", organisatie="Vlaamse overheid", url="https://codex.opendata.api.vlaanderen.be/",
         bron_type=BronType.API, frequentie="doorlopend", machinaal="GET /api/WetgevingDocument/Zoeken?Zoekterm=…; /api/WetgevingDocument/{id}/Structuur",
         opmerking="Juridische grondslag per voorziening (bv. BVR 27-11-2015 PVB; BWHI = document 1004736)."),
    Bron(bron_id="datavindplaats", naam="Datavindplaats (Vlaamse open-datacatalogus)", organisatie="Digitaal Vlaanderen",
         url="https://www.vlaanderen.be/datavindplaats/catalogus?q=wachtlijst", bron_type=BronType.HTML, frequentie="doorlopend",
         machinaal="API https://datavindplaats.api.vlaanderen.be (DCAT-AP-VL)", opmerking="Zoekterm 'wachtlijst' -> 0 datasets (2026-10-01): geen open dataset wachtlijsten."),
    Bron(bron_id="statistiek-vlaanderen", naam="Statistiek Vlaanderen — uitgaven Vlaamse overheid (COFOG)", organisatie="Statistiek Vlaanderen",
         url="https://www.vlaanderen.be/statistiek-vlaanderen/overheidsfinancien/uitgaven-vlaamse-overheid", bron_type=BronType.HTML,
         frequentie="jaarlijks", machinaal="HTML + bevragingsmodule; geen API", opmerking="Macro-check: 'sociale bescherming' ≈ 27 % van 64,7 mld (2025). Geen detail per voorziening."),
    Bron(bron_id="dfb-begroting", naam="Departement Financiën en Begroting — begroting in cijfers", organisatie="Departement Financiën en Begroting",
         url="https://www.vlaanderen.be/departement-financien-en-begroting/begroting/in-cijfers/uitgaven", bron_type=BronType.DASHBOARD,
         frequentie="per begrotingsronde", machinaal="Datawrapper-embeds (dataset.csv niet geverifieerd)", opmerking="Enkel totalen per beleidsdomein; algemene rekening als PDF."),
    Bron(bron_id="vaph-cijfers-2025", naam="Het VAPH in cijfers 2025", organisatie="VAPH", url="https://publicaties.vlaanderen.be/view-file/85057",
         bron_type=BronType.PDF, frequentie="jaarlijks (juni)", machinaal="PDF, pdfplumber; patroon 'Op 31 december JJJJ waren N personen …'",
         opmerking="PDF-versie 1 juni 2026. Bevat wachtlijst (p. 34), terbeschikkingstellingen (p. 36) én budget (p. 70-71)."),
    Bron(bron_id="vaph-cijfers-2022", naam="Het VAPH in cijfers 2022", organisatie="VAPH", url="https://publicaties.vlaanderen.be/view-file/57023",
         bron_type=BronType.PDF, frequentie="jaarlijks", machinaal="PDF", opmerking="PDF-versie 19 juni 2023."),
    Bron(bron_id="vaph-cijfers-2021", naam="Het VAPH in cijfers 2021", organisatie="VAPH", url="https://publicaties.vlaanderen.be/view-file/50259",
         bron_type=BronType.PDF, frequentie="jaarlijks", machinaal="PDF", opmerking="Versie 30 mei 2022."),
    Bron(bron_id="vaph-cijfers-2019", naam="Het VAPH in cijfers 2019", organisatie="VAPH", url="https://publicaties.vlaanderen.be/view-file/42019",
         bron_type=BronType.PDF, frequentie="jaarlijks", machinaal="PDF", opmerking="Versie 4 juni 2020."),
    Bron(bron_id="vaph-jaarverslag-2024", naam="VAPH jaarverslag 2024 (HTML)", organisatie="VAPH", url="https://extranet.vaph.be/jaarverslag/2024/pages/25",
         bron_type=BronType.HTML, frequentie="jaarlijks", machinaal="extranet.vaph.be/jaarverslag/{jaar}/pages/{n}; 'Prioriteitengroepen' = pages/25, 'Terbeschikkingstellingen' = pages/26, 'Inzet middelen' = pages/78",
         opmerking="www.vaph.be blokkeert bots (403); extranet niet."),
    Bron(bron_id="vaph-jaarverslag-2024-h1", naam="VAPH jaarverslag 2024 — eerste jaarhelft (HTML)", organisatie="VAPH",
         url="https://extranet.vaph.be/jaarverslag/2024-eerste-jaarhelft/pages/25/", bron_type=BronType.HTML, frequentie="halfjaarlijks", machinaal="idem"),
    Bron(bron_id="vaph-jaarverslag-2023", naam="VAPH jaarverslag 2023 (HTML)", organisatie="VAPH", url="https://extranet.vaph.be/jaarverslag/2023/pages/25",
         bron_type=BronType.HTML, frequentie="jaarlijks", machinaal="'Prioriteitengroepen' = pages/25; 'Inzet middelen' = pages/42"),
    Bron(bron_id="vaph-jaarverslag-2022", naam="VAPH jaarverslag 2022 (HTML) — Evolutie in ondersteuning", organisatie="VAPH",
         url="https://extranet.vaph.be/jaarverslag/2022/pages/54/", bron_type=BronType.HTML, frequentie="jaarlijks", machinaal="jaarreekstabel 2018-2022",
         opmerking="Tabelwaarden wijken voor 2019/2021 licht af van de jaar-PDF's (personen vs vragen?)."),
    Bron(bron_id="vaph-financieel-2024", naam="VAPH financieel verslag 2024", organisatie="VAPH",
         url="https://extranet.vaph.be/jaarverslag/2024/media/files/financieel-verslag-2024-in-lay-out.pdf", bron_type=BronType.PDF, frequentie="jaarlijks"),
    Bron(bron_id="vaph-financieel-2023", naam="VAPH financieel verslag 2023", organisatie="VAPH",
         url="https://extranet.vaph.be/jaarverslag/2023/media/files/financieel-verslag-2023-in-lay-out-definitief.pdf", bron_type=BronType.PDF, frequentie="jaarlijks"),
    Bron(bron_id="vlpar-uitgavenbegroting-2025", naam="Ontwerp van decreet houdende de uitgavenbegroting 2025 — stuk 15 (2024-2025) nr. 1",
         organisatie="Vlaams Parlement", url="https://docs.vlaamsparlement.be/files/pfile?id=2078969", bron_type=BronType.PDF, frequentie="jaarlijks",
         machinaal="PDF; artikeltabellen VAK/VEK in k€", opmerking="Ingediend 8-11-2024; decreet 20-12-2024."),
    Bron(bron_id="vlpar-plenaire-2026-04-01", naam="Plenaire vergadering Vlaams Parlement 1 april 2026 — verslag", organisatie="Vlaams Parlement",
         url="https://www.vlaamsparlement.be/nl/parlementair-werk/plenaire-vergaderingen/2010388/verslag/2019101", bron_type=BronType.HTML, frequentie="eenmalig"),
    Bron(bron_id="vlpar-sv-125-2022", naam="Schriftelijke vraag nr. 125 (Van der Vloet, 28-10-2022) — PVB prioriteitengroep 1", organisatie="Vlaams Parlement",
         url="https://docs.vlaamsparlement.be/files/pfile?id=1896316", bron_type=BronType.PDF, frequentie="eenmalig"),
    Bron(bron_id="opgroeien-nrtj", naam="Opgroeien — aanvragen crisisjeugdhulp en niet-rechtstreeks toegankelijke jeugdhulp", organisatie="Agentschap Opgroeien",
         url="https://www.opgroeien.be/kennis/cijfers-en-onderzoek/aanvragen-crisisjeugdhulp-en-niet-rechtstreeks-toegankelijke-jeugdhulp",
         bron_type=BronType.DASHBOARD, frequentie="jaarlijks", machinaal="Power BI 'Cijfers op maat' (geen download gevonden)", opmerking="Laatst bijgewerkt 16-07-2026."),
    Bron(bron_id="vlpar-sv-213-2026", naam="Schriftelijke vraag nr. 213 (Naji, 30-01-2026) — kandidaat-huurders sociale huur", organisatie="Vlaams Parlement",
         url="https://docs.vlaamsparlement.be/files/pfile?id=2291613", bron_type=BronType.PDF, frequentie="eenmalig"),
    Bron(bron_id="agii-jaarverslag-2023", naam="Agentschap Integratie en Inburgering — jaarverslag 2023", organisatie="AgII",
         url="https://integratie-inburgering.be/sites/default/files/2024-06/AgII_Jaarverslag_2023.pdf", bron_type=BronType.PDF, frequentie="jaarlijks"),
    Bron(bron_id="vdab-maatwerk-toelichting", naam="VDAB — toelichting indicering en toeleiding collectief maatwerk (commissie 19-03-2025)", organisatie="VDAB / Vlaams Parlement",
         url="https://docs.vlaamsparlement.be/files/pfile?id=2118435", bron_type=BronType.PDF, frequentie="eenmalig"),
    Bron(bron_id="vsb-dossiers", naam="Departement Zorg — aantal dossiers zorgbudgetten Vlaamse sociale bescherming", organisatie="Departement Zorg / VSB",
         url="https://www.departementzorg.be/nl/aantal-dossiers-zorgbudgetten-vlaamse-sociale-bescherming", bron_type=BronType.DOWNLOAD, frequentie="jaarlijks",
         machinaal="Excel per jaar + ZIP draaitabellen (2017-2024)"),
    Bron(bron_id="rekenhof-begroting-2026", naam="Rekenhof — verslag over het onderzoek van de Vlaamse begroting 2026 (stuk 16 (2025-2026) nr. 1)",
         organisatie="Rekenhof", url="https://docs.vlaamsparlement.be/files/pfile?id=2235038", bron_type=BronType.PDF, frequentie="jaarlijks",
         opmerking="ccrek.be blokkeert bots; Rekenhof-verslagen zijn via de Parlement-API bereikbaar (aggregaattype 'Verslag van het Rekenhof')."),
    Bron(bron_id="grip-wachtlijst-2022", naam="GRIP vzw — 'Verbetering in wachtlijst nog niet vast te stellen' (6-5-2022)", organisatie="GRIP vzw (secundair)",
         url="https://www.gripvzw.be/nl/artikel/549/verbetering-in-wachtlijst-nog-niet-vast-te-stellen", bron_type=BronType.HTML, frequentie="eenmalig",
         opmerking="Citeert VAPH-halfjaarverslagen; secundaire bron."),
    Bron(bron_id="vrt-2026-05-25", naam="VRT NWS 25-5-2026 — 'nog altijd 18.000 mensen op wachtlijst'", organisatie="VRT (secundair)",
         url="https://www.vrt.be/vrtnws/nl/2026/05/25/18-000-mensen-met-een-handicap-wachten-op-persoonlijk-budget/", bron_type=BronType.HTML, frequentie="eenmalig"),
]

# ---------------------------------------------------------------------------------------- voorzieningen
V = Voorziening
WT = WachtlijstType
VOORZIENINGEN = [
    V(voorziening_id="vaph-pvb", naam="Persoonsvolgend budget (PVB) meerderjarigen", domein="handicap", entiteit="VAPH", bevoegdheid=GEM,
      wachtlijst_naam="Prioriteitengroepen 1/2/3 (vragen naar PVB)", wachtlijst_type=WT.CENTRAAL_GEPUBLICEERD, publicatie_bron_id="vaph-cijfers-2025",
      frequentie="halfjaarlijks (30/06, 31/12)", laatste_peildatum=date(2025, 12, 31), scan_status="proef_uitgewerkt",
      opmerking="Best gedocumenteerde wachtlijst; jaarverslag HTML + PDF 'VAPH in cijfers'. Automatische toekenningsgroepen (nood, spoed, zorgcontinuïteit) staan buiten de PG's."),
    V(voorziening_id="opgroeien-nrtj", naam="Niet-rechtstreeks toegankelijke jeugdhulp (incl. VAPH-MFC, pleegzorg; excl. PAB)", domein="jeugdhulp", entiteit="Agentschap Opgroeien (intersectorale toegangspoort)",
      bevoegdheid=GEM, wachtlijst_naam="Wachtenden NRTJ per typemodule", wachtlijst_type=WT.CENTRAAL_GEPUBLICEERD, publicatie_bron_id="opgroeien-nrtj",
      frequentie="jaarlijks", laatste_peildatum=date(2025, 12, 31), scan_status="in_onderzoek", opmerking="31/12/2025: 9.748 wachtenden (+6 %); 2024: 9.194. Minderjarigen met PAB-vraag zitten hier, niet bij VAPH."),
    V(voorziening_id="wonen-sociale-huur", naam="Sociale huurwoning", domein="wonen", entiteit="Wonen in Vlaanderen / woonmaatschappijen", bevoegdheid=GEW,
      wachtlijst_naam="Centraal inschrijvingsregister (CIR) kandidaat-huurders", wachtlijst_type=WT.CENTRAAL_GEPUBLICEERD, publicatie_bron_id="vlpar-sv-213-2026",
      frequentie="jaarlijks (jaarverslag)", laatste_peildatum=date(2025, 4, 30), scan_status="in_onderzoek",
      opmerking="199.085 kandidaat-huurders (april 2025, na herbevestiging CIR); 176.026 eind 2022; gem. wachttijd 4,8 jaar (2024). Primaire statistiekpagina nog te lokaliseren."),
    V(voorziening_id="wonen-huurpremie", naam="Vlaamse huurpremie", domein="wonen", entiteit="Wonen in Vlaanderen", bevoegdheid=GEW,
      wachtlijst_naam="geen eigen lijst; afgeleid van 4 jaar inschrijving CIR", wachtlijst_type=WT.GEEN, scan_status="afgerond"),
    V(voorziening_id="wonen-sociale-koop", naam="Sociale koopwoning", domein="wonen", entiteit="Woonmaatschappijen / Wonen in Vlaanderen", bevoegdheid=GEW,
      wachtlijst_naam="Inschrijvingsregister kandidaat-kopers per woonmaatschappij", wachtlijst_type=WT.DECENTRAAL, scan_status="in_onderzoek",
      opmerking="SV 448 (Mertens, 15-04-2025): Wonen in Vlaanderen beschikt niet over centrale data."),
    V(voorziening_id="agii-mo", naam="Inburgering — maatschappelijke oriëntatie", domein="inburgering", entiteit="Agentschap Integratie en Inburgering (Atlas/IN-Gent)", bevoegdheid=GEM,
      wachtlijst_naam="KPI 'zonder passend MO-aanbod' / '> 6 maanden wachtend'", wachtlijst_type=WT.CENTRAAL_GEPUBLICEERD, publicatie_bron_id="agii-jaarverslag-2023",
      frequentie="jaarlijks", laatste_peildatum=date(2023, 12, 31), scan_status="in_onderzoek", opmerking="2023: 1.229 zonder passend aanbod; 1.588 > 6 maanden. Jaarverslag 2024/2025 nog na te kijken."),
    V(voorziening_id="vdab-collectief-maatwerk", naam="Collectief maatwerk (sociale economie)", domein="werk", entiteit="VDAB / Departement Werk en Sociale Economie", bevoegdheid=GEW,
      wachtlijst_naam="Werkzoekenden met CMW-advies zonder job (vacaturegedreven)", wachtlijst_type=WT.CENTRAAL_NIET_GEPUBLICEERD, publicatie_bron_id="vdab-maatwerk-toelichting",
      frequentie="op vraag (parlement)", laatste_peildatum=date(2024, 12, 31), scan_status="in_onderzoek", opmerking="dec 2024: 3.086 met advies vs 751 openstaande vacatures; individueel maatwerk 9.615 (feb 2025)."),
    V(voorziening_id="zorg-woonzorgcentra", naam="Woonzorgcentra, kortverblijf, dagverzorging, assistentiewoningen", domein="ouderenzorg", entiteit="Departement Zorg (afd. Woonzorg)", bevoegdheid=GEM,
      wachtlijst_naam="Wachtlijst per voorziening; erkenningskalender (aanbodzijde)", wachtlijst_type=WT.DECENTRAAL, scan_status="in_onderzoek",
      opmerking="Geen centrale bewonerswachtlijst. Erkenningskalender = wachtlijst voor erkenning van bijkomende woongelegenheden."),
    V(voorziening_id="zorg-cgg", naam="Centra voor Geestelijke Gezondheidszorg", domein="ggz", entiteit="Departement Zorg", bevoegdheid=GEM,
      wachtlijst_naam="Wachttijd aanmelding→1e contact (EPD), per CGG", wachtlijst_type=WT.CENTRAAL_NIET_GEPUBLICEERD, scan_status="in_onderzoek",
      opmerking="Minister (SV 379, 12-02-2025): wachtlijst niet centraal gemonitord; wachttijden wel in bijlage bij SV (pfile 2138635)."),
    V(voorziening_id="zorg-cos", naam="Centra voor Ontwikkelingsstoornissen (diagnostiek)", domein="handicap", entiteit="Departement Zorg", bevoegdheid=GEM,
      wachtlijst_naam="Wachtlijst per centrum", wachtlijst_type=WT.DECENTRAAL, scan_status="te_onderzoeken", opmerking="jan 2023: > 2.000 kinderen, 12 maanden tot 2,5 jaar; geen recente centrale cijfers."),
    V(voorziening_id="opgroeien-kinderopvang", naam="Kinderopvang baby's en peuters", domein="gezin", entiteit="Agentschap Opgroeien (Lokaal Loket Kinderopvang)", bevoegdheid=GEM,
      wachtlijst_naam="Opvangvragen via lokale loketten; geen Vlaamse wachtlijst", wachtlijst_type=WT.DECENTRAAL, scan_status="in_onderzoek",
      opmerking="Onderzoek 2025: 26.355 van 71.238 aanvragende ouders zonder plaats (dubbeltellingen mogelijk). Uitbreidingsrondes = gerangschikte lijst voor organisatoren."),
    V(voorziening_id="opgroeien-pleegzorg", naam="Pleegzorg", domein="jeugdhulp", entiteit="Opgroeien / diensten voor pleegzorg", bevoegdheid=GEM,
      wachtlijst_naam="Kinderen wachtend op pleeggezin (per provinciale dienst)", wachtlijst_type=WT.DECENTRAAL, scan_status="te_onderzoeken", opmerking="Grotendeels vervat in NRTJ-wachtenden (2.707 verblijfsvragen pleeggezin, 2025)."),
    V(voorziening_id="onderwijs-buitengewoon", naam="Buitengewoon onderwijs (capaciteit)", domein="onderwijs", entiteit="AGODI / Departement Onderwijs, LOP's", bevoegdheid=GEM,
      wachtlijst_naam="Wachtlijsten per school / LOP-aanmelding; geen centrale registratie", wachtlijst_type=WT.DECENTRAAL, scan_status="in_onderzoek",
      opmerking="SV 1152 (Werbrouck, 04-09-2025): geen structurele monitoring. Capaciteitsmonitor: tekort ± 5.700 plaatsen 2030-31."),
    V(voorziening_id="nt2", naam="Nederlands tweede taal (NT2)", domein="inburgering", entiteit="AgII / CVO's / Ligo / UTC", bevoegdheid=GEM,
      wachtlijst_naam="Wachtlijsten per aanbieder", wachtlijst_type=WT.DECENTRAAL, scan_status="te_onderzoeken", opmerking="Afsprakenkader NT2 vraagt de agentschappen wachtlijsten in kaart te brengen; geen publiek cijfer."),
    V(voorziening_id="zorg-gezinszorg", naam="Gezinszorg en aanvullende thuiszorg", domein="thuiszorg", entiteit="Departement Zorg", bevoegdheid=GEM,
      wachtlijst_naam="Urencontingent per dienst (MB); wachtlijsten per dienst", wachtlijst_type=WT.DECENTRAAL, scan_status="te_onderzoeken", opmerking="Rantsoenering via urencontingent; besparing 2026 ± 30 mln euro."),
    V(voorziening_id="vsb-zorgbudget", naam="Zorgbudgetten Vlaamse sociale bescherming", domein="zorg", entiteit="Agentschap VSB / Departement Zorg", bevoegdheid=GEM,
      wachtlijst_naam="geen (rechtsgebonden; wel doorlooptijd)", wachtlijst_type=WT.GEEN, publicatie_bron_id="vsb-dossiers", frequentie="jaarlijks", scan_status="afgerond",
      opmerking="Excel-downloads per jaar (dossiers 2017-2024) — bruikbaar als referentie voor open-dataformaat."),
    V(voorziening_id="ajh-justitiehuizen", naam="Justitiehuizen (werkstraf, probatie, slachtofferonthaal)", domein="justitie", entiteit="Agentschap Justitie en Handhaving", bevoegdheid=GEM,
      wachtlijst_naam="Niet-opgestarte mandaten (niet geverifieerd)", wachtlijst_type=WT.ONBEKEND, scan_status="te_onderzoeken"),
    V(voorziening_id="wonen-premies", naam="Mijn VerbouwPremie / Mijn VerbouwLening / Noodkoopfonds", domein="wonen-energie", entiteit="Wonen in Vlaanderen / VEKA / Energiehuizen", bevoegdheid=GEW,
      wachtlijst_naam="geen; Noodkoopfonds werkt met enveloppes per OCMW (lokale lijsten mogelijk)", wachtlijst_type=WT.GEEN, scan_status="afgerond"),
    V(voorziening_id="vwf-woonlening", naam="Vlaamse woonlening (Vlaams Woningfonds)", domein="wonen", entiteit="Vlaams Woningfonds", bevoegdheid=GEW,
      wachtlijst_naam="geen", wachtlijst_type=WT.GEEN, scan_status="afgerond"),
    V(voorziening_id="vdab-ibo", naam="Individuele beroepsopleiding (IBO)", domein="werk", entiteit="VDAB", bevoegdheid=GEW, wachtlijst_naam="geen",
      wachtlijst_type=WT.GEEN, scan_status="afgerond"),
]

# ------------------------------------------------------------------------------------------ bevindingen
DEF_VRAGEN = ("Aantal vragen naar een PVB geregistreerd in de prioriteitengroepen op de peildatum; eenzelfde persoon kan in twee "
              "prioriteitengroepen voorkomen (hoofd- en deelvraag). Som PG1+PG2+PG3 = totaal vragen.")
DEF_PERSONEN = "Aantal unieke personen met minstens één vraag geregistreerd in de prioriteitengroepen."
DEF_PRIO = "Prioriteringsdatum (datum aanvraag/herziening) van de eerstvolgende wachtende; uitgedrukt als dagen vóór de peildatum."
DEF_TBS = "Aantal persoonsvolgende budgetten ter beschikking gesteld in het kalenderjaar (één persoon kan meerdere budgetten krijgen)."


def _b(metriek, waarde, eenheid, peildatum, bron_id, url, titel, pagina, passage, definitie, status, pub=None, door="", opm=""):
    return Bevinding(
        bevinding_id=f"vaph-pvb:{metriek}:{peildatum.isoformat()}", voorziening_id="vaph-pvb", metriek=metriek, waarde=waarde,
        eenheid=eenheid, peildatum=peildatum, bron_id=bron_id, bron_url=url, documenttitel=titel, pagina=pagina, passage=passage,
        definitie=definitie, publicatiedatum=pub, controlestatus=status, gecontroleerd_door=door,
        gecontroleerd_op=VANDAAG if door else None, opmerking=opm,
    )


def _pg_set(peildatum, personen, vragen, pg, prio, bron_id, url, titel, pagina, passage, status, pub, door, opm=""):
    uit = [
        _b("wachtenden_personen", personen, "personen", peildatum, bron_id, url, titel, pagina, passage, DEF_PERSONEN, status, pub, door, opm),
        _b("wachtenden_vragen_totaal", vragen, "vragen", peildatum, bron_id, url, titel, pagina, passage, DEF_VRAGEN, status, pub, door, opm),
    ]
    for i, n in enumerate(pg, start=1):
        uit.append(_b(f"wachtenden_vragen_pg{i}", n, "vragen", peildatum, bron_id, url, titel, pagina, passage, DEF_VRAGEN, status, pub, door, opm))
    for i, d in enumerate(prio, start=1):
        if d:
            uit.append(_b(f"wachttijd_eerstvolgende_pg{i}_dagen", (peildatum - d).days, "dagen", peildatum, bron_id, url, titel, pagina, passage,
                          DEF_PRIO + f" Prioriteringsdatum: {d.isoformat()}.", status, pub, door, opm))
    return uit


U85057 = "https://publicaties.vlaanderen.be/view-file/85057"
U24 = "https://extranet.vaph.be/jaarverslag/2024/pages/25"
U24H1 = "https://extranet.vaph.be/jaarverslag/2024-eerste-jaarhelft/pages/25/"
U23 = "https://extranet.vaph.be/jaarverslag/2023/pages/25"
U57023 = "https://publicaties.vlaanderen.be/view-file/57023"
U50259 = "https://publicaties.vlaanderen.be/view-file/50259"
U42019 = "https://publicaties.vlaanderen.be/view-file/42019"
U22T = "https://extranet.vaph.be/jaarverslag/2022/pages/54/"
D_EB = "onderzoeksagent + 2e lezing Claude + EB (2026-10-01)"

BEVINDINGEN: list[Bevinding] = []
BEVINDINGEN += _pg_set(
    date(2025, 12, 31), 17889, 17947, (867, 7856, 9224), (date(2024, 10, 1), date(2018, 3, 15), date(2002, 1, 16)),
    "vaph-cijfers-2025", U85057, "Het VAPH in cijfers 2025", "p. 34",
    "Op 31 december 2025 waren 17.889 personen met in totaal 17.947 vragen geregistreerd in de prioriteitengroepen: 867 vragen in "
    "prioriteitengroep 1, 7856 vragen in prioriteitengroep 2, 9224 vragen in prioriteitengroep 3. De eerstvolgende wachtende in elke "
    "prioriteitengroep had op 31 december 2025 de volgende prioriteringsdatum: prioriteitengroep 1: 1 oktober 2024, prioriteitengroep 2: "
    "15 maart 2018, prioriteitengroep 3: 16 januari 2002.",
    GEC, date(2026, 6, 1), "onderzoeksagent + 2e lezing Claude (2026-10-01)",
)
BEVINDINGEN += _pg_set(
    date(2024, 12, 31), 18261, 18302, (526, 8091, 9685), (date(2024, 1, 1), date(2016, 10, 1), date(2002, 1, 16)),
    "vaph-jaarverslag-2024", U24, "VAPH jaarverslag 2024 — Prioriteitengroepen", "pages/25",
    "Op 31 december 2024 waren 18.261 personen met in totaal 18.302 vragen geregistreerd in de prioriteitengroepen: 526 vragen in "
    "prioriteitengroep 1, 8091 vragen in prioriteitengroep 2, 9685 vragen in prioriteitengroep 3. Prioriteringsdatum eerstvolgende "
    "wachtende: prioriteitengroep 1: 1 januari 2024, prioriteitengroep 2: 1 oktober 2016, prioriteitengroep 3: 16 januari 2002.",
    GEC, None, "onderzoeksagent + 2e lezing Claude (2026-10-01)", "publicatiedatum HTML-jaarverslag niet op de pagina gelezen (± mei 2025)",
)
BEVINDINGEN += _pg_set(
    date(2024, 6, 30), 17848, 17889, (371, 7633, 9885), (None, None, None),
    "vaph-jaarverslag-2024-h1", U24H1, "VAPH jaarverslag 2024 eerste jaarhelft — Prioriteitengroepen", "pages/25",
    "Op 30 juni 2024 waren 17.848 personen met in totaal 17.889 vragen geregistreerd in de prioriteitengroepen: 371 vragen in "
    "prioriteitengroep 1, 7633 vragen in prioriteitengroep 2 en 9885 vragen in prioriteitengroep 3.",
    GEC, None, D_EB,
)
BEVINDINGEN += _pg_set(
    date(2023, 12, 31), 17648, 17678, (261, 7255, 10162), (date(2023, 10, 1), date(2016, 10, 1), date(2002, 1, 16)),
    "vaph-jaarverslag-2023", U23, "VAPH jaarverslag 2023 — Prioriteitengroepen", "pages/25",
    "Op 31 december 2023 waren 17.648 personen met in totaal 17.678 vragen geregistreerd in de prioriteitengroepen: 261 vragen in "
    "prioriteitengroep 1, 7255 vragen in prioriteitengroep 2, 10.162 vragen in prioriteitengroep 3. Prioriteringsdatum eerstvolgende "
    "wachtende: prioriteitengroep 1: 1 oktober 2023, prioriteitengroep 2: 1 oktober 2016, prioriteitengroep 3: 16 januari 2002.",
    GEC, None, "onderzoeksagent + 2e lezing Claude (2026-10-01)",
)
BEVINDINGEN += _pg_set(
    date(2022, 12, 31), 16702, 16727, (210, 6172, 10345), (date(2022, 10, 1), date(2016, 10, 1), date(2002, 1, 16)),
    "vaph-cijfers-2022", U57023, "Het VAPH in cijfers 2022", "sectie 'Vragen geregistreerd in prioriteitengroepen' (PDF p. 20-21)",
    "Op 31 december 2022 waren 16.702 personen met in totaal 16.727 vragen geregistreerd in de prioriteitengroepen (eenzelfde persoon kan "
    "in twee prioriteitengroepen voorkomen met een hoofd- en een deelvraag naar ondersteuning): • 210 vragen in prioriteitengroep 1 "
    "• 6.172 vragen in prioriteitengroep 2 • 10.345 vragen in prioriteitengroep 3 … De eerstvolgende wachtende in elke prioriteitengroep "
    "had op 31.12.2022 de volgende prioriteringsdatum: • prioriteitengroep 1: 01.10.2022 • prioriteitengroep 2: 01.10.2016 "
    "• prioriteitengroep 3: 16.01.2002",
    GEC, date(2023, 6, 19), D_EB,
)
# 2021: PDF geeft enkel vragen per PG (geen personen/totaal expliciet gelezen) -> aparte rijen
for pg, n in ((1, 328), (2, 5034), (3, 10590)):
    BEVINDINGEN.append(_b(f"wachtenden_vragen_pg{pg}", n, "vragen", date(2021, 12, 31), "vaph-cijfers-2021", U50259, "Het VAPH in cijfers 2021",
                          "sectie prioriteitengroepen", "328 vragen in prioriteitengroep 1, 5034 vragen in prioriteitengroep 2, 10.590 vragen in prioriteitengroep 3",
                          DEF_VRAGEN, GEL, date(2022, 5, 30), "onderzoeksagent (2026-10-01)",
                          "jaarreekstabel jaarverslag 2022 geeft PG3 10.595 (afwijking 5)"))
BEVINDINGEN.append(_b("wachtenden_vragen_totaal", 328 + 5034 + 10590, "vragen", date(2021, 12, 31), "vaph-cijfers-2021", U50259, "Het VAPH in cijfers 2021",
                      "sectie prioriteitengroepen", "(som van de drie prioriteitengroepen)", DEF_VRAGEN, GEL, date(2022, 5, 30), "onderzoeksagent (2026-10-01)", "afgeleid: som PG1-3"))
for pg, d in ((1, date(2021, 1, 1)), (2, date(2016, 10, 1)), (3, date(2002, 1, 16))):
    BEVINDINGEN.append(_b(f"wachttijd_eerstvolgende_pg{pg}_dagen", (date(2021, 12, 31) - d).days, "dagen", date(2021, 12, 31), "vaph-cijfers-2021", U50259,
                          "Het VAPH in cijfers 2021", "sectie prioriteitengroepen", "prioriteringsdatum eerstvolgende wachtende: PG1 1 januari 2021, PG2 1 oktober 2016, PG3 16 januari 2002",
                          DEF_PRIO + f" Prioriteringsdatum: {d.isoformat()}.", GEL, date(2022, 5, 30), "onderzoeksagent (2026-10-01)"))
# 2020: enkel uit jaarreekstabel (extranet 2022) -> betwist/ongecontroleerd
for pg, n in ((1, 1802), (2, 3777), (3, 11044)):
    BEVINDINGEN.append(_b(f"wachtenden_vragen_pg{pg}", n, "vragen", date(2020, 12, 31), "vaph-jaarverslag-2022", U22T, "VAPH jaarverslag 2022 — Evolutie in ondersteuning",
                          "pages/54 (tabel 2018-2022)", "jaarreekstabel prioriteitengroepen 2018-2022", DEF_VRAGEN, ONG, None, "",
                          "eenheid (personen/vragen) niet expliciet in tabel; jaar-PDF 2020 nog op te halen"))
BEVINDINGEN.append(_b("wachtenden_vragen_totaal", 1802 + 3777 + 11044, "vragen", date(2020, 12, 31), "vaph-jaarverslag-2022", U22T, "VAPH jaarverslag 2022 — Evolutie in ondersteuning",
                      "pages/54", "(som)", DEF_VRAGEN, ONG, None, "", "afgeleid: som PG1-3"))
# 2019
for pg, n in ((1, 1837), (2, 2826), (3, 11496)):
    BEVINDINGEN.append(_b(f"wachtenden_vragen_pg{pg}", n, "vragen", date(2019, 12, 31), "vaph-cijfers-2019", U42019, "Het VAPH in cijfers 2019",
                          "sectie prioriteitengroepen", "vragen per prioriteitengroep op 31.12.2019; prioriteringsdata PG1 28.04.2017, PG2 11.07.2016, PG3 09.07.2001",
                          DEF_VRAGEN, BET, date(2020, 6, 4), "onderzoeksagent (2026-10-01)", "jaarreekstabel jaarverslag 2022 geeft PG1 1.829 / PG3 11.487 — verschil niet opgehelderd"))
BEVINDINGEN.append(_b("wachtenden_vragen_totaal", 1837 + 2826 + 11496, "vragen", date(2019, 12, 31), "vaph-cijfers-2019", U42019, "Het VAPH in cijfers 2019",
                      "sectie prioriteitengroepen", "(som)", DEF_VRAGEN, BET, date(2020, 6, 4), "onderzoeksagent (2026-10-01)", "afgeleid: som PG1-3"))
for pg, d in ((1, date(2017, 4, 28)), (2, date(2016, 7, 11)), (3, date(2001, 7, 9))):
    BEVINDINGEN.append(_b(f"wachttijd_eerstvolgende_pg{pg}_dagen", (date(2019, 12, 31) - d).days, "dagen", date(2019, 12, 31), "vaph-cijfers-2019", U42019,
                          "Het VAPH in cijfers 2019", "sectie prioriteitengroepen", "prioriteitengroep 1: 28.04.2017 … 2: 11.07.2016 … 3: 09.07.2001",
                          DEF_PRIO + f" Prioriteringsdatum: {d.isoformat()}.", GEL, date(2020, 6, 4), "onderzoeksagent (2026-10-01)"))
# Halfjaarcijfers via GRIP (secundair)
for pd_, pgs in ((date(2021, 6, 30), (1909, 4424, 10765)), (date(2020, 6, 30), (2014, 3473, 11213)), (date(2019, 6, 30), (1538, 2233, 11812))):
    for pg, n in enumerate(pgs, start=1):
        BEVINDINGEN.append(_b(f"wachtenden_vragen_pg{pg}", n, "vragen", pd_, "grip-wachtlijst-2022",
                              "https://www.gripvzw.be/nl/artikel/549/verbetering-in-wachtlijst-nog-niet-vast-te-stellen", "GRIP — Verbetering in wachtlijst nog niet vast te stellen",
                              "artikeltekst", "halfjaarcijfers VAPH geciteerd door GRIP", DEF_VRAGEN, ONG, date(2022, 5, 6), "", "secundaire bron; te verifiëren in VAPH-halfjaarverslag"))
    BEVINDINGEN.append(_b("wachtenden_vragen_totaal", sum(pgs), "vragen", pd_, "grip-wachtlijst-2022",
                          "https://www.gripvzw.be/nl/artikel/549/verbetering-in-wachtlijst-nog-niet-vast-te-stellen", "GRIP — Verbetering in wachtlijst nog niet vast te stellen",
                          "artikeltekst", "halfjaarcijfers VAPH geciteerd door GRIP", DEF_VRAGEN, ONG, date(2022, 5, 6), "", "secundaire bron"))
# Terbeschikkingstellingen en budgethouders
BEVINDINGEN += [
    _b("terbeschikkingstellingen_budgetten", 5201, "budgetten", date(2025, 12, 31), "vaph-cijfers-2025", U85057, "Het VAPH in cijfers 2025", "p. 37",
       "Tabel: aantal terbeschikkingstellingen in 2025 … Terbeschikkingstelling in prioriteitengroep 1 1.125 21,63% · Terbeschikkingstelling "
       "in prioriteitengroep 2 1.151 22,13% · Totaal aantal terbeschikkingstellingen 5.201 100,00% · Totaal unieke personen** 4.551",
       DEF_TBS, GEC, date(2026, 6, 1), D_EB,
       "automatische toekenningsgroepen 2.925 = afgeleid (som van de zes overige tabelrijen 832+792+669+121+329+182), niet als totaal in de bron"),
    _b("terbeschikkingstellingen_personen", 4551, "personen", date(2025, 12, 31), "vaph-cijfers-2025", U85057, "Het VAPH in cijfers 2025", "p. 37",
       "Totaal aantal terbeschikkingstellingen 5.201 100,00% · Totaal unieke personen** 4.551", DEF_TBS, GEC, date(2026, 6, 1), D_EB),
    _b("terbeschikkingstellingen_budgetten", 3692, "budgetten", date(2024, 12, 31), "vaph-jaarverslag-2024", "https://extranet.vaph.be/jaarverslag/2024/pages/26",
       "VAPH jaarverslag 2024 — Terbeschikkingstellingen", "pages/26", "In 2024 werden 3692 persoonsvolgende budgetten ter beschikking gesteld aan 3056 personen.", DEF_TBS, GEL, None, "onderzoeksagent (2026-10-01)"),
    _b("terbeschikkingstellingen_personen", 3056, "personen", date(2024, 12, 31), "vaph-jaarverslag-2024", "https://extranet.vaph.be/jaarverslag/2024/pages/26",
       "VAPH jaarverslag 2024 — Terbeschikkingstellingen", "pages/26", "… ter beschikking gesteld aan 3056 personen.", DEF_TBS, GEL, None, "onderzoeksagent (2026-10-01)"),
    _b("terbeschikkingstellingen_budgetten", 3412, "budgetten", date(2022, 12, 31), "vaph-cijfers-2022", U57023, "Het VAPH in cijfers 2022", "tabel 'aantal terbeschikkingstellingen in 2022'",
       "3.412 terbeschikkingstellingen; PG1 867; PG2 972 (deelbudgetten)", DEF_TBS, GEL, date(2023, 6, 19), "onderzoeksagent (2026-10-01)"),
    _b("budgethouders_pvb", 31312, "personen", date(2025, 12, 31), "vrt-2026-05-25", "https://www.vrt.be/vrtnws/nl/2026/05/25/18-000-mensen-met-een-handicap-wachten-op-persoonlijk-budget/",
       "VRT NWS — Recordaantal mensen met handicap krijgt ondersteuning", "artikeltekst", "31.312 budgethouders PVB eind 2025 (VRT, op basis van VAPH-cijfers)",
       "Aantal personen met een lopend persoonsvolgend budget.", ONG, date(2026, 5, 25), "", "secundaire bron; te verifiëren in VAPH in cijfers 2025"),
]

# -------------------------------------------------------------------------------------------- budgetten
def _bu(jaar, fase, niveau, bedrag, bron_id, url, titel, pagina, passage, status, door="", krediet=Kredietsoort.NVT, artikel="", programma="", ise="", label="", opm=""):
    key = artikel or label.replace(" ", "_")[:40]
    return Budget(budget_id=f"vaph-pvb:{jaar}:{fase.value}:{niveau}:{krediet.value}:{key}", voorziening_id="vaph-pvb", begrotingsjaar=jaar, fase=fase, niveau=niveau,
                  bedrag_eur=bedrag, kredietsoort=krediet, artikel_code=artikel, programma=programma, ise=ise, label=label, bron_id=bron_id, bron_url=url,
                  documenttitel=titel, pagina=pagina, passage=passage, controlestatus=status, gecontroleerd_door=door, gecontroleerd_op=VANDAAG if door else None, opmerking=opm)


B, A = Budgetfase, "onderzoeksagent (2026-10-01)"
U23M = "https://extranet.vaph.be/jaarverslag/2023/pages/42"
U24M = "https://extranet.vaph.be/jaarverslag/2024/pages/78"
BUDGETTEN = [
    _bu(2019, B.BELEID, "uitbreidingsbeleid", 92_500_000, "vaph-cijfers-2019", U42019, "Het VAPH in cijfers 2019", "sectie uitbreidingsbeleid",
        "92,5 mln euro (trap 1: 35,49 mln; trap 2: 57,01 mln)", GEL, A, label="uitbreidingsbeleid VAPH-breed"),
    _bu(2020, B.BELEID, "uitbreidingsbeleid", 40_000_000, "vaph-jaarverslag-2023", U23M, "VAPH jaarverslag 2023 — Inzet middelen", "pages/42", "2020: 40,0 mln euro", GEL, A, label="uitbreidingsbeleid VAPH-breed"),
    _bu(2021, B.BELEID, "uitbreidingsbeleid", 45_000_000, "vaph-jaarverslag-2023", U23M, "VAPH jaarverslag 2023 — Inzet middelen", "pages/42", "2021: 45,0 mln euro jaarlijkse aangroei", GEL, A, label="uitbreidingsbeleid VAPH-breed",
        opm="VAPH in cijfers 2021: 230 mln euro extra vanaf 2021 (15 % minderjarigen / 85 % meerderjarigen)"),
    _bu(2022, B.BELEID, "uitbreidingsbeleid", 120_800_000, "vaph-jaarverslag-2023", U23M, "VAPH jaarverslag 2023 — Inzet middelen", "pages/42", "2022: 120,8 mln euro (60 mln aangroei + zorginvesteringsplan)", GEL, A, label="uitbreidingsbeleid VAPH-breed",
        opm="waarvan PG1 42,0 mln; PG2 deelbudgetten 20 mln"),
    _bu(2023, B.BELEID, "uitbreidingsbeleid", 98_100_000, "vaph-jaarverslag-2023", U23M, "VAPH jaarverslag 2023 — Inzet middelen", "pages/42", "2023: 98,1 mln euro (86,2 + 11,9 compensatie)", GEL, A, label="uitbreidingsbeleid VAPH-breed",
        opm="automatische toekenningsgroepen 68 mln; PG1 43 mln"),
    _bu(2023, B.AGENTSCHAP, "realisatie", 2_379_000_000, "vaph-financieel-2023", "https://extranet.vaph.be/jaarverslag/2023/media/files/financieel-verslag-2023-in-lay-out-definitief.pdf",
        "VAPH financieel verslag 2023", "p. 2-4", "totale uitgaven 2023: 2,379 mld euro", GEL, A, label="totale uitgaven VAPH"),
    _bu(2023, B.AGENTSCHAP, "realisatie", 1_346_041_672, "vaph-financieel-2023", "https://extranet.vaph.be/jaarverslag/2023/media/files/financieel-verslag-2023-in-lay-out-definitief.pdf",
        "VAPH financieel verslag 2023", "p. 2-4", "PVB 1.346.041.672 euro", GEL, A, label="uitgaven persoonsvolgende budgetten"),
    _bu(2023, B.AGENTSCHAP, "realisatie", 2_008_519_000, "vaph-financieel-2023", "https://extranet.vaph.be/jaarverslag/2023/media/files/financieel-verslag-2023-in-lay-out-definitief.pdf",
        "VAPH financieel verslag 2023", "p. 2-4", "basisdotatie 2.008.519.000 euro", GEL, A, label="basisdotatie Vlaamse Gemeenschap"),
    _bu(2024, B.BELEID, "uitbreidingsbeleid", 38_800_000, "vaph-jaarverslag-2024", U24M, "VAPH jaarverslag 2024 — Inzet middelen", "pages/78", "2024: 38,8 mln euro (PAB 10,5; MFC 24,4; PVB 3,6; andere 0,3)", GEL, A, label="uitbreidingsbeleid VAPH-breed",
        opm="2020-2024 totaal 342,7 mln (270 regulier + 72,7 zorginvesteringsplan)"),
    _bu(2024, B.AGENTSCHAP, "realisatie", 2_581_868_570, "vaph-financieel-2024", "https://extranet.vaph.be/jaarverslag/2024/media/files/financieel-verslag-2024-in-lay-out.pdf",
        "VAPH financieel verslag 2024", "p. 2-3", "uitgaven 2.581.868.570 euro", GEL, A, label="totale uitgaven VAPH"),
    _bu(2024, B.AGENTSCHAP, "realisatie", 1_404_861_255, "vaph-financieel-2024", "https://extranet.vaph.be/jaarverslag/2024/media/files/financieel-verslag-2024-in-lay-out.pdf",
        "VAPH financieel verslag 2024", "p. 2-3", "PVB 1.404.861.255 euro", GEL, A, label="uitgaven persoonsvolgende budgetten"),
    _bu(2024, B.AGENTSCHAP, "realisatie", 2_117_665_000, "vaph-financieel-2024", "https://extranet.vaph.be/jaarverslag/2024/media/files/financieel-verslag-2024-in-lay-out.pdf",
        "VAPH financieel verslag 2024", "p. 2-3", "werkingstoelagen 2.117.665.000 euro", GEL, A, label="werkingstoelagen Vlaamse Gemeenschap"),
    _bu(2025, B.BELEID, "uitbreidingsbeleid", 102_400_000, "vaph-cijfers-2025", U85057, "Het VAPH in cijfers 2025", "p. 70-71", "In 2025 werd 102,4 miljoen euro geïnvesteerd",
        GEC, "onderzoeksagent + 2e lezing Claude (2026-10-01)", label="uitbreidingsbeleid VAPH-breed", opm="PVB PG1+autom. 52,4; PG2 deelbudgetten 24,1; PAB 13; MFC 8,5; RTH 4,4"),
    _bu(2025, B.BELEID, "meerjarenplan", 478_000_000, "vaph-cijfers-2025", U85057, "Het VAPH in cijfers 2025", "p. 71",
        "werd een extra budget van 478 miljoen euro voorzien voor de sector handicap voor de periode 2025-2029", GEC, "onderzoeksagent + 2e lezing Claude (2026-10-01)",
        label="uitbreidingsbeleid 2025-2029 (totaal periode)", opm="278 PVB PG1+autom.; 200 hervormingen. Periode-bedrag, niet jaarbedrag."),
    _bu(2025, B.BO, "dept_artikel", 2_991_680_000, "vlpar-uitgavenbegroting-2025", "https://docs.vlaamsparlement.be/files/pfile?id=2078969",
        "Ontwerp van decreet uitgavenbegroting 2025 — stuk 15 (2024-2025) nr. 1", "p. 4", "GB0-1GGF2RX-IS VAK 2.991.680 k€ / VEK 2.726.246 k€", GEL, A,
        krediet=Kredietsoort.VAK, artikel="GB0-1GGF2RX-IS", programma="GG Personen met een beperking", ise="Personen met een handicap", label="dotatie aan het VAPH (interne stroom)"),
    _bu(2025, B.BO, "dept_artikel", 2_726_246_000, "vlpar-uitgavenbegroting-2025", "https://docs.vlaamsparlement.be/files/pfile?id=2078969",
        "Ontwerp van decreet uitgavenbegroting 2025 — stuk 15 (2024-2025) nr. 1", "p. 4", "GB0-1GGF2RX-IS VAK 2.991.680 k€ / VEK 2.726.246 k€", GEL, A,
        krediet=Kredietsoort.VEK, artikel="GB0-1GGF2RX-IS", programma="GG Personen met een beperking", ise="Personen met een handicap", label="dotatie aan het VAPH (interne stroom)"),
    _bu(2025, B.BO, "entiteit_begroting", 3_018_897_000, "vlpar-uitgavenbegroting-2025", "https://docs.vlaamsparlement.be/files/pfile?id=2078969",
        "Decreet uitgavenbegroting 2025, art. 36 (begroting IVA VAPH)", "art. 36", "uitgaven 3.018.897.000 euro VAK / 2.754.411.000 euro VEK; ontvangsten 2.754.411.000", GEL, A,
        krediet=Kredietsoort.VAK, label="begroting VAPH (uitgaven)"),
    _bu(2025, B.BO, "entiteit_begroting", 2_754_411_000, "vlpar-uitgavenbegroting-2025", "https://docs.vlaamsparlement.be/files/pfile?id=2078969",
        "Decreet uitgavenbegroting 2025, art. 36 (begroting IVA VAPH)", "art. 36", "uitgaven 3.018.897.000 euro VAK / 2.754.411.000 euro VEK", GEL, A,
        krediet=Kredietsoort.VEK, label="begroting VAPH (uitgaven)"),
    _bu(2026, B.BELEID, "uitbreidingsbeleid", 46_500_000, "vlpar-plenaire-2026-04-01", "https://www.vlaamsparlement.be/nl/parlementair-werk/plenaire-vergaderingen/2010388/verslag/2019101",
        "Plenaire vergadering 1 april 2026 — verslag", "tussenkomst minister Gennez", "In 2026 komt daar nog eens 46,5 miljoen euro bij", ONG, label="uitbreidingsbeleid (uitspraak minister)",
        opm="te verifiëren in uitgavenbegroting 2026 (stuk 15 (2025-2026)) en BBT WVG"),
]


# ==================================================================================== proef 2: sociale huur
# Tweede proefvoorziening (bevestigd door het team op 2026-10-01). Peildata eind 2018–2025; 2023 ontbreekt (overgang CIR).
BRONNEN += [
    Bron(bron_id="wiv-jaarverslag-2025-toegang", naam="Wonen in Vlaanderen — Jaarverslag 2025, Gelijke toegang tot wonen", organisatie="Agentschap Wonen in Vlaanderen",
         url="https://www.vlaanderen.be/wonen-in-vlaanderen/onderzoek-en-cijfers-wonen/jaarverslag-2025/gelijke-toegang-tot-wonen", bron_type=BronType.HTML,
         frequentie="jaarlijks", machinaal="HTML scrapebaar; PDF-steekkaarten op assets.vlaanderen.be"),
    Bron(bron_id="wiv-jaarverslag-2025-aanbod", naam="Wonen in Vlaanderen — Jaarverslag 2025, Woonaanbod afgestemd op de vraag", organisatie="Agentschap Wonen in Vlaanderen",
         url="https://www.vlaanderen.be/wonen-in-vlaanderen/onderzoek-en-cijfers-wonen/jaarverslag-2025/woonaanbod-afgestemd-op-de-vraag", bron_type=BronType.HTML, frequentie="jaarlijks"),
    Bron(bron_id="wiv-jaarverslag-2025-betaalbaar", naam="Wonen in Vlaanderen — Jaarverslag 2025, Betaalbaar wonen", organisatie="Agentschap Wonen in Vlaanderen",
         url="https://www.vlaanderen.be/wonen-in-vlaanderen/onderzoek-en-cijfers-wonen/jaarverslag-2025/betaalbaar-wonen", bron_type=BronType.HTML, frequentie="jaarlijks"),
    Bron(bron_id="wiv-jaarverslag-2024-toegang", naam="Wonen in Vlaanderen — Jaarverslag 2024, Gelijke toegang tot wonen", organisatie="Agentschap Wonen in Vlaanderen",
         url="https://www.vlaanderen.be/wonen-in-vlaanderen/onderzoek-en-cijfers-wonen/jaarverslag-2024/gelijke-toegang-tot-wonen", bron_type=BronType.HTML, frequentie="jaarlijks"),
    Bron(bron_id="wiv-jaarverslag-2024-aanbod", naam="Wonen in Vlaanderen — Jaarverslag 2024, Woonaanbod afgestemd op de vraag", organisatie="Agentschap Wonen in Vlaanderen",
         url="https://www.vlaanderen.be/wonen-in-vlaanderen/onderzoek-en-cijfers-wonen/jaarverslag-2024/woonaanbod-afgestemd-op-de-vraag", bron_type=BronType.HTML, frequentie="jaarlijks"),
    Bron(bron_id="wiv-cijfers-tot-2023", naam="Wonen in Vlaanderen — kandidaat-huurders, cijfers tot 2023 (Excel-tabellen 2022)", organisatie="Agentschap Wonen in Vlaanderen",
         url="https://www.vlaanderen.be/sociaal-woonbeleid/cijfers/oudere-cijfers-over-sociaal-wonen/kandidaat-huurders-cijfers-tot-2023", bron_type=BronType.DOWNLOAD, frequentie="jaarlijks (gestopt 2022)",
         machinaal="18 Excel-tabellen op assets.vlaanderen.be (Tabel 1 totaal per jaar, 11 toewijzingen, 12 wachttijden, 18 schrappingen); URL bevat versie-hash",
         opmerking="Reeks 2018-2022 gelezen uit Tabel 1 op 2026-10-01 (lokale kopie in data/raw/wonen/)."),
    Bron(bron_id="wiv-powerbi-kandidaat-huurders", naam="Wonen in Vlaanderen — Power BI kandidaat-huurders (CIR)", organisatie="Agentschap Wonen in Vlaanderen",
         url="https://app.powerbi.com/view?r=eyJrIjoiNDE0MDEwYTItMjkyYy00NTExLTkwYTYtZGFjZjVkNDEyNWI0IiwidCI6IjBjMDMzOGE2LTk1NjEtNGVlOC1iOGQ2LTRlODljYmQ1MjBhMCIsImMiOjh9",
         bron_type=BronType.DASHBOARD, frequentie="doorlopend", machinaal="geen API; UI-export"),
    Bron(bron_id="vlpar-bbt-wonen-2026", naam="BBT Wonen begroting 2026 — stuk 13-G (2025-2026) nr. 1", organisatie="Vlaams Parlement",
         url="https://docs.vlaamsparlement.be/files/pfile?id=2226288", bron_type=BronType.PDF, frequentie="jaarlijks", opmerking="Ingediend 24-10-2025 (min. Depraetere). ISE Vraagzijde/Aanbodzijde woningmarkt."),
    Bron(bron_id="themis-bbt-wonen-2026", naam="BBT Wonen begroting 2026 (Themis, VR 2025 2410 MED.0424/1)", organisatie="Vlaamse Regering / Themis",
         url="https://themis.vlaanderen.be/files/128397c0-b033-11f0-9b44-3797f8128cc9/download", bron_type=BronType.PDF, frequentie="jaarlijks"),
    Bron(bron_id="codex-kaderbesluit-sociale-huur", naam="Kaderbesluit Sociale Huur (BVR 12-10-2007), geconsolideerd 1-1-2020", organisatie="Vlaamse Codex",
         url="https://codex.vlaanderen.be/PrintDocument.ashx?id=1016403&datum=2020-01-01&geannoteerd=false&print=false", bron_type=BronType.HTML, frequentie="eenmalig",
         opmerking="art. 8 actualisatie oneven jaren; art. 12 §1 7° schrapping bij niet-reageren."),
    Bron(bron_id="vrt-2019-08-19", naam="VRT NWS 20-8-2019 — wachtlijsten sociale woning nemen fors toe", organisatie="VRT (secundair)",
         url="https://www.vrt.be/vrtnws/nl/2019/08/19/sociale-woningen/", bron_type=BronType.HTML, frequentie="eenmalig"),
    Bron(bron_id="vrt-2021-06-30", naam="VRT NWS 30-6-2021 — 169.096 mensen wachtten vorig jaar op een sociale woning", organisatie="VRT (secundair)",
         url="https://www.vrt.be/vrtnws/nl/2021/06/30/169-096-mensen-wachtten-vorig-jaar-op-een-sociale-woning/", bron_type=BronType.HTML, frequentie="eenmalig"),
    Bron(bron_id="vrt-2023-04-05", naam="VRT NWS 15-4-2023 — sociale woningen in Vlaanderen, welke gemeenten zijn goede leerlingen", organisatie="VRT (secundair)",
         url="https://www.vrt.be/vrtnws/nl/2023/04/05/sociale-woningen-in-vlaanderen-welke-gemeenten-zijn-goede-leerl/", bron_type=BronType.HTML, frequentie="eenmalig"),
    Bron(bron_id="huurdersplatform-2025-04", naam="Vlaams Huurdersplatform 24-4-2025 — bijna 200.000 huishoudens wachten op een sociale woning", organisatie="Huurdersplatform (secundair)",
         url="https://huurdersplatform.be/actualiteit-hb/bijna-200-000-huishoudens-wachten-op-een-sociale-woning/", bron_type=BronType.HTML, frequentie="eenmalig"),
    Bron(bron_id="vrt-2025-04-09", naam="VRT NWS 10-4-2025 — nooit eerder zoveel mensen op wachtlijst voor sociale woning", organisatie="VRT (secundair)",
         url="https://www.vrt.be/vrtnws/nl/2025/04/09/nooit-eerder-zoveel-mensen-op-wachtlijst-voor-sociale-woning/", bron_type=BronType.HTML, frequentie="eenmalig"),
]

# ISE-koppeling (BBT) en status van de tweede proef op bestaande voorzieningen zetten
_ISE = {
    "vaph-pvb": "PERSONEN MET EEN BEPERKING", "opgroeien-nrtj": "JEUGDHULP", "opgroeien-kinderopvang": "GEINTEGREERD GEZINSBELEID",
    "zorg-woonzorgcentra": "WOONZORG", "vsb-zorgbudget": "SOCIALE BESCHERMING", "zorg-cgg": "GESPECIALISEERDE ZORG",
    "wonen-sociale-huur": "AANBODZIJDE WONINGMARKT", "wonen-huurpremie": "VRAAGZIJDE WONINGMARKT", "opgroeien-pleegzorg": "JEUGDHULP",
}
for _v in VOORZIENINGEN:
    _v.ise_koppeling = _ISE.get(_v.voorziening_id, "")
    if _v.voorziening_id == "wonen-sociale-huur":
        _v.scan_status = "proef_uitgewerkt"
        _v.laatste_peildatum = date(2025, 12, 31)
        _v.publicatie_bron_id = "wiv-jaarverslag-2025-toegang"
        _v.frequentie = "jaarlijks (jaarverslag WiV, ± juni); Power BI doorlopend"
        _v.opmerking = ("Reeks breekt in 2023 (overgang naar CIR, geen cijfers) en wisselt van definitie: unieke kandidaat-huurders (VMSW, t/m 2022) "
                        "-> kandidaten CIR (2024) -> actieve inschrijvingen incl. 15 % zittende sociale huurders (2025). Wachttijd enkel bij toewijzing gemeten.")


def _bv(vid, metriek, waarde, eenheid, peildatum, bron_id, url, titel, pagina, passage, definitie, status, pub=None, door="", opm=""):
    return Bevinding(
        bevinding_id=f"{vid}:{metriek}:{peildatum.isoformat()}", voorziening_id=vid, metriek=metriek, waarde=waarde, eenheid=eenheid,
        peildatum=peildatum, bron_id=bron_id, bron_url=url, documenttitel=titel, pagina=pagina, passage=passage, definitie=definitie,
        publicatiedatum=pub, controlestatus=status, gecontroleerd_door=door, gecontroleerd_op=VANDAAG if door else None, opmerking=opm,
    )


SH = "wonen-sociale-huur"
DEF_KH_VMSW = "Unieke kandidaat-huurders (huishoudens) ingeschreven bij één of meer sociale huisvestingsmaatschappijen, ontdubbeld door de VMSW; peildatum 31/12. Actualisatie in oneven jaren drukt het cijfer."
DEF_KH_CIR = "Kandidaten ingeschreven in het Centraal Inschrijvingsregister (CIR) op 31/12; één inschrijving per huishouden."
DEF_KH_ACTIEF = "Actieve inschrijvingen in het CIR op 31/12, inclusief zittende sociale huurders met een mutatievraag (15 % in 2025)."
DEF_TOEW = "Aantal kandidaat-huurders geschrapt uit het register omdat hun een sociale huurwoning werd toegewezen (kalenderjaar)."
DEF_WT = "Gemiddelde tijd tussen inschrijving en toewijzing voor wie in het jaar een woning kreeg; wachttijd wordt enkel bij toewijzing bepaald."
U25T = "https://www.vlaanderen.be/wonen-in-vlaanderen/onderzoek-en-cijfers-wonen/jaarverslag-2025/gelijke-toegang-tot-wonen"
U24T = "https://www.vlaanderen.be/wonen-in-vlaanderen/onderzoek-en-cijfers-wonen/jaarverslag-2024/gelijke-toegang-tot-wonen"
U25A = "https://www.vlaanderen.be/wonen-in-vlaanderen/onderzoek-en-cijfers-wonen/jaarverslag-2025/woonaanbod-afgestemd-op-de-vraag"
USV213 = "https://docs.vlaamsparlement.be/files/pfile?id=2291613"
D2 = "onderzoeksagent + 2e lezing Claude (2026-10-01)"

BEVINDINGEN += [
    # --- eind 2025 (jaarverslag 2025)
    _bv(SH, "wachtenden_actieve_inschrijvingen", 215337, "inschrijvingen", date(2025, 12, 31), "wiv-jaarverslag-2025-toegang", U25T, "Jaarverslag 2025 Wonen in Vlaanderen — Gelijke toegang tot wonen",
        "hoofdstuk 3", "Eind 2025 waren er in totaal 215.337 actieve inschrijvingen op de wachtlijst voor een sociale huurwoning. Van deze actieve inschrijvingen is 15% momenteel al huurder van een sociale woning.",
        DEF_KH_ACTIEF, GEC, date(2026, 6, 30), D2, "andere definitie dan 2024 (kandidaten) en t/m 2022 (unieke kandidaat-huurders)"),
    _bv(SH, "nieuwe_inschrijvingen", 44521, "inschrijvingen", date(2025, 12, 31), "wiv-jaarverslag-2025-toegang", U25T, "Jaarverslag 2025 WiV — Gelijke toegang tot wonen", "hoofdstuk 3",
        "Er kwamen in 2025 44.521 nieuwe inschrijvingen bij", "Nieuwe inschrijvingen in het CIR in het kalenderjaar.", GEC, date(2026, 6, 30), D2),
    _bv(SH, "schrappingen", 34149, "dossiers", date(2025, 12, 31), "wiv-jaarverslag-2025-toegang", U25T, "Jaarverslag 2025 WiV — Gelijke toegang tot wonen", "hoofdstuk 3",
        "34.149 kandidatendossiers werden geschrapt. Belangrijkste reden van schrapping was het aanvaarden van een aanbod voor een sociale woning.", "Schrappingen uit het CIR (alle redenen) in het kalenderjaar.", GEC, date(2026, 6, 30), D2),
    _bv(SH, "wachttijd_bij_toewijzing_jaren", 5.0, "jaar", date(2025, 12, 31), "wiv-jaarverslag-2025-toegang", U25T, "Jaarverslag 2025 WiV — Gelijke toegang tot wonen", "hoofdstuk 3",
        "Een kandidaat-huurder die in 2025 een sociale huurwoning kreeg toegewezen stond gemiddeld 5 jaren op de wachtlijst.", DEF_WT, GEC, date(2026, 6, 30), D2),
    _bv(SH, "sociale_huurwoningen", 178743, "woningen", date(2025, 12, 31), "wiv-jaarverslag-2025-aanbod", U25A, "Jaarverslag 2025 WiV — Woonaanbod afgestemd op de vraag", "hoofdstuk 2",
        "Op 31 december 2025 waren er in het Vlaamse Gewest in totaal 178.743 sociale huurwoningen: 166.077 woningen in eigendom van de woonmaatschappij en 12.666 ingehuurde woningen",
        "Sociale huurwoningen (eigendom + ingehuurd) van woonmaatschappijen op 31/12.", GEC, date(2026, 6, 30), D_EB),
    _bv(SH, "huurpremie_gerechtigden", 23353, "huishoudens", date(2025, 12, 31), "wiv-jaarverslag-2025-betaalbaar",
        "https://www.vlaanderen.be/wonen-in-vlaanderen/onderzoek-en-cijfers-wonen/jaarverslag-2025/betaalbaar-wonen", "Jaarverslag 2025 WiV — Betaalbaar wonen", "hoofdstuk 1",
        "23.353 private huurders die minstens vier jaar wachten op een sociale huurwoning kregen eind 2025 een Vlaamse huurpremie", "Private huurders met ≥ 4 jaar ononderbroken inschrijving die de huurpremie ontvangen (wachtlijst-afgeleid recht).",
        GEC, date(2026, 6, 30), D_EB),
    # --- eind 2024 (jaarverslag 2024 + SV 213)
    _bv(SH, "wachtenden_kandidaten", 187874, "kandidaten", date(2024, 12, 31), "wiv-jaarverslag-2024-toegang", U24T, "Jaarverslag 2024 Wonen in Vlaanderen — Gelijke toegang tot wonen", "hoofdstuk 3",
        "Eind 2024 stonden er 187.874 kandidaten op de wachtlijst voor een sociale woning. Eén op drie kandidaten woont in provincie Antwerpen.", DEF_KH_CIR, GEC, date(2025, 7, 1), D2),
    _bv(SH, "toewijzingen", 8864, "toewijzingen", date(2024, 12, 31), "vlpar-sv-213-2026", USV213, "Schriftelijke vraag nr. 213 (Naji, 30-01-2026) — antwoord min. Bonte", "antwoord",
        "Samen met het aantal toewijzingen – 8.864 in 2024 – gaat het in totaal om 66.033 schrappingen.", DEF_TOEW, GEC, date(2026, 3, 1), D2, "ook jaarverslag 2024: 'schrapten in 2024 8.864 kandidaat-huurders … omdat hen een sociale huurwoning werd toegewezen'"),
    _bv(SH, "schrappingen_andere_reden", 57169, "schrappingen", date(2024, 12, 31), "vlpar-sv-213-2026", USV213, "SV nr. 213 (Naji, 30-01-2026)", "antwoord",
        "57.169 schrappingen om een andere reden dan de toewijzing van een sociale huurwoning", "Schrappingen uit het CIR om een andere reden dan toewijzing (kalenderjaar).", GEC, date(2026, 3, 1), D2),
    _bv(SH, "wachttijd_bij_toewijzing_jaren", 4.8, "jaar", date(2024, 12, 31), "vlpar-sv-213-2026", USV213, "SV nr. 213 (Naji, 30-01-2026)", "antwoord, tabel verdeling",
        "De verdeling van de gemiddelde wachttijd van 4,8 jaar voor deze toewijzingen is als volgt … minder dan 1 jaar 1.927 (21,74 %) … 15 jaar of meer 353 (3,98 %); totaal 8.864. Er wordt alleen een wachttijd bepaald bij de toewijzing van een sociale huurwoning.",
        DEF_WT, GEC, date(2026, 3, 1), D2),
    _bv(SH, "sociale_huurwoningen", 177461, "woningen", date(2024, 12, 31), "themis-bbt-wonen-2026", "https://themis.vlaanderen.be/files/128397c0-b033-11f0-9b44-3797f8128cc9/download",
        "BBT Wonen begroting 2026 (VR 2025 2410 MED.0424/1)", "p. 38-39", "177.461, waarvan 13.321 ingehuurde woningen en 164.140 woningen in eigendom.", "Sociale huurwoningen (eigendom + ingehuurd) op 31/12; prestatie-indicator.",
        GEL, date(2025, 10, 24), "onderzoeksagent (2026-10-01)"),
    # --- april 2025 (herbevestigingsronde CIR; cijfer minister via pers)
    _bv(SH, "wachtenden_kandidaten", 199085, "huishoudens", date(2025, 4, 9), "vrt-2025-04-09", "https://www.vrt.be/vrtnws/nl/2025/04/09/nooit-eerder-zoveel-mensen-op-wachtlijst-voor-sociale-woning/",
        "VRT NWS 10-4-2025", "artikeltekst", "199.085 mensen wachten op een goedkope woning … 52.322 nieuwe kandidaten hebben zich aangemeld", DEF_KH_CIR + " Stand na de herbevestigingsronde (38.801 geschrapt, 52.322 nieuw).",
        ONG, date(2025, 4, 10), "", "secundaire bron (cijfer minister Depraetere); Huurdersplatform 24-4-2025 bevestigt 199.085"),
    # --- 2023: geen cijfer. SV 213: "Voor 2023 zijn er geen relevante cijfers beschikbaar over kandidaat-huurders. Door de uitrol van het
    #     centraal inschrijvingsregister (CIR) ... zijn er geen complete gegevens beschikbaar op de referentiedatum van 31 december 2023."
    #     (gecontroleerd; bewust geen rij — breuk in de reeks staat in voorzieningen.opmerking en docs/03-inventaris.md)
]
# --- t/m 2022 (VMSW-reeks): Excel Tabel 1 van WiV, gelezen 2026-10-01 (stap A5); secundaire bronnen gaven dezelfde cijfers
UT1 = "https://assets.vlaanderen.be/raw/upload/v1688034006/Wonen_-_2022_Tabel_1_Totaal_kandidaat-huurders_per_jaar_wgapbw.xlsx"
P_T1 = "Aantal kandidaat-huurders | 2022 2021 2020 2019 2018 | 176026 182436 169096 153510 153910"
for jaar, n, extra, secundair in (
    (2022, 176026, "", "Huurdersplatform 24-4-2025 (176.026 gezinnen)"),
    (2021, 182436, " 2021 = actualisatiejaar.", "VRT NWS 15-4-2023"),
    (2020, 169096, "", "VRT NWS 30-6-2021"),
    (2019, 153510, " 2019 = actualisatiejaar.", "VRT NWS 30-6-2021"),
    (2018, 153910, "", "VRT NWS 20-8-2019"),
):
    BEVINDINGEN.append(_bv(SH, "wachtenden_kandidaten", n, "kandidaat-huurders", date(jaar, 12, 31), "wiv-cijfers-tot-2023", UT1,
                           "Wonen in Vlaanderen — Tabel 1 Totaal kandidaat-huurders per jaar (2022)", "werkblad 'Aantal'", P_T1,
                           DEF_KH_VMSW + extra, GEC, date(2023, 6, 29), "Claude + 2e lezing EB (2026-10-01)", f"zelfde cijfer in secundaire bron: {secundair}"))


def _bus(vid, jaar, fase, niveau, bedrag, bron_id, url, titel, pagina, passage, status, door="", krediet=Kredietsoort.NVT, artikel="", programma="", ise="", label="", opm=""):
    key = artikel or label.replace(" ", "_")[:40]
    return Budget(budget_id=f"{vid}:{jaar}:{fase.value}:{niveau}:{krediet.value}:{key}", voorziening_id=vid, begrotingsjaar=jaar, fase=fase, niveau=niveau,
                  bedrag_eur=bedrag, kredietsoort=krediet, artikel_code=artikel, programma=programma, ise=ise, label=label, bron_id=bron_id, bron_url=url,
                  documenttitel=titel, pagina=pagina, passage=passage, controlestatus=status, gecontroleerd_door=door, gecontroleerd_op=VANDAAG if door else None, opmerking=opm)


UBBTW = "https://docs.vlaamsparlement.be/files/pfile?id=2226288"
UREK = "https://docs.vlaamsparlement.be/files/pfile?id=2235038"
BUDGETTEN += [
    _bus(SH, 2024, B.AGENTSCHAP, "realisatie", 997_000_000, "wiv-jaarverslag-2024-aanbod", "https://www.vlaanderen.be/wonen-in-vlaanderen/onderzoek-en-cijfers-wonen/jaarverslag-2024/woonaanbod-afgestemd-op-de-vraag",
         "Jaarverslag 2024 WiV — Woonaanbod afgestemd op de vraag", "hoofdstuk 2", "In 2024 kon Wonen in Vlaanderen 997 miljoen euro aan gesubsidieerde financiering toekennen aan woonmaatschappijen (dat is de zogenoemde FS3-financiering).",
         GEL, A, label="FS3-financiering toegekend aan woonmaatschappijen", opm="63 % renovatie, 37 % nieuwbouw"),
    _bus(SH, 2025, B.AGENTSCHAP, "realisatie", 742_180_000, "wiv-jaarverslag-2025-aanbod", U25A, "Jaarverslag 2025 WiV — Woonaanbod afgestemd op de vraag", "hoofdstuk 2",
         "In 2025 kon Wonen in Vlaanderen 742,18 miljoen euro aan gesubsidieerde financiering toewijzen aan woonmaatschappijen", GEL, A, label="FS3-financiering toegekend aan woonmaatschappijen", opm="45 % nieuwbouw, 52 % renovatie; + 19,52 mln renteloos; + 59,36 mln SSI-subsidies"),
    _bus(SH, 2025, B.AGENTSCHAP, "realisatie", 63_500_000, "wiv-jaarverslag-2025-betaalbaar", "https://www.vlaanderen.be/wonen-in-vlaanderen/onderzoek-en-cijfers-wonen/jaarverslag-2025/betaalbaar-wonen",
         "Jaarverslag 2025 WiV — Betaalbaar wonen", "hoofdstuk 1", "betaalde voor 63,5 miljoen euro huurpremies uit", GEL, A, label="Vlaamse huurpremie uitbetaald (wachtlijst-afgeleid)"),
    _bus(SH, 2025, B.BA, "dept_artikel", 140_839_000, "vlpar-bbt-wonen-2026", UBBTW, "BBT Wonen 2026 — stuk 13-G (2025-2026) nr. 1", "p. 21-22",
         "QF0-1QDB2PA-WT — Een betaalbare woningmarkt met woonzekerheid: BA 2025 140.839 / BO 2026 152.085 (k€). De belangrijkste uitgavenposten zijn de huursubsidie en -premie.",
         GEL, A, krediet=Kredietsoort.VAK, artikel="QF0-1QDB2PA-WT", programma="QD", ise="VRAAGZIJDE WONINGMARKT", label="Een betaalbare woningmarkt met woonzekerheid (huursubsidie/-premie)", opm="VAK = VEK"),
    _bus(SH, 2026, B.BO, "dept_artikel", 152_085_000, "vlpar-bbt-wonen-2026", UBBTW, "BBT Wonen 2026 — stuk 13-G (2025-2026) nr. 1", "p. 21-22",
         "QF0-1QDB2PA-WT: BO 2026 152.085 k€", GEL, A, krediet=Kredietsoort.VAK, artikel="QF0-1QDB2PA-WT", programma="QD", ise="VRAAGZIJDE WONINGMARKT", label="Een betaalbare woningmarkt met woonzekerheid (huursubsidie/-premie)", opm="VAK = VEK"),
    _bus(SH, 2026, B.BO, "dept_artikel", 1_720_000_000, "vlpar-bbt-wonen-2026", UBBTW, "BBT Wonen 2026 — stuk 13-G (2025-2026) nr. 1", "p. 25",
         "QF0-1QDB5PJ-IS — machtiging die het Vlaams Woningfonds krijgt om bijzondere sociale leningen en huurwaarborgleningen te verstrekken: 1.720.000 k€ (VEK 0)", GEL, A,
         krediet=Kredietsoort.VAK, artikel="QF0-1QDB5PJ-IS", programma="QD", ise="VRAAGZIJDE WONINGMARKT", label="Machtiging VWF sociale leningen", opm="machtiging, geen ESR-uitgave"),
    _bus(SH, 2025, B.BA, "entiteit_begroting", 798_800_000, "rekenhof-begroting-2026", UREK, "Rekenhof — onderzoek Vlaamse begroting 2026, stuk 16 (2025-2026) nr. 1", "tabel 12, p. 32",
         "Netto financiering VMSW 798,8 / 920,5", GEL, A, label="nettofinanciering VMSW (directe schuld)", opm="BA 2025"),
    _bus(SH, 2026, B.BO, "entiteit_begroting", 920_500_000, "rekenhof-begroting-2026", UREK, "Rekenhof — onderzoek Vlaamse begroting 2026, stuk 16 (2025-2026) nr. 1", "tabel 12, p. 32",
         "Netto financiering VMSW 798,8 / 920,5", GEL, A, label="nettofinanciering VMSW (directe schuld)", opm="BO 2026"),
    _bus(SH, 2026, B.BO, "entiteit_begroting", 1_356_700_000, "rekenhof-begroting-2026", UREK, "Rekenhof — onderzoek Vlaamse begroting 2026", "tabel 12, p. 32",
         "Netto financiering VWF 1.427,3 / 1.356,7", GEL, A, label="nettofinanciering Vlaams Woningfonds (directe schuld)", opm="BO 2026; BA 2025 = 1.427,3 mln"),
]


def main() -> None:
    base = Path(__file__).resolve().parents[1] / "data" / "curated"
    write_rows("bronnen", BRONNEN, base)
    write_rows("voorzieningen", VOORZIENINGEN, base)
    write_rows("bevindingen", BEVINDINGEN, base)
    write_rows("budgetten", BUDGETTEN, base)
    print(f"bronnen {len(BRONNEN)}, voorzieningen {len(VOORZIENINGEN)}, bevindingen {len(BEVINDINGEN)}, budgetten {len(BUDGETTEN)} -> {base}")


if __name__ == "__main__":
    main()
