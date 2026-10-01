"""Aanvullende dossiers (ronde 3, 1-10-2026): inburgering maatschappelijke oriëntatie (AgII) en CGG-wachttijden.

Draai ná seed_proef.py en seed_opgroeien.py:  ``python scripts/seed_aanvullingen.py``  (upsert op sleutel).

Vervolgstappen uit docs/03-inventaris.md afgehandeld:
1. CIR-stand 31-12-2025 — al in curated (jaarverslag WiV 2025).
2. AgII jaarverslag 2024/2025 — gelezen: KPI wachtenden MO wordt sinds jaarverslag 2023 NIET meer gepubliceerd (zie hieronder).
3. Bijlage SV 379 (CGG) — Excel-bijlagen 379/382/645/107 gelezen; sectorgemiddelden zijn eigen berekening (ongewogen).
4. VAPH halfjaarverslag 2026 — nog niet online (extranet.vaph.be/jaarverslag/2026-eerste-jaarhelft geeft 404 op 1-10-2026).
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from wachtlijst.models import Bevinding, Bron, BronType, Budget, Budgetfase, Controlestatus, Kredietsoort, WachtlijstType  # noqa: E402
from wachtlijst.store import load, upsert  # noqa: E402

VANDAAG = date(2026, 10, 1)
GEC, GEL, ONG, BET = (Controlestatus.GECONTROLEERD, Controlestatus.BRON_GELEZEN, Controlestatus.ONGECONTROLEERD, Controlestatus.BETWIST)
A = "onderzoeksagent (2026-10-01)"
D_EB = "onderzoeksagent + 2e lezing Claude + EB (2026-10-01)"
PF ="https://docs.vlaamsparlement.be/files/pfile?id={}"

BRONNEN = [
    Bron(bron_id="agii-jaarverslag-2022", naam="AgII — jaarverslag 2022 (uitvoeringsrapportering)", organisatie="Agentschap Integratie en Inburgering",
         url="https://publicaties.vlaanderen.be/view-file/62947", bron_type=BronType.PDF, frequentie="jaarlijks", opmerking="30-03-2023; fig. 33 reeks 'geen passend aanbod' 2019-2022"),
    Bron(bron_id="agii-jaarverslag-2023", naam="AgII — jaarverslag 2023", organisatie="Agentschap Integratie en Inburgering",
         url="https://integratie-inburgering.be/sites/default/files/2024-06/AgII_Jaarverslag_2023.pdf", bron_type=BronType.PDF, frequentie="jaarlijks", opmerking="29-03-2024; laatste jaarverslag met wacht-KPI"),
    Bron(bron_id="agii-jaarverslag-2024", naam="AgII — jaarverslag 2024", organisatie="Agentschap Integratie en Inburgering",
         url="https://www.integratie-inburgering.be/sites/default/files/2025-05/AgII_Jaarverslag_2024_0.pdf", bron_type=BronType.PDF, frequentie="jaarlijks", opmerking="21-03-2025; GEEN wacht-KPI meer"),
    Bron(bron_id="agii-jaarverslag-2025", naam="AgII — jaarverslag 2025", organisatie="Agentschap Integratie en Inburgering",
         url="https://integratie-inburgering.be/sites/default/files/2026-05/AgII_jaarverslag_2025.pdf", bron_type=BronType.PDF, frequentie="jaarlijks", opmerking="26-03-2026; GEEN wacht-KPI"),
    Bron(bron_id="vlpar-commissie-c249-2025", naam="Commissie Binnenlands Bestuur en Inburgering 20-05-2025 — woordelijk verslag C249", organisatie="Vlaams Parlement",
         url=PF.format(2242860), bron_type=BronType.PDF, frequentie="eenmalig"),
    Bron(bron_id="vlpar-sv-275-2023", naam="SV nr. 275 (2022-2023), Janssens → min. Somers — wachtenden MO per reden", organisatie="Vlaams Parlement",
         url=PF.format(1956034), bron_type=BronType.PDF, frequentie="eenmalig"),
    Bron(bron_id="vrt-2025-05-07", naam="VRT NWS 07-05-2025 — inburgering: 1.500 nieuwkomers wachten langer dan 6 maanden", organisatie="VRT (secundair)",
         url="https://www.vrt.be/vrtnws/nl/2025/05/07/inburgeringscursus-integratie-nieuwkomers-vlaanderen-2024/", bron_type=BronType.HTML, frequentie="eenmalig"),
    Bron(bron_id="themis-bbt-ii-2026", naam="BBT Integratie en Inburgering, begroting 2026 (VR 2025 2410 MED.0428/1)", organisatie="Vlaamse Regering / Themis",
         url="https://themis.vlaanderen.be/files/d7fdef70-afff-11f0-9b44-3797f8128cc9/download", bron_type=BronType.PDF, frequentie="jaarlijks"),
    Bron(bron_id="vlpar-bbt-ii-uitv-2025", naam="BBT Integratie en Inburgering, begrotingsuitvoering 2025 — stuk 23-M (2025-2026) nr. 1", organisatie="Vlaams Parlement",
         url=PF.format(2325115), bron_type=BronType.PDF, frequentie="jaarlijks"),
    Bron(bron_id="vlpar-sv-379-2025", naam="SV nr. 379 (2024-2025), Mertens → min. Gennez — wachttijden CGG 2019-2023 (PDF + Excel-bijlage)", organisatie="Vlaams Parlement",
         url=PF.format(2138635), bron_type=BronType.PDF, frequentie="eenmalig", machinaal="Excel-bijlage pfile?id=2132648 (tabbladen per CGG × leeftijd × geslacht); bijlage-URL via ws.vlpar.be/e/opendata/schv/<id>",
         opmerking="gepubliceerd 08-04-2025; minister: wachtlijst niet centraal gemonitord (EPD pas vanaf eerste contact)"),
    Bron(bron_id="vlpar-sv-382-2025", naam="SV nr. 382 (2024-2025), Wouters — zorgperiodes en behandelduur CGG 2019-2023 (Excel-bijlage)", organisatie="Vlaams Parlement",
         url=PF.format(2140346), bron_type=BronType.PDF, frequentie="eenmalig", machinaal="Excel-bijlage pfile?id=2132652"),
    Bron(bron_id="vlpar-sv-645-2026", naam="SV nr. 645 (2025-2026), Wouters — CGG wachttijd, zorgperiodes, behandelduur 2024 (Excel-bijlage)", organisatie="Vlaams Parlement",
         url=PF.format(2308255), bron_type=BronType.PDF, frequentie="jaarlijks (reeks Wouters/Mertens feb-mrt)", machinaal="Excel-bijlage pfile?id=2307491", opmerking="gepubliceerd 08-05-2026; cijfers 2025 'nog niet beschikbaar'"),
    Bron(bron_id="vlpar-sv-107-2024", naam="SV nr. 107 (2023-2024), Vaneeckhout — enveloppes CGG 2010-2024 en wachttijden 2009-2022 (Excel-bijlage)", organisatie="Vlaams Parlement",
         url=PF.format(2015964), bron_type=BronType.PDF, frequentie="eenmalig", machinaal="Excel-bijlage pfile?id=2015915, tabblad 'Enveloppe per jaar'"),
    Bron(bron_id="zorgatlas-cgg", naam="Departement Zorg — cijfers CGG (ZorgAtlas Tableau-dashboard, EPD 2016-2024)", organisatie="Departement Zorg",
         url="https://www.departementzorg.be/nl/cijfers-centra-voor-geestelijke-gezondheidszorg", bron_type=BronType.DASHBOARD, frequentie="jaarlijks",
         machinaal="Tableau-embed zorgatlas.vlaanderen.be/views/CGG-Jaarverslag-OverzichtWEB/Welkom; geen Excel; sectorgemiddelde wachttijd enkel hier"),
]


def _update_voorzieningen() -> None:
    vz = {v.voorziening_id: v for v in load("voorzieningen")}
    a = vz["agii-mo"]
    a.scan_status = "proef_uitgewerkt"
    a.laatste_peildatum = date(2025, 5, 20)
    a.publicatie_bron_id = "agii-jaarverslag-2023"
    a.frequentie = "jaarverslag (KPI gestopt na 2023); parlement op vraag"
    a.wachtlijst_type = WachtlijstType.CENTRAAL_NIET_GEPUBLICEERD
    a.ise_koppeling = ""
    a.opmerking = ("Twee KPI's t/m jaarverslag 2023: 'geen passend aanbod' (2.592 in 2019 → 1.076 in 2022 → 1.229 in 2023) en '> 6 maanden na contract niet gestart' "
                   "(993 begin 2023 → 1.588 eind 2023 → 1.354 maart 2024). Jaarverslagen 2024 en 2025 bevatten GEEN wacht-KPI meer; daarna enkel VRT (± 1.500, mei 2025) "
                   "en minister (< 5 % van lopende trajecten, mei 2025). Werkingsgebied AgII excl. Atlas (Antwerpen) en IN-Gent. Budget: beleidsdomein Kanselarij/ABB, artikel SJ0-1SFC2DY-IS.")
    c = vz["zorg-cgg"]
    c.scan_status = "proef_uitgewerkt"
    c.laatste_peildatum = date(2024, 12, 31)
    c.publicatie_bron_id = "vlpar-sv-645-2026"
    c.frequentie = "jaarlijks via SV (Excel-bijlage), cijfers jaar N ± mei N+2; ZorgAtlas-dashboard"
    c.wachtlijst_type = WachtlijstType.CENTRAAL_NIET_GEPUBLICEERD
    c.ise_koppeling = "GESPECIALISEERDE ZORG"
    c.opmerking = ("Geen centrale wachtlijst (EPD pas vanaf eerste contact). Wel wachttijden in dagen: aanmelding → eerste direct contact (FTF1) en FTF1 → FTF2, per CGG × leeftijd × "
                   "geslacht in Excel-bijlagen bij SV's; geen officieel sectorgemiddelde buiten ZorgAtlas. Breuken: 2022 ZorgAtlas (telefonische contacten tellen mee), 2024 nieuwe leeftijdsgroepen (18-64/65+). "
                   "Budget: enveloppe CGG ± 93 mln (2024) binnen artikel GB0-1GCF2LA-WT (± 147 mln).")
    upsert("voorzieningen", [a, c])


def _b(vid, metriek, waarde, eenheid, peildatum, bron_id, url, titel, pagina, passage, definitie, status, pub=None, door="", opm=""):
    return Bevinding(bevinding_id=f"{vid}:{metriek}:{peildatum.isoformat()}", voorziening_id=vid, metriek=metriek, waarde=waarde, eenheid=eenheid, peildatum=peildatum,
                     bron_id=bron_id, bron_url=url, documenttitel=titel, pagina=pagina, passage=passage, definitie=definitie, publicatiedatum=pub,
                     controlestatus=status, gecontroleerd_door=door, gecontroleerd_op=VANDAAG if door else None, opmerking=opm)


AG, CG = "agii-mo", "zorg-cgg"
UJV22 = "https://publicaties.vlaanderen.be/view-file/62947"
UJV23 = "https://integratie-inburgering.be/sites/default/files/2024-06/AgII_Jaarverslag_2023.pdf"
DEF_GPA = "Inburgeraars met inburgeringscontract die niet ingeschreven zijn in een MO-cursus en wachten op een passend aanbod (locatie, lesmoment, taal, volzet); werkingsgebied AgII."
UJV24 = "https://www.integratie-inburgering.be/sites/default/files/2025-05/AgII_Jaarverslag_2024_0.pdf"
UJV25 = "https://integratie-inburgering.be/sites/default/files/2026-05/AgII_jaarverslag_2025.pdf"
DEF_EIC = "Eerste inburgeringscontracten in het jaar, werkingsgebied AgII."
DEF_MO = "Gestarte cursussen maatschappelijke oriëntatie in het jaar."
DEF_6M ="Inburgeraars die > 6 maanden na ondertekening van het inburgeringscontract nog niet gestart zijn met MO (ingeschreven + niet ingeschreven); > 6 maanden = 'geen aanvaardbare wachttijd'."

BEVINDINGEN = [
    # 2019-2021: datalabels uit grafiek fig. 33 (onregelmatige tijdas mei/19 … dec/22) -> peildatum benaderend, blijft bron_gelezen
    _b(AG, "wachtenden_geen_passend_aanbod", 2592, "personen", date(2019, 12, 31), "agii-jaarverslag-2022", UJV22, "AgII jaarverslag 2022 — uitvoeringsrapportering", "p. 19 (PDF p. 81), fig. 33",
       "vanaf het begin van de metingen in 2019 een blijvende daling van 2.592 naar 1.076 in 2022", DEF_GPA, GEL, date(2023, 3, 30), A, "peildatum benaderend (grafiek); datalabel ± december 2019"),
    _b(AG, "wachtenden_geen_passend_aanbod", 1646, "personen", date(2020, 12, 31), "agii-jaarverslag-2022", UJV22, "AgII jaarverslag 2022", "p. 19 (PDF p. 81), fig. 33",
       "fig. 33, datalabels: 2.592 · 1.646 · 1.313 · 1.076 (tijdas mei/19 … dec/22)", DEF_GPA, GEL, date(2023, 3, 30), A, "peildatum benaderend (grafiek); datalabel ± december 2020"),
    _b(AG, "wachtenden_geen_passend_aanbod", 1313, "personen", date(2021, 12, 31), "agii-jaarverslag-2022", UJV22, "AgII jaarverslag 2022", "p. 19 (PDF p. 81), fig. 33",
       "fig. 33, datalabels: 2.592 · 1.646 · 1.313 · 1.076 (tijdas mei/19 … dec/22)", DEF_GPA, GEL, date(2023, 3, 30), A, "peildatum benaderend (grafiek); datalabel vlak vóór 'feb/22', mogelijk januari 2022"),
    _b(AG, "wachtenden_geen_passend_aanbod", 1076, "personen", date(2023, 1, 6), "agii-jaarverslag-2022", UJV22, "AgII jaarverslag 2022", "p. 17 (PDF p. 79), fig. 29",
       "Op peildatum van 6 januari 2023 zijn er 23.333 lopende inburgeringstrajecten … Geen Passend Aanbod 1.076 5%", DEF_GPA, GEC, date(2023, 3, 30), D_EB, "= 5 % van 23.333 lopende trajecten"),
    _b(AG, "wachtenden_6_maanden", 993, "personen", date(2023, 1, 6), "agii-jaarverslag-2022", UJV22, "AgII jaarverslag 2022", "p. 17 (PDF p. 79)",
       "waren er 993 inburgeraars die niet binnen een redelijke termijn kunnen starten met MO, waarvan 570 niet ingeschreven zijn in een cursus en 423 ingeschreven", DEF_6M, GEC, date(2023, 3, 30), D_EB),
    _b(AG, "wachtenden_geen_passend_aanbod_min_3m", 632, "personen", date(2023, 4, 27), "vlpar-sv-275-2023", PF.format(1956034), "SV nr. 275 (2022-2023), Janssens → Somers", "antwoord, PDF p. 2-3, tabel 3",
       "Hieronder een tabel met het aantal personen dat minstens drie maanden geleden een inburgeringscontract ondertekende en op 27/4/2023 een status ‘geen passend aanbod’ … "
       "Tabel 3: Aantal personen met status ‘geen passend aanbod’ naar reden … GPA locatie 246 GPA lesmoment 196 GPA taal 135 GPA volzet 54 onbekend 1 totaal 632",
       "Inburgeraars die minstens 3 maanden geleden een inburgeringscontract tekenden en op de peildatum de status 'geen passend aanbod' hebben; deelverzameling, niet vergelijkbaar met de GPA-reeks.",
       GEC, date(2023, 6, 1), D_EB, "tabel 2 'onbeschikbaar' (304) + tabel 3 GPA (632) = 936"),
    _b(AG, "wachtenden_geen_passend_aanbod", 1229, "personen", date(2023, 12, 31), "agii-jaarverslag-2023", UJV23, "AgII jaarverslag 2023", "p. 9",
       "Er is (nog) geen passend cursusaanbod MO voor 1.229 inburgeraars. Dat zijn er 113 meer dan de vooropgezette target van 1.126", DEF_GPA, GEC, date(2024, 3, 29), D_EB, "doel < 1.126; peildatum niet vermeld (31/12 aangenomen)"),
    _b(AG, "wachtenden_6_maanden", 1588, "personen", date(2023, 12, 31), "agii-jaarverslag-2023", UJV23, "AgII jaarverslag 2023", "p. 9",
       "Er wachten 1.588 inburgeraars na ondertekening van het inburgeringscontract langer dan 6 maanden op de start van de lessen of een inschrijving in een cursus", DEF_6M, GEC, date(2024, 3, 29), D_EB,
       "891 ingeschreven + 697 niet ingeschreven; peildatum niet vermeld (31/12 aangenomen)"),
    _b(AG, "wachtenden_6_maanden", 1354, "personen", date(2024, 3, 31), "agii-jaarverslag-2023", UJV23, "AgII jaarverslag 2023", "p. 10",
       "Dat resulteerde in maart 2024 tot een daling van 1.588 naar 1.354", DEF_6M, GEC, date(2024, 3, 29), D_EB, "bron zegt enkel 'maart 2024'"),
    _b(AG, "wachtenden_6_maanden", 1500, "personen", date(2025, 5, 7), "vrt-2025-05-07", "https://www.vrt.be/vrtnws/nl/2025/05/07/inburgeringscursus-integratie-nieuwkomers-vlaanderen-2024/", "VRT NWS 07-05-2025", "artikeltekst",
       "Bij het Agentschap Integratie en Inburgering … wachten vandaag nog zo'n 1.500 nieuwkomers langer dan 6 maanden", DEF_6M, ONG, date(2025, 5, 7), "", "afgerond cijfer, secundair; herhaald door Janssens in commissie C249 (20-05-2025)"),
    _b(AG, "wachtenden_aandeel_lopende_trajecten_pct", 5.0, "procent (bovengrens)", date(2025, 5, 20), "vlpar-commissie-c249-2025", PF.format(2242860), "Commissie Binnenlands Bestuur en Inburgering 20-05-2025 (C249)", "p. 15, min. Crevits",
       "Het aantal inburgeraars dat wacht op een passend aanbod of dat langer dan zes maanden wacht op de start van het aanbod waarvoor ze zich inschreven, bedraagt minder dan 5 procent van alle lopende inburgeringstrajecten. … De verhouding tussen het aantal cursisten en het aantal cursusplaatsen is 0,96.",
       "Aandeel wachtenden (GPA + > 6 maanden) in de lopende inburgeringstrajecten; enkel als bovengrens meegedeeld.", GEC, date(2025, 5, 20), D_EB,
       "waarde = bovengrens '< 5 %'; peildatum = datum commissievergadering, referentiedatum van de data niet vermeld"),
    _b(AG, "eerste_inburgeringscontracten", 14526, "contracten", date(2022, 12, 31), "agii-jaarverslag-2022", UJV22, "AgII jaarverslag 2022", "p. 8 (PDF p. 70), fig. 11",
       "In het werkingsgebied van het AgII ondertekenden in 2022 14.526 nieuwkomers voor het eerst een inburgeringscontract.", DEF_EIC, GEC, date(2023, 3, 30), D_EB, "jaarverslag 2023 herneemt 2022 als 14.527"),
    _b(AG, "eerste_inburgeringscontracten", 17071, "contracten", date(2023, 12, 31), "agii-jaarverslag-2024", UJV24, "AgII jaarverslag 2024", "p. 44, fig. 12",
       "Werkingsgebied 2023 2024 Evolutie … Totaal 17.071 16.522 -3%", DEF_EIC, GEC, date(2025, 3, 21), D_EB, "jaarverslag 2023 (p. 9) gaf 17.078"),
    _b(AG, "eerste_inburgeringscontracten", 16522, "contracten", date(2024, 12, 31), "agii-jaarverslag-2024", UJV24, "AgII jaarverslag 2024", "p. 43",
       "In het werkingsgebied van AgII ondertekenden in 2024 16.522 inburgeraars voor het eerst een inburgeringscontract.", DEF_EIC, GEC, date(2025, 3, 21), D_EB, "jaarverslag 2025 herneemt 2024 als 16.525"),
    _b(AG, "eerste_inburgeringscontracten", 14815, "contracten", date(2025, 12, 31), "agii-jaarverslag-2025", UJV25, "AgII jaarverslag 2025", "p. 32",
       "In het werkingsgebied van AgII ondertekenden in 2025 14.815 inburgeraars voor het eerst een inburgeringscontract. Dat is een daling van -10% ten opzichte van 2024.", DEF_EIC, GEC, date(2026, 3, 26), D_EB),
    _b(AG, "gestarte_mo_cursussen", 880, "cursussen", date(2023, 12, 31), "agii-jaarverslag-2023", UJV23, "AgII jaarverslag 2023", "p. 68",
       "In 2023 startten 880 cursussen MO.", DEF_MO, GEC, date(2024, 3, 29), D_EB, "eerste MO-cursisten 2023: 12.206 (jaarverslag 2024 herneemt 12.182)"),
    _b(AG, "gestarte_mo_cursussen", 898, "cursussen", date(2024, 12, 31), "agii-jaarverslag-2024", UJV24, "AgII jaarverslag 2024", "p. 47",
       "In 2024 startten 898 cursussen maatschappelijke oriëntatie.", DEF_MO, GEC, date(2025, 3, 21), D_EB,
       "eerste MO-cursisten 2024: 13.163 (p. 47); 31.042 lopende contracten op 20-02-2025 (p. 45); jaarverslag 2025 herneemt 2024 als 900 cursussen / 13.055 cursisten"),
    _b(AG, "gestarte_mo_cursussen", 929, "cursussen", date(2025, 12, 31), "agii-jaarverslag-2025", UJV25, "AgII jaarverslag 2025", "p. 34",
       "In 2025 startten 929 cursussen maatschappelijke oriëntatie. Dit betekent een stijging van 3% t.o.v. 2024.", DEF_MO, GEC, date(2026, 3, 26), D_EB, "eerste MO-cursisten 2025: 12.928"),
]

# --- CGG: wachttijden (dagen). Sectorwaarden = ONGEWOGEN gemiddelde over CGG × geslacht uit de Excel-bijlagen (eigen berekening) -> ongecontroleerd.
DEF_W1 = "Gemiddeld aantal dagen tussen aanmelding en eerste direct cliëntencontact (FTF1), per registratiejaar; ongewogen gemiddelde over CGG × geslacht (eigen berekening uit de Excel-bijlage)."
DEF_W2 = "Gemiddeld aantal dagen tussen eerste (FTF1) en tweede (FTF2) direct cliëntencontact; ongewogen gemiddelde over CGG × geslacht (eigen berekening)."
U379X = PF.format(2132648)
U645X = PF.format(2307491)
for jaar, (k, v, o) in zip(range(2019, 2024), ((56.2, 45.5, 30.8), (59.5, 49.9, 34.6), (63.5, 46.8, 29.5), (48.0, 37.3, 26.2), (42.2, 36.9, 27.6))):
    for m, val, lab in (("wachttijd_ftf1_0_17_dagen", k, "0-17 jaar"), ("wachttijd_ftf1_18_59_dagen", v, "18-59 jaar"), ("wachttijd_ftf1_60plus_dagen", o, "60+")):
        BEVINDINGEN.append(_b(CG, m, val, "dagen", date(jaar, 12, 31), "vlpar-sv-379-2025", U379X, "SV nr. 379 — Excel-bijlage wachttijden CGG", "tabblad 'wachtijd tot eerste FTF'",
                              f"ongewogen gemiddelde {lab} {jaar} over alle CGG × geslacht: {val} dagen", DEF_W1, ONG, date(2025, 4, 8), "", "eigen berekening; officieel sectorgemiddelde enkel in ZorgAtlas"))
for jaar, (k, v, o) in zip(range(2019, 2024), ((63.3, 60.9, 45.7), (70.3, 69.0, 45.3), (62.9, 61.9, 46.0), (58.2, 48.5, 37.0), (57.8, 48.4, 37.1))):
    for m, val, lab in (("wachttijd_ftf2_0_17_dagen", k, "0-17 jaar"), ("wachttijd_ftf2_18_59_dagen", v, "18-59 jaar"), ("wachttijd_ftf2_60plus_dagen", o, "60+")):
        BEVINDINGEN.append(_b(CG, m, val, "dagen", date(jaar, 12, 31), "vlpar-sv-379-2025", U379X, "SV nr. 379 — Excel-bijlage wachttijden CGG", "tabblad 'wachttijd FTF1 en FTF2'",
                              f"ongewogen gemiddelde {lab} {jaar}: {val} dagen", DEF_W2, ONG, date(2025, 4, 8), "", "eigen berekening"))
for m, val, lab in (("wachttijd_ftf1_0_17_dagen", 42.0, "jongeren 0-17"), ("wachttijd_ftf1_18_64_dagen", 37.0, "volwassenen 18-64"), ("wachttijd_ftf1_65plus_dagen", 25.3, "ouderen 65+")):
    BEVINDINGEN.append(_b(CG, m, val, "dagen", date(2024, 12, 31), "vlpar-sv-645-2026", U645X, "SV nr. 645 — Excel-bijlage CGG 2024", "tabblad 'wachttijd tot FTF1'",
                          f"ongewogen gemiddelde {lab} 2024 over 17 CGG: {val} dagen (bv. F1 jongeren M 31,0 / V 33,8; F7 81,1 / 68,7)", DEF_W1 + " Leeftijdsgroepen gewijzigd in 2024 (18-64 / 65+).", ONG, date(2026, 5, 8), "", "eigen berekening; cijfers 2025 nog niet beschikbaar"))
# CGG: officiële totalen
for jaar, m, v, kol in ((2019, 24239, 29611, "C+D"), (2020, 21250, 26991, "E+F"), (2021, 21999, 28573, "G+H"), (2022, 24931, 33272, "I+J"), (2023, 24381, 32460, "K+L")):
    fusie = {2022: "F19 gestopt wegens fusie (vanaf 2022); ", 2023: "F17 en F19 gestopt wegens fusie; "}.get(jaar, "")
    BEVINDINGEN.append(_b(CG, "zorgperiodes_actief", m + v, "zorgperiodes", date(jaar, 12, 31), "vlpar-sv-382-2025", PF.format(2132652), "SV nr. 382 — Excel-bijlage zorgperiodes CGG (antw.382.bijl.1.xlsx)",
                          f"tabblad 'Zorgperiodes', rij 68 (Totaal), kolommen {kol}", f"Totaal – Registratie in {jaar}: MANNEN {m} VROUWEN {v}",
                          "Actieve zorgperiodes (hoofdcliënten) in het registratiejaar; één zorggebruiker kan meerdere zorgperiodes hebben (SV 382, antwoord p. 2).", GEC, date(2025, 4, 8), D_EB,
                          f"{fusie}afgeleid: som mannen + vrouwen"))
BEVINDINGEN += [
    _b(CG, "zorgperiodes_actief", 57370, "zorgperiodes", date(2024, 12, 31), "vlpar-sv-645-2026", U645X, "SV nr. 645 — Excel-bijlage CGG 2024", "tabblad 'aantal zorgperiodes'",
       "som over 17 CGG: 57.370 (0-17: 12.575; 18-64: 40.929; 65+: 3.866)", "Actieve zorgperiodes in 2024 (eigen optelling, geen Totaal-rij).", ONG, date(2026, 5, 8), "", "eigen optelling"),
    _b(CG, "unieke_zorggebruikers", 55202, "personen", date(2024, 12, 31), "vlpar-bbt-wvg-2026", PF.format(2227516), "BBT Welzijn en Armoedebestrijding 2026 — 13-Z (2025-2026)", "p. 91 (indicator p. 90)",
       "CGG: • Aantal unieke zorggebruikers 2024: 55202 • Aantal doorgegane activiteiten 2024: 474220", "Unieke zorggebruikers CGG in het jaar (prestatie-indicator BBT; geen streefwaarde, geen wachttijdindicator).", GEC, date(2025, 10, 24), D_EB,
       "indicator 'Gebruik van het aanbod ambulante gespecialiseerde geestelijke gezondheidszorg binnen de Centra voor ambulante Revalidatie (CAR) en Centra voor geestelijke gezondheidszorg (CGG)'; "
       "voorblad zegt 'ingediend op 24 oktober 2024' (vermoedelijk tikfout voor 2025)"),
    _b(CG, "vte_enveloppe", 891, "VTE", date(2024, 12, 31), "vlpar-sv-379-2025", U379X, "SV nr. 379 — Excel-bijlage", "tabblad 'vraag 6 VTE'", "som 20 CGG 2024: 891 VTE (2020: 811; 2021: 813; 2022: 864; 2023: 886)", "Enveloppe-personeel CGG in VTE (eigen optelling).", ONG, date(2025, 4, 8), "", "eigen optelling"),
]


def _bu(vid, jaar, fase, niveau, bedrag, bron_id, url, titel, pagina, passage, status, door="", krediet=Kredietsoort.NVT, artikel="", programma="", ise="", label="", opm=""):
    key = artikel or label.replace(" ", "_")[:40]
    return Budget(budget_id=f"{vid}:{jaar}:{fase.value}:{niveau}:{krediet.value}:{key}", voorziening_id=vid, begrotingsjaar=jaar, fase=fase, niveau=niveau, bedrag_eur=bedrag,
                  kredietsoort=krediet, artikel_code=artikel, programma=programma, ise=ise, label=label, bron_id=bron_id, bron_url=url, documenttitel=titel, pagina=pagina,
                  passage=passage, controlestatus=status, gecontroleerd_door=door, gecontroleerd_op=VANDAAG if door else None, opmerking=opm)


B = Budgetfase
UTH = "https://themis.vlaanderen.be/files/d7fdef70-afff-11f0-9b44-3797f8128cc9/download"
BUDGETTEN = [
    _bu(AG, 2025, B.BA, "dept_artikel", 63_617_000, "themis-bbt-ii-2026", UTH, "BBT Integratie en Inburgering, begroting 2026", "p. 21-25", "SJ0-1SFC2DY-IS structurele financiering van het Agentschap Integratie en Inburgering: BA 2025 63.617 → BO 2026 64.611 (k€)", GEL, A,
        krediet=Kredietsoort.VAK, artikel="SJ0-1SFC2DY-IS", programma="SF", label="dotatie AgII"),
    _bu(AG, 2026, B.BO, "dept_artikel", 64_611_000, "themis-bbt-ii-2026", UTH, "BBT Integratie en Inburgering, begroting 2026", "p. 21-25", "BO 2026 64.611 (index +999, compensatie −5)", GEL, A, krediet=Kredietsoort.VAK, artikel="SJ0-1SFC2DY-IS", programma="SF", label="dotatie AgII"),
    _bu(AG, 2025, B.UITV, "dept_artikel", 81_126_000, "vlpar-bbt-ii-uitv-2025", PF.format(2325115), "BBT Integratie en Inburgering, begrotingsuitvoering 2025 — 23-M (2025-2026)", "tabel SJ0-1SFC2DY-IS",
        "BA-JR 81.181 VAK / 73.369 VEK; BU 81.126 VAK / 71.950 VEK (herverdelingen o.a. +3.845 turbo, +2.422 decreetwijzigingen, +919 Noodfonds Oekraïne)", GEL, A, krediet=Kredietsoort.VAK, artikel="SJ0-1SFC2DY-IS", programma="SF", label="dotatie AgII (uitvoering)"),
    _bu(AG, 2026, B.BO, "dept_artikel", 51_033_000, "themis-bbt-ii-2026", UTH, "BBT Integratie en Inburgering, begroting 2026", "p. 21-25",
        "SJ0-1SFC2DA-WT uitbouw Vlaams integratie- en inburgeringsbeleid (o.a. subsidies Atlas, IN-Gent, Huis van het Nederlands Brussel): BA 2025 56.528 → BO 2026 51.033 (Turboplan −10.000; generieke besparing −2.817)", GEL, A,
        krediet=Kredietsoort.VAK, artikel="SJ0-1SFC2DA-WT", programma="SF", label="subsidies stedelijke agentschappen e.a."),
    _bu(CG, 2026, B.BO, "dept_artikel", 146_731_000, "vlpar-bbt-wvg-2026", PF.format(2227516), "BBT Welzijn en Armoedebestrijding 2026 — 13-Z (2025-2026)", "p. 100-102",
        "GB0-1GCF2LA-WT Beleid over ziekenhuizen en geestelijke gezondheidszorg: BA 2025 VAK 143.027 / VEK 142.027 → BO 2026 146.731 / 146.731 (index +2.746, compensaties +1.458)", GEL, A,
        krediet=Kredietsoort.VAK, artikel="GB0-1GCF2LA-WT", programma="GC", ise="GESPECIALISEERDE ZORG", label="ziekenhuizen en GGZ (bevat subsidie CGG, OPZ, Psyche, Tandem, …)", opm="CGG-aandeel ± 93 mln niet afgesplitst"),
]
for jaar, eur in ((2019, 71_768_057), (2020, 70_835_072), (2021, 72_110_103), (2022, 78_294_485), (2023, 92_186_781), (2024, 93_007_246)):
    BUDGETTEN.append(_bu(CG, jaar, B.AGENTSCHAP, "realisatie", eur, "vlpar-sv-107-2024", PF.format(2015915), "SV nr. 107 — Excel-bijlage enveloppes CGG", "tabblad 'Enveloppe per jaar', rij Totaal",
                         f"voorlopige enveloppe-subsidie CGG sectortotaal {jaar}: € {eur:,}".replace(",", "."), GEL, A, label="enveloppe-subsidie CGG (sectortotaal)", opm="2025: 'nog niet beschikbaar' (SV 247, maart 2025)"))


def main() -> None:
    nb = upsert("bronnen", BRONNEN)
    _update_voorzieningen()
    nv = upsert("bevindingen", BEVINDINGEN)
    nu = upsert("budgetten", BUDGETTEN)
    print(f"aanvullingen: bronnen {nb}, bevindingen {nv}, budgetten {nu} (upsert); draai 'wachtlijst validate' en 'wachtlijst publish'")


if __name__ == "__main__":
    main()
