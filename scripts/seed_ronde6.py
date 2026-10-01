"""Ronde 6 (1-10-2026): de vijf 'in onderzoek'-voorzieningen naar 'uitgewerkt' — VAPH RTH/hulpmiddelen, CAR, CAW/verslavingszorg,
forensische zorg, art. 60/wijk-werken — met reeksen, definities en budget.

Draai ná seed_ronde5b.py:  ``python scripts/seed_ronde6.py``  (upsert op sleutel).

- RTH: gebruikers 35.711 (2024) → 37.133 (2025); 222 erkende aanbieders, 102.058,82 personeelspunten; max. 8 punten per persoon per jaar
  (rantsoenering, geen wachtlijst); artikel GH0-AGGF2RC-WT 72,5 mln (BO 2019) → 124,4 (uitv. 2024) → 117,4 (BO 2026); UB RTH 4,4 mln (2025).
  Hulpmiddelen: 31.900-33.500 goedkeuringen per jaar (2021-2023); mediaan doorlooptijd SDA-aanvragen 67 → 28 dagen (2020-2022).
- CAR: sinds oktober 2023 in de VSB, 100 % prestatiefinanciering; VSB-artikel revalidatie 207,9 → 213,4 mln (BA 2025 → BO 2026);
  pilootfase CAR-CGG 1-4-2026 → 31-12-2027 (6 CAR + 3 CGG); geen gevalideerde wachttijden (SV 234).
- CAW: bereikte cliënten 2024 onthaal 109.290, begeleiding 28.797, totaal 125.488; 1.468,93 VTE, enveloppe ± 128 mln; artikel Welzijnswerk
  GB0-1GCF2EA-WT 141,7 → 141,6 mln; geen wachtindicator (BBT 2026).
- Forensische zorg: VAPH-projecten in de gevangenissen 287 (2021) → 701 (2025) ondersteunde personen, 7 projecten, 2,1 → 3,2 mln.
- Art. 60 / wijk-werken: geen wachtlijstmechanisme bevestigd; reeksen uit ronde 5b.
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
RTH, CAR, CAW, FOR, A60 = "vaph-rth-hulpmiddelen", "zorg-car", "zorg-caw-verslavingszorg", "zorg-forensisch", "dwse-art60-wijkwerken"
W = WachtlijstType
JV25 = "https://extranet.vaph.be/jaarverslag/2025/pages/{}"

BRONNEN = [
    Bron(bron_id="vaph-jaarverslag-2025", naam="VAPH — jaarverslag 2025 (HTML, extranet)", organisatie="VAPH", url=JV25.format(2), bron_type=BronType.HTML, frequentie="jaarlijks (juni)",
         machinaal="https://extranet.vaph.be/jaarverslag/2025/pages/{n}; RTH = pages/16, cijfers = pages/12, uitbreidingsbeleid = pages/45", opmerking="gelezen 1-10-2026"),
    Bron(bron_id="vlpar-bbt-wvg-2020", naam="BBT WVG, begroting 2020 — stuk 13-Y (2019-2020) nr. 1", organisatie="Vlaams Parlement", url=PF.format(1551598), bron_type=BronType.PDF, frequentie="jaarlijks", opmerking="ingediend 08-11-2019; in config/bbt_documenten.yaml"),
    Bron(bron_id="vlpar-sv-783-2025-rth", naam="SV nr. 783 (2024-2025), Dillen → min. Crevits — rechtstreeks toegankelijke hulp, gebruik (punten per gebruiker)",
         organisatie="Vlaams Parlement", url=PF.format(2184544), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 23-07-2025"),
    Bron(bron_id="vlpar-sv-499-2025-hulpm", naam="SV nr. 499 (2024-2025), Vandromme → min. Crevits — hulpmiddelen en aanpassingen in de thuissituatie (goedkeuringen 2021-2024, bedragen)",
         organisatie="Vlaams Parlement", url=PF.format(2147608), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 08-05-2025"),
    Bron(bron_id="vlpar-sv-279-2024-hulpm", naam="SV nr. 279 (2023-2024), — snel degeneratieve aandoening, aanvragen hulpmiddelen (2): mediaan doorlooptijd",
         organisatie="Vlaams Parlement", url=PF.format(2052521), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 07-05-2024"),
    Bron(bron_id="vlpar-sv-624-2026-car", naam="SV nr. 624 (2025-2026), Perdaens → min. Gennez — CAR en CGG, traject nieuw kwaliteits- en financieringsmodel (pilootfase 2026-2027)",
         organisatie="Vlaams Parlement", url=PF.format(2306698), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 28-04-2026; CAR in VSB sinds oktober 2023, 100 % prestatiefinanciering"),
    Bron(bron_id="vlpar-sv-950-2026-for", naam="SV nr. 950 (2025-2026), De Reuse → min. Crevits — personen met een handicap in detentie, aangepaste ondersteuning (VAPH-projecten in gevangenissen)",
         organisatie="Vlaams Parlement", url=PF.format(2349515), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 14-07-2026"),
]


def _update_voorzieningen() -> None:
    vz = {v.voorziening_id: v for v in load("voorzieningen")}
    r = vz[RTH]
    r.scan_status, r.laatste_peildatum, r.publicatie_bron_id, r.wachtlijst_type = "proef_uitgewerkt", date(2025, 12, 31), "vaph-jaarverslag-2025", W.GEEN
    r.frequentie, r.wachtlijst_naam = "VAPH-jaarverslag (juni); SV's", "geen wachtlijst: rantsoenering via maximum 8 RTH-punten per persoon per jaar en personeelspunten per aanbieder"
    r.opmerking = ("Uitgewerkt 1-10-2026. RTH = laagdrempelige ondersteuning zonder VAPH-aanvraag (max. 8 punten/jaar; pilootfase 2023-2025 tot meer); gebruikers 35.711 (2024) → 37.133 (2025); 222 erkende aanbieders met "
                   "102.058,82 personeelspunten (+ 17.799 pilootfase, 1.990 GIO). Geen centrale wachtlijst; RTH dient als 'vangnet' voor nRTH-wachtenden (SV 146) en wordt in de hervorming zorgniveau 1 (cesuur 15,29 punten; "
                   "2.407 PVB-wachtenden eronder). Hulpmiddelen en aanpassingen: individuele tegemoetkomingen (± 32-34.000 goedkeuringen/jaar, ± 26 mln uitbetaald in 9 maanden 2024), mediaan doorlooptijd voor snel degeneratieve "
                   "aandoeningen 67 → 28 dagen (2020-2022); geen wachtlijst. Budget: artikel GH0-AGGF2RC-WT 72,5 mln (BO 2019) → 124,4 (uitv. 2024) → 116,7 (uitv. 2025) → 117,4 (BO 2026); uitbreidingsbeleid RTH 4,4 mln (2025, −6-jarigen, start 2026).")
    c = vz[CAR]
    c.scan_status, c.laatste_peildatum, c.publicatie_bron_id = "proef_uitgewerkt", date(2026, 4, 1), "vlpar-sv-624-2026-car"
    c.frequentie, c.wachtlijst_naam = "geen; SV's", "wachtlijst per centrum; geen gevalideerde centrale cijfers"
    c.opmerking = ("Uitgewerkt 1-10-2026 (zonder wachtcijfer: 'Het Departement Zorg beschikt niet over gevalideerde cijfers over de wachttijden bij de CAR', SV 234, jan 2026). CAR sinds oktober 2023 in de Vlaamse sociale bescherming, "
                   "100 % prestatiefinanciering via revalidatieovereenkomst; nieuw kwaliteits- en financieringsmodel (vast organisatiedeel + variabel zorgdeel, minima per functie D/E/G) in pilootfase 1-4-2026 → 31-12-2027 "
                   "met 6 CAR en 3 CGG, brede uitrol 2028; de minister verwacht 'impact op de wachttijden'. Projecten uitbreiding gespecialiseerde diagnostiek (6 CAR). Federale stopzetting terugbetaling monodisciplinaire "
                   "logopedie (juni 2025) verhoogt de druk. Budget: VSB-artikel revalidatie GM0-AGCF2LF-WT 207,9 mln (BA 2025) → 213,4 mln (BO 2026) — bevat CAR, revalidatievoorzieningen verslavingszorg en andere "
                   "revalidatieconventies; CAR-aandeel niet afgesplitst. Monitoring van wachttijden hoort bij de hervorming (kwaliteitskader: toegankelijkheid).")
    w = vz[CAW]
    w.scan_status, w.laatste_peildatum, w.publicatie_bron_id = "proef_uitgewerkt", date(2024, 12, 31), "vlpar-bbt-wvg-2026"
    w.frequentie, w.wachtlijst_naam = "BBT-indicator jaarlijks (bereik CAW); wachttijden niet gemeten", "geen wachtindicator; aanmeldstops/wachtlijsten per voorziening"
    w.opmerking = ("Uitgewerkt 1-10-2026. CAW (11 centra, 1.468,93 VTE erkend per 1-1-2025, enveloppe ± 128 mln): bereikte cliënten 2024 onthaal 109.290, begeleiding 28.797, totaal 125.488; 28.626 begeleidingsmodules; "
                   "BBT-indicator zonder streefwaarde en zonder wachttijd ('bij ongewijzigd budget blijft het bereik op hetzelfde niveau'). Artikel Welzijnswerk GB0-1GCF2EA-WT 141,7 mln (BA 2025) → 141,6 mln (BO 2026; −1,5 mln besparing, "
                   "−2,4 mln naar Justitie en Handhaving). Verslavingszorg: 'geen structurele monitoring van de wachttijden over alle sectoren heen' (SV 568); CGG-verslavingsteams 45 dagen tot eerste contact (2021-2023); "
                   "revalidatievoorzieningen 7.73 (VSB-artikel revalidatie) en psychiatrische ziekenhuizen (federaal): geen cijfers; geen gecentraliseerd overzicht aanmeldstops (SV 561); monitoringssysteem wachtlijsten GGZ aangekondigd. "
                   "Vlaams Parlement vroeg in 2023 wel wachtlijsten justitieel welzijnswerk per gevangenis (zie zorg-forensisch).")
    f = vz[FOR]
    f.scan_status, f.laatste_peildatum = "proef_uitgewerkt", date(2025, 12, 31)
    f.opmerking = ("Uitgewerkt 1-10-2026 (Vlaamse kant). CGG forensische zorg: wachttijd aanmelding → eerste contact 111 d (2018) → 48 d (2024), gemiddeld 54; hulp- en dienstverlening in de gevangenis (CGG) 150 → 29 d; "
                   "actieve forensische zorgperiodes 5.731 (2019) → 6.992 (2024); 1.546 voortijdig stopgezette trajecten (2024). CAW justitieel welzijnswerk: geen overkoepelende wachtlijst, per gevangenis 209 wachtenden/ingeplanden "
                   "(juni 2023); 5.789 gedetineerden onthaald, 1.217 begeleid (2022). VAPH: 7 projecten voor personen met een (vermoeden van) handicap in de gevangenis — 287 (2021) → 701 (2025) ondersteunde personen "
                   "(230 geïnterneerd, 345 gedetineerd, 126 beklaagd), kost 2,1 mln (2024) → 3,2 mln (2025), geen VAPH-aanvraagprocedure. Federale kant (FPC's Gent/Antwerpen/Aalst, interneringskamers, PVT) buiten scope; "
                   "forensische VAPH-units buiten de gevangenis: geen wachtcijfers gevonden. Budget forensische CGG binnen enveloppe CGG (VIA-6: +0,5 VTE per forensische werking sinds 2021).")
    a = vz[A60]
    a.scan_status, a.wachtlijst_type = "proef_uitgewerkt", W.GEEN
    a.opmerking = ("Uitgewerkt 1-10-2026: geen wachtlijstmechanisme. Art. 60 §7 is sinds de zesde staatshervorming ingebed in het traject Tijdelijke Werkervaring OCMW (TWE-OCMW); VDAB telt geen art. 60-tewerkstellingen maar "
                   "trajecten met 'tijdig werk' (tewerkstelling start binnen 2 maanden na de start van het traject): 9.222 (2024), 9.763 (t/m nov 2025); uitstroom naar werk 28,8 % (2024). Het OCMW blijft juridisch werkgever "
                   "(DIMONA), plaats van tewerkstelling niet gekend; Vlaamse opleidings- en omkaderingspremie (art. 61) in 170-179 trajecten. Wijk-werken: 3.365 actieve wijk-werkers (eind 2025), 1.708 met overgangsmaatregel PWA; "
                   "VDAB-budget 9,17 mln netto (2026); overgang naar samenlevingsjobs; beperking werkloosheid in de tijd raakt de doelgroep. Geen begrotingsartikel art. 60 in de BBT Werk 2026 (financiering via VDAB en federale leefloontoelage).")
    upsert("voorzieningen", [r, c, w, f, a])


def _b(vid, metriek, waarde, eenheid, peildatum, bron_id, url, titel, pagina, passage, definitie, status, pub=None, door="", opm=""):
    return Bevinding(bevinding_id=f"{vid}:{metriek}:{peildatum.isoformat()}", voorziening_id=vid, metriek=metriek, waarde=waarde, eenheid=eenheid, peildatum=peildatum,
                     bron_id=bron_id, bron_url=url, documenttitel=titel, pagina=pagina, passage=passage, definitie=definitie, publicatiedatum=pub,
                     controlestatus=status, gecontroleerd_door=door, gecontroleerd_op=VANDAAG if door else None, opmerking=opm)


BEVINDINGEN: list[Bevinding] = []
JV, TJV, PJV = "vaph-jaarverslag-2025", "VAPH jaarverslag 2025", date(2026, 6, 1)
BEVINDINGEN += [
    _b(RTH, "gebruikers_rth", 35711, "personen", date(2024, 12, 31), JV, JV25.format(16), TJV, "pages/16 'Gebruikers van rechtstreeks toegankelijke hulp'", "In 2024 deden er 35.711 mensen een beroep op RTH-ondersteuning.",
       "Unieke personen die in het jaar gebruik maakten van rechtstreeks toegankelijke hulp (VAPH).", GEL, PJV, A),
    _b(RTH, "gebruikers_rth", 37133, "personen", date(2025, 12, 31), JV, JV25.format(16), TJV, "pages/16", "In totaal maakten 37.133 personen gebruik van RTH, waarvan 20.054 van 21 jaar of jonger, 17.078 ouder dan 22 jaar", "Idem, 2025.", GEL, PJV, A),
    _b(RTH, "erkende_aanbieders_rth", 222, "aanbieders", date(2025, 12, 31), JV, JV25.format(16), TJV, "pages/16", "Op 31 december 2025 waren er 222 erkende aanbieders van rechtstreeks toegankelijke hulp (RTH) goed voor 102.058,82 personeelspunten", "Erkende RTH-aanbieders op 31/12 (229 aanbieders in totaal incl. niet-erkende).", GEL, PJV, A),
    _b(RTH, "personeelspunten_rth", 102058.82, "personeelspunten", date(2025, 12, 31), JV, JV25.format(16), TJV, "pages/16", "… goed voor 102.058,82 personeelspunten (minder- en meerderjarigen)", "Erkende RTH-personeelspunten op 31/12 (excl. pilootfase 17.799,45 en GIO 1.990,31).", GEL, PJV, A),
    _b(RTH, "personeelspunten_rth", 101926.28, "personeelspunten", date(2024, 12, 31), JV, JV25.format(16), TJV, "pages/16", "De stijging in personeelspunten ten opzichte van 2024 (101.926,28 punten)", "Idem, 2024.", GEL, PJV, A),
    _b(RTH, "punten_per_gebruiker", 2.65, "punten", date(2024, 12, 31), "vlpar-sv-783-2025-rth", PF.format(2184544), "SV nr. 783 (2024-2025) Dillen", "antwoord 3", "Het gemiddeld aantal punten per gebruiker bedroeg in 2023 2,68 punten en in 2024 2,65.", "Gemiddeld aantal RTH-punten per gebruiker op jaarbasis (max. 8).", GEL, date(2025, 7, 23), A),
    _b(RTH, "punten_per_gebruiker", 2.68, "punten", date(2023, 12, 31), "vlpar-sv-783-2025-rth", PF.format(2184544), "SV nr. 783 (2024-2025) Dillen", "antwoord 3", "… in 2023 2,68 punten", "Idem, 2023.", GEL, date(2025, 7, 23), A),
]
for jaar, n in ((2021, 33545), (2022, 31938), (2023, 33333)):
    BEVINDINGEN.append(_b(RTH, "goedkeuringen_hulpmiddelen", n, "goedkeuringen", date(jaar, 12, 31), "vlpar-sv-499-2025-hulpm", PF.format(2147608), "SV nr. 499 (2024-2025) Vandromme", "antwoord 1, tabel",
                          f"som van de 10 cellen (5 provincies × minder-/meerderjarig) voor {jaar} = {n:,}".replace(",", "."), "Goedkeuringen voor hulpmiddelen en aanpassingen (VAPH) in het jaar, Vlaanderen.", GEL, date(2025, 5, 8), A, opm="eigen som"))
for jaar, d in ((2020, 67), (2021, 39), (2022, 28)):
    BEVINDINGEN.append(_b(RTH, "mediaan_doorlooptijd_hulpmiddelen_sda_dagen", d, "dagen", date(jaar, 12, 31), "vlpar-sv-279-2024-hulpm", PF.format(2052521), "SV nr. 279 (2023-2024)", "antwoord 3c, tabel",
                          f"Jaar aanvraag {jaar}: Mediaan doorlooptijd (dagen) {d}", "Mediaan doorlooptijd van de behandeling door het VAPH van hulpmiddelenaanvragen van personen met een snel degeneratieve aandoening (SDA), incl. buiten refertelijst.", GEL, date(2024, 5, 7), A))
BEVINDINGEN += [
    _b(CAR, "pilootprojecten_car_cgg", 9, "voorzieningen", date(2026, 4, 1), "vlpar-sv-624-2026-car", PF.format(2306698), "SV nr. 624 (2025-2026) Perdaens", "antwoord 1-2",
       "De pilootfase zal starten op 1 april 2026 en zal lopen tot en met 31 december 2027. … Volgende negen voorzieningen werden geselecteerd: CAR Brussel, CAR Spermalie, CAR Buggenhout, CAR De Hert, CAR Kohesi, CAR Ascendere, CGG Kohesi, CGG Passant en CGG VBO.",
       "Voorzieningen in de pilootfase van het nieuwe kwaliteits- en financieringsmodel CAR-CGG (6 CAR + 3 CGG).", GEL, date(2026, 4, 28), A),
    _b(CAW, "caw_bereikte_clienten_onthaal", 109290, "personen", date(2024, 12, 31), "vlpar-bbt-wvg-2026", PF.format(2227516), "BBT Welzijn en Armoedebestrijding 2026 — 13-Z", "p. 50, prestatie-informatie CAW", "Aantal bereikte cliënten in 2024: Onthaal: 109.290 · Begeleiding: 28.797 · Totaal: 125.488; Aantal ingezette modules in 2024: 28.626",
       "Personen met een hulpvraag bereikt in CAW-onthaal (vraagverheldering, directe hulp, doorverwijzing) in het jaar.", GEL, date(2025, 12, 9), A),
    _b(CAW, "caw_bereikte_clienten_begeleiding", 28797, "personen", date(2024, 12, 31), "vlpar-bbt-wvg-2026", PF.format(2227516), "BBT Welzijn en Armoedebestrijding 2026 — 13-Z", "p. 50", "Begeleiding: 28.797", "Personen met een opgestart CAW-begeleidingstraject in het jaar.", GEL, date(2025, 12, 9), A),
    _b(CAW, "caw_bereikte_clienten_totaal", 125488, "personen", date(2024, 12, 31), "vlpar-bbt-wvg-2026", PF.format(2227516), "BBT Welzijn en Armoedebestrijding 2026 — 13-Z", "p. 50", "Totaal: 125.488", "Unieke cliënten bereikt in onthaal en/of begeleiding (geen streefwaarde; geen wachttijdindicator).", GEL, date(2025, 12, 9), A),
    _b(CAW, "caw_vte_erkend", 1468.93, "VTE", date(2025, 1, 1), "vlpar-bbt-wvg-2026", PF.format(2227516), "BBT Welzijn en Armoedebestrijding 2026 — 13-Z", "p. 50-51", "De CAW's zijn per 1 januari 2025 erkend voor 1.468,93 voltijdse equivalenten. Dit correspondeert met een subsidie-enveloppe van ongeveer 128 miljoen.", "Erkende VTE van de CAW's.", GEL, date(2025, 12, 9), A),
]
S950, U950, T950, P950 = "vlpar-sv-950-2026-for", PF.format(2349515), "SV nr. 950 (2025-2026) De Reuse", date(2026, 7, 14)
for jaar, n in ((2021, 287), (2022, 288), (2023, 336), (2024, 440), (2025, 701)):
    BEVINDINGEN.append(_b(FOR, "vaph_ondersteund_in_gevangenis", n, "personen", date(jaar, 12, 31), S950, U950, T950, "antwoord 1c, tabel", f"Totaal {jaar}: {n}",
                          "Personen met een (vermoeden van) handicap ondersteund door de VAPH-projecten in de gevangenissen (geïnterneerd, gedetineerd, beklaagd); 7 projecten sinds mei 2024 (3 ervoor).", GEL, P950, A))
BEVINDINGEN.append(_b(FOR, "vaph_projecten_gevangenis", 7, "projecten", date(2025, 12, 31), S950, U950, T950, "antwoord 1a", "Het gaat in totaal over 7 projecten … 752 + 179 + 716 + 154 + 250 + 250 + 232 personeelspunten", "Erkende VAPH-projecten voor ondersteuning in de gevangenissen (2.533 personeelspunten).", GEL, P950, A))


def _bu(vid, jaar, fase, niveau, bedrag, bron_id, url, titel, pagina, passage, status, door="", krediet=Kredietsoort.NVT, artikel="", programma="", ise="", label="", opm=""):
    key = artikel or label.replace(" ", "_")[:40]
    return Budget(budget_id=f"{vid}:{jaar}:{fase.value}:{niveau}:{krediet.value}:{key}", voorziening_id=vid, begrotingsjaar=jaar, fase=fase, niveau=niveau, bedrag_eur=bedrag,
                  kredietsoort=krediet, artikel_code=artikel, programma=programma, ise=ise, label=label, bron_id=bron_id, bron_url=url, documenttitel=titel, pagina=pagina,
                  passage=passage, controlestatus=status, gecontroleerd_door=door, gecontroleerd_op=VANDAAG if door else None, opmerking=opm)


B, VAK = Budgetfase, Kredietsoort.VAK
PMB = "PERSONEN MET EEN BEPERKING"
BUDGETTEN = [
    _bu(RTH, 2019, B.BO, "entiteit_begroting", 72_500_000, "vlpar-bbt-wvg-2020", PF.format(1551598), "BBT WVG 2020 — 13-Y (2019-2020)", "p. 76, artikel GH0-AGGF2RC-WT", "FINANCIERING VAN RECHTSTREEKS TOEGANKELIJKE ZORG EN ONDERSTEUNING: BO 2019 72.500 (keuro)", GEL, A, VAK, "GH0-AGGF2RC-WT", "GG", PMB, "RTH (VAPH-begroting)", opm="uit kredieten.csv (parser), stuk 13-Y"),
    _bu(RTH, 2024, B.UITV, "entiteit_begroting", 124_370_000, "vlpar-bbt-wvg-uitv-2024", PF.format(2162480), "BBT WVG begrotingsuitvoering 2024 — 23-T (2024-2025)", "p. 133, artikel GH0-AGGF2RC-WT", "Uitvoering 2024: 124.370 (keuro, VAK)", GEL, A, VAK, "GH0-AGGF2RC-WT", "GG", PMB, "RTH (VAPH-begroting, uitvoering)", opm="uit kredieten.csv"),
    _bu(RTH, 2025, B.UITV, "entiteit_begroting", 116_723_000, "vlpar-bbt-wvg-uitv-2025", PF.format(2325132), "BBT WVG begrotingsuitvoering 2025 — 23-V (2025-2026)", "p. 124, artikel GH0-AGGF2RC-WT", "BA 2025 115.400 / Uitvoering 2025 116.723 (keuro, VAK)", GEL, A, VAK, "GH0-AGGF2RC-WT", "GG", PMB, "RTH (VAPH-begroting, uitvoering)", opm="uit kredieten.csv"),
    _bu(RTH, 2026, B.BO, "entiteit_begroting", 117_400_000, "vlpar-bbt-wvg-2026", PF.format(2227516), "BBT Welzijn en Armoedebestrijding 2026 — 13-Z (2025-2026)", "p. 187, artikel GH0-AGGF2RC-WT", "BA 2025 115.400 → BO 2026 117.400 (keuro, VAK)", GEL, A, VAK, "GH0-AGGF2RC-WT", "GG", PMB, "RTH (VAPH-begroting)", opm="uit kredieten.csv"),
    _bu(RTH, 2025, B.BELEID, "uitbreidingsbeleid", 4_400_000, JV, JV25.format(45), TJV, "pages/45, tabel middelen uitbreidingsbeleid 2025", "Rechtstreeks toegankelijke hulp 4,4 miljoen (totaal uitbreidingsbeleid 102,4 miljoen); uitbreiding … aan −6-jarigen van 4,3 miljoen euro, die zijn opstart zal kennen vanaf 2026", GEL, A, label="uitbreidingsbeleid RTH (−6-jarigen)"),
    _bu(CAR, 2025, B.BA, "entiteit_begroting", 207_852_000, "vlpar-bbt-wvg-2026", PF.format(2227516), "BBT Welzijn en Armoedebestrijding 2026 — 13-Z (2025-2026)", "p. 106, artikel GM0-AGCF2LF-WT", "Werking en Toelagen – Sociale Bescherming – Revalidatie: BA 2025 207.852 → BO 2026 213.430 (keuro, VAK)", GEL, A, VAK, "GM0-AGCF2LF-WT", "GC", "GESPECIALISEERDE ZORG", "revalidatie VSB (CAR, verslavingszorg 7.73 e.a.)", opm="CAR-aandeel niet afgesplitst"),
    _bu(CAR, 2026, B.BO, "entiteit_begroting", 213_430_000, "vlpar-bbt-wvg-2026", PF.format(2227516), "BBT Welzijn en Armoedebestrijding 2026 — 13-Z (2025-2026)", "p. 106, artikel GM0-AGCF2LF-WT", "BO 2026 213.430 (keuro, VAK)", GEL, A, VAK, "GM0-AGCF2LF-WT", "GC", "GESPECIALISEERDE ZORG", "revalidatie VSB (CAR, verslavingszorg 7.73 e.a.)"),
    _bu(CAW, 2025, B.BA, "dept_artikel", 141_740_000, "vlpar-bbt-wvg-2026", PF.format(2227516), "BBT Welzijn en Armoedebestrijding 2026 — 13-Z (2025-2026)", "p. 59-60, artikel GB0-1GCF2EA-WT", "WELZIJNSWERK (CAW's, Tele-Onthaal, schuldhulpverlening): BA 2025 141.740 / Index 2.793 / Compensaties −1.477 / Andere bijstellingen −1.500 / BO 2026 141.556 (keuro)", GEL, A, VAK, "GB0-1GCF2EA-WT", "GC", "WELZIJN EN SAMENLEVING", "welzijnswerk (CAW e.a.)"),
    _bu(CAW, 2026, B.BO, "dept_artikel", 141_556_000, "vlpar-bbt-wvg-2026", PF.format(2227516), "BBT Welzijn en Armoedebestrijding 2026 — 13-Z (2025-2026)", "p. 59-60, artikel GB0-1GCF2EA-WT", "BO 2026 141.556 (keuro, VAK = VEK); CAW-enveloppe ± 128 mln (1.468,93 VTE)", GEL, A, VAK, "GB0-1GCF2EA-WT", "GC", "WELZIJN EN SAMENLEVING", "welzijnswerk (CAW e.a.)"),
    _bu(FOR, 2024, B.BELEID, "realisatie", 2_075_000, S950, U950, T950, "antwoord 1b", "Voor 2024 waren er 3 projecten erkend. De jaarlijkse kostprijs bedroeg toen 2.075.000 € voor personeel en werkingsmiddelen.", GEL, A, label="VAPH-projecten ondersteuning in gevangenissen"),
    _bu(FOR, 2025, B.BELEID, "realisatie", 3_200_000, S950, U950, T950, "antwoord 1b", "Na de uitbreiding in 2024 en rekening houdend met de indexering was de kostprijs in 2025 ongeveer 3.200.000 €.", GEL, A, label="VAPH-projecten ondersteuning in gevangenissen", opm="'ongeveer'"),
]


def main() -> None:
    nb = upsert("bronnen", BRONNEN)
    _update_voorzieningen()
    nv = upsert("bevindingen", BEVINDINGEN)
    nu = upsert("budgetten", BUDGETTEN)
    print(f"ronde 6: bronnen {nb}, bevindingen {nv}, budgetten {nu} (upsert); draai 'wachtlijst validate' en 'wachtlijst publish'")


if __name__ == "__main__":
    main()
