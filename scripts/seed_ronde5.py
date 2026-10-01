"""Ronde 5 (1-10-2026): de vijf resterende voorzieningen uit de inventaris (gezinszorg, COS, NT2, pleegzorg, justitiehuizen) en zes
nieuwe voorzieningen (PAB minderjarigen als eigen dossier, VAPH RTH/hulpmiddelen, CAR, CAW/verslavingszorg, forensische zorg,
art. 60/wijk-werken) plus de kostprijs van de VAPH-wachtlijst (SV 1010).

Draai ná seed_vervolg.py:  ``python scripts/seed_ronde5.py``  (upsert op sleutel).

Samenvatting:
- Gezinszorg: geen wachtlijst, rantsoenering via het jaarlijkse urencontingent per dienst (MB); 2022: contingent 18,86 mln uur, gepresteerd
  15,95 mln uur, 126.570 gezinnen. Realisatie van het contingent pas gekend in jaar X+1 (saldering). Onderbenutting door personeelskrapte.
- COS: "geen centrale, uniforme registratie van wachtenden" (SV 633, 2022) en "geen cijfers m.b.t. de wachtlijsten beschikbaar" (SV 504, 2025);
  wachttijden per COS 12-34 maanden (2020-2021); trajecten 0-6 j ± 4.400 kinderen/jaar (2022-2024). CAR: "geen gevalideerde cijfers" (SV 234).
- NT2: aanbodbevraging NT2 van Ahovoks (2× per jaar): september 2025 geen cursisten met intake op een wachtlijst bij CBE of CVO → afgerond.
- Pleegzorg: wachtenden op een pleeggezin (perspectiefzoekend/-biedend) 702 (2018) → 1.307 (2024), +86 %; SV-reeks Schryvers; 10.676
  pleegzorgsituaties (31-12-2024).
- Justitiehuizen: wachttijd ontvangst werkstrafdossier → aanstelling justitieassistent 49 d (jan 2023) → 22-23 d (2024-2026); aanstelling →
  effectieve opstart 126 d (2024), 121 d (2025); daders in begeleiding 17.206 (2019) → 24.430 (2025).
- PAB minderjarigen: wachtenden 1.478 (2022) → 1.763 (2024, Opgroeien) / 1.958 (VAPH-telling incl. priors, 84,4 mln benodigd) → +39 % in 2025;
  nieuwe vragen 540 → 1.074 (2022-2025); 372 PAB's toegekend in 2025 (13,3 mln); 2.554 budgethouders (31-12-2025).
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from wachtlijst.models import Bevinding, Bevoegdheid, Bron, BronType, Budget, Budgetfase, Controlestatus, Kredietsoort, Voorziening, WachtlijstType  # noqa: E402
from wachtlijst.store import load, upsert  # noqa: E402

VANDAAG = date(2026, 10, 1)
GEC, GEL, ONG, BET = (Controlestatus.GECONTROLEERD, Controlestatus.BRON_GELEZEN, Controlestatus.ONGECONTROLEERD, Controlestatus.BETWIST)
A = "onderzoeksagent (2026-10-01)"
PF = "https://docs.vlaamsparlement.be/files/pfile?id={}"
GZ, COS, NT2, PZ, JH = "zorg-gezinszorg", "zorg-cos", "nt2", "opgroeien-pleegzorg", "ajh-justitiehuizen"
PAB, RTH, CAR, CAW, FOR, A60, PVB = "vaph-pab-minderjarigen", "vaph-rth-hulpmiddelen", "zorg-car", "zorg-caw-verslavingszorg", "zorg-forensisch", "dwse-art60-wijkwerken", "vaph-pvb"
GEM, GEW = Bevoegdheid.GEMEENSCHAP, Bevoegdheid.GEWEST
W = WachtlijstType

BRONNEN = [
    Bron(bron_id="vlpar-sv-950-2023-gz", naam="SV nr. 950 (2022-2023), Schryvers → min. Crevits — gezinszorg, stand van zaken (uren, gebruikers, urencontingent 2022)",
         organisatie="Vlaams Parlement", url=PF.format(1992606), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 20-10-2023; tabel gepresteerde uren en gebruikers 2018-2022 (Vesta)"),
    Bron(bron_id="vlpar-sv-630-2025-gz", naam="SV nr. 630 (2024-2025), Lachaert → min. Gennez — gezinshulp, urencontingent (+ bijlage realisatie 2022-2023 per dienst)",
         organisatie="Vlaams Parlement", url=PF.format(2165610), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 03-06-2025; 104 diensten (2022-2023), 103 (2024); inkanteling in VSB aangekondigd"),
    Bron(bron_id="vlpar-sv-293-2026-gz", naam="SV nr. 293 (2025-2026), Smeyers → min. Gennez — urencontingent gezinszorg, afwijking voor onderbenutting",
         organisatie="Vlaams Parlement", url=PF.format(2266704), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 05-02-2026; redenen onderbenutting: corona, personeelskrapte, verminderde vraag"),
    Bron(bron_id="vlpar-sv-633-2022-cos", naam="SV nr. 633 (2021-2022), Wouters → min. Beke — COS, optimalisering en wachttijden (tabel feb 2020 / dec 2021)",
         organisatie="Vlaams Parlement", url=PF.format(1861756), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 29-07-2022; 'geen centrale, uniforme registratie van wachtenden'"),
    Bron(bron_id="vlpar-sv-504-2025-cos", naam="SV nr. 504 (2024-2025), Claesen → min. Crevits — COS, registratie en wachttijden",
         organisatie="Vlaams Parlement", url=PF.format(2150944), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 08-05-2025; 'Er zijn geen cijfers m.b.t. de wachtlijsten beschikbaar'; projectmiddelen brugzorg t/m 2025"),
    Bron(bron_id="vlpar-sv-1007-2025-cos", naam="SV nr. 1007 (2024-2025), Vandromme → min. Crevits — ontwikkelingsstoornissen, diagnose en diagnosecentra (trajecten COS 2022-2024)",
         organisatie="Vlaams Parlement", url=PF.format(2216493), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 17-10-2025"),
    Bron(bron_id="vlpar-sv-234-2026-car", naam="SV nr. 234 (2025-2026), Vaneeckhout → min. Crevits — CAR, wachtlijsten en terugbetaling",
         organisatie="Vlaams Parlement", url=PF.format(2261493), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 29-01-2026; 'geen gevalideerde cijfers over de wachttijden bij de CAR'; CAR-CGG-hervormingstraject"),
    Bron(bron_id="vlpar-sv-34-2025-nt2", naam="SV nr. 34 (2025-2026), Tombeur → min. Demir — NT2, opleidingsaanbod (aanbodbevraging NT2 Ahovoks)",
         organisatie="Vlaams Parlement", url=PF.format(2237755), bron_type=BronType.PDF, frequentie="eenmalig", machinaal="cursistenaantallen NT2 via Dataloep (onderwijs.vlaanderen.be)",
         opmerking="gepubliceerd 05-12-2025; aanbodbevraging NT2 twee keer per jaar (CBE en CVO)"),
    Bron(bron_id="vlpar-sv-203-2025-pz", naam="SV nr. 203 (2024-2025), Schryvers → min. Crevits — pleegzorg, wachtlijsten (2): wachtenden 2018-2022 per provincie en leeftijd",
         organisatie="Vlaams Parlement", url=PF.format(2119342), bron_type=BronType.PDF, frequentie="jaarlijks (reeks Schryvers)", opmerking="gepubliceerd 28-02-2025; cijfers Domino, enkel NRTJ-pleegzorg (niet ondersteunende pleegzorg)"),
    Bron(bron_id="vlpar-sv-75-2024-pz", naam="SV nr. 75 (2024-2025), Schryvers → min. Crevits — pleegzorg, wachtlijsten: 2023",
         organisatie="Vlaams Parlement", url=PF.format(2099807), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 15-01-2025"),
    Bron(bron_id="vlpar-sv-194-2026-pz", naam="SV nr. 194 (2025-2026), Schryvers → min. Crevits — pleegzorg, wachtlijsten (2): 31-12-2024 en pleegzorgsituaties",
         organisatie="Vlaams Parlement", url=PF.format(2253598), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 15-01-2026; SV 789 (jul 2025) en 1003 (sep 2025): cijfers 2024 toen 'niet beschikbaar'"),
    Bron(bron_id="vlpar-sv-348-2023-jh", naam="SV nr. 348 (2022-2023), Schryvers → min. Demir — uitvoering werkstraffen, wachttijden (jan 2023)",
         organisatie="Vlaams Parlement", url=PF.format(1924206), bron_type=BronType.PDF, frequentie="jaarlijks (reeks Schryvers)", opmerking="gepubliceerd 07-03-2023"),
    Bron(bron_id="vlpar-sv-212-2024-jh", naam="SV nr. 212 (2023-2024), Schryvers → min. Demir — uitvoering werkstraffen, wachttijden (2023 per justitiehuis)",
         organisatie="Vlaams Parlement", url=PF.format(2043114), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 26-03-2024"),
    Bron(bron_id="vlpar-sv-369-2025-jh", naam="SV nr. 369 (2024-2025), Schryvers → min. Demir — uitvoering werkstraffen, wachttijden (dec 2024; opstart 2024)",
         organisatie="Vlaams Parlement", url=PF.format(2146400), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 15-04-2025"),
    Bron(bron_id="vlpar-sv-386-2026-jh", naam="SV nr. 386 (2025-2026), Schryvers → min. Demir — uitvoering werkstraffen, wachttijden (jan 2026; opstart 2025)",
         organisatie="Vlaams Parlement", url=PF.format(2291166), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 09-03-2026"),
    Bron(bron_id="vlpar-bbt-jh-2026", naam="BBT Justitie en Handhaving, begroting 2026 — stuk 13-S (2025-2026) nr. 1", organisatie="Vlaams Parlement",
         url=PF.format(2227488), bron_type=BronType.PDF, frequentie="jaarlijks", opmerking="ingediend 09-12-2025; OD 2.2 daders in begeleiding; artikelen SL0-1SDE2JA-WT (ET-kosten), SL0-1SAE2ZZ-LO (lonen AJH)"),
    Bron(bron_id="vlpar-sv-36-2025-pab", naam="SV nr. 36 (2025-2026), Kasmi → min. Crevits — PAB voor minderjarigen, transparantie (vindplaatsen cijfers)",
         organisatie="Vlaams Parlement", url=PF.format(2226506), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 14-11-2025; wachtenden: Opgroeien-rapport (foto 31/12, INSISTO); budgethouders en toekenningen: VAPH-jaarverslag"),
    Bron(bron_id="vlpar-sv-305-2026-pab", naam="SV nr. 305 (2025-2026), Dillen → min. Crevits — PAB's en MFC's, uitbreidingsbeleid 2025",
         organisatie="Vlaams Parlement", url=PF.format(2270460), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 13-02-2026"),
    Bron(bron_id="vlpar-sv-1010-2026-vaph", naam="SV nr. 1010 (2025-2026), Vaneeckhout → min. Crevits — wachtlijsten personen met een handicap, budgetten (kostprijs PG2/PG3, wachtenden PAB)",
         organisatie="Vlaams Parlement", url=PF.format(2355346), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 03-08-2026; prijzen per punt 2025 incl. meerkost"),
    Bron(bron_id="vlpar-sv-1054-2026-vaph", naam="SV nr. 1054 (2025-2026), Vandromme → min. Crevits — impact optrekken cesuur RTH-punten (wachtenden onder de cesuur, PAB-budgethouders)",
         organisatie="Vlaams Parlement", url=PF.format(2358068), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 12-08-2026"),
    Bron(bron_id="vlpar-sv-1048-2026-mfc", naam="SV nr. 1048 (2025-2026), De Reuse → min. Crevits — MFC's, wachtlijsten (uitbreidingsbeleid 2023-2025)",
         organisatie="Vlaams Parlement", url=PF.format(2357993), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 07-08-2026; wachttijden MFC: 'geen cijfers beschikbaar'"),
    Bron(bron_id="vlpar-sv-561-2025-versl", naam="SV nr. 561 (2024-2025), De Reuse → min. Gennez — verslavingszorg, aanmeldstops",
         organisatie="Vlaams Parlement", url=PF.format(2158184), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 22-05-2025; geen gecentraliseerd overzicht; beleidsnota: registratie- en monitoringssysteem wachtlijsten GGZ"),
]


def _update_voorzieningen() -> None:
    vz = {v.voorziening_id: v for v in load("voorzieningen")}
    g = vz[GZ]
    g.scan_status, g.laatste_peildatum, g.publicatie_bron_id = "proef_uitgewerkt", date(2022, 12, 31), "vlpar-sv-950-2023-gz"
    g.frequentie, g.wachtlijst_type = "urencontingent jaarlijks bij MB; realisatie gekend in jaar X+1; cijfers enkel via SV", W.GEEN
    g.wachtlijst_naam, g.ise_koppeling = "geen wachtlijst; rantsoenering via urencontingent per dienst", "WOONZORG EN EERSTE LIJN"
    g.opmerking = ("Rantsoenering, geen wachtlijst: elke erkende dienst (103 in 2024) krijgt jaarlijks een subsidiabel urencontingent (2022: 18,86 mln uur; gepresteerd 15,95 mln uur gezinszorg "
                   "voor 126.570 gezinnen). Niet-gerealiseerde uren kunnen niet naar andere diensten; onderbenutting door personeelskrapte (SV 293). Gebruikers gezinszorg 118.280 (2018) → "
                   "126.570 (2022). Lokale wachtlijsten per dienst worden niet centraal geregistreerd. Hervorming: inkanteling in de Vlaamse sociale bescherming (regeerakkoord 2024-2029).")
    c = vz[COS]
    c.scan_status, c.laatste_peildatum, c.publicatie_bron_id = "proef_uitgewerkt", date(2024, 12, 31), "vlpar-sv-1007-2025-cos"
    c.frequentie, c.wachtlijst_type = "geen; SV's", W.DECENTRAAL
    c.wachtlijst_naam, c.ise_koppeling = "wachtlijst per COS (4 centra), geen uniforme registratie", "JEUGDHULP"
    c.opmerking = ("'De COS kennen geen centrale, uniforme registratie van wachtenden' (SV 633, 2022); 'Er zijn geen cijfers m.b.t. de wachtlijsten beschikbaar' (SV 504, 2025). Laatste wachttijden: dec 2021 "
                   "COS Antwerpen 33 maanden (> 3 j; aanmeldingsstop sinds sept 2020), Brussel 15, Gent 34 (> 2,5 j), Leuven 15. Trajecten 0-6 j: ± 4.400 kinderen per jaar (2022-2024). Projectmiddelen "
                   "brugzorg t/m 2025; nieuw organisatiemodel diagnostiek in voorbereiding. CAR: 'geen gevalideerde cijfers over de wachttijden' (SV 234, 2026).")
    n = vz[NT2]
    n.scan_status, n.laatste_peildatum, n.publicatie_bron_id = "afgerond", date(2025, 9, 10), "vlpar-sv-34-2025-nt2"
    n.frequentie, n.wachtlijst_type = "aanbodbevraging NT2 (Ahovoks) twee keer per jaar; niet gepubliceerd", W.CENTRAAL_NIET_GEPUBLICEERD
    n.wachtlijst_naam, n.ise_koppeling = "wachtlijst per CBE/CVO, centraal bevraagd door Ahovoks", ""
    n.opmerking = ("Aanbodbevraging NT2 van 10 september 2025: 'geen cursisten (met intake bij een Agentschap Integratie en Inburgering of het Huis van het Nederlands Brussel) op de wachtlijst bij een CBE of CVO' "
                   "(SV 34). Geen wachtlijstprobleem op Vlaams niveau → afgerond; herbevragen bij signalen (Brussel, dagaanbod). Cursistenaantallen via Dataloep.")
    p = vz[PZ]
    p.scan_status, p.laatste_peildatum, p.publicatie_bron_id = "proef_uitgewerkt", date(2024, 12, 31), "vlpar-sv-194-2026-pz"
    p.frequentie, p.wachtlijst_type = "jaarlijks via SV-reeks Schryvers (cijfers jaar N ± januari N+2)", W.CENTRAAL_NIET_GEPUBLICEERD
    p.wachtlijst_naam, p.ise_koppeling = "kinderen die op 31/12 wachten op een pleeggezin (perspectiefzoekende en -biedende pleegzorg, Domino)", "JEUGDHULP"
    p.opmerking = ("Wachtenden op een pleeggezin 702 (2018) → 961 (2022) → 1.189 (2023) → 1.307 (31-12-2024), +86 % in zes jaar; 37 % jonger dan 6. Ondersteunende pleegzorg (RTJ) wordt niet geteld. "
                   "10.676 pleegzorgsituaties op 31-12-2024 (8.221 perspectiefbiedend). Deelverzameling van de NRTJ-wachtlijst (2.707 verblijfsvragen pleeggezin in 2025, andere teleenheid). "
                   "Budget: binnen artikel jeugdhulp GB0-1GEF2MX-IS; BO 2026 +11,1 mln kostendrijver pleegzorg.")
    j = vz[JH]
    j.scan_status, j.laatste_peildatum, j.publicatie_bron_id = "proef_uitgewerkt", date(2026, 1, 16), "vlpar-sv-386-2026-jh"
    j.frequentie, j.wachtlijst_type = "jaarlijks via SV-reeks Schryvers (januari)", W.CENTRAAL_NIET_GEPUBLICEERD
    j.wachtlijst_naam, j.ise_koppeling = "werkstrafdossiers in afwachting van een justitieassistent (SIPAR)", "JUSTITIE EN HANDHAVING"
    j.opmerking = ("Wachttijd tussen ontvangst van een werkstrafdossier en aanstelling van een justitieassistent: 49 dagen (jan 2023) → 26,3 (dec 2023) → 22 (dec 2024) → 23 (jan 2026); daarna gemiddeld 121-126 dagen "
                   "tot de effectieve opstart (procedure, prestatieplaats, probatiecommissie). Daders in begeleiding 17.206 (2019) → 24.430 (2025, +42 %); federale noodwet overbevolking (aug 2025) en nieuw "
                   "Strafwetboek (april 2026) doen de instroom stijgen. Andere mandaten (probatie, ET, slachtofferonthaal): geen wachtcijfers gevonden. Budget: lonen AJH BO 2026 164,9 mln (incl. overheveling gemeenschapsinstellingen).")
    nieuw = [
        Voorziening(voorziening_id=PAB, naam="Persoonlijke-assistentiebudget (PAB) minderjarigen", domein="handicap", entiteit="Agentschap Opgroeien (intersectorale toegangspoort) / VAPH", bevoegdheid=GEM,
                    wachtlijst_naam="minderjarigen met een toegewezen PAB-vraag zonder budget (foto 31/12, INSISTO)", wachtlijst_type=W.CENTRAAL_GEPUBLICEERD, publicatie_bron_id="opgroeien-nrtj",
                    frequentie="jaarlijks (Opgroeien cijferrapport NRTJ, cijfers op maat); VAPH-jaarverslag", laatste_peildatum=date(2025, 12, 31), scan_status="proef_uitgewerkt", ise_koppeling="PERSONEN MET EEN BEPERKING | JEUGDHULP",
                    opmerking=("Afgesplitst van het NRTJ-dossier (1-10-2026). Wachtenden 1.478 (2022) → 1.763 (31-12-2024, Opgroeien) en +39 % in 2025 (≈ 2.450, afgeleid); VAPH telt 1.958 unieke wachtenden incl. priors "
                               "(31-12-2024, benodigd budget 84,4 mln). Nieuwe PAB-vragen verdubbeld 540 → 1.074 (2022-2025); toekenningen 244 (2024, ± 9 mln) → 372 (2025, 13,3 mln); 2.554 budgethouders (31-12-2025). "
                               "Geen prioriteitengroepen zoals bij PVB; 'prior' = budget de maand nadien. Budget: uitbreidingsbeleid PAB 13 mln (2025), 7,3 mln VEK overgedragen naar 2026.")),
        Voorziening(voorziening_id=RTH, naam="VAPH rechtstreeks toegankelijke hulp (RTH) en hulpmiddelen", domein="handicap", entiteit="VAPH / RTH-aanbieders", bevoegdheid=GEM,
                    wachtlijst_naam="lokale wachtlijsten bij RTH-aanbieders; hulpmiddelen: aanvraagprocedure zonder wachtlijst", wachtlijst_type=W.DECENTRAAL, publicatie_bron_id="",
                    frequentie="geen", laatste_peildatum=None, scan_status="in_onderzoek", ise_koppeling="PERSONEN MET EEN BEPERKING",
                    opmerking=("Eerste scan 1-10-2026: geen centrale RTH-wachtlijst; RTH is bedoeld als 'vangnet voor mensen die wachten op een nRTH-budget' (SV 146). Uitbreiding 3.410 RTH-punten minderjarigen (2025-2026, SV 305). "
                               "Hervorming zorgniveaus: cesuur RTH opgetrokken naar 15,29 punten; 2.407 PVB-wachtenden (340 PG2, 2.067 PG3) vallen onder de cesuur (SV 1054). Hulpmiddelen: individuele tegemoetkomingen, geen rangschikking. "
                               "Te doen: SV-reeks over RTH-wachtenden per aanbieder; VAPH-jaarverslag RTH-gebruik.")),
        Voorziening(voorziening_id=CAR, naam="Centra voor ambulante revalidatie (CAR)", domein="zorg", entiteit="Departement Zorg", bevoegdheid=GEM,
                    wachtlijst_naam="wachtlijst per centrum", wachtlijst_type=W.DECENTRAAL, publicatie_bron_id="vlpar-sv-234-2026-car", frequentie="geen", laatste_peildatum=date(2026, 1, 29), scan_status="in_onderzoek",
                    ise_koppeling="GESPECIALISEERDE ZORG",
                    opmerking=("Eerste scan 1-10-2026: 'Het Departement Zorg beschikt niet over gevalideerde cijfers over de wachttijden bij de Centra voor Ambulante Revalidatie' (SV 234); geen budgettaire analyse mogelijk. "
                               "CAR-CGG-hervormingstraject en projecten 'uitbreiding capaciteit gespecialiseerde diagnostiek' (6 CAR); federale stopzetting terugbetaling monodisciplinaire logopedie (juni 2025) verhoogt de druk. "
                               "Samen met COS opvolgen.")),
        Voorziening(voorziening_id=CAW, naam="CAW en verslavingszorg", domein="welzijn / ggz", entiteit="Departement Zorg (CAW's, revalidatievoorzieningen verslavingszorg 7.73)", bevoegdheid=GEM,
                    wachtlijst_naam="aanmeldstops / wachtlijsten per voorziening", wachtlijst_type=W.DECENTRAAL, publicatie_bron_id="vlpar-sv-561-2025-versl", frequentie="geen", laatste_peildatum=date(2025, 5, 22),
                    scan_status="te_onderzoeken", ise_koppeling="GESPECIALISEERDE ZORG",
                    opmerking=("Eerste scan 1-10-2026: 'geen gecentraliseerd(e) informatie/overzicht beschikbaar omtrent eventuele aanmeldingsstops in de verslavingszorg' (SV 561); koepels melden geen aanmeldstops (maart 2025). "
                               "Beleidsnota 2024-2029 belooft 'een registratie- en monitoringssysteem voor de wachtlijsten' in de GGZ. CAW: geen wachtcijfers gevonden in SV's 2024-2026. Te doen: jaarverslag CAW Groep, SV over wachttijden onthaal/begeleiding.")),
        Voorziening(voorziening_id=FOR, naam="Forensische zorg (geïnterneerden, forensisch VAPH)", domein="zorg / justitie", entiteit="Departement Zorg / VAPH (deels federaal: FPC's)", bevoegdheid=GEM,
                    wachtlijst_naam="geïnterneerden in de gevangenis wachtend op een plaats in FPC of forensische VAPH-unit", wachtlijst_type=W.ONBEKEND, publicatie_bron_id="", frequentie="geen", laatste_peildatum=None,
                    scan_status="te_onderzoeken", ise_koppeling="GESPECIALISEERDE ZORG",
                    opmerking=("Eerste scan 1-10-2026: geen schriftelijke vragen met wachtcijfers gevonden in het Vlaams Parlement (2024-2026); de bevoegdheid is gedeeld (FPC's en internering federaal, forensische VAPH-units en "
                               "psychiatrische zorg Vlaams). BBT Justitie en Handhaving 2026, OD 2.6: 'toegankelijke en toereikende forensische zorg'. Afbakening nodig vóór verder onderzoek.")),
        Voorziening(voorziening_id=A60, naam="Sociale tewerkstelling via OCMW (art. 60 §7) en wijk-werken", domein="werk", entiteit="OCMW's / VDAB / Departement WEWIS", bevoegdheid=GEW,
                    wachtlijst_naam="geen rangschikking bekend", wachtlijst_type=W.ONBEKEND, publicatie_bron_id="", frequentie="geen", laatste_peildatum=None, scan_status="te_onderzoeken", ise_koppeling="ACTIVERING (SOCIALE ECONOMIE)",
                    opmerking=("Eerste scan 1-10-2026: geen schriftelijke vragen over wachtlijsten voor art. 60 of wijk-werken gevonden (2024-2026). Art. 60-tewerkstelling wordt per OCMW toegekend (federale financiering via "
                               "leefloon-subsidie + Vlaamse omkaderingspremie); wijk-werken via VDAB-toeleiding. Vermoedelijk 'geen wachtlijstmechanisme'; te bevestigen via VDAB-jaarverslag of SV.")),
    ]
    upsert("voorzieningen", [g, c, n, p, j] + nieuw)


def _b(vid, metriek, waarde, eenheid, peildatum, bron_id, url, titel, pagina, passage, definitie, status, pub=None, door="", opm=""):
    return Bevinding(bevinding_id=f"{vid}:{metriek}:{peildatum.isoformat()}", voorziening_id=vid, metriek=metriek, waarde=waarde, eenheid=eenheid, peildatum=peildatum,
                     bron_id=bron_id, bron_url=url, documenttitel=titel, pagina=pagina, passage=passage, definitie=definitie, publicatiedatum=pub,
                     controlestatus=status, gecontroleerd_door=door, gecontroleerd_op=VANDAAG if door else None, opmerking=opm)


BEVINDINGEN: list[Bevinding] = []

# ------------------------------------------------------------------------------------------------ gezinszorg
S950, U950, T950, P950 = "vlpar-sv-950-2023-gz", PF.format(1992606), "SV nr. 950 (2022-2023) Schryvers", date(2023, 10, 20)
for jaar, uren, gebr in ((2018, 16203534, 118280), (2019, 16419304, 121208), (2020, 16487724, 123144), (2021, 16343589, 123384), (2022, 15947262, 126570)):
    BEVINDINGEN.append(_b(GZ, "uren_gezinszorg_gepresteerd", uren, "uren", date(jaar, 12, 31), S950, U950, T950, "antwoord 8, tabel", f"Gezinszorg {jaar}: gepresteerde uren {uren:,} (afgerond)".replace(",", "."),
                          "Gepresteerde uren gezinszorg door de erkende diensten (Vesta), incl. niet-gesubsidieerd verzorgend personeel.", GEL, P950, A))
    BEVINDINGEN.append(_b(GZ, "gebruikers_gezinszorg", gebr, "gezinnen", date(jaar, 12, 31), S950, U950, T950, "antwoord 8, tabel", f"Gezinszorg {jaar}: aantal gebruikers {gebr:,}".replace(",", "."),
                          "Gezinnen/dossiers met gezinszorg in het jaar (Vesta).", GEL, P950, A))
BEVINDINGEN += [
    _b(GZ, "urencontingent_toegekend", 18857001, "uren", date(2022, 12, 31), S950, U950, T950, "antwoord 2", "totale urencontingent gezinszorg voor 2022, dat toegekend werd aan de diensten: a. openbare diensten: 2.974.978 uur; b. private diensten: 15.882.023 uur.",
       "Subsidiabel urencontingent gezinszorg (MB), som openbaar + privaat; bevat ook gelijkgestelde uren.", GEL, P950, A, opm="eigen som; niet één op één vergelijkbaar met gepresteerde uren (zie antwoord 2)"),
    _b(GZ, "aandeel_zwaar_zorgbehoevend_pct", 41.97, "procent", date(2022, 12, 31), S950, U950, T950, "antwoord 7", "Van de 126.570 dossiers gezinszorg in 2022 waren er 53.124 dossiers (41,97%) bij zwaar zorgbehoevenden.",
       "Aandeel dossiers gezinszorg bij zwaar zorgbehoevenden (BelRAI Screener ≥ 13 of IADL+ADL ≥ 5,5).", GEL, P950, A),
    _b(GZ, "erkende_diensten", 103, "diensten", date(2024, 12, 31), "vlpar-sv-630-2025-gz", PF.format(2165610), "SV nr. 630 (2024-2025) Lachaert", "antwoord 1", "Het aantal erkende diensten voor gezinszorg bedraagt 104 diensten in zowel 2022 als in 2023, en 103 diensten in 2024.",
       "Erkende diensten voor gezinszorg.", GEL, date(2025, 6, 3), A),
]

# ------------------------------------------------------------------------------------------------ COS
S633, U633, T633, P633 = "vlpar-sv-633-2022-cos", PF.format(1861756), "SV nr. 633 (2021-2022) Wouters", date(2022, 7, 29)
for cos, d, m, pas in (("antwerpen", date(2020, 2, 1), 34, "Februari 2020 COS Antwerpen: Kinderen > 3 jaar = 34 maanden"), ("antwerpen", date(2021, 12, 1), 33, "December 2021 COS Antwerpen: Kinderen > 3 jaar = 33 maanden (aanmeldingsstop sinds september 2020 voor kinderen ouder dan 3 jaar)"),
                       ("brussel", date(2020, 2, 1), 12, "Februari 2020 COS Brussel: 12 maanden"), ("brussel", date(2021, 12, 1), 15, "December 2021 COS Brussel: 15 maanden"),
                       ("gent", date(2020, 2, 1), 22, "Februari 2020 COS Gent: Kinderen > 2,5 jaar = 22 maanden"), ("gent", date(2021, 12, 1), 34, "December 2021 COS Gent: Kinderen > 2,5 jaar = 34 maanden"),
                       ("leuven", date(2020, 2, 1), 12, "Februari 2020 COS Leuven: 12 maanden"), ("leuven", date(2021, 12, 1), 15, "December 2021 COS Leuven: 15 maanden")):
    BEVINDINGEN.append(_b(COS, f"wachttijd_{cos}_maanden", m, "maanden", d, S633, U633, T633, "antwoord 1, tabel", pas, f"Wachttijd voor een volledig multidisciplinair onderzoek bij COS {cos.capitalize()} (oudste leeftijdsgroep).", GEL, P633, A,
                          opm="COS kennen geen centrale, uniforme registratie van wachtenden (antwoord 2)"))
S1007, U1007, T1007 = "vlpar-sv-1007-2025-cos", PF.format(2216493), "SV nr. 1007 (2024-2025) Vandromme"
for jaar, k in ((2022, 1128 + 1171 + 738 + 1389), (2023, 1242 + 1018 + 793 + 1300), (2024, 1160 + 1003 + 784 + 1421)):
    BEVINDINGEN.append(_b(COS, "trajecten_kinderen_0_6", k, "kinderen", date(jaar, 12, 31), S1007, U1007, T1007, "antwoord 1, tabel COS", f"aantal kinderen {jaar}: Leuven/Hasselt + Brussel + Antwerpen + Gent = {k:,}".replace(",", "."),
                          "Kinderen 0-6 jaar met een traject (multidisciplinair onderzoek) bij de vier COS in het jaar (som).", GEL, date(2025, 10, 17), A, opm="eigen som van de vier centra"))

# ------------------------------------------------------------------------------------------------ NT2
BEVINDINGEN.append(_b(NT2, "wachtenden_cbe_cvo", 0, "cursisten", date(2025, 9, 10), "vlpar-sv-34-2025-nt2", PF.format(2237755), "SV nr. 34 (2025-2026) Tombeur", "antwoord 4",
                      "Uit de cijfers van de aanbodbevraging NT2 van 10 september 2025 blijkt dat er geen cursisten (die een intakeprocedure achter de rug hebben bij een Agentschap Integratie en Inburgering of het Huis van het Nederlands Brussel) op de wachtlijst staan bij een CBE of CVO.",
                      "Cursisten met intake die op de wachtlijst staan bij een centrum voor basiseducatie of volwassenenonderwijs (aanbodbevraging NT2, Ahovoks).", GEL, date(2025, 12, 5), A))

# ------------------------------------------------------------------------------------------------ pleegzorg
D_PZ = "Kinderen en jongeren (0-25) die op 31/12 wachten op een pleeggezin in het kader van perspectiefzoekende en -biedende pleegzorg (NRTJ, Domino); som van de vijf provincies."
for jaar, n in ((2018, 702), (2019, 727), (2020, 833), (2021, 872), (2022, 961)):
    BEVINDINGEN.append(_b(PZ, "wachtenden_pleeggezin", n, "kinderen", date(jaar, 12, 31), "vlpar-sv-203-2025-pz", PF.format(2119342), "SV nr. 203 (2024-2025) Schryvers", f"antwoord 2, tabel {jaar}",
                          f"{jaar}: som van de provincies × leeftijdsgroepen = {n}", D_PZ, GEL, date(2025, 2, 28), A, opm="eigen som van 20 cellen"))
BEVINDINGEN += [
    _b(PZ, "wachtenden_pleeggezin", 1189, "kinderen", date(2023, 12, 31), "vlpar-sv-75-2024-pz", PF.format(2099807), "SV nr. 75 (2024-2025) Schryvers", "antwoord",
       "In 2023 wachtten 1189 kinderen op een pleeggezin (perspectief biedende en -zoekende hulp). Dit aantal ligt hoger dan vorig jaar.", D_PZ, GEL, date(2025, 1, 15), A),
    _b(PZ, "wachtenden_pleeggezin", 1307, "kinderen", date(2024, 12, 31), "vlpar-sv-194-2026-pz", PF.format(2253598), "SV nr. 194 (2025-2026) Schryvers", "antwoord 2a, tabel 2024",
       "Totaal 479 (0-5) 385 (6-11) 341 (12-17) 92 (18-25) 1307", D_PZ, GEL, date(2026, 1, 15), A),
    _b(PZ, "pleegzorgsituaties", 10676, "situaties", date(2024, 12, 31), "vlpar-sv-194-2026-pz", PF.format(2253598), "SV nr. 194 (2025-2026) Schryvers", "antwoord 2c",
       "Op 31/12/2024 telden we 10.676 pleegzorgsituaties. De grootste groep vormt perspectiefbiedende pleegzorg met 8.221 pleegzorgsituaties", "Lopende pleegzorgsituaties op 31/12 (alle vormen).", GEL, date(2026, 1, 15), A),
]

# ------------------------------------------------------------------------------------------------ justitiehuizen
D_JH1 = "Gemiddelde duurtijd (dagen) tussen ontvangst van een werkstrafdossier op het justitiehuis en aanstelling van een justitieassistent (SIPAR)."
D_JH2 = "Gemiddelde duurtijd (dagen) tussen aanstelling van de justitieassistent en effectieve opstart van de werkstraf, afgesloten dossiers van het jaar."
BEVINDINGEN += [
    _b(JH, "wachttijd_werkstraf_aanstelling_dagen", 49, "dagen", date(2023, 1, 31), "vlpar-sv-348-2023-jh", PF.format(1924206), "SV nr. 348 (2022-2023) Schryvers", "antwoord 1-2", "bedroeg de duurtijd in januari 2023 49 dagen of een dikke anderhalve maand", D_JH1, GEL, date(2023, 3, 7), A),
    _b(JH, "wachttijd_werkstraf_aanstelling_dagen", 26.3, "dagen", date(2023, 12, 31), "vlpar-sv-212-2024-jh", PF.format(2043114), "SV nr. 212 (2023-2024) Schryvers", "antwoord 1-2", "bedroeg in december 2023 gemiddeld 26,3 dagen", D_JH1, GEL, date(2024, 3, 26), A),
    _b(JH, "wachttijd_werkstraf_aanstelling_dagen", 22, "dagen", date(2024, 12, 31), "vlpar-sv-369-2025-jh", PF.format(2146400), "SV nr. 369 (2024-2025) Schryvers", "antwoord 1-2, tabel", "Globaal gezien betrof de gemiddelde wachttijd in december 22 dagen. … Antwerpen 66 … Veurne 0", D_JH1, GEL, date(2025, 4, 15), A),
    _b(JH, "wachttijd_werkstraf_aanstelling_dagen", 23, "dagen", date(2026, 1, 16), "vlpar-sv-386-2026-jh", PF.format(2291166), "SV nr. 386 (2025-2026) Schryvers", "antwoord 1-2", "Op dit moment betreft de gemiddelde wachttijd voor werkstrafdossiers 23 dagen.", D_JH1, GEL, date(2026, 3, 9), A),
    _b(JH, "doorlooptijd_werkstraf_opstart_dagen", 126, "dagen", date(2024, 12, 31), "vlpar-sv-369-2025-jh", PF.format(2146400), "SV nr. 369 (2024-2025) Schryvers", "antwoord 3", "Van de dossiers die in 2024 zijn afgesloten, bedroeg de gemiddelde duurtijd tussen de aanstelling van de justitieassistent en de effectieve opstart van de werkstraf 126 dagen.", D_JH2, GEL, date(2025, 4, 15), A),
    _b(JH, "doorlooptijd_werkstraf_opstart_dagen", 121, "dagen", date(2025, 12, 31), "vlpar-sv-386-2026-jh", PF.format(2291166), "SV nr. 386 (2025-2026) Schryvers", "antwoord 3", "Van de afgesloten dossiers in 2025 bedroeg de gemiddelde duurtijd tussen de aanstelling van de justitieassistent en de effectieve opstart van de werkstraf 121 dagen.", D_JH2, GEL, date(2026, 3, 9), A),
    _b(JH, "daders_in_begeleiding", 17206, "personen", date(2019, 12, 31), "vlpar-bbt-jh-2026", PF.format(2227488), "BBT Justitie en Handhaving 2026 — 13-S", "OD 2.2", "steeg het aantal daders in begeleiding door de justitiehuizen met maar liefst 42% (van 17.206 daders in 2019 naar 24.430 daders in 2025)", "Daders in begeleiding door de justitiehuizen in het jaar.", GEL, date(2025, 12, 9), A),
    _b(JH, "daders_in_begeleiding", 24430, "personen", date(2025, 12, 31), "vlpar-bbt-jh-2026", PF.format(2227488), "BBT Justitie en Handhaving 2026 — 13-S", "OD 2.2", "… naar 24.430 daders in 2025", "Idem.", GEL, date(2025, 12, 9), A),
]

# ------------------------------------------------------------------------------------------------ PAB minderjarigen (eigen dossier)
D_PAB = "Unieke minderjarigen met een toegewezen vraag naar een persoonlijke-assistentiebudget zonder opgestart budget, foto op 31/12 (intersectorale toegangspoort, INSISTO)."
BEVINDINGEN += [
    _b(PAB, "wachtenden_pab", 1478, "personen", date(2022, 12, 31), "vlpar-sv-416-2023", PF.format(1935207), "SV nr. 416 (2022-2023)", "antwoord, PDF p. 3", "1478 unieke kinderen en jongeren hadden een vraag naar ondersteuning via PAB", D_PAB, GEL, date(2023, 5, 10), A, opm="ook in dossier opgroeien-nrtj (metriek wachtenden_pab)"),
    _b(PAB, "wachtenden_pab", 1763, "personen", date(2024, 12, 31), "vlpar-sv-242-2026", PF.format(2261521), "SV nr. 242 (2025-2026)", "antwoord, PDF p. 3", "Evolutie aantal kinderen en jongeren dat wacht op een persoonlijkeassistentiebudget (PAB): 1763", D_PAB, GEL, date(2026, 1, 29), A, opm="ook in dossier opgroeien-nrtj"),
    _b(PAB, "wachtenden_pab", 2450, "personen", date(2025, 12, 31), "opgroeien-nrtj", "https://www.opgroeien.be/kennis/cijfers-en-onderzoek/aanvragen-crisisjeugdhulp-en-niet-rechtstreeks-toegankelijke-jeugdhulp", "Opgroeien — cijferrapport NRTJ (2025)", "sectie wachtenden",
       "Het aantal wachtenden op een persoonlijk assistentiebudget (PAB) is in 2025 opnieuw gestegen en wel met 39 %.", D_PAB, ONG, date(2026, 6, 1), opm="afgeleid: 1.763 × 1,39 ≈ 2.450; exact cijfer in 'cijfers op maat' (Power BI) nog te lezen"),
    _b(PAB, "wachtenden_pab_vaph_incl_prior", 1958, "personen", date(2024, 12, 31), "vlpar-sv-1010-2026-vaph", PF.format(2355346), "SV nr. 1010 (2025-2026) Vaneeckhout", "antwoord 4, tabel 3",
       "Aantal wachtenden PAB en het benodigde budget op 31/12/2024: wachtend met prior 14, wachtend zonder prior 1.944; Totaal 1.958; € 84.439.277", "Unieke cliënten wachtend op een PAB volgens VAPH-telling per budgetcategorie (incl. priors), met geïndexeerd benodigd jaarbudget.", GEL, date(2026, 8, 3), A,
       opm="andere teleenheid dan de Opgroeien-foto (1.763): 195 verschil"),
    _b(PAB, "benodigd_budget_wachtenden_eur", 84439277, "euro", date(2024, 12, 31), "vlpar-sv-1010-2026-vaph", PF.format(2355346), "SV nr. 1010 (2025-2026) Vaneeckhout", "antwoord 4, tabel 3", "Totaal 1.958 € 84.439.277", "Geïndexeerd jaarbudget nodig om alle wachtenden PAB een budget te geven (31-12-2024).", GEL, date(2026, 8, 3), A),
    _b(PAB, "nieuwe_vragen_pab", 540, "vragen", date(2022, 12, 31), "opgroeien-nrtj", "https://www.opgroeien.be/kennis/cijfers-en-onderzoek/aanvragen-crisisjeugdhulp-en-niet-rechtstreeks-toegankelijke-jeugdhulp", "Opgroeien — cijferrapport NRTJ (2025)", "sectie wachtenden",
       "De vragen naar PAB zijn toegenomen de afgelopen jaren, in cijfers op maat is te zien dat er op drie jaar tijd een verdubbeling is van 540 naar 1.074.", "Nieuwe aanvragen voor een erkenning PAB in het jaar (cijfers op maat).", GEL, date(2026, 6, 1), A, opm="jaar afgeleid: 'drie jaar' vóór 2025"),
    _b(PAB, "nieuwe_vragen_pab", 1074, "vragen", date(2025, 12, 31), "opgroeien-nrtj", "https://www.opgroeien.be/kennis/cijfers-en-onderzoek/aanvragen-crisisjeugdhulp-en-niet-rechtstreeks-toegankelijke-jeugdhulp", "Opgroeien — cijferrapport NRTJ (2025)", "sectie wachtenden", "… verdubbeling is van 540 naar 1.074", "Idem.", GEL, date(2026, 6, 1), A),
    _b(PAB, "toekenningen_pab", 244, "budgetten", date(2024, 12, 31), "vlpar-sv-305-2026-pab", PF.format(2270460), "SV nr. 305 (2025-2026) Dillen", "antwoord 2", "Voor 2024 waren er 244 PAB's twv ongeveer 9 miljoen euro.", "Nieuw toegekende PAB's in het jaar (spoed, prior en langst wachtenden).", GEL, date(2026, 2, 13), A),
    _b(PAB, "toekenningen_pab", 372, "budgetten", date(2025, 12, 31), "vlpar-sv-305-2026-pab", PF.format(2270460), "SV nr. 305 (2025-2026) Dillen", "antwoord 1-2", "Het voorziene budget heeft gezorgd voor 372 PAB budgetten. Dit zijn zowel spoedpab's, priors als PAB's voor de langst wachtenden. … In 2025 werden twv 13,3 miljoen euro pab's uitgedeeld.", "Idem.", GEL, date(2026, 2, 13), A),
    _b(PAB, "budgethouders_pab", 2554, "personen", date(2025, 12, 31), "vlpar-sv-1054-2026-vaph", PF.format(2358068), "SV nr. 1054 (2025-2026) Vandromme", "vragen 1 en 2", "Voor PAB vallen 6 van de 2554 budgethouders op 31.12.2025 onder de cesuur van 15,29 punten.", "Minderjarigen met een lopend PAB op 31/12.", GEL, date(2026, 8, 12), A),
    _b(PAB, "aandeel_wachtenden_met_nrtj_hulp_pct", 27.6, "procent", date(2025, 12, 31), "opgroeien-nrtj", "https://www.opgroeien.be/kennis/cijfers-en-onderzoek/aanvragen-crisisjeugdhulp-en-niet-rechtstreeks-toegankelijke-jeugdhulp", "Opgroeien — cijferrapport NRTJ (2025)", "sectie wachtenden",
       "In 2025 maakte 27,6% van de kinderen en jongeren die stonden te wachten op een PAB eveneens gebruik van niet rechtstreeks toegankelijke jeugdhulp van een voorziening, waar dit twee jaar voordien nog 45% was.", "Aandeel PAB-wachtenden dat intussen NRTJ-hulp van een voorziening krijgt.", GEL, date(2026, 6, 1), A),
]

# ------------------------------------------------------------------------------------------------ VAPH-PVB: kostprijs van de wachtlijst (SV 1010)
BEVINDINGEN += [
    _b(PVB, "kostprijs_wachtlijst_pg2_eur", 332_000_000, "euro", date(2025, 12, 31), "vlpar-sv-1010-2026-vaph", PF.format(2355346), "SV nr. 1010 (2025-2026) Vaneeckhout", "antwoord 2, tabel 1",
       "Kostprijs prioriteitengroep 2 op 31 december 2025 naar ingang prioriteit: … Eindtotaal 7856 — 332 (miljoen euro; prijzen aan bedrag per punt 2025 inclusief meerkost)", "Geraamd jaarbudget om alle 7.856 vragen in prioriteitengroep 2 een budget te geven (31-12-2025).", GEL, date(2026, 8, 3), A),
    _b(PVB, "kostprijs_wachtlijst_pg3_eur", 284_200_000, "euro", date(2025, 12, 31), "vlpar-sv-1010-2026-vaph", PF.format(2355346), "SV nr. 1010 (2025-2026) Vaneeckhout", "antwoord 2, tabel 2",
       "kostprijs prioriteitengroep 3 op 31 december 2025 naar ingang prioriteit: … Totaal 9224 — 284,2", "Geraamd jaarbudget om alle 9.224 vragen in prioriteitengroep 3 een budget te geven (31-12-2025).", GEL, date(2026, 8, 3), A),
    _b(PVB, "wachtenden_onder_cesuur_rth", 2407, "personen", date(2025, 12, 31), "vlpar-sv-1054-2026-vaph", PF.format(2358068), "SV nr. 1054 (2025-2026) Vandromme", "vragen 1 en 2",
       "Bij het totaal aantal wachtende voor een PVB op 31.12.205 vielen 2407 personen onder de cesuur waarvan 340 in prioriteitengroep 2 en 2067 in prioriteitengroep 3.", "PVB-wachtenden met een budgetcategorie onder de nieuwe RTH-cesuur (15,29 punten); zouden na de hervorming naar zorgniveau 1 (RTH) gaan.", GEL, date(2026, 8, 12), A,
       opm="bron schrijft '31.12.205' (tikfout voor 2025)"),
]


def _bu(vid, jaar, fase, niveau, bedrag, bron_id, url, titel, pagina, passage, status, door="", krediet=Kredietsoort.NVT, artikel="", programma="", ise="", label="", opm=""):
    key = artikel or label.replace(" ", "_")[:40]
    return Budget(budget_id=f"{vid}:{jaar}:{fase.value}:{niveau}:{krediet.value}:{key}", voorziening_id=vid, begrotingsjaar=jaar, fase=fase, niveau=niveau, bedrag_eur=bedrag,
                  kredietsoort=krediet, artikel_code=artikel, programma=programma, ise=ise, label=label, bron_id=bron_id, bron_url=url, documenttitel=titel, pagina=pagina,
                  passage=passage, controlestatus=status, gecontroleerd_door=door, gecontroleerd_op=VANDAAG if door else None, opmerking=opm)


B, VAK = Budgetfase, Kredietsoort.VAK
BUDGETTEN = [
    _bu(PAB, 2025, B.BELEID, "uitbreidingsbeleid", 13_000_000, "vlpar-sv-305-2026-pab", PF.format(2270460), "SV nr. 305 (2025-2026) Dillen", "antwoord 1",
        "Er werd 13 miljoen euro UB voorzien voor PAB. In 2025 werden twv 13,3 miljoen euro pab's uitgedeeld. … ongeveer 6 miljoen euro VEK van het UB gespendeerd. De resterende middelen worden geraamd op 7,3 miljoen euro VEK en in 2026 ingezet", GEL, A, label="uitbreidingsbeleid PAB minderjarigen"),
    _bu(PAB, 2025, B.BELEID, "realisatie", 13_300_000, "vlpar-sv-305-2026-pab", PF.format(2270460), "SV nr. 305 (2025-2026) Dillen", "antwoord 1", "In 2025 werden twv 13,3 miljoen euro pab's uitgedeeld (372 budgetten).", GEL, A, label="toegekende PAB's (waarde)"),
    _bu(PAB, 2024, B.BELEID, "realisatie", 9_000_000, "vlpar-sv-305-2026-pab", PF.format(2270460), "SV nr. 305 (2025-2026) Dillen", "antwoord 2", "Voor 2024 waren er 244 PAB's twv ongeveer 9 miljoen euro.", GEL, A, label="toegekende PAB's (waarde)", opm="'ongeveer'"),
    _bu(PAB, 2025, B.BELEID, "uitbreidingsbeleid", 12_900_000, "vlpar-sv-305-2026-pab", PF.format(2270460), "SV nr. 305 (2025-2026) Dillen", "antwoord 1", "Daarnaast was er 12,9 miljoen euro voorzien voor ondersteuning van minderjarigen in een MFC en voor RTH in 2025. Deze worden vanaf 2026 ingezet.", GEL, A, label="uitbreidingsbeleid MFC + RTH minderjarigen (ingezet vanaf 2026)"),
    _bu(JH, 2026, B.BO, "dept_artikel", 164_868_000, "vlpar-bbt-jh-2026", PF.format(2227488), "BBT Justitie en Handhaving 2026 — 13-S", "artikel SL0-1SAE2ZZ-LO",
        "LONEN: BA 2025 83.098 / Index 1.660 / Compensaties 72.084 / Andere bijstellingen 8.026 / BO 2026 164.868 (keuro); personeelsplan 1.179 VTE (vóór overheveling)", GEL, A, VAK, "SL0-1SAE2ZZ-LO", "SA", "", "lonen Agentschap Justitie en Handhaving (incl. justitieassistenten)", opm="compensatie 72.084 = overheveling gemeenschapsinstellingen van Opgroeien"),
    _bu(JH, 2026, B.BO, "dept_artikel", 7_022_000, "vlpar-bbt-jh-2026", PF.format(2227488), "BBT Justitie en Handhaving 2026 — 13-S", "p. 51-52, artikel SL0-1SDE2JA-WT",
        "JUSTITIEHUIZEN EN ELEKTRONISCH TOEZICHT KOSTEN: BA 2025 5.635 / Index 40 / Andere bijstellingen 1.347 / BO 2026 7.022 (federale noodmaatregel)", GEL, A, VAK, "SL0-1SDE2JA-WT", "SD", "JUSTITIE EN HANDHAVING", "werkingskosten elektronisch toezicht"),
]


def main() -> None:
    nb = upsert("bronnen", BRONNEN)
    _update_voorzieningen()
    nv = upsert("bevindingen", BEVINDINGEN)
    nu = upsert("budgetten", BUDGETTEN)
    print(f"ronde 5: bronnen {nb}, bevindingen {nv}, budgetten {nu} (upsert); draai 'wachtlijst validate' en 'wachtlijst publish'")


if __name__ == "__main__":
    main()
