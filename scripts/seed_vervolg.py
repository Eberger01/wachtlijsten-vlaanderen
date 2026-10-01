"""Vervolgdossiers (ronde 4, 1-10-2026): collectief maatwerk (VDAB/DWSE), woonzorg (erkenningskalender), buitengewoon onderwijs,
sociale koop.

Draai ná seed_proef.py, seed_opgroeien.py en seed_aanvullingen.py:  ``python scripts/seed_vervolg.py``  (upsert op sleutel).

Samenvatting van de bevindingen:
- Collectief maatwerk: wachtenden = werkzoekenden zonder werk met een geldig advies CMW (zonder lager advies), reeks 2019-2025 uit
  bijlage 1 bij SV 15 (Awouters, nov 2025); openstaand contingent (toegekende VTE − ingevulde VTE) per kwartaal uit het open-dataplatform
  van het Departement WEWIS (dataset cmw03_product_v1) — eerste wachtlijst-ISE met echte open data. Budget: artikel Collectief Maatwerk
  (JB0-1JEB2HA-WT → JB0-1JEC2HA-WT → TB0-1THC2UA-WT) uit de BBT's Werk en Sociale Economie / Sociale Economie.
- Woonzorg: "De Vlaamse overheid heeft geen zicht op de eventuele wachtlijsten van een voorziening" (SV 951, 2026). Wel een
  aanbodwachtlijst: de erkennings- en omzettingskalender (goedgekeurd / gerealiseerd / uitgesteld / vervallen) uit de SV-reeks Schryvers
  en Vandecasteele; erkende capaciteit uit de Excel-bijlage bij SV 951.
- Buitengewoon onderwijs: "Er is geen centrale structurele registratie of monitoring van de wachtlijsten" (SV 1152, 1192, 1003, 1019);
  Rekenhof (jan 2025): leerlingen +12,9 % 2018-19 → 2022-23 en geen kwaliteitsvolle data over weigeringen; capaciteitsmonitor
  (aug 2025): tekort ± 5.700 plaatsen tegen 2030-31; LOP-toewijzingsresultaten 2026 (Gent 58 %, Aalst 70 % geen school van voorkeur).
- Sociale koop: "De gegevens met betrekking tot kandidaat-kopers worden door de woonmaatschappijen beheerd. Wonen in Vlaanderen beschikt
  dan ook niet over deze data" (SV 448 en 450, 2025) → decentraal, afgerond; aanbodreeks verkochte sociale koopwoningen 2014-2023.
"""

from __future__ import annotations

import sys
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from wachtlijst.models import Bevinding, Bron, BronType, Budget, Budgetfase, Controlestatus, Kredietsoort, WachtlijstType  # noqa: E402
from wachtlijst.store import load, upsert  # noqa: E402

VANDAAG = date(2026, 10, 1)
GEC, GEL, ONG, BET = (Controlestatus.GECONTROLEERD, Controlestatus.BRON_GELEZEN, Controlestatus.ONGECONTROLEERD, Controlestatus.BETWIST)
A = "onderzoeksagent (2026-10-01)"
PF = "https://docs.vlaamsparlement.be/files/pfile?id={}"
CM, WZ, BU, SK = "vdab-collectief-maatwerk", "zorg-woonzorgcentra", "onderwijs-buitengewoon", "wonen-sociale-koop"

