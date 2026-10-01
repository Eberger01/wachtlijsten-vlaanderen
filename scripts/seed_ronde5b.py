"""Ronde 5b (1-10-2026): de drie 'te onderzoeken' voorzieningen uit ronde 5 naar 'in onderzoek' — CAW/verslavingszorg, forensische zorg,
art. 60/wijk-werken — met de eerste cijferreeksen uit het Vlaams Parlement.

Draai ná seed_ronde5.py:  ``python scripts/seed_ronde5b.py``  (upsert op sleutel; raakt seed_ronde5.py niet).

- Forensische zorg: CGG-wachttijd forensische zorg (aanmelding → eerste contact) 111 d (2018) → 48 d (2024); hulp- en dienstverlening in de
  gevangenis (CGG) 150 → 29 d; actieve forensische zorgperiodes 5.731 (2018) → 6.992 (2024) (SV 844). CAW justitieel welzijnswerk: geen
  overkoepelende wachtlijst, wel per gevangenis (juni 2023: o.a. Leuven Centraal 30, Wortel 43, Hasselt 26+1) (SV 815, 2023).
- CAW / verslavingszorg: "geen structurele monitoring van de wachttijden over alle sectoren heen"; verslavingszorgteams CGG gemiddeld 45 dagen
  tot eerste contact (2021-2023) (SV 568); geen gecentraliseerd overzicht van aanmeldstops (SV 561).
- Art. 60 / wijk-werken: geen wachtlijst; VDAB meet 'tijdig werk' (start binnen 2 maanden na start TWE-OCMW-traject): 9.222 lopende trajecten
  met tijdig werk (2024), 9.763 (t/m nov 2025); uitstroom naar werk 28,8 %; 3.365 actieve wijk-werkers (eind 2025); VDAB-budget wijk-werken
  9,17 mln (2026) (SV 319, 171, 420).
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from wachtlijst.models import Bevinding, Bron, BronType, Budget, Budgetfase, Controlestatus, Kredietsoort, WachtlijstType  # noqa: E402
from wachtlijst.store import load, upsert  # noqa: E402

VANDAAG = date(2026, 10, 1)
GEL = Controlestatus.BRON_GELEZEN
A = "onderzoeksagent (2026-10-01)"
PF = "https://docs.vlaamsparlement.be/files/pfile?id={}"
CAW, FOR, A60 = "zorg-caw-verslavingszorg", "zorg-forensisch", "dwse-art60-wijkwerken"
W = WachtlijstType

BRONNEN = [
    Bron(bron_id="vlpar-sv-844-2025-for", naam="SV nr. 844 (2024-2025), Vandeurzen → min. Gennez — hulp- en dienstverlening aan gedetineerden, wachtlijsten (CGG-wachttijden forensische zorg 2018-2024)",
         organisatie="Vlaams Parlement", url=PF.format(2196828), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 31-07-2025; CAW: geen overkoepelende wachtlijsten; CGG: retrograde wachttijden"),
    Bron(bron_id="vlpar-sv-815-2023-caw", naam="SV nr. 815 (2022-2023), Wouters → min. Crevits — hulp- en dienstverlening aan gedetineerden, wachtlijst CAW's (per gevangenis, juni 2023)",
         organisatie="Vlaams Parlement", url=PF.format(1981298), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 10-08-2023; onthaal en begeleiding gedetineerden per CAW 2018-2022"),
    Bron(bron_id="vlpar-sv-568-2025-versl", naam="SV nr. 568 (2024-2025), Vandeurzen → min. Gennez — drughulpverlening, stand van zaken (landschap, wachttijden, Druglijn)",
         organisatie="Vlaams Parlement", url=PF.format(2158191), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 22-05-2025; 'geen structurele monitoring van de wachttijden over alle sectoren heen'"),
    Bron(bron_id="vlpar-sv-319-2026-a60", naam="SV nr. 319 (2025-2026), Tombeur → min. Demir — tewerkstelling artikel 60 en 61 OCMW-wet, evolutie (TWE-OCMW)",
         organisatie="Vlaams Parlement", url=PF.format(2281810), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 24-02-2026; VDAB meet 'tijdig werk' (start binnen 2 maanden), niet het aantal art. 60-tewerkstellingen"),
    Bron(bron_id="vlpar-sv-171-2025-ww", naam="SV nr. 171 (2025-2026), Tombeur → min. Demir — wijk-werken, stand van zaken (okt 2025)",
         organisatie="Vlaams Parlement", url=PF.format(2248963), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 22-12-2025"),
    Bron(bron_id="vlpar-sv-420-2026-ww", naam="SV nr. 420 (2025-2026), Bothuyne → min. Demir — wijk-werken 2025, evaluatie (profiel, cheques, budget 2026)",
         organisatie="Vlaams Parlement", url=PF.format(2294264), bron_type=BronType.PDF, frequentie="jaarlijks (reeks Bothuyne)", opmerking="gepubliceerd 17-03-2026"),
]


def _update_voorzieningen() -> None:
    vz = {v.voorziening_id: v for v in load("voorzieningen")}
    f = vz[FOR]
    f.scan_status, f.laatste_peildatum, f.publicatie_bron_id, f.wachtlijst_type = "in_onderzoek", date(2024, 12, 31), "vlpar-sv-844-2025-for", W.CENTRAAL_NIET_GEPUBLICEERD
    f.frequentie = "enkel via SV; CGG-wachttijden retrograde berekend (jaar N in N+1)"
    f.wachtlijst_naam = "CGG forensische zorg: wachttijd aanmelding → eerste contact; CAW justitieel welzijnswerk: wachtlijst per gevangenis"
    f.opmerking = ("In onderzoek sinds 1-10-2026. Vlaams gefinancierde kant: CGG forensische zorg — wachttijd tot eerste contact 111 d (2018) → 48 d (2024), gemiddeld 54; hulp- en dienstverlening in de gevangenis "
                   "(CGG) 150 → 29 d; actieve forensische zorgperiodes 5.731 (2018) → 6.992 (2024); 1.546 voortijdig stopgezette trajecten (2024), vooral 'einde detentie' en 'transfer gevangenis'. "
                   "CAW: 'op overkoepelend niveau geen wachtlijsten of wachttijden bijgehouden', wel per gevangenis (juni 2023: Leuven Centraal 30, Wortel 43, Hoogstraten 26, Hasselt 27; Antwerpen/Brussel geen). "
                   "Federale kant (FPC's, internering, plaatsen forensisch VAPH via interneringskamers) buiten scope; nog te zoeken: forensische VAPH-units (wachtenden) en PVT/beschut wonen forensisch.")
    c = vz[CAW]
    c.scan_status, c.laatste_peildatum, c.publicatie_bron_id, c.wachtlijst_type = "in_onderzoek", date(2023, 12, 31), "vlpar-sv-568-2025-versl", W.DECENTRAAL
    c.frequentie = "geen; CGG-verslavingsteams: wachttijd via SV"
    c.opmerking = ("In onderzoek sinds 1-10-2026. 'Er is geen structurele monitoring van de wachttijden over alle sectoren heen' (SV 568, 2025): de minister noemt wachttijden een 'vertekend beeld' (meerdere "
                   "wachtlijsten, in-/door-/uitstroombeleid). Enige cijfer: verslavingszorgteams van de CGG gemiddeld 45 dagen tot het eerste cliëntencontact (2021-2023); revalidatievoorzieningen verslavingszorg (7.73) en "
                   "psychiatrische ziekenhuizen: geen actuele wachttijdgegevens. Geen gecentraliseerd overzicht van aanmeldstops; koepels melden er geen (maart 2025, SV 561). Beleidsnota 2024-2029: registratie- en "
                   "monitoringssysteem wachtlijsten GGZ. CAW algemeen (onthaal, begeleiding, vluchthuizen): geen wachtcijfers gevonden buiten de gevangenissen (zie zorg-forensisch) en de Veilige Huizen (SV 539).")
    a = vz[A60]
    a.scan_status, a.laatste_peildatum, a.publicatie_bron_id, a.wachtlijst_type = "in_onderzoek", date(2025, 12, 31), "vlpar-sv-319-2026-a60", W.GEEN
    a.frequentie = "VDAB-monitoring TWE-OCMW (via SV); wijk-werken jaarlijks via SV-reeks Bothuyne"
    a.wachtlijst_naam = "geen wachtlijst; VDAB-indicator 'tijdig werk' (art. 60-tewerkstelling start binnen 2 maanden na start traject)"
    a.opmerking = ("In onderzoek sinds 1-10-2026; vermoedelijk af te sluiten als 'geen wachtlijstmechanisme'. Art. 60 §7 is sinds de zesde staatshervorming ingebed in het traject Tijdelijke Werkervaring OCMW (TWE-OCMW); "
                   "VDAB telt geen art. 60-tewerkstellingen maar trajecten met 'tijdig werk': 9.222 (2024), 9.763 (t/m nov 2025); uitstroom naar werk 28,8 % (2024). Het OCMW blijft juridisch werkgever (DIMONA), "
                   "dus de plaats van tewerkstelling is niet gekend. Wijk-werken: 3.365 actieve wijk-werkers (eind 2025), 1.708 met overgangsmaatregel PWA; VDAB-budget 9,17 mln (2026); overgang naar samenlevingsjobs.")
    upsert("voorzieningen", [f, c, a])


def _b(vid, metriek, waarde, eenheid, peildatum, bron_id, url, titel, pagina, passage, definitie, status, pub=None, door="", opm=""):
    return Bevinding(bevinding_id=f"{vid}:{metriek}:{peildatum.isoformat()}", voorziening_id=vid, metriek=metriek, waarde=waarde, eenheid=eenheid, peildatum=peildatum,
                     bron_id=bron_id, bron_url=url, documenttitel=titel, pagina=pagina, passage=passage, definitie=definitie, publicatiedatum=pub,
                     controlestatus=status, gecontroleerd_door=door, gecontroleerd_op=VANDAAG if door else None, opmerking=opm)


BEVINDINGEN: list[Bevinding] = []
# Tweede lezing 1-10-2026 (goedgekeurd door EB): passages letterlijk (tabelrijen zoals in de bron), PDF-pagina's toegevoegd, definities aangescherpt.
GEC, D = Controlestatus.GECONTROLEERD, "onderzoeksagent + 2e lezing Claude + EB (2026-10-01)"
S844, U844, T844, P844 = "vlpar-sv-844-2025-for", PF.format(2196828), "SV nr. 844 (2024-2025) Vandeurzen", date(2025, 7, 31)
K844 = "Wachttijd van aanmelding tot eerste directe cliëntencontact Jaartal 2018 2019 2020 2021 2022 2023 2024 Gemiddelde … "
OPM_WT = ("De bron spreekt zichzelf tegen: de tekst noemt 'het gemiddeld aantal dagen van intakegesprek tot moment van aanmelding', de tabelkop "
          "'Wachttijd van aanmelding tot eerste directe cliëntencontact'; definitie volgt de tabelkop. 'Gegevens per gevangenis zijn niet beschikbaar.'")
for jaar, fz, hd in ((2018, 111, 150), (2019, 49, 39), (2020, 60, 47), (2021, 57, 42), (2022, 54, 40), (2023, 56, 39), (2024, 48, 29)):
    opm = OPM_WT + (" 2018 ligt veel hoger dan de latere jaren; de bron verklaart dat niet." if jaar == 2018 else "")
    BEVINDINGEN.append(_b(FOR, "wachttijd_cgg_forensisch_dagen", fz, "dagen", date(jaar, 12, 31), S844, U844, T844, "antwoord 1a, PDF p. 2, tabel",
                          K844 + "Gemiddelde wachttijd forensische zorg CGG 111 49 60 57 54 56 48 54",
                          "Gemiddelde wachttijd (dagen) van aanmelding tot eerste directe cliëntencontact, forensische zorg CGG (retrograde berekend).", GEC, P844, D, opm=opm))
    BEVINDINGEN.append(_b(FOR, "wachttijd_cgg_gevangenis_dagen", hd, "dagen", date(jaar, 12, 31), S844, U844, T844, "antwoord 1a, PDF p. 2, tabel",
                          K844 + "Gemiddelde wachttijd hulp- en dienstverlening in gevangenis CGG 150 39 47 42 40 39 29 42",
                          "Gemiddelde wachttijd (dagen) van aanmelding tot eerste directe cliëntencontact, hulp- en dienstverlening in de gevangenis door de CGG (retrograde berekend).",
                          GEC, P844, D, opm=opm))
K844b = "Reden voortijdige stopzetting hulp- en dienstverlening CGG 2019 2020 2021 2022 2023 2024 … "
for jaar, zp, stop in ((2019, 5731, 1447), (2020, 5174, 1106), (2021, 5544, 1278), (2022, 5837, 1319), (2023, 6137, 1408), (2024, 6992, 1546)):
    BEVINDINGEN.append(_b(FOR, "forensische_zorgperiodes_actief", zp, "zorgperiodes", date(jaar, 12, 31), S844, U844, T844, "antwoord 2, PDF p. 3, tabel",
                          K844b + "Totaal aantal actieve forensische zorgperiodes 5731 5174 5544 5837 6137 6992",
                          "Actieve forensische zorgperiodes bij de CGG in het jaar.", GEC, P844, D, opm="kolomkoppen 2019-2024 (tabel begint bij 2019)"))
    BEVINDINGEN.append(_b(FOR, "forensische_trajecten_voortijdig_gestopt", stop, "trajecten", date(jaar, 12, 31), S844, U844, T844, "antwoord 2, PDF p. 3, tabel",
                          K844b + "Totaal voortijdig stopgezette forensische trajecten 1447 1106 1278 1319 1408 1546",
                          "Voortijdig (vroegtijdig) beëindigde of stopgezette forensische CGG-trajecten, totaal.", GEC, P844, D,
                          opm="De opdeling naar reden (o.a. einde detentie, transfer gevangenis) hoort bij de deelrij 'hulp- en dienstverlening CGG' "
                              "(totaal 785 537 630 666 654 701), niet bij dit totaal; voor 2024 enkel totalen."))
S815, U815, T815, P815 = "vlpar-sv-815-2023-caw", PF.format(1981298), "SV nr. 815 (2022-2023) Wouters", date(2023, 8, 10)
BEVINDINGEN.append(_b(
    FOR, "caw_wachtenden_gevangenissen", 164, "gedetineerden", date(2023, 6, 30), S815, U815, T815, "antwoord 3, PDF p. 3-4, tabel",
    "De wachtlijstgegevens werden verkregen via de sector (d.d. eind juni 2023) … CAW Gevangenis Aantal gedetineerden op de wachtlijst … Mechelen 13 wachten op een onthaal gesprek … "
    "Hoogstraten 26 Wortel 43 Merksplas 8 Turnhout 8 … Hasselt Wachtlijst trajectbegeleiding mannen: 26 … Wachtlijst trajectbegeleiding vrouwen: 1 … "
    "Brugge Begeleiding: op de aanmeldingslijst zijn er momenteel 2 nog niet toegewezen cases. Ruiselede Er wordt niet gewerkt met wachtlijsten. "
    "Leuven Hulp 7 personen Leuven Centraal 30 personen",
    "Gedetineerden op een wachtlijst bij het justitieel welzijnswerk (CAW) per gevangenis, bevraagd bij de sector eind juni 2023; som van de gevangenissen met een wachtlijst "
    "(onthaal, trajectbegeleiding of nog niet toegewezen cases).", GEC, P815, D,
    opm="eigen som: 13 + 26 + 43 + 8 + 8 + 26 + 1 + 2 + 7 + 30 = 164. Niet meegeteld: CAW Oost-Vlaanderen ('Wij werken niet met een wachtlijst'; Gent 16, Oudenaarde 3, "
        "Beveren 15, Dendermonde 11 = 45 personen ingepland voor een fysiek gesprek). Antwerpen, Sint-Gillis, Haren, Kortrijk: geen; Ruiselede: geen wachtlijsten; "
        "Ieper gesloten. Brugge telt cases."))
for jaar, ont, beg in ((2018, 5551, 1232), (2019, 6092, 1137), (2020, 5220, 948), (2021, 5703, 1023), (2022, 5789, 1217)):
    BEVINDINGEN.append(_b(FOR, "caw_gedetineerden_onthaal", ont, "personen", date(jaar, 12, 31), S815, U815, T815, "antwoord 1, PDF p. 2, tabel",
                          "Gedetineerden - onthaal 2018 2019 2020 2021 2022 … Sector 5551 6.092 5.220 5.703 5.789",
                          "Gedetineerden met een onthaal door het CAW (justitieel welzijnswerk) in het jaar, sectortotaal.", *((GEC, P815, D) if jaar == 2022 else (GEL, P815, A)),
                          opm="eenheid: de tabel zegt niet of het om unieke personen gaat" + ("; daling West-Vlaanderen: Ieper gesloten sinds 1-1-2022" if jaar == 2022 else "")))
    BEVINDINGEN.append(_b(FOR, "caw_gedetineerden_begeleiding", beg, "personen", date(jaar, 12, 31), S815, U815, T815, "antwoord 1, PDF p. 2-3, tabel",
                          "Gedetineerden - begeleiding 2018 2019 2020 2021 2022 … Sector 1232 1.137 948 1.023 1.217",
                          "Gedetineerden in begeleiding door het CAW in het jaar, sectortotaal.", *((GEC, P815, D) if jaar == 2022 else (GEL, P815, A)), opm="eenheid: de tabel zegt niet of het om unieke personen gaat"))
P319, U319, T319 = date(2026, 2, 24), PF.format(2281810), "SV nr. 319 (2025-2026) Tombeur"
OPM_TW = "De minister: 'Dit geeft een indicatie van het aantal artikel 60, § 7 tewerkstellingen'; geen telling ervan."
BEVINDINGEN += [
    _b(CAW, "wachttijd_cgg_verslavingsteams_dagen", 45, "dagen", date(2023, 12, 31), "vlpar-sv-568-2025-versl", PF.format(2158191), "SV nr. 568 (2024-2025) Vandeurzen",
       "antwoord 2, PDF p. 4",
       "De wachttijd bij de verslavingszorg teams van de CGG betrof van 2021 tot 2023 gemiddeld 45 dagen tot het eerste cliëntencontact (cijfers 2024 nog niet beschikbaar).",
       "Gemiddelde wachttijd tot het eerste cliëntencontact bij de CGG-verslavingszorgteams, 2021-2023 (peildatum = einde periode).", GEC, date(2025, 5, 22), D,
       opm="'Er is geen structurele monitoring van de wachttijden over alle sectoren heen.' 'Over de gespecialiseerde revalidatievoorzieningen verslavingszorg en de "
           "psychiatrische ziekenhuizen zijn er geen actuele gegevens over de wachttijd beschikbaar.' Er zijn 5 CGG met een verslavingsteam (antwoord 3, huidige stand)."),
    _b(A60, "twe_ocmw_trajecten_tijdig_werk", 9222, "trajecten", date(2024, 12, 31), "vlpar-sv-319-2026-a60", U319, T319, "antwoord 1, PDF p. 3",
       "In 2024 waren er 9.222 lopende TWE-OCMW-trajecten met tijdig werk.",
       "Trajecten Tijdelijke Werkervaring OCMW die in de loop van het jaar liepen en waarbij de art. 60 §7-tewerkstelling binnen twee maanden na de start van het traject "
       "begon (VDAB-monitoring); jaarvolume, geen stand op 31/12.", GEC, P319, D, opm=OPM_TW),
    _b(A60, "twe_ocmw_trajecten_tijdig_werk", 9763, "trajecten", date(2025, 11, 30), "vlpar-sv-319-2026-a60", U319, T319, "antwoord 1, PDF p. 3",
       "In 2025 waren er t.e.m. november 9.763 lopende TWE-OCMW-trajecten met tijdig werk.", "Idem, volume januari t/m november 2025.", GEC, P319, D, opm=OPM_TW),
    _b(A60, "twe_ocmw_uitstroom_werk_pct", 28.8, "procent", date(2024, 12, 31), "vlpar-sv-319-2026-a60", U319, T319, "antwoord 2, PDF p. 3",
       "Voor TWE-OCMW-trajecten die beëindigd werden in 2024 en een eerste resultaatsmeting hadden, ligt de uitstroom naar werk op 28,80 %.",
       "Uitstroom naar werk bij de eerste resultaatsmeting (één dag na het einde van het traject), voor TWE-OCMW-trajecten beëindigd in het jaar.", GEC, P319, D),
    _b(A60, "twe_ocmw_uitstroom_werk_pct", 27.95, "procent", date(2025, 11, 30), "vlpar-sv-319-2026-a60", U319, T319, "antwoord 2, PDF p. 3",
       "Voor TWE-OCMW-trajecten die beëindigd werden in 2025 (t.e.m. november) en een eerste resultaatsmeting hadden, ligt de uitstroom naar werk op 27,95 %.",
       "Idem, trajecten beëindigd in 2025 t/m november.", GEL, P319, A,
       opm="De minister noemt ook een gemiddelde van 39,21 % 'over de voorbije jaren' zonder periode of meting; niet opgenomen."),
    _b(A60, "wijkwerkers_actief", 3365, "personen", date(2025, 12, 31), "vlpar-sv-420-2026-ww", PF.format(2294264), "SV nr. 420 (2025-2026) Bothuyne", "antwoord 1, PDF p. 3",
       "Eind december 2025 waren er 3.365 actieve wijkwerkers:",
       "Actieve wijk-werkers eind december (VDAB); 'Actief wil zeggen met een actieve status en gepresteerde uren' (SV 171).", GEC, date(2026, 3, 17), D,
       opm="de provincies in de bron tellen op tot 3.363"),
    _b(A60, "wijkwerkers_overgangsmaatregel", 1708, "personen", date(2025, 10, 31), "vlpar-sv-171-2025-ww", PF.format(2248963), "SV nr. 171 (2025-2026) Tombeur", "antwoord 1, PDF p. 2",
       "Eind oktober 2025 waren er 1708 actieve wijk-werkers met recht op overgangsmaatregel. Actief wil zeggen met een actieve status en gepresteerde uren.",
       "Actieve wijk-werkers (voormalige PWA'ers) met recht op de overgangsmaatregel.", GEC, date(2025, 12, 22), D),
]

def _bu(vid, jaar, fase, niveau, bedrag, bron_id, url, titel, pagina, passage, status, door="", krediet=Kredietsoort.NVT, artikel="", programma="", ise="", label="", opm=""):
    key = artikel or label.replace(" ", "_")[:40]
    return Budget(budget_id=f"{vid}:{jaar}:{fase.value}:{niveau}:{krediet.value}:{key}", voorziening_id=vid, begrotingsjaar=jaar, fase=fase, niveau=niveau, bedrag_eur=bedrag,
                  kredietsoort=krediet, artikel_code=artikel, programma=programma, ise=ise, label=label, bron_id=bron_id, bron_url=url, documenttitel=titel, pagina=pagina,
                  passage=passage, controlestatus=status, gecontroleerd_door=door, gecontroleerd_op=VANDAAG if door else None, opmerking=opm)


BUDGETTEN = [
    _bu(A60, 2026, Budgetfase.AGENTSCHAP, "beleidsenveloppe", 9_166_461, "vlpar-sv-420-2026-ww", PF.format(2294264), "SV nr. 420 (2025-2026) Bothuyne", "antwoord 7, PDF p. 3",
        "VDAB heeft in 2026 een bedrag van 9.166.461 euro gepland. Dit is opgesplitst naar: a) inzet wijk-werkbemiddelaars: 8.747.658 euro b) Werkingskosten: 543.606 euro "
        "c) Wijk-werken organisatoren 1.791.511 euro d) Wijk-werken gebruikersbijdragen 49.153 euro e) Prestatievergoeding 3.339.519 euro f) Verplaatsingsvergoeding 336.904 euro "
        "g) Wijk-werken inkomsten uit cheques -5.590.350 euro h) Wijk-werken gebruikersbijdrage -45.540 euro", GEC, D, label="VDAB-budget wijk-werken (gepland)",
        opm="De deelposten in de bron tellen op tot 9.172.461 euro, 6.000 euro meer dan het vermelde totaal (fout in de bron); bedrag = het totaal van de minister."),
]


def main() -> None:
    nb = upsert("bronnen", BRONNEN)
    _update_voorzieningen()
    nv = upsert("bevindingen", BEVINDINGEN)
    nu = upsert("budgetten", BUDGETTEN)
    print(f"ronde 5b: bronnen {nb}, bevindingen {nv}, budgetten {nu} (upsert); draai 'wachtlijst validate' en 'wachtlijst publish'")


if __name__ == "__main__":
    main()
