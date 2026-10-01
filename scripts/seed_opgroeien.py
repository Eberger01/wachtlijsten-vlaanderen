"""Proefdossiers 3 en 4 (Agentschap Opgroeien): jeugdhulp NRTJ en kinderopvang baby's en peuters.

Draai: ``python scripts/seed_opgroeien.py``  — voegt toe/overschrijft op sleutel (upsert) in data/curated,
zonder de rijen van seed_proef.py aan te raken. Volgorde: eerst seed_proef.py, dan dit script.

Bronnen gelezen op 1-10-2026. Controlestatus: gecontroleerd = twee onafhankelijke lezingen (onderzoeksagent + Claude);
bron_gelezen = één lezing; ongecontroleerd = secundaire bron of mondeling cijfer; betwist = bronnen spreken elkaar tegen.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from wachtlijst.models import (  # noqa: E402
    Bevinding, Bron, BronType, Budget, Budgetfase, Controlestatus, Kredietsoort, WachtlijstType,
)
from wachtlijst.store import load, upsert  # noqa: E402

VANDAAG = date(2026, 10, 1)
GEC, GEL, ONG, BET = (Controlestatus.GECONTROLEERD, Controlestatus.BRON_GELEZEN,
                      Controlestatus.ONGECONTROLEERD, Controlestatus.BETWIST)
A = "onderzoeksagent (2026-10-01)"
D2 = "onderzoeksagent + 2e lezing Claude (2026-10-01)"
D_EB = "onderzoeksagent + 2e lezing Claude + EB (2026-10-01)"
PF = "https://docs.vlaamsparlement.be/files/pfile?id={}"

# ----------------------------------------------------------------------------------------------- bronnen
BRONNEN = [
    Bron(bron_id="opgroeien-nrtj", naam="Opgroeien — aanvragen crisisjeugdhulp en niet-rechtstreeks toegankelijke jeugdhulp (cijferrapport)", organisatie="Agentschap Opgroeien",
         url="https://www.opgroeien.be/kennis/cijfers-en-onderzoek/aanvragen-crisisjeugdhulp-en-niet-rechtstreeks-toegankelijke-jeugdhulp",
         bron_type=BronType.HTML, frequentie="jaarlijks (cijfers 31/12 verschijnen ± januari–juli)",
         machinaal="HTML met vaste zinsstructuur 'Op 31 december JJJJ stonden in totaal N kinderen en jongeren op een NRTJ-wachtlijst'; Power BI 'cijfers op maat' zonder download",
         opmerking="Laatst gewijzigd 16-07-2026. Definitie 2025 expliciet 'inclusief wachtend op zorg door een MFC, exclusief PAB'."),
    Bron(bron_id="opgroeien-nrtj-achtergrond", naam="Opgroeien — achtergrondinformatie en documentatie bij de jeugdhulpcijfers (definities)", organisatie="Agentschap Opgroeien",
         url="https://www.opgroeien.be/kennis/cijfers-en-onderzoek/aanvragen-crisisjeugdhulp-en-niet-rechtstreeks-toegankelijke-jeugdhulp/achtergrondinformatie-en-documentatie",
         bron_type=BronType.HTML, frequentie="doorlopend"),
    Bron(bron_id="vlpar-sv-50-2021", naam="SV nr. 50 (2021-2022), Vaneeckhout → min. Beke, 'Jeugdhulp — capaciteit en wachttijden'", organisatie="Vlaams Parlement",
         url=PF.format(1770292), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="vraag 13-10-2021; reeks 2017/2019/2020"),
    Bron(bron_id="vlpar-sv-341-2024", naam="SV nr. 341 (2023-2024), Vaneeckhout → min. Crevits — wachtenden NRTJ per sector 2017-2022", organisatie="Vlaams Parlement",
         url=PF.format(2062865), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 07-06-2024; bevat ook provinciale tabellen"),
    Bron(bron_id="vlpar-sv-242-2026", naam="SV nr. 242 (2025-2026), Ryde → min. Gennez — evolutie wachtenden NRTJ en PAB", organisatie="Vlaams Parlement",
         url=PF.format(2261521), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 29-01-2026"),
    Bron(bron_id="vlpar-sv-246-2026", naam="SV nr. 246 (2025-2026), Vandecasteele — wachtenden NRTJ 2023 (citeert Opgroeien-site)", organisatie="Vlaams Parlement",
         url=PF.format(2261523), bron_type=BronType.PDF, frequentie="eenmalig"),
    Bron(bron_id="vlpar-sv-416-2023", naam="SV nr. 416 (2022-2023) — wachtenden PAB en MFC op 31-12-2022", organisatie="Vlaams Parlement",
         url=PF.format(1935207), bron_type=BronType.PDF, frequentie="eenmalig"),
    Bron(bron_id="cjm-kinderrechtenmonitor", naam="Kinderrechtenmonitor (Departement CJM) — thema alternatieve zorg (citeert Opgroeien)", organisatie="Departement Cultuur, Jeugd en Media (secundair)",
         url="https://www.vlaanderen.be/cjm/nl/jeugd/vlaams-jeugd-en-kinderrechtenbeleid/tools-voor-beleidsmakers/kinderrechtenmonitor/alternatieve-zorg",
         bron_type=BronType.HTML, frequentie="jaarlijks"),
    Bron(bron_id="vlpar-commissie-2020-10-20", naam="Commissie Welzijn 20-10-2020 — bespreking Jaarverslag Jeugdhulp 2019", organisatie="Vlaams Parlement",
         url="https://www.vlaamsparlement.be/nl/parlementair-werk/commissies/commissievergaderingen/1430487/verslag/1434312", bron_type=BronType.HTML, frequentie="eenmalig"),
    Bron(bron_id="vlpar-bbt-wvg-2026", naam="BBT Welzijn en Armoedebestrijding, begroting 2026 — stuk 13-Z (2025-2026) nr. 1", organisatie="Vlaams Parlement",
         url=PF.format(2227516), bron_type=BronType.PDF, frequentie="jaarlijks"),
    Bron(bron_id="vlpar-bbt-wvg-uitv-2025", naam="BBT WVG begrotingsuitvoering 2025 — stuk 23-V (2025-2026) nr. 1", organisatie="Vlaams Parlement",
         url=PF.format(2325132), bron_type=BronType.PDF, frequentie="jaarlijks"),
    Bron(bron_id="vlpar-bbt-wvg-uitv-2024", naam="BBT WVG begrotingsuitvoering 2024 — stuk 23-T (2024-2025) nr. 1", organisatie="Vlaams Parlement",
         url=PF.format(2162480), bron_type=BronType.PDF, frequentie="jaarlijks"),
    Bron(bron_id="vlpar-bbt-wvg-2025", naam="BBT WVG en Armoedebestrijding, begroting 2025 — stuk 13-V (2024-2025) nr. 1", organisatie="Vlaams Parlement",
         url=PF.format(2081035), bron_type=BronType.PDF, frequentie="jaarlijks"),
    Bron(bron_id="vlpar-sv-852-2025", naam="SV nr. 852 (2024-2025), Schryvers → min. Gennez — lokale loketten kinderopvang, registratie 2023-2024", organisatie="Vlaams Parlement",
         url=PF.format(2196812), bron_type=BronType.PDF, frequentie="jaarlijks (zelfde vraag elk jaar)", opmerking="vraag 06-06-2025; dubbeltellingen over loketten heen mogelijk"),
    Bron(bron_id="vlpar-sv-650-2026", naam="SV nr. 650 (2025-2026), Schryvers — lokale loketten kinderopvang, cijfers 2025 nog niet beschikbaar", organisatie="Vlaams Parlement",
         url=PF.format(2308258), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="vraag 13-03-2026; cijfers 2025 'ten vroegste mei 2026'"),
    Bron(bron_id="vlpar-sv-664-2023", naam="SV nr. 664 (2022-2023), Daniëls → min. Crevits — onderzoek kinderopvang 2018 en uitbreiding 2023", organisatie="Vlaams Parlement",
         url=PF.format(1969521), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="vraag 05-05-2023"),
    Bron(bron_id="vlpar-commissie-2025-06-10", naam="Commissie WVG 10-06-2025 — vragen om uitleg over onbeantwoorde opvangvragen", organisatie="Vlaams Parlement",
         url="https://www.vlaamsparlement.be/nl/parlementair-werk/commissies/commissievergaderingen/1911758/verslag/1917726", bron_type=BronType.HTML, frequentie="eenmalig"),
    Bron(bron_id="opgroeien-onderzoek-2025-rapport", naam="HIVA/Opgroeien — Onderzoek naar het gebruik van en de behoefte aan kinderopvang 2025 (rapport nr. 57)", organisatie="Agentschap Opgroeien / HIVA-KU Leuven",
         url="https://www.opgroeien.be/sites/default/files/tool-documents/2026_01_rapport_57_ef__53_gebruik_behoefte_kinderopvang.pdf", bron_type=BronType.PDF, frequentie="± 7-jaarlijks (2018, 2025)",
         opmerking="januari 2026; steekproef 4.114 gezinnen, respons 19 %"),
    Bron(bron_id="opgroeien-onderzoek-2025-nieuws", naam="Opgroeien — nieuwsbericht onderzoek kinderopvang 2025: gebruik, noden en een groeiend tekort aan plaatsen", organisatie="Agentschap Opgroeien",
         url="https://www.opgroeien.be/over-opgroeien/nieuws-en-pers/onderzoek-kinderopvang-2025-gebruik-noden-en-een-groeiend-tekort-aan-plaatsen", bron_type=BronType.HTML, frequentie="eenmalig",
         opmerking="09-03-2026; bevat de prognose 11.500 plaatsen tegen 2029 (niet in het rapport zelf)"),
    Bron(bron_id="opgroeien-kinderopvang-cijfers", naam="Opgroeien — kinderopvang baby's en peuters, cijfers (Power BI + Excel 'cijfers op maat')", organisatie="Agentschap Opgroeien",
         url="https://www.opgroeien.be/kennis/cijfers-en-onderzoek/kinderopvang-babys-en-peuters/cijfers-op-maat", bron_type=BronType.DOWNLOAD, frequentie="jaarlijks + kwartaal",
         machinaal="Excel 'b-p-aantal-plaatsen-en-locaties-naar-vergunningstype-en-inkomenstarief_<n>.xlsx' (2014–2026/kw1, gemeenteniveau; versie-suffix wijzigt) en 'aantal-plaatsen-per-100-kinderen_<n>.xlsx'; scrape de pagina op href=*.xlsx",
         opmerking="Correctie 04-06-2026: ± 2.500 onthaalouderplaatsen 2020-2024 te hoog geteld."),
    Bron(bron_id="opgroeien-persbericht-2026-06-04", naam="Opgroeien persbericht 04-06-2026 — kinderopvangcijfers 2025 en correctie cijfers onthaalouders", organisatie="Agentschap Opgroeien",
         url="https://pers.opgroeien.be/opgroeien-publiceert-kinderopvangcijfers-2025-en-kondigt-correctie-cijfers-onthaalouders-aan", bron_type=BronType.HTML, frequentie="eenmalig"),
    Bron(bron_id="opgroeien-masterplan-2025", naam="Opgroeien — Masterplan kinderopvang, meerjarenprogrammatie (snelinfo 07-04-2025)", organisatie="Agentschap Opgroeien",
         url="https://www.opgroeien.be/sites/default/files/documenten/masterplan-kinderopvang-meerjarenprogrammatie-snelinfo.pdf", bron_type=BronType.PDF, frequentie="eenmalig"),
    Bron(bron_id="opgroeien-sectoroverleg-2025-11", naam="Opgroeien — algemene presentatie sectoroverleg kinderopvang 28-11-2025 (meerjarenoproep T2)", organisatie="Agentschap Opgroeien",
         url="https://www.opgroeien.be/sites/default/files/documenten/algemene-presentatie-28-november-2025.pdf", bron_type=BronType.PDF, frequentie="eenmalig"),
    Bron(bron_id="opgroeien-oproepen-beslissingen", naam="Opgroeien — oproepen en beslissingen subsidies kinderopvang (overzicht per ronde)", organisatie="Agentschap Opgroeien",
         url="https://www.opgroeien.be/aanbod/kinderopvang/voorzieningen/subsidies-en-financieel/oproepen-en-beslissingen", bron_type=BronType.HTML, frequentie="per ronde",
         machinaal="PDF-lijsten per ronde (toekenningen per gemeente/organisator)"),
    Bron(bron_id="opgroeien-toekenning-t2-2025", naam="Opgroeien — plaatsen met subsidie voor inkomenstarief 2025-2029, beslissingen december 2025 (toekenning T2)", organisatie="Agentschap Opgroeien",
         url="https://www.opgroeien.be/sites/default/files/documenten/oproep-meerjarenprogrammatie-toekenning-subsidiebeloftes-t2-ikt-kinderopvang.pdf", bron_type=BronType.PDF, frequentie="per ronde",
         opmerking="datum 15-12-2025; toekenningen per gemeente en tabel per jaar (p. 13)"),
    Bron(bron_id="vlpar-begroting-2023-vragen", naam="Vragen en antwoorden bij de begroting 2023 — uitbreidingsbudget kinderopvang", organisatie="Vlaams Parlement",
         url=PF.format(1897634), bron_type=BronType.PDF, frequentie="eenmalig"),
]

# ------------------------------------------------------------------------------------------ voorzieningen
def _update_voorzieningen() -> None:
    vz = {v.voorziening_id: v for v in load("voorzieningen")}
    n = vz["opgroeien-nrtj"]
    n.scan_status = "proef_uitgewerkt"
    n.laatste_peildatum = date(2025, 12, 31)
    n.wachtlijst_type = WachtlijstType.CENTRAAL_GEPUBLICEERD
    n.publicatie_bron_id = "opgroeien-nrtj"
    n.frequentie = "jaarlijks (foto op 31/12; publicatie januari–juli)"
    n.ise_koppeling = "JEUGDHULP"
    n.opmerking = ("Foto op 31/12 van alle kinderen/jongeren met een indicatiestelling in regie zonder opstart van de gevraagde hulp (excl. PAB; MFC inbegrepen). "
                   "± 52 % krijgt intussen andere NRTJ-hulp. Wachttijden worden officieel niet gepubliceerd (SV 341/1045/1048: 'onvoldoende betrouwbare gegevens'). "
                   "Reeks 2017–2025 heeft lichte breuken (2022: 7.397 vs 7.448; 2024: 9.194 vs 9.154 VRT).")
    k = vz["opgroeien-kinderopvang"]
    k.scan_status = "proef_uitgewerkt"
    k.laatste_peildatum = date(2025, 12, 31)
    k.wachtlijst_type = WachtlijstType.DECENTRAAL
    k.publicatie_bron_id = "vlpar-sv-852-2025"
    k.frequentie = "jaarlijks (opvangvragen via SV; capaciteit Excel per jaar/kwartaal)"
    k.ise_koppeling = "GEINTEGREERD GEZINSBELEID"
    k.opmerking = ("Geen Vlaamse wachtlijst voor gezinnen. Drie schaarste-indicatoren: (1) onbeantwoorde opvangvragen bij de lokale loketten (dubbeltellingen over gemeenten mogelijk), "
                   "(2) onvervulde behoefte uit steekproefonderzoek (2018: 8,3 %; 2025: 11,6 %, alle kinderen 3 m–3 j), (3) gerangschikte lijst van organisatoren in uitbreidingsrondes (aangevraagd vs toegekend). "
                   "Capaciteit 2020-2024 bevat ± 2.500 te hoog getelde onthaalouderplaatsen (correctie 04-06-2026).")
    upsert("voorzieningen", [n, k])


# ------------------------------------------------------------------------------------------- bevindingen
def _b(vid, metriek, waarde, eenheid, peildatum, bron_id, url, titel, pagina, passage, definitie, status, pub=None, door="", opm=""):
    return Bevinding(
        bevinding_id=f"{vid}:{metriek}:{peildatum.isoformat()}", voorziening_id=vid, metriek=metriek, waarde=waarde, eenheid=eenheid,
        peildatum=peildatum, bron_id=bron_id, bron_url=url, documenttitel=titel, pagina=pagina, passage=passage, definitie=definitie,
        publicatiedatum=pub, controlestatus=status, gecontroleerd_door=door, gecontroleerd_op=VANDAAG if door else None, opmerking=opm,
    )


NR = "opgroeien-nrtj"
KO = "opgroeien-kinderopvang"
UNR = "https://www.opgroeien.be/kennis/cijfers-en-onderzoek/aanvragen-crisisjeugdhulp-en-niet-rechtstreeks-toegankelijke-jeugdhulp"
DEF_NRTJ = ("Unieke kinderen/jongeren die op 31/12 op een NRTJ-wachtlijst staan: indicatiestelling via de intersectorale toegangspoort, vraag in regie, "
            "gevraagde hulp nog niet opgestart; exclusief PAB, inclusief wachtenden op een MFC. Een deel krijgt intussen andere NRTJ- of RTJ-hulp.")
DEF_KH = "Door de gesubsidieerde lokale loketten kinderopvang geregistreerde opvangvragen (één unieke aanvrager + één uniek kind) in het kalenderjaar; dubbeltellingen over gemeenten mogelijk."
DEF_ONB = "Geregistreerde opvangvragen waarvoor het lokaal loket geen plaats vond (vervallen vragen tellen niet mee); dubbeltellingen over gemeenten mogelijk."
DEF_PL = "Vergunde plaatsen kinderopvang baby's en peuters op 31/12 (Vlaams Gewest + Brussel), alle vergunningstypes; 2020-2024 incl. ± 2.500 te hoog getelde onthaalouderplaatsen."
P_ONV18 = ("8,31% van de kinderen (14.831 kinderen) tussen 3 maanden en 3 jaar in het Vlaams Gewest een onvervulde behoefte heeft aan formele opvang")
P_ZONDER ="Het aantal unieke kinderen en jongeren dat wacht zonder NRTJ hulp bedroeg op 31/12/2023 4166 en op 31/12/2024 4559"

BEVINDINGEN = [
    # --- NRTJ hoofdreeks
    _b(NR, "wachtenden_nrtj", 5273, "personen", date(2017, 12, 31), "vlpar-sv-50-2021", PF.format(1770292), "SV nr. 50 (2021-2022), Vaneeckhout → Beke", "antwoord p. 3",
       "van 25 procent in 2017 (1.361/5.273) tot 37 procent in 2020 (2.305/6.113)", DEF_NRTJ + " Noemer van het aandeel met NRTJ-alternatief.", GEC, date(2021, 12, 10), D2),
    _b(NR, "wachtenden_nrtj", 5600, "personen", date(2018, 12, 31), "vlpar-commissie-2020-10-20", "https://www.vlaamsparlement.be/nl/parlementair-werk/commissies/commissievergaderingen/1430487/verslag/1434312",
       "Commissie Welzijn 20-10-2020 — Jaarverslag Jeugdhulp 2019", "tussenkomst minister Beke", "In 2019 stonden 5543 kinderen en jongeren op een lijst voor gespecialiseerde en intensieve jeugdhulp. Dat zijn er iets minder dan het jaar voordien. Toen waren het er ongeveer 5600.",
       DEF_NRTJ, ONG, date(2020, 10, 20), "", "afgerond cijfer ('ongeveer 5600'); exact cijfer uit Jaarverslag Jeugdhulp 2018 nog op te zoeken"),
    _b(NR, "wachtenden_nrtj", 5543, "personen", date(2019, 12, 31), "vlpar-sv-50-2021", PF.format(1770292), "SV nr. 50 (2021-2022), Vaneeckhout → Beke", "antwoord p. 3",
       "Dat zijn er ongeveer 10 procent meer dan in 2019 (5.543).", DEF_NRTJ, GEC, date(2021, 12, 10), D2),
    _b(NR, "wachtenden_nrtj", 6113, "personen", date(2020, 12, 31), "vlpar-sv-50-2021", PF.format(1770292), "SV nr. 50 (2021-2022), Vaneeckhout → Beke", "antwoord p. 3",
       "Op 31 december 2020 stonden in totaal 6.113 kinderen en jongeren op een NRTJ-wachtlijst (exclusief Persoonlijke assistentiebudget (PAB)). Dat zijn er ongeveer 10 procent meer dan in 2019 (5.543).",
       DEF_NRTJ, GEC, date(2021, 12, 10), D2, "37 % (2.305) kreeg intussen een NRTJ-alternatief"),
    _b(NR, "wachtenden_nrtj", 6985, "personen", date(2021, 12, 31), "cjm-kinderrechtenmonitor", "https://www.vlaanderen.be/cjm/nl/jeugd/vlaams-jeugd-en-kinderrechtenbeleid/tools-voor-beleidsmakers/kinderrechtenmonitor/alternatieve-zorg",
       "Kinderrechtenmonitor — alternatieve zorg", "tekst (bron: website Opgroeien)", "Dat is ongeveer 6% meer dan in 2021 (6.985)", DEF_NRTJ, ONG, None, "", "secundaire bron die Opgroeien citeert; SV 614 noemt foutief 6113 voor 2021"),
    _b(NR, "wachtenden_nrtj", 7448, "personen", date(2022, 12, 31), "cjm-kinderrechtenmonitor", "https://www.vlaanderen.be/cjm/nl/jeugd/vlaams-jeugd-en-kinderrechtenbeleid/tools-voor-beleidsmakers/kinderrechtenmonitor/alternatieve-zorg",
       "Kinderrechtenmonitor — alternatieve zorg", "tekst", "Op 31 december 2022 stonden in totaal 7.448 kinderen en jongeren op een NRTJ-wachtlijst (exclusief Persoonlijke assistentiebudget (PAB)). Dat is ongeveer 6% meer dan in 2021 (6.985) en bedraagt iets meer dan de helft (56,22%) van het totaal aantal aanmeldingen.",
       DEF_NRTJ, BET, None, A, "SV 341 (19-04-2024) geeft 7.397 voor 31-12-2022 ('Jaarrapport van Opgroeien'); SV 246 citeert 7448 — vermoedelijk herberekening"),
    _b(NR, "wachtenden_nrtj", 8545, "personen", date(2023, 12, 31), "vlpar-sv-246-2026", PF.format(2261523), "SV nr. 246 (2025-2026), Vandecasteele", "vraag, PDF p. 1 (citeert Opgroeien-site)",
       "Op 31 december 2023 stonden in totaal 8545 kinderen en jongeren op een NRTJ-wachtlijst (exclusief het persoonlijkeassistentiebudget(PAB)). Dat is ongeveer 15 procent meer dan in 2022 (7448).",
       DEF_NRTJ, GEC, date(2026, 1, 29), D_EB, "citaat van de (intussen overschreven) Opgroeien-pagina in de vraag; definitie-details uit de Opgroeien-achtergrondpagina"),
    _b(NR, "wachtenden_nrtj", 9194, "personen", date(2024, 12, 31), "opgroeien-nrtj", UNR, "Opgroeien — cijferrapport NRTJ", "sectie 'Wachtenden niet-rechtstreeks toegankelijke jeugdhulp'",
       "Dat zijn er 6 procent meer dan in 2024 (9.194).", DEF_NRTJ, GEC, date(2026, 7, 16), D2, "VRT 22-01-2026 meldt 9.154 (afwijking 40); SV 242 bevestigt 9194"),
    _b(NR, "wachtenden_nrtj", 9748, "personen", date(2025, 12, 31), "opgroeien-nrtj", UNR, "Opgroeien — cijferrapport NRTJ", "sectie 'Wachtenden niet-rechtstreeks toegankelijke jeugdhulp'",
       "Op 31 december 2025 stonden in totaal 9.748 kinderen en jongeren op een NRTJ-wachtlijst (inclusief wachtend op zorg door een MFC, exclusief Persoonlijke assistentiebudget (PAB)). Dat zijn er 6 procent meer dan in 2024 (9.194). Die stijging is te verklaren door een stabiele instroom van vragen in combinatie met een tragere opstart van hulp.",
       DEF_NRTJ, GEC, date(2026, 7, 16), D2, "51,6 % krijgt intussen andere NRTJ-hulp; 812 wachtenden zonder NRTJ kregen RTJ-hulp"),
    # --- NRTJ: wachtenden zonder enige NRTJ-hulp
    _b(NR, "wachtenden_nrtj_zonder_hulp", 4166, "personen", date(2023, 12, 31), "vlpar-sv-242-2026", PF.format(2261521), "SV nr. 242 (2025-2026), Ryde → Gennez", "antwoord, PDF p. 3",
       P_ZONDER, "Wachtenden die op 31/12 geen enkele NRTJ-hulp lopen hebben.", GEC, date(2026, 1, 29), D_EB),
    _b(NR, "wachtenden_nrtj_zonder_hulp", 4559, "personen", date(2024, 12, 31), "vlpar-sv-242-2026", PF.format(2261521), "SV nr. 242 (2025-2026), Ryde → Gennez", "antwoord, PDF p. 3",
       P_ZONDER, "Wachtenden die op 31/12 geen enkele NRTJ-hulp lopen hebben.", GEC, date(2026, 1, 29), D_EB),
    # --- NRTJ: instroom en opstart
    _b(NR, "aanmeldingen_a_document", 13249, "personen", date(2022, 12, 31), "cjm-kinderrechtenmonitor", "https://www.vlaanderen.be/cjm/nl/jeugd/vlaams-jeugd-en-kinderrechtenbeleid/tools-voor-beleidsmakers/kinderrechtenmonitor/alternatieve-zorg",
       "Kinderrechtenmonitor — alternatieve zorg", "tekst", "aantal aanmeldingen 2022: 13.249", "Unieke kinderen/jongeren met een aanmelding (A-document) bij de intersectorale toegangspoort in het jaar.", ONG, None, "", "secundair"),
    _b(NR, "aanmeldingen_a_document", 14870, "personen", date(2024, 12, 31), "vlpar-sv-242-2026", PF.format(2261521), "SV nr. 242 (2025-2026)", "antwoord, PDF p. 3",
       "Aantal kinderen en jongeren met een aanmelding bij de toegangspoort: 14.870",
       "Unieke kinderen/jongeren met een aanmelding (A-document) bij de intersectorale toegangspoort in het jaar.", GEC, date(2026, 1, 29), D_EB,
       "jaarcijfer 2024; 'A-document' komt uit de Opgroeien-formulering van dezelfde reeks (2025: 15.446)"),
    _b(NR, "aanmeldingen_a_document", 15446, "personen", date(2025, 12, 31), "opgroeien-nrtj", UNR, "Opgroeien — cijferrapport NRTJ", "sectie aanmeldingen",
       "Het aantal kinderen en jongeren met een aanmelding bij de intersectorale toegangspoort door middel van een A document is in 2025 gestegen naar 15.446 (+3,9%). Het betreft hier ongeveer 0,68% van de bevolking (0-25 jaar)",
       "Unieke kinderen/jongeren met een aanmelding (A-document) bij de intersectorale toegangspoort in het jaar.", GEC, date(2026, 7, 16), D2),
    _b(NR, "nieuwe_hulpvraag", 12314, "personen", date(2024, 12, 31), "vlpar-sv-242-2026", PF.format(2261521), "SV nr. 242 (2025-2026)", "antwoord, PDF p. 3",
       "Aantal kinderen en jongeren met een nieuwe aanmelding bij de toegangspoort: 12.314",
       "Unieke kinderen/jongeren voor wie een typemodule voor het eerst in regie werd genomen.", GEC, date(2026, 1, 29), D_EB,
       "SV 242 noemt dit 'nieuwe aanmelding bij de toegangspoort'; Opgroeien noemt dezelfde reeks 'nieuwe hulpvraag' (2025: 12.897, '+4,9 %'; t.o.v. 12.314 is dat +4,7 %). "
       "Niet te verwarren met 'nieuwe hulpvragen NRTJ-hulp bij een voorziening en/of pleegzorg' (9.945)"),
    _b(NR, "nieuwe_hulpvragen_voorziening", 9945, "hulpvragen", date(2024, 12, 31), "vlpar-sv-242-2026", PF.format(2261521), "SV nr. 242 (2025-2026)", "antwoord, PDF p. 3",
       "Aantal nieuwe hulpvragen NRTJ-hulp bij een voorziening en/of pleegzorg: 9945",
       "Nieuwe hulpvragen naar NRTJ-hulp bij een voorziening en/of pleegzorg in het jaar (hulpvragen, niet unieke personen).", GEC, date(2026, 1, 29), D_EB),
    _b(NR, "nieuwe_hulpvraag", 12897, "personen", date(2025, 12, 31), "opgroeien-nrtj", UNR, "Opgroeien — cijferrapport NRTJ", "sectie hulpvragen",
       "Het aantal kinderen en jongeren met een nieuwe hulpvraag is toegenomen (+ 4,9%, 12.897 in 2025)", "Unieke kinderen/jongeren voor wie een typemodule voor het eerst in regie werd genomen.", GEC, date(2026, 7, 16), D2),
    _b(NR, "nieuwe_vragen_verblijf", 5756, "vragen", date(2025, 12, 31), "opgroeien-nrtj", UNR, "Opgroeien — cijferrapport NRTJ", "sectie hulpvragen",
       "De grootste groep zijn 5.756 vragen voor verblijf, waarvan 2707 voor een pleeggezin.", "Nieuwe hulpvragen naar typemodule verblijf in het jaar.", GEC, date(2026, 7, 16), D2),
    _b(NR, "nieuwe_vragen_pleeggezin", 2707, "vragen", date(2025, 12, 31), "opgroeien-nrtj", UNR, "Opgroeien — cijferrapport NRTJ", "sectie hulpvragen",
       "De grootste groep zijn 5.756 vragen voor verblijf, waarvan 2707 voor een pleeggezin.", "Nieuwe hulpvragen naar verblijf in een pleeggezin in het jaar.", GEC, date(2026, 7, 16), D2),
    _b(NR, "nrtj_opgestart_personen", 6419, "personen", date(2024, 12, 31), "vlpar-sv-242-2026", PF.format(2261521), "SV nr. 242 (2025-2026)", "antwoord, PDF p. 3",
       "Aantal opgestarte NRTJ-hulp bij een voorziening en/of pleegzorg: 6419",
       "Unieke kinderen/jongeren voor wie in het jaar NRTJ-hulp opstartte bij een voorziening van Opgroeien, het VAPH of via pleegzorg.", GEC, date(2026, 1, 29), D_EB,
       "SV 242 zegt 'opgestarte NRTJ-hulp'; Opgroeien beschrijft dezelfde reeks als kinderen en jongeren (2025: 6.801, '+6 % t.o.v. 2024')"),
    _b(NR, "nrtj_opgestart_personen", 6801, "personen", date(2025, 12, 31), "opgroeien-nrtj", UNR, "Opgroeien — cijferrapport NRTJ", "sectie opstart",
       "Het grootste deel van de kinderen en jongeren waarvoor jeugdhulp opstartte in 2025, kon een beroep doen op hulp van een jeugdhulpvoorziening van Opgroeien of het VAPH of via pleegzorg (6.801 in 2025, +6% ten opzichte van 2024)",
       "Unieke kinderen/jongeren voor wie in het jaar NRTJ-hulp opstartte bij een voorziening van Opgroeien, het VAPH of via pleegzorg.", GEC, date(2026, 7, 16), D2),
    # --- NRTJ: PAB en MFC (apart geteld)
    _b(NR, "wachtenden_pab", 1478, "personen", date(2022, 12, 31), "vlpar-sv-416-2023", PF.format(1935207), "SV nr. 416 (2022-2023)", "antwoord, PDF p. 3",
       "1478 unieke kinderen en jongeren hadden een vraag naar ondersteuning via PAB", "Unieke minderjarigen met een openstaande PAB-vraag op 31/12 (apart van de NRTJ-reeks).", GEC, None, D_EB,
       "volgens de bron ligt de startdatum van de wachttijd voor elk van hen na 1 februari 2017"),
    _b(NR, "wachtenden_pab", 1763, "personen", date(2024, 12, 31), "vlpar-sv-242-2026", PF.format(2261521), "SV nr. 242 (2025-2026)", "antwoord, PDF p. 3",
       "Evolutie aantal kinderen en jongeren dat wacht op een persoonlijkeassistentiebudget (PAB): 1763",
       "Unieke minderjarigen met een openstaande PAB-vraag op 31/12 (apart van de NRTJ-reeks).", GEC, date(2026, 1, 29), D_EB,
       "waarvan 1.106 zonder andere NRTJ-hulp (31/12/2023: 796); peildatum 31/12/2024 af te leiden uit de reeks, niet expliciet in deze regel"),
    _b(NR, "wachtenden_mfc", 2733, "personen", date(2022, 12, 31), "vlpar-sv-416-2023", PF.format(1935207), "SV nr. 416 (2022-2023)", "antwoord, PDF p. 3",
       "Op 31 december 2022 hadden 2733 kinderen en jongeren een vraag naar ondersteuning in een MFC", "Minderjarigen met een openstaande vraag naar een multifunctioneel centrum (VAPH) op 31/12.", GEC, None, D_EB,
       "SV 341 geeft voor het VAPH-subtotaal 2022 2731"),
]
# --- NRTJ per sector (SV 341): unieke personen per sector, som ≠ totaal
SV341_JHO = "wachtenden op 31/12/xxxx (unieke mj) 2017 2018 2019 2020 2021 2022 … JHO … Subtotaal 2989 3216 3432 4108 4585 4912"
SV341_VAPH = "wachtenden op 31/12/xxxx (unieke mj) 2017 2018 2019 2020 2021 2022 … VAPH … Subtotaal 2378 2498 2234 2143 2610 2731"
for jaar, jho, vaph in ((2017, 2989, 2378), (2018, 3216, 2498), (2019, 3432, 2234), (2020, 4108, 2143), (2021, 4585, 2610), (2022, 4912, 2731)):
    for m, v, lab, passage in (("wachtenden_nrtj_sector_jho", jho, "JHO (jeugdhulpvoorzieningen Opgroeien)", SV341_JHO),
                               ("wachtenden_nrtj_sector_vaph", vaph, "VAPH", SV341_VAPH)):
        BEVINDINGEN.append(_b(NR, m, v, "personen", date(jaar, 12, 31), "vlpar-sv-341-2024", PF.format(2062865), "SV nr. 341 (2023-2024), Vaneeckhout → Crevits",
                              "antwoord, PDF p. 2, tabel 'Vlaanderen en Brussel' ('aard van de wachtenden bij de intersectorale toegangspoort')",
                              passage, f"Unieke wachtenden naar sector {lab} op 31/12; iemand kan in meerdere sectoren wachten.", GEC, date(2024, 6, 7), D_EB))

# --- Kinderopvang
BEVINDINGEN += [
    _b(KO, "opvangvragen_lokale_loketten", 57105, "vragen", date(2023, 12, 31), "vlpar-sv-852-2025", PF.format(2196812), "SV nr. 852 (2024-2025), Schryvers → Gennez", "antwoord, tabel per provincie",
       "totaal 2023: 57.105 (Antwerpen 14.377; Brussel 5.946; Limburg 4.434; Oost-Vl. 12.202; Vl.-Brabant 13.776; West-Vl. 6.370)", DEF_KH, GEC, date(2025, 7, 29), D2),
    _b(KO, "opvangvragen_lokale_loketten", 71268, "vragen", date(2024, 12, 31), "vlpar-sv-852-2025", PF.format(2196812), "SV nr. 852 (2024-2025), Schryvers → Gennez", "antwoord, tabel per provincie",
       "totaal 2024: 71.268 (Antwerpen 17.925; Brussel 6.124; Limburg 7.455; Oost-Vl. 16.613; Vl.-Brabant 16.016; West-Vl. 7.135)", DEF_KH, GEC, date(2025, 7, 29), D2,
       "pers/commissie citeren 71.238; stijging deels door meer deelnemende loketten (jaren niet vergelijkbaar)"),
    _b(KO, "onbeantwoorde_opvangvragen", 22722, "vragen", date(2023, 12, 31), "vlpar-sv-852-2025", PF.format(2196812), "SV nr. 852 (2024-2025)", "antwoord, tabel per provincie",
       "onbeantwoord 2023: 22.722 (Antwerpen 5.249; Brussel 2.394; Limburg 1.872; Oost-Vl. 5.458; Vl.-Brabant 5.283; West-Vl. 2.466)", DEF_ONB, GEC, date(2025, 7, 29), D2),
    _b(KO, "onbeantwoorde_opvangvragen", 26355, "vragen", date(2024, 12, 31), "vlpar-sv-852-2025", PF.format(2196812), "SV nr. 852 (2024-2025)", "antwoord, tabel per provincie",
       "onbeantwoord 2024: 26.355 (Antwerpen 6.029; Brussel 2.289; Limburg 2.547; Oost-Vl. 7.277; Vl.-Brabant 5.400; West-Vl. 2.813). 'Ouders kunnen hun vraag aan verschillende lokale loketten in verschillende gemeenten stellen. De lokale loketten weten dit niet van elkaar.'",
       DEF_ONB, GEC, date(2025, 7, 29), D2, "= 37 % van de vragen; cijfers 2025 ten vroegste mei 2026 (SV 650)"),
    _b(KO, "opvangvragen_voorrangsgezinnen", 9655, "vragen", date(2023, 12, 31), "vlpar-sv-852-2025", PF.format(2196812), "SV nr. 852 (2024-2025)", "antwoord, PDF p. 4",
       "Totaal 9.655 4.171 … Door de gewijzigde regelgeving m.b.t. voorrangsregels, werden in 2024 niet langer vragen geregistreerd onder de subcategorie “Vraag van een gezin dat voldoet aan de voorrangsregels”.",
       "Unieke opvangvragen uit voorranggroepen bij lokale loketten (loketten met registraties voor een volledig kalenderjaar).", GEC, date(2025, 7, 29), D_EB, "4.171 daarvan zonder opvangvoorstel"),
    _b(KO, "onvervulde_behoefte_pct", 8.31, "procent", date(2018, 12, 31), "vlpar-sv-664-2023", PF.format(1969521), "SV nr. 664 (2022-2023), Daniëls → Crevits", "antwoord, PDF p. 3",
       P_ONV18, "Aandeel kinderen 3 m–3 j in het Vlaams Gewest met een onvervulde behoefte aan formele opvang (steekproefonderzoek Kind en Gezin 2018; alle kinderen).", GEC, date(2023, 6, 1), D_EB),
    _b(KO, "onvervulde_behoefte_kinderen", 14831, "kinderen", date(2018, 12, 31), "vlpar-sv-664-2023", PF.format(1969521), "SV nr. 664 (2022-2023)", "antwoord, PDF p. 3",
       P_ONV18, "Geraamd aantal kinderen 3 m–3 j in het Vlaams Gewest met onvervulde behoefte (populatieniveau; alle kinderen).", GEC, date(2023, 6, 1), D_EB,
       "= 13.473 niet-schoolgaande + 1.358 schoolgaande kinderen (rapport 57, tabel p. 215)"),
    _b(KO, "onvervulde_behoefte_pct", 11.6, "procent", date(2025, 3, 10), "opgroeien-onderzoek-2025-rapport", "https://www.opgroeien.be/sites/default/files/tool-documents/2026_01_rapport_57_ef__53_gebruik_behoefte_kinderopvang.pdf",
       "HIVA/Opgroeien — Onderzoek gebruik en behoefte kinderopvang 2025 (rapport 57)", "p. 12 (ook tabel p. 215)",
       "De totale onvervulde behoefte aan formele opvang voor alle (niet-schoolgaande en schoolgaande) kinderen tussen 3 maanden en 3 jaar in het Vlaamse Gewest bedraagt 11.6%.",
       "Aandeel kinderen 3 m–3 j (Vlaams Gewest) met onvervulde behoefte aan formele opvang; alle kinderen, vergelijkbaar met 2018; steekproef 4.114 gezinnen, respons 19 %.",
       GEC, date(2026, 1, 31), D_EB, "enkel niet-schoolgaande kinderen: 12,0 % (rapport p. 12) — verklaart het vroegere verschil met de toolbox-pagina (11,6 %)"),
    _b(KO, "onvervulde_behoefte_kinderen", 20494, "kinderen", date(2025, 3, 10), "opgroeien-onderzoek-2025-rapport", "https://www.opgroeien.be/sites/default/files/tool-documents/2026_01_rapport_57_ef__53_gebruik_behoefte_kinderopvang.pdf",
       "HIVA/Opgroeien — rapport 57", "p. 12 (ook tabel p. 215)",
       "De totale onvervulde behoefte aan formele opvang voor alle (niet-schoolgaande en schoolgaande) kinderen tussen 3 maanden en 3 jaar in het Vlaamse Gewest bedraagt 11.6%. "
       "Op populatieniveau komt dit overeen met ongeveer 20 494 kinderen die gemiddeld 2.6 dagen in de week nood hebben aan formele opvang.",
       "Geraamd aantal kinderen 3 m–3 j in het Vlaams Gewest met onvervulde behoefte (populatieniveau; alle kinderen, vergelijkbaar met 2018).", GEC, date(2026, 1, 31), D_EB,
       "enkel niet-schoolgaande kinderen: 18 045 (12,0 %); peildatum = referentiedatum steekproef (kinderen 3 m–3 j op 10-03-2025)"),
    _b(KO, "tekort_plaatsen_prognose_2029", 11500, "plaatsen", date(2026, 3, 9), "opgroeien-onderzoek-2025-nieuws", "https://www.opgroeien.be/over-opgroeien/nieuws-en-pers/onderzoek-kinderopvang-2025-gebruik-noden-en-een-groeiend-tekort-aan-plaatsen",
       "Opgroeien — nieuwsbericht onderzoek kinderopvang 2025", "tekst", "Vlaanderen tegen 2029 ongeveer 11.500 extra opvangplaatsen nodig heeft", "Prognose van Opgroeien: extra opvangplaatsen nodig tegen 2029 (berekeningswijze niet gepubliceerd).",
       GEC, date(2026, 3, 9), D_EB, "berekening staat niet in het rapport en niet in het persbericht"),
    _b(KO, "vergunde_plaatsen", 92819, "plaatsen", date(2025, 12, 31), "opgroeien-persbericht-2026-06-04", "https://pers.opgroeien.be/opgroeien-publiceert-kinderopvangcijfers-2025-en-kondigt-correctie-cijfers-onthaalouders-aan",
       "Opgroeien persbericht 04-06-2026", "tekst", "De Vlaamse kinderopvang telde eind 2025 92.819 vergunde opvangplaatsen voor baby's en peuters in Vlaanderen en Brussel.",
       DEF_PL, GEC, date(2026, 6, 4), D_EB, "46,07 plaatsen per 100 kinderen (persbericht); IKT 79.271 en 5.389 locaties uit de Excel"),
    _b(KO, "meerjarenoproep_t2_aangevraagd", 11382, "plaatsen", date(2025, 9, 14), "opgroeien-sectoroverleg-2025-11", "https://www.opgroeien.be/sites/default/files/documenten/algemene-presentatie-28-november-2025.pdf",
       "Opgroeien — sectoroverleg 28-11-2025", "dia p. 10",
       "4500 Nieuwe T2 via meerjarenoproep … Aanvragen kon tot en met 14 september 2025 ➢ Aantal aanvragen: 534 ➢ Aantal aangevraagde plaatsen: 11.382",
       "Door organisatoren aangevraagde T2-plaatsen in de meerjarenoproep 2025 (gerangschikte lijst, aanbodzijde).", GEC, date(2025, 11, 28), D_EB, "peildatum = einde indieningstermijn"),
    _b(KO, "meerjarenoproep_t2_toegekend", 3936, "plaatsen", date(2025, 12, 15), "opgroeien-toekenning-t2-2025",
       "https://www.opgroeien.be/sites/default/files/documenten/oproep-meerjarenprogrammatie-toekenning-subsidiebeloftes-t2-ikt-kinderopvang.pdf",
       "Opgroeien — plaatsen met subsidie voor inkomenstarief 2025-2029, beslissingen december 2025", "p. 1 en p. 13",
       "Opgroeien besliste over de toekenning van 3.936 nieuwe plaatsen met subsidie inkomenstarief. … 2026 962 2027 685 2028 1.291 2029 998 Totaal 3.936 … "
       "Het gaat om 578 plaatsen voor gemeenten in Vlaanderen en 60 plaatsen voor het tweetalig gebied Brussel-Hoofdstad. Eind februari 2026 zal er een herhalingsoproep volgen",
       "Toegekende subsidiebeloftes T2 in de meerjarenoproep 2025 (realisatie 2026-2029).", GEC, date(2025, 12, 15), D_EB,
       "222 gehonoreerde aanvragen = eigen telling van de toekenningsrijen (niet als getal in de bron)"),
]
# Capaciteitsreeks uit de Opgroeien-Excel (aggregatie gemeenteniveau -> Vl. Gewest + Brussel)
UXL = "https://www.opgroeien.be/sites/default/files/documenten/b-p-aantal-plaatsen-en-locaties-naar-vergunningstype-en-inkomenstarief_8.xlsx"
for jaar, tot, ikt in ((2018, 93363, 70015), (2019, 95027, 72050), (2020, 94924, 72078), (2021, 94681, 72261), (2022, 93128, 71841), (2023, 93035, 74485), (2024, 93175, 79284)):
    opm = "incl. ± 2.500 te hoog getelde onthaalouderplaatsen (correctie 04-06-2026)" if 2020 <= jaar <= 2024 else ""
    BEVINDINGEN.append(_b(KO, "vergunde_plaatsen", tot, "plaatsen", date(jaar, 12, 31), "opgroeien-kinderopvang-cijfers", UXL, "Opgroeien — Excel plaatsen en locaties naar vergunningstype en inkomenstarief (versie 17-07-2026)",
                          f"werkblad 'BP aantal pl en loc', rijen Jaar={jaar}, som kolom H 'Totaal aantal plaatsen'", f"som gemeenteniveau {jaar}: {tot:,} plaatsen (IKT {ikt:,})".replace(",", "."), DEF_PL, GEC, date(2026, 7, 17), D_EB, opm))
    BEVINDINGEN.append(_b(KO, "plaatsen_inkomenstarief", ikt, "plaatsen", date(jaar, 12, 31), "opgroeien-kinderopvang-cijfers", UXL, "Opgroeien — Excel plaatsen en locaties (versie 17-07-2026)",
                          f"werkblad 'BP aantal pl en loc', rijen Jaar={jaar}, som kolom I 'Plaatsen IKT'", f"som gemeenteniveau {jaar}: IKT {ikt:,}".replace(",", "."), "Vergunde plaatsen met subsidie inkomenstarief (trap 2/3) op 31/12.", GEC, date(2026, 7, 17), D_EB, opm))
BEVINDINGEN.append(_b(KO, "plaatsen_inkomenstarief", 79271, "plaatsen", date(2025, 12, 31), "opgroeien-kinderopvang-cijfers", UXL, "Opgroeien — Excel plaatsen en locaties (versie 17-07-2026)",
                      "werkblad 'BP aantal pl en loc', rijen Jaar=2025, som kolom I 'Plaatsen IKT'", "som gemeenteniveau 2025: IKT 79.271 (totaal 92.819; 5.389 locaties)",
                      "Vergunde plaatsen met subsidie inkomenstarief (trap 2/3) op 31/12.", GEC, date(2026, 7, 17), D_EB, "zelfde totaal als het persbericht van 04-06-2026"))

# ----------------------------------------------------------------------------------------------- budgetten
def _bu(vid, jaar, fase, niveau, bedrag, bron_id, url, titel, pagina, passage, status, door="", krediet=Kredietsoort.NVT, artikel="", programma="", ise="", label="", opm=""):
    key = artikel or label.replace(" ", "_")[:40]
    return Budget(budget_id=f"{vid}:{jaar}:{fase.value}:{niveau}:{krediet.value}:{key}", voorziening_id=vid, begrotingsjaar=jaar, fase=fase, niveau=niveau,
                  bedrag_eur=bedrag, kredietsoort=krediet, artikel_code=artikel, programma=programma, ise=ise, label=label, bron_id=bron_id, bron_url=url,
                  documenttitel=titel, pagina=pagina, passage=passage, controlestatus=status, gecontroleerd_door=door, gecontroleerd_op=VANDAAG if door else None, opmerking=opm)


B = Budgetfase
BUDGETTEN = [
    # NRTJ — dotatie Opgroeien Regie jeugdhulp (ISE Jeugdhulp, GE-M); volledige reeks 2020-2026 zit in kredieten.csv
    _bu(NR, 2024, B.UITV, "dept_artikel", 898_510_000, "vlpar-bbt-wvg-uitv-2024", PF.format(2162480), "BBT WVG begrotingsuitvoering 2024 — 23-T (2024-2025)", "± p. 86",
        "Uitgaven 864.127 895.317 898.510 867.698 901.175 901.174 (BA / BA-JR / BU, VAK | VEK)", GEL, A, krediet=Kredietsoort.VAK, artikel="GB0-1GEF2MX-IS", programma="GE", ise="JEUGDHULP", label="Opgroeien Regie — werkingstoelage jeugdhulp (uitvoering)"),
    _bu(NR, 2025, B.BO, "dept_artikel", 934_496_000, "vlpar-bbt-wvg-2025", PF.format(2081035), "BBT WVG begroting 2025 — 13-V (2024-2025)", "p. 79",
        "BO 2025 934.496 (VAK = VEK); 'Regeerakkoord - Jeugdhulp 10.000'; 'Aangroei kostendrijver pleegzorg 9.696'", GEL, A, krediet=Kredietsoort.VAK, artikel="GB0-1GEF2MX-IS", programma="GE", ise="JEUGDHULP", label="Opgroeien Regie — werkingstoelage jeugdhulp"),
    _bu(NR, 2025, B.UITV, "dept_artikel", 946_170_000, "vlpar-bbt-wvg-uitv-2025", PF.format(2325132), "BBT WVG begrotingsuitvoering 2025 — 23-V (2025-2026)", "p. 87",
        "Uitgaven 937.575 946.170 946.170 937.575 947.760 947.760", GEL, A, krediet=Kredietsoort.VAK, artikel="GB0-1GEF2MX-IS", programma="GE", ise="JEUGDHULP", label="Opgroeien Regie — werkingstoelage jeugdhulp (uitvoering)"),
    _bu(NR, 2026, B.BO, "dept_artikel", 945_549_000, "vlpar-bbt-wvg-2026", PF.format(2227516), "BBT Welzijn en Armoedebestrijding, begroting 2026 — 13-Z (2025-2026)", "p. 132-134",
        "BA 2025 937.575 / Index 18.752 / Compensaties -26.222 / Andere bijstellingen 15.444 / BO 2026 945.549; 'Regeerakkoord - jeugdhulp 8.798'; 'Jeugdhulp -7.000 Vertragen groeipad uitbreidingsbeleid naar 2027'; 'Kostendrijver pleegzorg 11.104'",
        GEL, A, krediet=Kredietsoort.VAK, artikel="GB0-1GEF2MX-IS", programma="GE", ise="JEUGDHULP", label="Opgroeien Regie — werkingstoelage jeugdhulp", opm="compensaties vooral overdracht Gemeenschapsinstellingen/HCA naar Agentschap Justitie en Handhaving"),
    _bu(NR, 2025, B.BELEID, "uitbreidingsbeleid", 10_000_000, "vlpar-bbt-wvg-2025", PF.format(2081035), "BBT WVG begroting 2025 — 13-V (2024-2025)", "p. 79", "Regeerakkoord - Jeugdhulp 10.000 (k€)", GEL, A, label="regeerakkoord nieuw beleid jeugdhulp"),
    _bu(NR, 2026, B.BELEID, "uitbreidingsbeleid", 8_798_000, "vlpar-bbt-wvg-2026", PF.format(2227516), "BBT WVG begroting 2026 — 13-Z (2025-2026)", "p. 133", "Regeerakkoord - jeugdhulp 8.798 Nieuw beleid binnen jeugdhulp", GEL, A, label="regeerakkoord nieuw beleid jeugdhulp", opm="-7.000 k€ vertraging groeipad naar 2027"),
    # Kinderopvang — dotatie Opgroeien Regie (ISE Geïntegreerd gezinsbeleid, GE-U; omvat ook preventieve gezinsondersteuning, adoptie, Groeipakket-apparaat)
    _bu(KO, 2025, B.BA, "dept_artikel", 1_372_560_000, "vlpar-bbt-wvg-2026", PF.format(2227516), "BBT WVG begroting 2026 — 13-Z (2025-2026)", "p. 145-147",
        "GB0-1GEF2UX-IS Opgroeien regie: BA 2025 VAK 1.372.560 / VEK 1.349.455 → BO 2026 VAK 1.445.064 / VEK 1.445.159 (k€); omvat apparaats- én beleidskredieten kinderopvang, preventieve gezinsondersteuning, adoptie, geïntegreerd gezinsbeleid en Groeipakket",
        GEL, A, krediet=Kredietsoort.VAK, artikel="GB0-1GEF2UX-IS", programma="GE", ise="GEINTEGREERD GEZINSBELEID", label="Opgroeien Regie — geïntegreerd gezinsbeleid (incl. kinderopvang)"),
    _bu(KO, 2026, B.BO, "dept_artikel", 1_445_064_000, "vlpar-bbt-wvg-2026", PF.format(2227516), "BBT WVG begroting 2026 — 13-Z (2025-2026)", "p. 145-147",
        "BO 2026 VAK 1.445.064; compensatie +60.000 k€ 'van VIPA voor de realisatie van infrastructuur in de kinderopvang via de lokale besturen'; +10.000 k€ VEK uitbreidingsbeleid kinderopvang BO2024",
        GEL, A, krediet=Kredietsoort.VAK, artikel="GB0-1GEF2UX-IS", programma="GE", ise="GEINTEGREERD GEZINSBELEID", label="Opgroeien Regie — geïntegreerd gezinsbeleid (incl. kinderopvang)"),
    _bu(KO, 2025, B.UITV, "dept_artikel", 1_392_279_000, "vlpar-bbt-wvg-uitv-2025", PF.format(2325132), "BBT WVG begrotingsuitvoering 2025 — 23-V (2025-2026)", "p. 99-101",
        "BU 2025 VAK 1.392.279 / VEK 1.369.467 (k€); ouderbijdragen kinderopvang gerealiseerd 233.463 k€ vs 249.360 geraamd", GEL, A, krediet=Kredietsoort.VAK, artikel="GB0-1GEF2UX-IS", programma="GE", ise="GEINTEGREERD GEZINSBELEID", label="Opgroeien Regie — geïntegreerd gezinsbeleid (uitvoering)"),
    _bu(KO, 2026, B.BO, "entiteit_begroting", 1_627_800_000, "vlpar-bbt-wvg-2026", PF.format(2227516), "BBT WVG begroting 2026 — 13-Z (2025-2026)", "p. 147",
        "GDF-AGEF2UA-WT werking en toelagen geïntegreerd gezinsbeleid: 1.627,8 mln € VEK (+96.414 k€). 'De belangrijkste uitgavenpost zijn de subsidies in het kader van kinderopvang, preventieve gezinsondersteuning en adoptie'; overschot 2025 79,2 mln VEK door 'meer geleidelijke opstart van nieuwe plekken'",
        GEL, A, krediet=Kredietsoort.VEK, artikel="GDF-AGEF2UA-WT", programma="GE", ise="GEINTEGREERD GEZINSBELEID", label="Opgroeien Regie — werking en toelagen gezinsbeleid (eigen begroting)"),
    _bu(KO, 2025, B.BELEID, "meerjarenplan", 200_000_000, "opgroeien-masterplan-2025", "https://www.opgroeien.be/sites/default/files/documenten/masterplan-kinderopvang-meerjarenprogrammatie-snelinfo.pdf", "Masterplan kinderopvang — snelinfo 07-04-2025", "tekst",
        "De Vlaamse Regering plant deze legislatuur 200 miljoen euro extra investeringen in de kinderopvang. 95,7 miljoen daarvan is voorzien voor de nieuwe plaatsen trap 2, 20 miljoen euro voor de nieuwe plaatsen trap 1",
        GEL, A, label="masterplan: +200 mln €/jaar tegen 2029 (100 vanaf 2025, +50 2028, +50 2029)", opm="jaarbedrag op kruissnelheid 2029; 10.000 nieuwe plaatsen (6.000 T2 + 4.000 T1); infrastructuur 70,2 mln"),
    _bu(KO, 2023, B.BELEID, "uitbreidingsbeleid", 115_000_000, "vlpar-begroting-2023-vragen", PF.format(1897634), "Vragen en antwoorden begroting 2023", "tekst",
        "115 mln (100 mln extra BO 2023 + 15 mln); 92 mln nieuwe investering: 38,2 mln T2B→T2A, 52,3 mln T0/T1, 1,0 mln gezinsopvang", GEL, A, label="uitbreidingsbudget kinderopvang 2023"),
]


def main() -> None:
    nb = upsert("bronnen", BRONNEN)
    _update_voorzieningen()
    nv = upsert("bevindingen", BEVINDINGEN)
    nu = upsert("budgetten", BUDGETTEN)
    print(f"opgroeien: bronnen {nb}, bevindingen {nv}, budgetten {nu} (upsert); draai 'wachtlijst validate' en 'wachtlijst publish'")


if __name__ == "__main__":
    main()