BRONNEN = [
    # --- collectief maatwerk
    Bron(bron_id="vlpar-sv-15-2025-cmw", naam="SV nr. 15 (2025-2026), Awouters → min. Crevits — discrepantie openstaande plaatsen / ticket collectief maatwerk (+ bijlage 1)",
         organisatie="Vlaams Parlement", url=PF.format(2229635), bron_type=BronType.PDF, frequentie="eenmalig",
         machinaal="bijlage 1 (pdf) pfile?id=2225033: tabel werkzoekenden met advies CMW per provincie 2019-2025; bijlage-URL via ws.vlpar.be/e/opendata/schv/1947140",
         opmerking="gepubliceerd 18-11-2025; bron VDAB-data"),
    Bron(bron_id="vlpar-sv-1-2024-cmw", naam="SV nr. 1 (2024-2025), Awouters → min. Crevits — tewerkstelling in de sociale economie, wachtlijst",
         organisatie="Vlaams Parlement", url=PF.format(2078707), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 04-12-2024; werknemers CMW 2019-2024 per provincie; wachtlijstvraag doorverwezen naar min. Demir"),
    Bron(bron_id="vlpar-sv-1115-2025-cmw", naam="SV nr. 1115 (2024-2025), Ongena → min. Demir — individueel en collectief maatwerk, indiceringen en doorstroom (gecoördineerd antwoord)",
         organisatie="Vlaams Parlement", url=PF.format(2219342), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 21-10-2025"),
    Bron(bron_id="wewis-opendata-cmw03", naam="Departement WEWIS — open data CMW03: subsidiebedrag en contingent collectief maatwerk per kwartaal",
         organisatie="Departement Werk, Economie, Wetenschap, Innovatie en Sociale Economie", url="https://opendata.wewis.vlaanderen.be/explore/dataset/cmw03_product_v1/",
         bron_type=BronType.API, licentie="open data (Opendatasoft)", frequentie="per kwartaal (afrekening)",
         machinaal="CSV-export: https://opendata.wewis.vlaanderen.be/api/explore/v2.1/catalog/datasets/cmw03_product_v1/exports/csv?delimiter=%3B ; velden cmw_aantal_toegekend_vte (contingent), cmw_aantal_vte (ingevuld), cmw_subsidiebedrag, per gemeente × kwartaal × maatregeltype",
         opmerking="eerste wachtlijst-gerelateerde reeks met echte open data; som over alle vestigingen = Vlaanderen + Brussel (maatwerkbedrijven en -afdelingen)"),
    Bron(bron_id="vlpar-bbt-se-2026", naam="BBT Sociale Economie, begroting 2026 — stuk 13-J (2025-2026) nr. 1", organisatie="Vlaams Parlement",
         url=PF.format(2226293), bron_type=BronType.PDF, frequentie="jaarlijks", opmerking="ingediend 26-11-2025; ISE Activering (Sociale economie), artikel TB0-1THC2UA-WT"),
    Bron(bron_id="vlpar-bbt-se-uitv-2025", naam="BBT Sociale Economie, begrotingsuitvoering 2025 — stuk 23-J (2025-2026) nr. 1", organisatie="Vlaams Parlement",
         url=PF.format(2325109), bron_type=BronType.PDF, frequentie="jaarlijks", opmerking="ingediend 13-05-2026"),
    Bron(bron_id="vlpar-bbt-se-uitv-2024", naam="BBT Sociale Economie, begrotingsuitvoering 2024 — stuk 23-K (2025-2026) nr. 1", organisatie="Vlaams Parlement",
         url=PF.format(2162520), bron_type=BronType.PDF, frequentie="jaarlijks", opmerking="ingediend 08-10-2025"),
    Bron(bron_id="vlpar-bbt-wse-uitv-2023", naam="BBT Werk en Sociale Economie, begrotingsuitvoering 2023 — stuk 23-G (2023-2024) nr. 1", organisatie="Vlaams Parlement",
         url=PF.format(2063726), bron_type=BronType.PDF, frequentie="jaarlijks"),
    Bron(bron_id="vlpar-bbt-wse-uitv-2022", naam="BBT Werk en Sociale Economie, begrotingsuitvoering 2022 — stuk 23-G (2022-2023) nr. 1", organisatie="Vlaams Parlement",
         url=PF.format(1955127), bron_type=BronType.PDF, frequentie="jaarlijks"),
    # --- woonzorg
    Bron(bron_id="vlpar-sv-400-2026-wzc", naam="SV nr. 400 (2025-2026), Schryvers → min. Gennez — erkenningskalender wzc en cvk (stand 1-1-2026)",
         organisatie="Vlaams Parlement", url=PF.format(2282951), bron_type=BronType.PDF, frequentie="jaarlijks (reeks Schryvers)", opmerking="gepubliceerd 16-03-2026; bijlagen 1-2 per voorziening"),
    Bron(bron_id="vlpar-sv-564-2025-wzc", naam="SV nr. 564 (2024-2025), Schryvers → min. Gennez — erkenningskalender wzc en cvk (stand 28-2-2025)",
         organisatie="Vlaams Parlement", url=PF.format(2158189), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 22-05-2025; tabel gerealiseerde capaciteit per jaar 2018-2024"),
    Bron(bron_id="vlpar-sv-1047-2025-wzc", naam="SV nr. 1047 (2024-2025), Schryvers → min. Gennez — erkenningskalender (2) (stand 1-9-2025)",
         organisatie="Vlaams Parlement", url=PF.format(2221155), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 27-10-2025"),
    Bron(bron_id="vlpar-sv-110-2024-wzc", naam="SV nr. 110 (2024-2025), Vandecasteele → min. Gennez — woongelegenheden ouderenzorg, aangroei",
         organisatie="Vlaams Parlement", url=PF.format(2113020), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 03-02-2025; 5.455 goedgekeurde woongelegenheden 2020-2025; vervallen per type uitbater; budget residentiële ouderenzorg 2024"),
    Bron(bron_id="vlpar-sv-668-2025-wzc", naam="SV nr. 668 (2024-2025), Vandecasteele → min. Gennez — woongelegenheden ouderenzorg, aangroei (2): uitstel per jaar",
         organisatie="Vlaams Parlement", url=PF.format(2168840), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 12-06-2025"),
    Bron(bron_id="vlpar-sv-979-2025-wzc", naam="SV nr. 979 (2024-2025), Schryvers → min. Gennez — wzc uitbreiding: doorlooptijd kalender → ingebruikname",
         organisatie="Vlaams Parlement", url=PF.format(2209176), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 07-10-2025"),
    Bron(bron_id="vlpar-sv-951-2026-wzc", naam="SV nr. 951 (2025-2026), Warnez → min. Gennez — wzc en cvk: capaciteit en programmatie (+ Excel-bijlage)",
         organisatie="Vlaams Parlement", url=PF.format(2342635), bron_type=BronType.PDF, frequentie="eenmalig",
         machinaal="Excel-bijlage pfile?id=2343662 (tabbladen erkende WZC/CVK per gemeente en uitbater, bijkomende erkenningen 2025-26, realisatie); via ws.vlpar.be/e/opendata/schv/2038661",
         opmerking="gepubliceerd 13-07-2026; 'De Vlaamse overheid heeft geen zicht op de eventuele wachtlijsten van een voorziening'; programmatiestop tot eind 2026; nieuwe kalender zomer 2026; zorgprognosemodel 2029"),
    # --- buitengewoon onderwijs
    Bron(bron_id="vlpar-sv-1152-2025-buo", naam="SV nr. 1152 (2024-2025), Werbrouck → min. Demir — buitengewoon onderwijs, plaatstekort",
         organisatie="Vlaams Parlement", url=PF.format(2224738), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 10-12-2025; 'geen centrale structurele registratie of monitoring van de wachtlijsten'"),
    Bron(bron_id="vlpar-sv-1192-2025-buo", naam="SV nr. 1192 (2024-2025), Buyst → min. Demir — buitengewoon onderwijs, arbeidsmarktfinaliteit en OKAN: plaatstekort",
         organisatie="Vlaams Parlement", url=PF.format(2225656), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 04-11-2025; evolutie wachtlijsten 'niet mogelijk' wegens geen registratie"),
    Bron(bron_id="vlpar-sv-829-2026-buo", naam="SV nr. 829 (2025-2026), D'Hose → min. Demir — buitengewoon basisonderwijs, aanhoudend plaatstekort (LOP Gent en Aalst)",
         organisatie="Vlaams Parlement", url=PF.format(2353372), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 15-07-2026"),
    Bron(bron_id="vlpar-sv-1019-2026-buo", naam="SV nr. 1019 (2025-2026), Peeters → min. Demir — capaciteit buso Limburg",
         organisatie="Vlaams Parlement", url=PF.format(2366058), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 28-09-2026; 'Er bestaat geen centrale registratie of monitoring'"),
    Bron(bron_id="rekenhof-buo-2025", naam="Rekenhof — Buitengewoon onderwijs: toegang en uitstroom (verslag aan het Vlaams Parlement, januari 2025)",
         organisatie="Rekenhof", url=PF.format(2102664), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="131 p.; leerlingenevolutie p. 35; weigeringen/capaciteit p. 84"),
    Bron(bron_id="capaciteitsmonitor-2025", naam="Capaciteitsmonitor schoolinfrastructuur leerplichtonderwijs, 4e editie (HIVA-KU Leuven & VUB, 27-08-2025) + dashboard",
         organisatie="HIVA-KU Leuven / VUB i.o.v. Departement Onderwijs", url="https://hiva.kuleuven.be/sites/capaciteitsmonitor/docs/capaciteitsmonitor-rapport-27-augustus-2025.pdf",
         bron_type=BronType.PDF, frequentie="driejaarlijks", machinaal="dashboard per onderwijszone (data-onderwijs.vlaanderen.be); pdf niet bereikbaar vanuit de cloudomgeving (verbinding gereset) — lokaal downloaden",
         opmerking="rapport lokaal gelezen op 01-10-2026 (kopie in data/raw/onderwijs/, niet in git); tekortcijfers BuO: PDF p. 83-84 en 93-94"),
    Bron(bron_id="vrt-2025-08-27-buo", naam="VRT NWS 27-08-2025 — 'Tegen 2030 plaatsoverschot in basisscholen, maar 5.700 plaatsen tekort in buitengewoon onderwijs'",
         organisatie="VRT (secundair)", url="https://www.vrt.be/vrtnws/nl/2025/08/27/studie-voorspelt-tekort-van-ruim-3-700-plaatsen-in-buitengewoon/", bron_type=BronType.HTML, frequentie="eenmalig"),
    # --- sociale koop
    Bron(bron_id="vlpar-sv-448-2025-koop", naam="SV nr. 448 (2024-2025), Mertens → min. Depraetere — sociale koopwoningen, nieuwbouw (+ 7 Excel-bijlagen)",
         organisatie="Vlaams Parlement", url=PF.format(2173675), bron_type=BronType.PDF, frequentie="eenmalig",
         machinaal="bijlage 1 pfile?id=2161755 (verkochte sociale en middelgrote koopwoningen 2014-2023 per provincie en woonmaatschappij); via ws.vlpar.be/e/opendata/schv/1892942",
         opmerking="gepubliceerd 11-06-2025; kandidaat-kopers: 'Wonen in Vlaanderen beschikt niet over deze data'"),
    Bron(bron_id="vlpar-sv-450-2025-koop", naam="SV nr. 450 (2024-2025), Mertens → min. Depraetere — sociale bouwgronden, kandidaat-kopers en bedragen",
         organisatie="Vlaams Parlement", url=PF.format(2173997), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 12-06-2025; verkoop sociale kavels dalend 2014-2023"),
]


def _update_voorzieningen() -> None:
    vz = {v.voorziening_id: v for v in load("voorzieningen")}
    c = vz[CM]
    c.scan_status = "proef_uitgewerkt"
    c.laatste_peildatum = date(2026, 3, 31)
    c.publicatie_bron_id = "wewis-opendata-cmw03"
    c.frequentie = "contingent per kwartaal (open data); wachtenden enkel via SV"
    c.wachtlijst_type = WachtlijstType.CENTRAAL_NIET_GEPUBLICEERD
    c.wachtlijst_naam = "werkzoekenden zonder werk met een geldig advies collectief maatwerk (zonder lager advies)"
    c.ise_koppeling = "ACTIVERING (SOCIALE ECONOMIE)"
    c.opmerking = ("Twee kanten: (1) wachtenden = werkzoekenden met een 'ticket' CMW die niet aan de slag zijn (VDAB-data, enkel via SV: 4.563 in 2019 → 3.089 in 2024 → 3.781 in aug 2025); "
                   "(2) openstaand contingent = toegekende min ingevulde VTE in maatwerkbedrijven (open data WEWIS: ± 900-2.300 VTE per kwartaal). Paradox: meer wachtenden dan open plaatsen → mismatch "
                   "(mobiliteit, gezondheid, taal, functievereisten), aldus de minister. Groeipad 1.000 plaatsen tegen 2029 (2025: 200 plaatsen, 189,5 VTE toegekend). Budget: artikel Collectief Maatwerk 466,7 mln (uitv. 2022) → 572,5 mln (uitv. 2025) → 600,7 mln (BO 2026).")
    w = vz[WZ]
    w.scan_status = "proef_uitgewerkt"
    w.laatste_peildatum = date(2026, 6, 30)
    w.publicatie_bron_id = "vlpar-sv-400-2026-wzc"
    w.frequentie = "SV-reeks Schryvers (jaarlijks) en Vandecasteele; geen eigen publicatie"
    w.wachtlijst_type = WachtlijstType.DECENTRAAL
    w.wachtlijst_naam = "geen bewonerswachtlijst; aanbodzijde: erkennings- en omzettingskalender"
    w.ise_koppeling = "WOONZORG EN EERSTE LIJN | SOCIALE BESCHERMING"
    w.opmerking = ("'De Vlaamse overheid heeft geen zicht op de eventuele wachtlijsten van een voorziening' (SV 951, juli 2026). Aanbodzijde: kalender 2020-2025 = 5.455 goedgekeurde woongelegenheden wzc; "
                   "sinds 2015 t/m Q4 2025 3.481 wzc + 377 cvk in gebruik genomen; nog te realiseren vanaf 2026: 2.110 wzc + 144 cvk; uitgesteld sinds 2021: 4.259 wzc + 323 cvk; vervallen t/m Q4 2025: 509 wzc + 40 cvk. "
                   "Doorlooptijd kalender → ingebruikname 2 kwartalen (2020) → 8 (2024). Erkende capaciteit medio 2026: 83.923 woongelegenheden wzc en 2.803 cvk (incl. Brussel). Programmatiestop tot eind 2026; "
                   "nieuwe kalender zomer 2026; zorgprognosemodel 2029. Budget residentiële ouderenzorg (VSB) 2,78 mld (2024) → 2,77 mld BO 2026 (artikel GM0-AGCF2VD-WT).")
    b = vz[BU]
    b.scan_status = "proef_uitgewerkt"
    b.laatste_peildatum = date(2026, 5, 18)
    b.publicatie_bron_id = "capaciteitsmonitor-2025"
    b.frequentie = "capaciteitsmonitor driejaarlijks; LOP-toewijzingsresultaten jaarlijks (lokaal); SV's"
    b.wachtlijst_type = WachtlijstType.DECENTRAAL
    b.wachtlijst_naam = "weigeringslijst per school (niet-gerealiseerde inschrijvingen); geen centrale monitoring"
    b.ise_koppeling = ""
    b.opmerking = ("'Er is geen centrale structurele registratie of monitoring van de wachtlijsten' (SV 1152, 1192, 1003, 1019); AGODI heeft geen volledig zicht op weigeringen (geen rijksregisternummer). "
                   "Rekenhof (jan 2025): leerlingen BuO 47.468 (2018-19) → 53.573 (2022-23), +12,9 %; capaciteitsmonitor (aug 2025): tekort ± 5.700 plaatsen tegen 2030-31 (basis 2.184, secundair 3.731). "
                   "LOP 2026: Antwerpen 680 kinderen zonder plaats (66 % van aanmeldingen, VRT), Gent 58 % en Aalst 70 % geen school van voorkeur (SV 829). Budget: niet afgesplitst in de BBT Onderwijs; extra werkingsbudget IAC type 2 automatisch vanaf 2026-27.")
    s = vz[SK]
    s.scan_status = "afgerond"
    s.laatste_peildatum = date(2023, 12, 31)
    s.publicatie_bron_id = "vlpar-sv-448-2025-koop"
    s.frequentie = "aanbodcijfers jaarlijks (jaarverslag WiV); kandidaten niet centraal"
    s.wachtlijst_type = WachtlijstType.DECENTRAAL
    s.wachtlijst_naam = "kandidatenregisters per woonmaatschappij"
    s.ise_koppeling = "AANBODZIJDE WONINGMARKT"
    s.opmerking = ("'De gegevens met betrekking tot kandidaat-kopers worden door de woonmaatschappijen beheerd. Wonen in Vlaanderen beschikt dan ook niet over deze data' (SV 448 en 450, 2025) → "
                   "geen centrale wachtlijst, afgesloten als decentraal. Aanbod: verkochte nieuwe sociale koopwoningen 867 (2014) → 1.053 (2018) → 505 (2023), dalend; verkoop sociale kavels dalend. "
                   "Eventueel later: steekproef bij de grootste woonmaatschappijen.")
    upsert("voorzieningen", [c, w, b, s])


def _b(vid, metriek, waarde, eenheid, peildatum, bron_id, url, titel, pagina, passage, definitie, status, pub=None, door="", opm=""):
    return Bevinding(bevinding_id=f"{vid}:{metriek}:{peildatum.isoformat()}", voorziening_id=vid, metriek=metriek, waarde=waarde, eenheid=eenheid, peildatum=peildatum,
                     bron_id=bron_id, bron_url=url, documenttitel=titel, pagina=pagina, passage=passage, definitie=definitie, publicatiedatum=pub,
                     controlestatus=status, gecontroleerd_door=door, gecontroleerd_op=VANDAAG if door else None, opmerking=opm)


BEVINDINGEN: list[Bevinding] = []

# ------------------------------------------------------------------------------------------------ collectief maatwerk
D_EB = "onderzoeksagent + 2e lezing Claude + EB (2026-10-01)"
D_CMW = "Werkzoekenden zonder werk met een geldig advies collectief maatwerk zonder lager advies (VDAB), per jaar (2025: augustus)."
T15, U15 = "SV nr. 15 (2025-2026) Awouters — bijlage 1", PF.format(2225033)
K15 = "Antwerpen Limburg Oost-Vlaanderen Vlaams-Brabant West-Vlaanderen Brussel Buiten Brussel/Vlaanderen Totaal"
for jaar, rij in ((2019, "1.276 637 1.004 413 1.184 37 12 4.563"), (2020, "1.533 670 1.084 505 1.267 43 9 5.111"), (2021, "1.449 623 1.012 451 1.112 43 14 4.704"),
                  (2022, "1.325 551 938 388 1.039 27 9 4.277"), (2023, "1.441 571 1.047 418 1.050 22 5 4.554"), (2024, "1.083 363 690 287 649 14 3 3.089")):
    n = int(rij.split()[-1].replace(".", ""))
    BEVINDINGEN.append(_b(CM, "wachtenden_advies_cmw", n, "personen", date(jaar, 12, 31), "vlpar-sv-15-2025-cmw", U15, T15, f"bijlage 1, tabel 1, rij {jaar}",
                          f"Aantal werkzoekenden zonder werk met een advies collectief maatwerk zonder lager advies (2019-2025) … {K15} … {jaar} {rij}", D_CMW, GEC, date(2025, 11, 18), D_EB,
                          "peildatum 31/12 aangenomen: de bijlage vermeldt de referentiemaand enkel voor 2025 (augustus)"))
BEVINDINGEN.append(_b(CM, "wachtenden_advies_cmw", 3781, "personen", date(2025, 8, 31), "vlpar-sv-15-2025-cmw", PF.format(2229635), "SV nr. 15 (2025-2026) Awouters", "antwoord 1 (PDF p. 2) + bijlage 1",
                      "In augustus 2025 zijn er 3.781 werkzoekenden met een advies collectief maatwerk, zonder lager advies.", D_CMW, GEC, date(2025, 11, 18), D_EB,
                      opm="* Voor het jaartal 2025 kijken we naar de laatste beschikbare maand (augustus 2025)"))
BEVINDINGEN.append(_b(CM, "wachtenden_advies_cmw", 3019, "personen", date(2025, 6, 30), "vlpar-sv-15-2025-cmw", PF.format(2229635), "SV nr. 15 (2025-2026) Awouters — vraagtekst (SERV)", "vraag",
                      "Uit cijfers van de SERV blijkt dat 11% van de vooropgestelde vte's in de maatwerkbedrijven niet wordt ingevuld, terwijl 3019 werkzoekenden een advies collectief maatwerk hebben.",
                      "SERV-cijfer geciteerd door de vraagsteller; peildatum onbekend (hier medio 2025)", ONG, date(2025, 11, 18), opm="secundair (vraagtekst); afwijkend van VDAB-reeks (3.781 aug 2025)"))
# open contingent per kwartaal uit WEWIS open data (K4 van elk jaar + laatst beschikbare)
D_CONT = ("Toegekend contingent (VTE) min ingevulde VTE doelgroepwerknemers in maatwerkbedrijven en -afdelingen, afrekening van het kwartaal; som over alle vestigingen (Vlaanderen + Brussel). "
          "K4 ligt doorgaans lager dan de andere kwartalen (2025: K1–K3 1.694–2.211 VTE, K4 904 VTE).")
UW = "https://opendata.wewis.vlaanderen.be/explore/dataset/cmw03_product_v1/"


def _nl(x: Decimal) -> str:
    return f"{x:,.2f}".replace(",", " ").replace(".", ",").replace(" ", ".")


def _r1(x: Decimal) -> float:
    return float(x.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


# exacte sommen per periode uit de CSV-export van 1-10-2026 (nagerekend bij de tweede lezing)
for (jaar, kw, d), nvest, cont, vte in (((2019, "K4", date(2019, 12, 31)), 103, "19533.80", "18602.73"), ((2020, "K4", date(2020, 12, 31)), 106, "19587.80", "18433.95"),
                                        ((2021, "K4", date(2021, 12, 31)), 105, "19804.80", "18748.94"), ((2022, "K4", date(2022, 12, 31)), 99, "19929.40", "18828.37"),
                                        ((2023, "K4", date(2023, 12, 31)), 84, "21421.94", "19790.62"), ((2024, "K4", date(2024, 12, 31)), 83, "21318.54", "19800.49"),
                                        ((2025, "K4", date(2025, 12, 31)), 82, "21245.67", "20341.62"), ((2026, "K1", date(2026, 3, 31)), 82, "21466.66", "19913.79")):
    cont, vte = Decimal(cont), Decimal(vte)
    pas = f"som periode = {jaar} {kw} ({nvest} vestigingen): cmw_aantal_toegekend_vte {_nl(cont)}; cmw_aantal_vte {_nl(vte)}"
    pag = f"CSV-export, periode = {jaar} {kw}, alle vestigingen"
    BEVINDINGEN.append(_b(CM, "contingent_toegekend_vte", _r1(cont), "VTE", d, "wewis-opendata-cmw03", UW, "WEWIS open data CMW03", pag, pas,
                          "Toegekend contingent collectief maatwerk (VTE), som over vestigingen.", GEC, None, D_EB, opm="eigen aggregatie (CSV-export 1-10-2026)"))
    BEVINDINGEN.append(_b(CM, "contingent_ingevuld_vte", _r1(vte), "VTE", d, "wewis-opendata-cmw03", UW, "WEWIS open data CMW03", pag, pas,
                          "Ingevulde VTE doelgroepwerknemers collectief maatwerk, som over vestigingen.", GEC, None, D_EB, opm="eigen aggregatie"))
    BEVINDINGEN.append(_b(CM, "contingent_open_vte", _r1(cont - vte), "VTE", d, "wewis-opendata-cmw03", UW, "WEWIS open data CMW03", pag, pas, D_CONT, GEC, None, D_EB,
                          opm=f"eigen berekening: toegekend − ingevuld = {_nl(cont - vte)}" + ("; maatwerkafdelingen gaan per 1-7-2023 op in individueel maatwerk" if jaar <= 2022 else "")))
# werknemers CMW (personen) uit SV 1
for jaar, n in ((2019, 23451), (2020, 23386), (2021, 24066), (2022, 24605), (2023, 25815)):
    BEVINDINGEN.append(_b(CM, "werknemers_cmw", n, "personen", date(jaar, 12, 31), "vlpar-sv-1-2024-cmw", PF.format(2078707), "SV nr. 1 (2024-2025) Awouters", "antwoord 1, tabel 1 (PDF p. 2)",
                          "Totaal 23.451 23.386 24.066 24.605 25.815 24.099 … Tabel 1. Aantal werknemers in Maatwerk bij Collectieve Inschakeling. Bron: Data DWSE … * Data 2019-2023 op jaarbasis",
                          "Aantal werknemers in Maatwerk bij Collectieve Inschakeling op jaarbasis (kwartaalafrekeningen, DWSE), incl. Brussel.", GEC, date(2024, 12, 4), D_EB,
                          "jaarcijfer, geen stand op 31/12; Totaal < som provincies (unieke personen)"))
# doorstroom en indicering uit SV 1115
D_DOOR = ("Personen die vanuit collectief maatwerk doorstromen naar het reguliere circuit (SV 1115, vraag en antwoord 10b); "
          "doorstroom naar individueel maatwerk is niet beschikbaar (antwoord 10a).")
P_DOOR = "In het eerste semester van 2025 stroomden 197 personen uit collectief maatwerk door. In 2024 waren dat er 344, in 2023 513, in 2022 403, in 2021 283 en in 2020 256."
for jaar, n in ((2020, 256), (2021, 283), (2022, 403), (2023, 513), (2024, 344)):
    BEVINDINGEN.append(_b(CM, "doorstroom_uit_cmw", n, "personen", date(jaar, 12, 31), "vlpar-sv-1115-2025-cmw", PF.format(2219342), "SV nr. 1115 (2024-2025) Ongena", "antwoord 10b (PDF p. 5)",
                          P_DOOR, D_DOOR, GEC, date(2025, 10, 21), D_EB))
BEVINDINGEN.append(_b(CM, "doorstroom_uit_cmw", 197, "personen", date(2025, 6, 30), "vlpar-sv-1115-2025-cmw", PF.format(2219342), "SV nr. 1115 (2024-2025) Ongena", "antwoord 10b (PDF p. 5)",
                      "In het eerste semester van 2025 stroomden 197 personen uit collectief maatwerk door.", D_DOOR + " Eerste semester 2025.", GEC, date(2025, 10, 21), D_EB))
BEVINDINGEN.append(_b(CM, "indiceringen_semester", 8425, "aanvragen", date(2025, 6, 30), "vlpar-sv-1115-2025-cmw", PF.format(2219342), "SV nr. 1115 (2024-2025) Ongena", "antwoord 1 (PDF p. 4)",
                      "Er werden in het eerste semester van 2025 voor individueel of collectief maatwerk samen 8.425 indiceringen verricht.",
                      "ICF-indiceringen (adviesaanvragen IMW/CMW) in het eerste semester 2025; gemiddeld traject 16,5 uur.", GEC, date(2025, 10, 21), D_EB,
                      "antwoord 3a: 'voor collectief maatwerk 320 adviesaanvragen geweigerd'; 3c: 2.219 toegekend"))
BEVINDINGEN.append(_b(CM, "advies_cmw_toegekend_semester", 2219, "adviezen", date(2025, 6, 30), "vlpar-sv-1115-2025-cmw", PF.format(2219342), "SV nr. 1115 (2024-2025) Ongena", "antwoord 3c (PDF p. 4)",
                      "Er werden in het eerste semester van 2025 2.219 adviesaanvragen voor een advies collectief maatwerk toegekend.", "Toegekende adviezen collectief maatwerk, eerste semester 2025.",
                      GEC, date(2025, 10, 21), D_EB, "3d: alle CMW-adviezen hebben ook een IMW-advies"))
BEVINDINGEN.append(_b(CM, "groeipad_plaatsen_toegekend_vte", 189.5, "VTE", date(2025, 4, 1), "vlpar-bbt-se-uitv-2025", PF.format(2325109), "BBT Sociale Economie, begrotingsuitvoering 2025 — 23-J", "OD 2, p. 9",
                      "In een eerste fase werden 200 bijkomende plaatsen opengesteld. Na beoordeling van de ingediende aanvragen werden 189,5 VTE effectief toegekend aan 48 maatwerkbedrijven, verspreid over Vlaanderen, met ingang vanaf 1 april 2025.",
                      "Eerste fase groeipad collectief maatwerk (minstens 1.000 plaatsen tegen 2029).", GEC, date(2026, 5, 13), D_EB))

# ------------------------------------------------------------------------------------------------ woonzorg
S400, U400, T400 = "vlpar-sv-400-2026-wzc", PF.format(2282951), "SV nr. 400 (2025-2026) Schryvers"
S564, U564, T564 = "vlpar-sv-564-2025-wzc", PF.format(2158189), "SV nr. 564 (2024-2025) Schryvers"
P564_1 = ("Hierbij een overzicht per provincie van de goedgekeurde erkennings-en omzettingskalender die nog in gebruik moet worden genomen vanaf het 1ste kwartaal van 2025 tot het uitputten van deze kalenders. "
          "- Provincie Antwerpen: 716 woongelegenheden woonzorgcentrum en 55 verblijfseenheden centrum voor kortverblijf type 1; - Provincie Limburg: 649 woongelegenheden woonzorgcentrum en 35 verblijfseenheden …; "
          "- Provincie Oost-Vlaanderen: 322 woongelegenheden woonzorgcentrum en 30 verblijfseenheden …; - Provincie Vlaams-Brabant: 493 woongelegenheden woonzorgcentrum en 17 verblijfseenheden …; "
          "- Provincie West-Vlaanderen: 583 woongelegenheden woonzorgcentrum en 74 verblijfseenheden centrum voor kortverblijf type 1.")
P564_2 = ("Hierbij een overzicht per provincie van de goedgekeurde erkennings-en omzettingskalenders die werden uitgesteld vanaf het tweede trimester van 2021, na verzending van de betreffende omzendbrief: "
          "- Provincie Antwerpen: 1078 woongelegenheden woonzorgcentrum en 59 verblijfseenheden …; - Provincie Limburg: 564 … en 39 …; - Provincie Oost-Vlaanderen: 507 … en 40 …; "
          "- Provincie Vlaams-Brabant: 450 … en 16 …; - Provincie West-Vlaanderen: 910 woongelegenheden woonzorgcentrum en 102 verblijfseenheden centrum voor kortverblijf type 1.")
P564_6 = ("Hierbij een overzicht van de bijkomende gerealiseerde capaciteit in een woonzorgcentrum of centrum voor kortverblijf type 1, per provincie: "
          "- Provincie Antwerpen: 990 woongelegenheden woonzorgcentrum en 81 verblijfseenheden …; - Provincie Limburg: 301 … en 53 …; - Provincie Oost-Vlaanderen: 396 … en 75 …; "
          "- Provincie Vlaams-Brabant: 385 … en 31 …; - Provincie West-Vlaanderen: 866 … en 82 …; - Brussels Hoofdstedelijk Gewest: 150 woongelegenheden woonzorgcentrum.")
P564_7 = ("Hieronder geef ik een overzicht van alle vervallen (niet-gerealiseerde) capaciteit uit de erkennings- en omzettingskalender tot eind 2024: "
          "- Provincie Antwerpen: 136 woongelegenheden woonzorgcentrum en 25 verblijfseenheden centrum voor kortverblijf type 1; - Provincie Limburg: 94 woongelegenheden woonzorgcentrum; "
          "- Provincie Oost-Vlaanderen: 45 woongelegenheden woonzorgcentrum;- Provincie Vlaams-Brabant:20 woongelegenheden woonzorgcentrum en 3 verblijfseenheden centrum voor kortverblijf type 1; "
          "- Provincie West-Vlaanderen: 17 woongelegenheden woonzorgcentrum; - Brussels Hoofdstedelijk Gewest: 15 woongelegenheden woonzorgcentrum.")
P400_1 = ("Hieronder geef ik een overzicht per provincie van de goedgekeurde erkennings-en omzettingskalender die nog in gebruik kunnen worden genomen vanaf het eerste kwartaal van 2026 tot het uitputten van deze kalenders: "
          "- Provincie Antwerpen: 692 woongelegenheden woonzorgcentrum en 44 verblijfseenheden …; - Provincie Limburg: 366 … en 24 …; - Provincie Oost-Vlaanderen: 242 … en 25 …; "
          "- Provincie Vlaams-Brabant: 317 woongelegenheden woonzorgcentrum; - Provincie West-Vlaanderen: 493 woongelegenheden woonzorgcentrum en 51 verblijfseenheden centrum voor kortverblijf type 1.")
P400_2 = ("Hieronder geef ik een overzicht per provincie van de goedgekeurde erkennings-en omzettingskalender die werd uitgesteld vanaf het tweede trimester van 2021, na verzending van de betreffende omzendbrief: "
          "- Provincie Antwerpen: 1247 woongelegenheden woonzorgcentrum en 84 verblijfseenheden …; - Provincie Limburg: 682 … en 44 …; - Provincie Oost-Vlaanderen: 607 … en 67 …; "
          "- Provincie Vlaams-Brabant: 454 … en 16 …; - Provincie West-Vlaanderen: 1119 … en 112 …; - Brussels Hoofdstedelijk Gewest: 150 woongelegenheden woonzorgcentrum.")
P400_5 = ("Hieronder vindt u een overzicht van de vervallen capaciteit uit de erkennings- en omzettingskalender tot en met het vierde kwartaal van 2025: "
          "- Provincie Antwerpen: 166 woongelegenheden woonzorgcentrum en 25 verblijfseenheden centrum voor kortverblijf type 1; - Provincie Limburg: 141 …; - Provincie Oost-Vlaanderen: 79 …; "
          "- Provincie Vlaams-Brabant: 86 woongelegenheden woonzorgcentrum en 15 verblijfseenheden centrum voor kortverblijf type 1; - Provincie West-Vlaanderen: 22 …; - Brussels Hoofdstedelijk Gewest: 15 woongelegenheden woonzorgcentrum.")
D_VERV = "Vervallen (niet-gerealiseerde) capaciteit uit de erkennings- en omzettingskalender (alle kalenders), cumulatief, per provincie + Brussel."
U951X = PF.format(2343662)
BEVINDINGEN += [
    _b(WZ, "kalender_goedgekeurd_wzc_2020_2025", 5455, "woongelegenheden", date(2019, 12, 31), "vlpar-sv-110-2024-wzc", PF.format(2113020), "SV nr. 110 (2024-2025) Vandecasteele", "antwoord 1 (PDF p. 2)",
       "Oorspronkelijk werden er in totaal 5.455 woongelegenheden erkenningskalender woonzorgcentrum goedgekeurd voor de periode 2020-2025.", "Goedgekeurde woongelegenheden wzc in de erkenningskalender 2020-2025 (vastgelegd in 2019).", GEC, date(2025, 2, 3), D_EB),
    _b(WZ, "kalender_gerealiseerd_wzc_cum", 3088, "woongelegenheden", date(2024, 12, 31), S564, U564, T564, "antwoord 6 (PDF p. 4)", P564_6,
       "Bijkomende gerealiseerde capaciteit wzc uit de erkennings- en omzettingskalender, cumulatief, per provincie + Brussel (tabel per jaar 2018-2024).", GEC, date(2025, 5, 22), D_EB, opm="eigen som van de provinciecijfers"),
    _b(WZ, "kalender_gerealiseerd_cvk_cum", 322, "verblijfseenheden", date(2024, 12, 31), S564, U564, T564, "antwoord 6 (PDF p. 4)", P564_6, "Idem, centra voor kortverblijf type 1.", GEC, date(2025, 5, 22), D_EB,
       opm="eigen som (81 + 53 + 75 + 31 + 82)"),
    _b(WZ, "kalender_gerealiseerd_wzc_cum", 3481, "woongelegenheden", date(2025, 12, 31), S400, U400, T400, "antwoord 4 (PDF p. 3)",
       "In totaal werden er inmiddels 3481 woongelegenheden woonzorgcentrum en 377 verblijfseenheden centrum voor kortverblijf type 1 effectief in gebruik genomen.", "Idem, t/m vierde kwartaal 2025.", GEC, date(2026, 3, 16), D_EB),
    _b(WZ, "kalender_gerealiseerd_cvk_cum", 377, "verblijfseenheden", date(2025, 12, 31), S400, U400, T400, "antwoord 4 (PDF p. 3)",
       "In totaal werden er inmiddels 3481 woongelegenheden woonzorgcentrum en 377 verblijfseenheden centrum voor kortverblijf type 1 effectief in gebruik genomen.", "Idem, cvk type 1, t/m Q4 2025.", GEC, date(2026, 3, 16), D_EB),
    _b(WZ, "kalender_nog_te_realiseren_wzc", 2763, "woongelegenheden", date(2025, 1, 1), S564, U564, T564, "antwoord 1 (PDF p. 3)", P564_1,
       "Goedgekeurde erkennings- en omzettingskalender wzc die nog in gebruik moet worden genomen (aanbodwachtlijst).", GEC, date(2025, 5, 22), D_EB, opm="eigen som (716 + 649 + 322 + 493 + 583)"),
    _b(WZ, "kalender_nog_te_realiseren_wzc", 2110, "woongelegenheden", date(2026, 1, 1), S400, U400, T400, "antwoord 1 (PDF p. 2)", P400_1, "Idem, stand 1-1-2026.", GEC, date(2026, 3, 16), D_EB,
       opm="eigen som (692 + 366 + 242 + 317 + 493)"),
    _b(WZ, "kalender_nog_te_realiseren_cvk", 144, "verblijfseenheden", date(2026, 1, 1), S400, U400, T400, "antwoord 1 (PDF p. 2)", P400_1, "Idem, cvk type 1.", GEC, date(2026, 3, 16), D_EB,
       opm="eigen som (44 + 24 + 25 + 51)"),
    _b(WZ, "kalender_uitgesteld_wzc_cum", 3509, "woongelegenheden", date(2025, 1, 1), S564, U564, T564, "antwoord 2 (PDF p. 3)", P564_2,
       "Goedgekeurde kalender wzc waarvoor uitstel werd gevraagd sinds de omzendbrief van 5-5-2021, cumulatief; vijf provincies (zonder Brussel).", GEC, date(2025, 5, 22), D_EB,
       opm="eigen som (1078 + 564 + 507 + 450 + 910); de bron dateert dit antwoord niet, peildatum gelijkgesteld aan antwoord 1 (vanaf Q1 2025)"),
    _b(WZ, "kalender_uitgesteld_wzc_cum", 4109, "woongelegenheden", date(2026, 1, 1), S400, U400, T400, "antwoord 2 (PDF p. 2)", P400_2,
       "Idem, stand 1-1-2026; vijf provincies (zonder Brussel), vergelijkbaar met 2025.", GEC, date(2026, 3, 16), D_EB,
       opm="eigen som (1247 + 682 + 607 + 454 + 1119); SV 400 vermeldt ook Brussel 150 (totaal 4.259), SV 564 niet"),
    _b(WZ, "kalender_uitgesteld_cvk_cum", 323, "verblijfseenheden", date(2026, 1, 1), S400, U400, T400, "antwoord 2 (PDF p. 2)", P400_2, "Idem, cvk type 1.", GEC, date(2026, 3, 16), D_EB,
       opm="eigen som (84 + 44 + 67 + 16 + 112)"),
    _b(WZ, "kalender_vervallen_wzc_2020_2025_kalender", 112, "woongelegenheden", date(2024, 12, 31), "vlpar-sv-110-2024-wzc", PF.format(2113020), "SV nr. 110 (2024-2025) Vandecasteele", "antwoord 1, tabel",
       "Totaal 86 (for-profit) + 26 (non-profit) + 0 (openbaar) = 112", "Vervallen (niet-gerealiseerde) woongelegenheden wzc uit enkel de kalender 2020-2025, 2020-2024 per kwartaal en type uitbater.", BET, date(2025, 2, 3), A,
       opm="andere afbakening dan de reeks kalender_vervallen_wzc_cum (alle kalenders: 327 tot eind 2024, SV 564)"),
    _b(WZ, "kalender_vervallen_wzc_cum", 327, "woongelegenheden", date(2024, 12, 31), S564, U564, T564, "antwoord 7 (PDF p. 4-5)", P564_7, D_VERV, GEC, date(2025, 5, 22), D_EB,
       opm="eigen som (136 + 94 + 45 + 20 + 17 + 15)"),
    _b(WZ, "kalender_vervallen_cvk_cum", 28, "verblijfseenheden", date(2024, 12, 31), S564, U564, T564, "antwoord 7 (PDF p. 4-5)", P564_7, "Idem, cvk type 1.", GEC, date(2025, 5, 22), D_EB,
       opm="eigen som (25 + 3)"),
    _b(WZ, "kalender_vervallen_wzc_cum", 509, "woongelegenheden", date(2025, 12, 31), S400, U400, T400, "antwoord 5 (PDF p. 3)", P400_5, D_VERV + " T/m Q4 2025.", GEC, date(2026, 3, 16), D_EB,
       opm="eigen som (166 + 141 + 79 + 86 + 22 + 15)"),
    _b(WZ, "kalender_vervallen_cvk_cum", 40, "verblijfseenheden", date(2025, 12, 31), S400, U400, T400, "antwoord 5 (PDF p. 3)", P400_5, "Idem, cvk type 1.", GEC, date(2026, 3, 16), D_EB, opm="eigen som (25 + 15)"),
    _b(WZ, "capaciteit_erkend_wzc", 83923, "woongelegenheden", date(2026, 6, 30), "vlpar-sv-951-2026-wzc", U951X, "SV nr. 951 (2025-2026) Warnez — Excel-bijlage", "tabblad '1. erkendeWZCpergemeente', rij 294 (B-E)",
       "Vzw Openbaar For-profit Eindtotaal … Eindtotaal 45319 23853 14751 83923", "Erkende woongelegenheden woonzorgcentrum per gemeente en type uitbater, incl. Brussel (1.019), medio 2026.", GEC, date(2026, 7, 13), D_EB,
       "peildatum afgeleid: de vraag (28-5-2026) vraagt de stand 'vandaag'; Excel laatst opgeslagen 29-6-2026"),
    _b(WZ, "capaciteit_erkend_cvk", 2803, "verblijfseenheden", date(2026, 6, 30), "vlpar-sv-951-2026-wzc", U951X, "SV nr. 951 (2025-2026) Warnez — Excel-bijlage", "tabblad '2. erkendeCKVpergemeente', rij 253 (B-E)",
       "Vzw Openbaar For-profit Eindtotaal … Eindtotaal 1879 688 236 2803", "Erkende verblijfseenheden centrum voor kortverblijf, incl. Brussel (13), medio 2026.", GEC, date(2026, 7, 13), D_EB,
       "peildatum afgeleid (zie capaciteit_erkend_wzc)"),
    _b(WZ, "capaciteit_raming_wzc", 84717, "woongelegenheden", date(2025, 12, 31), "vlpar-sv-110-2024-wzc", PF.format(2113020), "SV nr. 110 (2024-2025) Vandecasteele", "vraagtekst, PDF p. 1 (citaat technisch antwoord BO 2025)",
       "Op basis van de ramingen in kader van BO2025 zouden er eind 2025, 84.717 woongelegenheden woonzorgcentrum en 2.771 woongelegenheden centrum voor kortverblijf zijn.", "Raming BO 2025 van het aantal woongelegenheden wzc eind 2025.", GEC, date(2025, 2, 3), D_EB, opm="geciteerd in de vraag uit een technisch antwoord van de administratie"),
]
D_DOORL = ("Gemiddelde tijd tussen de toegekende periode in de erkenningskalender en de effectieve ingebruikname (wzc), per jaar van de toegekende periode, stand oktober 2025; "
           "recente jaren tellen enkel kalenders die al in gebruik zijn en kunnen nog stijgen.")
for jaar, n, cvk in ((2020, 2, 3), (2021, 6, 3), (2022, 4, 7), (2023, 8, 8), (2024, 8, 7)):
    BEVINDINGEN.append(_b(WZ, "doorlooptijd_kalender_ingebruikname_kwartalen", n, "kwartalen", date(jaar, 12, 31), "vlpar-sv-979-2025-wzc", PF.format(2209176), "SV nr. 979 (2024-2025) Schryvers", "antwoord 1 (PDF p. 2)",
                          f"in {jaar} {n} kwartalen voor WZC en {cvk} voor CKV type 1", D_DOORL, GEC, date(2025, 10, 7), D_EB))
for jaar, n, nv in ((2020, 985, 25), (2021, 418, 16), (2022, 401, 19), (2023, 659, 17), (2024, 1137, 32)):
    BEVINDINGEN.append(_b(WZ, "kalender_uitstel_gevraagd_wzc", n, "woongelegenheden", date(jaar, 12, 31), "vlpar-sv-668-2025-wzc", PF.format(2168840), "SV nr. 668 (2024-2025) Vandecasteele", "antwoord a en b (PDF p. 2)",
                          f"In {jaar} vroegen {nv} woonzorgcentra uitstel op de goedgekeurde erkenningskalender voor {n} woongelegenheden",
                          "Woongelegenheden wzc waarvoor in het jaar uitstel van de erkenningskalender werd gevraagd (per jaar, niet cumulatief).", GEC, date(2025, 6, 12), D_EB,
                          "uitstel kon pas vanaf de omzendbrief van mei 2021; '2020' volgt de formulering van de bron" if jaar == 2020 else ""))

# ------------------------------------------------------------------------------------------------ buitengewoon onderwijs
RH, URH = "rekenhof-buo-2025", PF.format(2102664)
BEVINDINGEN += [
    _b(BU, "leerlingen_buo", 47468, "leerlingen", date(2019, 2, 1), RH, URH, "Rekenhof — Buitengewoon onderwijs: toegang en uitstroom (verslag september 2024, gepubliceerd januari 2025)", "PDF p. 35 (gedrukt p. 32), §2.2.2",
       "het aantal leerlingen in het buitengewoon onderwijs gestegen van 47.468 leerlingen in 2018-2019 tot 53.573 in 2022-2023. Dat is een stijging met 12,9 % in 4 jaar.", "Leerlingen buitengewoon basis- en secundair onderwijs, schooljaar 2018-2019 (Datawarehouse Leerplicht).", GEC, date(2025, 1, 9), D_EB,
       opm="peildatum 1 februari = projectconventie voor een schooljaar; de bron noemt enkel het schooljaar"),
    _b(BU, "leerlingen_buo", 53573, "leerlingen", date(2023, 2, 1), RH, URH, "Rekenhof — Buitengewoon onderwijs: toegang en uitstroom (verslag september 2024, gepubliceerd januari 2025)", "PDF p. 35 (gedrukt p. 32), §2.2.2",
       "… tot 53.573 in 2022-2023. Dat is een stijging met 12,9 % in 4 jaar.", "Idem, schooljaar 2022-2023.", GEC, date(2025, 1, 9), D_EB,
       opm="= 2.739 kleuter + 27.117 lager + 23.717 secundair (PDF p. 20); peildatum 1 februari = projectconventie; actuelere cijfers via Dataloep"),
    _b(BU, "tekort_plaatsen_2030_basis", 2184, "plaatsen", date(2030, 9, 1), "capaciteitsmonitor-2025", "https://hiva.kuleuven.be/sites/capaciteitsmonitor/docs/capaciteitsmonitor-rapport-27-augustus-2025.pdf", "Capaciteitsmonitor 2024 – Analyse van capaciteitsnoden en pendelbewegingen in Vlaanderen (BRISPO-VUB & HIVA-KU Leuven, mei 2025; gepubliceerd 27-08-2025)", "PDF p. 83-84, tabel 3.12",
       "Er wordt een tekort verwacht van 2184 plaatsen, of in relatieve termen 7,3% van het verwachte aanbod. … Basisonderwijs 32 098 29 914 -2 184 -7,3%",
       "Verwacht tekort aan plaatsen buitengewoon basisonderwijs in 2030-2031: vraagprognose (32.098) min aanbodprognose (29.914); % t.o.v. het verwachte aanbod.", GEC, date(2025, 8, 27), "Claude + 2e lezing EB (2026-10-01)",
       opm="tekort enkel in het buitengewoon lager onderwijs (tekst: 2 307 of 8,4 %; tabel: -8,6 %); VRT 27-08-2025 noemde het % foutief 'van totale vraag'"),
    _b(BU, "tekort_plaatsen_2030_secundair", 3731, "plaatsen", date(2030, 9, 1), "capaciteitsmonitor-2025", "https://hiva.kuleuven.be/sites/capaciteitsmonitor/docs/capaciteitsmonitor-rapport-27-augustus-2025.pdf", "Capaciteitsmonitor 2024 – Analyse van capaciteitsnoden en pendelbewegingen in Vlaanderen (BRISPO-VUB & HIVA-KU Leuven, mei 2025; gepubliceerd 27-08-2025)", "PDF p. 93-94, tabel 3.17",
       "In 2030-2031 wordt een tekort verwacht van 3 731 plaatsen, of 15,1% van het verwachte aanbod.",
       "Verwacht tekort aan plaatsen buitengewoon secundair onderwijs in 2030-2031 (tekstwaarde; tabel: vraagprognose 28.386 min aanbodprognose 24.654 = 3.732); % t.o.v. het verwachte aanbod.", GEC, date(2025, 8, 27), "Claude + 2e lezing EB (2026-10-01)",
       opm="tabel 3.17 geeft -3 732 (afronding); besluit (PDF p. 128) noemt 15,2 %; tekort in elke opleidingsvorm, grootst in OV4 (-1 635, -31,8 %)"),
    _b(BU, "lop_antwerpen_zonder_plaats", 680, "kinderen", date(2026, 5, 18), "vlpar-sv-829-2026-buo", PF.format(2353372), "SV nr. 829 (2025-2026) D'Hose — vraagtekst (LOP Antwerpen / VRT)", "vraag",
       "In totaal staan volgens dezelfde berichtgeving 680 kinderen op een wachtlijst voor het buitengewoon onderwijs in Antwerpen, goed voor ongeveer 66 procent van de aanmeldingen.", "Aangemelde kinderen zonder toegewezen plaats in het buitengewoon basisonderwijs, LOP Antwerpen, aanmeldingen 2026-2027.", ONG, date(2026, 7, 15), opm="secundair (vraagtekst, VRT); LOP-rapport zelf nog op te vragen"),
    _b(BU, "lop_gent_pct_geen_voorkeurschool", 58, "procent", date(2026, 5, 18), "vlpar-sv-829-2026-buo", PF.format(2353372), "SV nr. 829 (2025-2026) D'Hose", "antwoord 2a",
       "In totaal vond 58% van de leerlingen geen plaats in de school van voorkeur via het aanmeldingssysteem. Vooral in type 2 en type 4 is dit aandeel het grootst.", "Aandeel aangemelde leerlingen zonder plaats in de school van voorkeur, buitengewoon basisonderwijs samenwerkingsverband LOP Gent (Beveren-Kruibeke-Zwijndrecht, Dendermonde, Gent, Lokeren, Sint-Niklaas, Zele); schooljaar 2026-2027 afgeleid uit de vraag.", GEC, date(2026, 7, 15), D_EB, opm="peildatum = datum van de vraag; het antwoord dateert de resultaten niet"),
    _b(BU, "lop_aalst_pct_geen_voorkeurschool", 70, "procent", date(2026, 5, 18), "vlpar-sv-829-2026-buo", PF.format(2353372), "SV nr. 829 (2025-2026) D'Hose", "antwoord 2b",
       "In totaal vond 70% van de leerlingen geen plaats in de school van voorkeur via het aanmeldingssysteem. De grootste tekorten zitten bij type 2 en type 9.", "Idem, LOP Aalst (Aalst en Erpe-Mere).", GEC, date(2026, 7, 15), D_EB, opm="peildatum = datum van de vraag"),
    _b(BU, "ov1_limburg_21plus", 117, "leerlingen", date(2025, 2, 1), "vlpar-sv-1019-2026-buo", PF.format(2366058), "SV nr. 1019 (2025-2026) Peeters", "antwoord 11",
       "In het schooljaar 2024-2025 schreven 117 leerlingen van 21 jaar of ouder zich in Limburg in opleidingsvorm 1 (OV1) van het buitengewoon secundair onderwijs in.", "Leerlingen ≥ 21 jaar in OV1 buso Limburg, schooljaar 2024-2025.", GEC, date(2026, 9, 28), D_EB,
       opm="eigen duiding: mogelijke indicator voor ontbrekende vervolgcapaciteit in zorg/dagopvang (de minister legt dat verband niet); peildatum 1 februari = projectconventie"),
]

# ------------------------------------------------------------------------------------------------ sociale koop
for jaar, n in ((2014, 867), (2015, 775), (2016, 860), (2017, 960), (2018, 1053), (2019, 825), (2020, 569), (2021, 735), (2022, 665), (2023, 505)):
    BEVINDINGEN.append(_b(SK, "verkochte_sociale_koopwoningen_nieuw", n, "woningen", date(jaar, 12, 31), "vlpar-sv-448-2025-koop", PF.format(2161755), "SV nr. 448 (2024-2025) Mertens — bijlage 1", "tabblad 'vraag 7', rij 'Aantal verkochte sociale koopwoningen (nieuw)'",
                          f"Aantal verkochte sociale koopwoningen (nieuw) {jaar}: {n}", "Nieuwe sociale koopwoningen (eerste ingebruikname, via nieuwbouw of renovatie) verkocht door de woonmaatschappijen in het jaar; excl. middelgrote koopwoningen en wederinkoop.", GEC, date(2025, 6, 11), D_EB))


def _bu(vid, jaar, fase, niveau, bedrag, bron_id, url, titel, pagina, passage, status, door="", krediet=Kredietsoort.NVT, artikel="", programma="", ise="", label="", opm=""):
    key = artikel or label.replace(" ", "_")[:40]
    return Budget(budget_id=f"{vid}:{jaar}:{fase.value}:{niveau}:{krediet.value}:{key}", voorziening_id=vid, begrotingsjaar=jaar, fase=fase, niveau=niveau, bedrag_eur=bedrag,
                  kredietsoort=krediet, artikel_code=artikel, programma=programma, ise=ise, label=label, bron_id=bron_id, bron_url=url, documenttitel=titel, pagina=pagina,
                  passage=passage, controlestatus=status, gecontroleerd_door=door, gecontroleerd_op=VANDAAG if door else None, opmerking=opm)


B, VAK, VEK = Budgetfase, Kredietsoort.VAK, Kredietsoort.VEK
ISE_SE = "ACTIVERING (SOCIALE ECONOMIE)"
BUDGETTEN = [
    _bu(CM, 2022, B.UITV, "dept_artikel", 466_727_000, "vlpar-bbt-wse-uitv-2022", PF.format(1955127), "BBT Werk en Sociale Economie, begrotingsuitvoering 2022 — 23-G", "artikel JB0-1JEB2HA-WT",
        "2022 2e BA 430.697 / 2e BA-JR 470.358 / BU 466.727 (VAK = VEK)", GEL, A, VAK, "JB0-1JEB2HA-WT", "JE", ISE_SE, "Collectief Maatwerk (uitvoering)"),
    _bu(CM, 2023, B.UITV, "dept_artikel", 526_727_000, "vlpar-bbt-wse-uitv-2023", PF.format(2063726), "BBT Werk en Sociale Economie, begrotingsuitvoering 2023 — 23-G", "artikel JB0-1JEB2HA-WT",
        "2023 1e BA 537.344 / 1e BA-JR 538.713 / BU 526.727 VAK (VEK 526.778)", GEL, A, VAK, "JB0-1JEB2HA-WT", "JE", ISE_SE, "Collectief Maatwerk (uitvoering)"),
    _bu(CM, 2024, B.UITV, "dept_artikel", 552_289_000, "vlpar-bbt-se-uitv-2024", PF.format(2162520), "BBT Sociale Economie, begrotingsuitvoering 2024 — 23-K", "artikel JB0-1JEC2HA-WT",
        "BA 2024 580.966 / BA-JR 2024 588.293 / BU 2024 552.289 VAK (VEK 552.157); uitvoering 93,9 % van het beschikbare VAK", GEL, A, VAK, "JB0-1JEC2HA-WT", "JE", ISE_SE, "Collectief Maatwerk (uitvoering)"),
    _bu(CM, 2025, B.BA, "dept_artikel", 598_220_000, "vlpar-bbt-se-uitv-2025", PF.format(2325109), "BBT Sociale Economie, begrotingsuitvoering 2025 — 23-J", "p. 12-13, artikel TB0-1THC2UA-WT",
        "BA 2025 598.220 VAK / 568.220 VEK (VEK eenmalig −30.000 keuro om het begrotingstekort in 2025 onder controle te houden)", GEL, A, VAK, "TB0-1THC2UA-WT", "TH", ISE_SE, "Collectief Maatwerk"),
    _bu(CM, 2025, B.UITV, "dept_artikel", 572_517_000, "vlpar-bbt-se-uitv-2025", PF.format(2325109), "BBT Sociale Economie, begrotingsuitvoering 2025 — 23-J", "p. 12-13, artikel TB0-1THC2UA-WT",
        "Uitgaven BA 2025 598.220 / BA-JR 2025 607.401 / BU 2025 572.517 VAK; VEK 568.220 / 577.401 / 572.517; uitvoering 94,3 % VAK, 99,2 % VEK", GEL, A, VAK, "TB0-1THC2UA-WT", "TH", ISE_SE, "Collectief Maatwerk (uitvoering)"),
    _bu(CM, 2026, B.BO, "dept_artikel", 600_665_000, "vlpar-bbt-se-2026", PF.format(2226293), "BBT Sociale Economie, begroting 2026 — 13-J", "p. 14-16, artikel TB0-1THC2UA-WT",
        "BA 2025 598.220 / Index 11.433 / Compensaties −1.174 / Andere bijstellingen −7.814 (VEK +22.186) / BO 2026 600.665 (VAK = VEK); punctuele maatregel −3.000 (geen automatische contingentherverdeling per 1-10-2025), actualisatie kredietbehoefte −4.814", GEL, A, VAK, "TB0-1THC2UA-WT", "TH", ISE_SE, "Collectief Maatwerk"),
    _bu(CM, 2026, B.BO, "ise_totaal", 756_844_000, "vlpar-bbt-se-2026", PF.format(2226293), "BBT Sociale Economie, begroting 2026 — 13-J", "p. 12-13",
        "ISE Activering (Sociale economie): BA 2025 710.352 / evolutie 46.492 / BO 2026 756.844 VAK (VEK 680.352 → 756.844)", GEL, A, VAK, "", "TH", ISE_SE, "ISE Activering (Sociale economie), totaal"),
    _bu(WZ, 2024, B.BELEID, "beleidsenveloppe", 2_777_000_000, "vlpar-sv-110-2024-wzc", PF.format(2113020), "SV nr. 110 (2024-2025) Vandecasteele", "antwoord 2",
        "Het budget 2024 voor residentiële ouderenzorg bedraagt 2,777 miljard euro. Het aantal vervallen dossiers in de periode 2020-2024 geven een gecumuleerde minderuitgave van -2,966 miljoen euro in 2024.", GEL, A, label="budget residentiële ouderenzorg (VSB)", opm="minderuitgave door vervallen kalenders: 2,966 mln (0,1 %)"),
    _bu(WZ, 2025, B.BA, "entiteit_begroting", 2_714_288_000, "vlpar-bbt-wvg-2026", PF.format(2227516), "BBT Welzijn en Armoedebestrijding 2026 — 13-Z (2025-2026)", "p. 117, artikel GM0-AGCF2VD-WT",
        "Werking en Toelagen – Sociale Bescherming – Residentiële ouderenzorg: BA 2025 2.714.288 / Index 54.259 / Andere bijstellingen −2.937 / BO 2026 2.765.610 (keuro, VAK)", GEL, A, VAK, "GM0-AGCF2VD-WT", "GC", "SOCIALE BESCHERMING", "residentiële ouderenzorg (VSB)"),
    _bu(WZ, 2026, B.BO, "entiteit_begroting", 2_765_610_000, "vlpar-bbt-wvg-2026", PF.format(2227516), "BBT Welzijn en Armoedebestrijding 2026 — 13-Z (2025-2026)", "p. 117, artikel GM0-AGCF2VD-WT",
        "BO 2026 2.765.610 keuro VAK", GEL, A, VAK, "GM0-AGCF2VD-WT", "GC", "SOCIALE BESCHERMING", "residentiële ouderenzorg (VSB)", opm="kredietenreeks zie kredieten.csv (parser)"),
]
for jaar, eur in ((2019, 386_122_060), (2020, 367_629_705), (2021, 403_092_727), (2022, 446_789_022), (2023, 502_975_281), (2024, 535_464_417), (2025, 560_540_971)):
    BUDGETTEN.append(_bu(CM, jaar, B.AGENTSCHAP, "realisatie", eur, "wewis-opendata-cmw03", "https://opendata.wewis.vlaanderen.be/explore/dataset/cmw03_product_v1/", "WEWIS open data CMW03", f"som cmw_subsidiebedrag {jaar}",
                         f"som van cmw_subsidiebedrag over alle vestigingen en kwartalen {jaar}: € {eur:,}".replace(",", "."), GEL, A, label="afgerekende subsidie collectief maatwerk (open data)", opm="eigen aggregatie; verschil met begrotingsartikel = o.a. VIA, overlopende rekening"))


def main() -> None:
    nb = upsert("bronnen", BRONNEN)
    _update_voorzieningen()
    nv = upsert("bevindingen", BEVINDINGEN)
    nu = upsert("budgetten", BUDGETTEN)
    print(f"vervolg: bronnen {nb}, bevindingen {nv}, budgetten {nu} (upsert); draai 'wachtlijst validate' en 'wachtlijst publish'")


if __name__ == "__main__":
    main()
