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
    Bron(bron_id="vlpar-sv-783-2025-rth", naam="SV nr. 783 (2024-2025), Dillen → min. Gennez — rechtstreeks toegankelijke hulp, gebruik (punten per gebruiker)",
         organisatie="Vlaams Parlement", url=PF.format(2184544), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 23-07-2025"),
    Bron(bron_id="vlpar-sv-499-2025-hulpm", naam="SV nr. 499 (2024-2025), Vandromme → min. Gennez — hulpmiddelen en aanpassingen in de thuissituatie (goedkeuringen 2021-2024, bedragen)",
         organisatie="Vlaams Parlement", url=PF.format(2147608), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 08-05-2025"),
    Bron(bron_id="vlpar-sv-279-2024-hulpm", naam="SV nr. 279 (2023-2024), Van der Vloet → min. Crevits — snel degeneratieve aandoening, aanvragen hulpmiddelen (2): mediaan doorlooptijd",
         organisatie="Vlaams Parlement", url=PF.format(2052521), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 07-05-2024"),
    Bron(bron_id="vlpar-sv-624-2026-car", naam="SV nr. 624 (2025-2026), Perdaens → min. Gennez — CAR en CGG, traject nieuw kwaliteits- en financieringsmodel (pilootfase 2026-2027)",
         organisatie="Vlaams Parlement", url=PF.format(2306698), bron_type=BronType.PDF, frequentie="eenmalig", opmerking="gepubliceerd 28-04-2026; CAR in VSB sinds oktober 2023, 100 % prestatiefinanciering"),
    Bron(bron_id="vlpar-sv-950-2026-for", naam="SV nr. 950 (2025-2026), De Reuse → min. Gennez — personen met een handicap in detentie, aangepaste ondersteuning (VAPH-projecten in gevangenissen)",
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
                   "aandoeningen 67 → 28 dagen (2020-2022); geen wachtlijst. Budget: artikel GH0-AGGF2RC-WT 72,5 mln (BO 2019) → 124,4 (uitv. 2024) → 116,7 (uitv. 2025) → 117,4 (BO 2026); hulpmiddelen GH0-AGGF2RB-WT uitvoering 35,2 (2024) en 35,1 mln (2025); uitbreidingsbeleid RTH 4,4 mln (2025, ‑6-jarigen, start 2026).")
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
                   "actieve forensische zorgperiodes 5.731 (2019) → 6.992 (2024); 1.546 voortijdig stopgezette trajecten (2024). CAW justitieel welzijnswerk: geen overkoepelende wachtlijst, per gevangenis 164 wachtenden (juni 2023; "
                   "daarnaast 45 ingeplande gesprekken in Oost-Vlaanderen, dat niet met een wachtlijst werkt); 5.551 → 5.789 gedetineerden onthaald, 1.232 → 1.217 begeleid (2018 → 2022).  VAPH: 7 projecten voor personen met een (vermoeden van) handicap in de gevangenis — 287 (2021) → 701 (2025) ondersteunde personen "
                   "(230 geïnterneerd, 345 gedetineerd, 126 beklaagd), jaarlijkse kostprijs 2,1 mln vóór de uitbreiding van 2024 (3 projecten) → ± 3,2 mln (2025), geen VAPH-aanvraagprocedure. Doorstroom: 85 geïnterneerden via directe financiering en 49 in een forensische VAPH-unit (31-12-2025). Federale kant (FPC's Gent/Antwerpen/Aalst, interneringskamers, PVT) buiten scope; "
                   "forensische VAPH-units buiten de gevangenis: geen wachtcijfers gevonden. Budget forensische CGG binnen enveloppe CGG (VIA-6: +0,5 VTE per forensische werking sinds 2021).")
    a = vz[A60]
    a.scan_status, a.wachtlijst_type = "proef_uitgewerkt", W.GEEN
    a.opmerking = ("Uitgewerkt 1-10-2026: geen wachtlijstmechanisme. Art. 60 §7 is sinds de zesde staatshervorming ingebed in het traject Tijdelijke Werkervaring OCMW (TWE-OCMW); VDAB telt geen art. 60-tewerkstellingen maar "
                   "trajecten met 'tijdig werk' (tewerkstelling start binnen 2 maanden na de start van het traject): 9.222 (2024), 9.763 (t/m nov 2025); uitstroom naar werk 28,8 % (2024), 27,95 % (2025 t/m nov). Het OCMW blijft juridisch werkgever "
                   "(DIMONA), plaats van tewerkstelling niet gekend; Vlaamse opleidings- en omkaderingspremie (art. 61) in 170-179 trajecten. Wijk-werken: 3.365 actieve wijk-werkers (eind 2025), 1.708 met overgangsmaatregel PWA; "
                   "VDAB-budget 9,17 mln (2026); overgang naar samenlevingsjobs; beperking werkloosheid in de tijd raakt de doelgroep. Geen begrotingsartikel art. 60 in de BBT Werk 2026 (financiering via VDAB en federale leefloontoelage).")
    upsert("voorzieningen", [r, c, w, f, a])


def _b(vid, metriek, waarde, eenheid, peildatum, bron_id, url, titel, pagina, passage, definitie, status, pub=None, door="", opm=""):
    return Bevinding(bevinding_id=f"{vid}:{metriek}:{peildatum.isoformat()}", voorziening_id=vid, metriek=metriek, waarde=waarde, eenheid=eenheid, peildatum=peildatum,
                     bron_id=bron_id, bron_url=url, documenttitel=titel, pagina=pagina, passage=passage, definitie=definitie, publicatiedatum=pub,
                     controlestatus=status, gecontroleerd_door=door, gecontroleerd_op=VANDAAG if door else None, opmerking=opm)


BEVINDINGEN: list[Bevinding] = []
JV, TJV, PJV = "vaph-jaarverslag-2025", "VAPH jaarverslag 2025", date(2026, 6, 1)
# Tweede lezing 1-10-2026 (goedgekeurd door EB): passages letterlijk, vindplaatsen gepreciseerd, definities aangescherpt.
GEC, D = Controlestatus.GECONTROLEERD, "onderzoeksagent + 2e lezing Claude + EB (2026-10-01)"
BEVINDINGEN += [
    _b(RTH, "gebruikers_rth", 35711, "personen", date(2024, 12, 31), JV, JV25.format(16), TJV, "pages/16 'Gebruikers van rechtstreeks toegankelijke hulp'", "In 2024 deden er 35.711 mensen een beroep op RTH-ondersteuning.",
       "Unieke personen die in het jaar gebruik maakten van rechtstreeks toegankelijke hulp (VAPH).", GEC, PJV, D),
    _b(RTH, "gebruikers_rth", 37133, "personen", date(2025, 12, 31), JV, JV25.format(16), TJV, "pages/16", "In totaal maakten 37.133 personen gebruik van RTH, waarvan 20.054 van 21 jaar of jonger, 17.078 ouder dan 22 jaar, en 1 waarvan de leeftijd niet gekend is.", "Idem, 2025.", GEC, PJV, D),
    _b(RTH, "erkende_aanbieders_rth", 222, "aanbieders", date(2025, 12, 31), JV, JV25.format(16), TJV, "pages/16", "Op 31 december 2025 waren er 222 erkende aanbieders van rechtstreeks toegankelijke hulp (RTH) goed voor 102.058,82 personeelspunten",
       "Erkende RTH-aanbieders op 31/12 ('In 2025 waren er in totaal 229 aanbieders', incl. niet-erkende).", GEC, PJV, D),
    _b(RTH, "personeelspunten_rth", 102058.82, "personeelspunten", date(2025, 12, 31), JV, JV25.format(16), TJV, "pages/16", "… goed voor 102.058,82 personeelspunten (minder- en meerderjarigen).",
       "Erkende RTH-personeelspunten op 31/12; daarnaast apart vermeld: 17.799,45 punten pilootfase RTH en 1990,31 punten GIO.", GEC, PJV, D,
       opm="vanaf 1-1-2025 zitten de punten RTH-kortverblijf en begeleid werken BuSO (GBO) in de RTH-capaciteit"),
    _b(RTH, "personeelspunten_rth", 101926.28, "personeelspunten", date(2024, 12, 31), JV, JV25.format(16), TJV, "pages/16", "De stijging in personeelspunten ten opzichte van 2024 (101.926,28 punten), is het gevolg van de stopzetting van 1 initiatief in de pilootfase", "Idem, 2024.", GEC, PJV, D,
       opm="peildatum 31/12 impliciet; vergelijkbaarheid met 2025 onzeker door de herindeling van 1-1-2025"),
    _b(RTH, "punten_per_gebruiker", 2.65, "punten", date(2024, 12, 31), "vlpar-sv-783-2025-rth", PF.format(2184544), "SV nr. 783 (2024-2025) Dillen", "antwoord 3, PDF p. 2", "Het gemiddeld aantal punten per gebruiker bedroeg in 2023 2,68 punten en in 2024 2,65.",
       "Gemiddeld aantal RTH-punten per gebruiker op jaarbasis (maximum 8 punten, in de pilootfase 12; VAPH-jaarverslag).", GEC, date(2025, 7, 23), D,
       opm="'het gaat hier om gemiddelde op jaarbasis en er wordt geen rekening gehouden met de effectieve startdatum van de ondersteuning'"),
    _b(RTH, "punten_per_gebruiker", 2.68, "punten", date(2023, 12, 31), "vlpar-sv-783-2025-rth", PF.format(2184544), "SV nr. 783 (2024-2025) Dillen", "antwoord 3, PDF p. 2", "Het gemiddeld aantal punten per gebruiker bedroeg in 2023 2,68 punten", "Idem, 2023.", GEC, date(2025, 7, 23), D),
]
for jaar, n in ((2021, 33545), (2022, 31938), (2023, 33333)):
    BEVINDINGEN.append(_b(RTH, "goedkeuringen_hulpmiddelen", n, "goedkeuringen", date(jaar, 12, 31), "vlpar-sv-499-2025-hulpm", PF.format(2147608), "SV nr. 499 (2024-2025) Vandromme", "antwoord 1, PDF p. 3, tabel",
                          "In deze tabel wordt het aantal goedkeuringen voor hulpmiddelen en aanpassingen weergegeven, opgesplitst per provincie en tussen minder- en meerderjarigen.",
                          "Goedkeuringen voor hulpmiddelen en aanpassingen (VAPH) in het jaar, som van de vijf Vlaamse provincies (Brussel niet in de tabel).", GEC, date(2025, 5, 8), D,
                          opm=f"eigen som van de 10 cellen (5 provincies × minder-/meerderjarig) voor {jaar} = {n:,}".replace(",", ".")))
for jaar, d, n in ((2020, 67, 6), (2021, 39, 8), (2022, 28, 8)):
    BEVINDINGEN.append(_b(RTH, "mediaan_doorlooptijd_hulpmiddelen_sda_dagen", d, "dagen", date(jaar, 12, 31), "vlpar-sv-279-2024-hulpm", PF.format(2052521), "SV nr. 279 (2023-2024) Van der Vloet",
                          "antwoord 3c, PDF p. 4, tabel",
                          "Onderstaande tabel geeft een overzicht van de mediaan van de doorlooptijd van de behandeling van een vraag door het VAPH voor hulpmiddelen aangevraagd buiten "
                          "de refertelijst voor personen met een SDA. … Jaar aanvraag 2020 2021 2022 Mediaan doorlooptijd (dagen) 67 39 28",
                          "Mediaan doorlooptijd van de behandeling door het VAPH van aanvragen voor hulpmiddelen buiten de refertelijst, personen met een snel degeneratieve aandoening (SDA), "
                          "per aanvraagjaar.", GEC, date(2024, 5, 7), D, opm=f"klein aantal: {n} aanvragen buiten de refertelijst in {jaar} (antwoord 3a)"))
BEVINDINGEN += [
    _b(CAR, "pilootprojecten_car_cgg", 9, "voorzieningen", date(2026, 4, 1), "vlpar-sv-624-2026-car", PF.format(2306698), "SV nr. 624 (2025-2026) Perdaens", "antwoord 1-2",
       "De pilootfase zal starten op 1 april 2026 en zal lopen tot en met 31 december 2027. … Volgende negen voorzieningen werden geselecteerd: CAR Brussel, CAR Spermalie, CAR Buggenhout, CAR De Hert, CAR Kohesi, CAR Ascendere, CGG Kohesi, CGG Passant en CGG VBO.",
       "Voorzieningen in de pilootfase van het nieuwe kwaliteits- en financieringsmodel CAR-CGG (6 CAR + 3 CGG).", GEC, date(2026, 4, 28), D, opm="vindplaats PDF p. 2"),
    _b(CAW, "caw_bereikte_clienten_onthaal", 109290, "personen", date(2024, 12, 31), "vlpar-bbt-wvg-2026", PF.format(2227516), "BBT Welzijn en Armoedebestrijding 2026 — 13-Z (2025-2026)", "p. 50, prestatie-informatie CAW (ISE Welzijnswerk)",
       "Aantal bereikte cliënten in 2024: • Onthaal:109.290 • Begeleiding: 28.797 • Totaal:125.488 Aantal ingezette modules in 2024: 28.626",
       "Personen met een hulpvraag bereikt in CAW-onthaal (vraagverheldering, directe hulp, doorverwijzing of toeleiding) in het jaar.", GEC, date(2025, 10, 24), D,
       opm="publicatiedatum: voorblad 'ingediend op 24 oktober 2024 (2025-2026)', typfout voor 2025"),
    _b(CAW, "caw_bereikte_clienten_begeleiding", 28797, "personen", date(2024, 12, 31), "vlpar-bbt-wvg-2026", PF.format(2227516), "BBT Welzijn en Armoedebestrijding 2026 — 13-Z (2025-2026)", "p. 50", "• Begeleiding: 28.797", "Personen met een opgestart CAW-begeleidingstraject in het jaar.", GEC, date(2025, 10, 24), D),
    _b(CAW, "caw_bereikte_clienten_totaal", 125488, "personen", date(2024, 12, 31), "vlpar-bbt-wvg-2026", PF.format(2227516), "BBT Welzijn en Armoedebestrijding 2026 — 13-Z (2025-2026)", "p. 50", "• Totaal:125.488", "Unieke cliënten bereikt in onthaal en/of begeleiding (geen streefwaarde; geen wachttijdindicator).", GEC, date(2025, 10, 24), D,
       opm="geen som: onthaal + begeleiding = 138.087 > totaal, cliënten in beide tellen één keer"),
    _b(CAW, "caw_vte_erkend", 1468.93, "VTE", date(2025, 1, 1), "vlpar-bbt-wvg-2026", PF.format(2227516), "BBT Welzijn en Armoedebestrijding 2026 — 13-Z (2025-2026)", "p. 51",
       "De CAW’s zijn per 1 januari 2025 erkend voor 1.468,93 voltijdse equivalenten. Dit correspondeert met een subsidie-enveloppe van ongeveer 128 miljoen.", "Erkende VTE van de CAW's.",
       GEC, date(2025, 10, 24), D),
]
S950, U950, T950, P950 = "vlpar-sv-950-2026-for", PF.format(2349515), "SV nr. 950 (2025-2026) De Reuse", date(2026, 7, 14)
for jaar, n in ((2021, 287), (2022, 288), (2023, 336), (2024, 440), (2025, 701)):
    BEVINDINGEN.append(_b(FOR, "vaph_ondersteund_in_gevangenis", n, "personen", date(jaar, 12, 31), S950, U950, T950, "antwoord 1c, PDF p. 4, tabel",
                          "2025 2024 2023 2022 2021 … Totaal 701 440 336 288 287",
                          "Personen met een (vermoeden van) handicap ondersteund door de VAPH-projecten in de gevangenissen (geïnterneerd, gedetineerd, beklaagd); 7 projecten sinds mei 2024 (3 ervoor).",
                          GEC, P950, D, opm=("reeksbreuk: 'Sinds 1 mei 2024 zijn er 4 bijkomende projecten erkend'; de uitbreiding verdubbelde het aantal bediende gevangenissen"
                                             if jaar >= 2024 else "")))
BEVINDINGEN += [
    _b(FOR, "vaph_projecten_gevangenis", 7, "projecten", date(2025, 12, 31), S950, U950, T950, "antwoord 1a, PDF p. 3", "Het gaat in totaal over 7 projecten.",
       "Erkende VAPH-projecten voor ondersteuning in de gevangenissen (2.533 personeelspunten).", GEC, P950, D,
       opm="peildatum = stand bij het antwoord (2026), ongewijzigd sinds 1-5-2024; personeelspunten 752 + 179 + 716 + 154 + 250 + 250 + 232 = 2.533 (eigen som)"),
    _b(FOR, "geinterneerden_directe_financiering", 85, "personen", date(2025, 12, 31), S950, U950, T950, "antwoord 4, PDF p. 5",
       "Op 31 december 2025 werden er 85 geïnterneerden ondersteund door een vergunde zorgaanbieder via de directe financiering geïnterneerden. 23 geïnterneerden stroomden in de loop van 2025 in.",
       "Geïnterneerden ondersteund door een vergunde zorgaanbieder via de directe financiering geïnterneerden (VAPH), op 31/12.", GEL, P950, A, opm="instroom 2025: 23"),
    _b(FOR, "geinterneerden_forensische_vaph_unit", 49, "personen", date(2025, 12, 31), S950, U950, T950, "antwoord 4, PDF p. 5",
       "Daarnaast waren er op 31 december 2025 ook 49 geïnterneerden opgenomen in een forensische VAPH-unit",
       "Geïnterneerden opgenomen in een forensische VAPH-unit op 31/12.", GEL, P950, A,
       opm="61 personen hadden een PVB ter beschikking volgend op een opname directe financiering (PDF p. 6); toegewezen PVB standaard in prioriteitengroep 1"),
]


def _bu(vid, jaar, fase, niveau, bedrag, bron_id, url, titel, pagina, passage, status, door="", krediet=Kredietsoort.NVT, artikel="", programma="", ise="", label="", opm=""):
    key = artikel or label.replace(" ", "_")[:40]
    return Budget(budget_id=f"{vid}:{jaar}:{fase.value}:{niveau}:{krediet.value}:{key}", voorziening_id=vid, begrotingsjaar=jaar, fase=fase, niveau=niveau, bedrag_eur=bedrag,
                  kredietsoort=krediet, artikel_code=artikel, programma=programma, ise=ise, label=label, bron_id=bron_id, bron_url=url, documenttitel=titel, pagina=pagina,
                  passage=passage, controlestatus=status, gecontroleerd_door=door, gecontroleerd_op=VANDAAG if door else None, opmerking=opm)


B, VAK = Budgetfase, Kredietsoort.VAK
PMB = "PERSONEN MET EEN BEPERKING"
BUDGETTEN = [
    _bu(RTH, 2019, B.BO, "entiteit_begroting", 72_500_000, "vlpar-bbt-wvg-2020", PF.format(1551598), "BBT WVG 2020 — 13-Y (2019-2020)", "p. 76, artikel GH0-AGGF2RC-WT", "GH0-AGGF2RC-WT FINANDIERING VAN RECHTSTREEKS TOEGANKELIJKE … Kredietevolutie: (duizend euro) VAK VEK … BO 2019 72.500 72.500", GEC, D, VAK,
        "GH0-AGGF2RC-WT", "GG", PMB, "RTH (VAPH-begroting)", opm="uit kredieten.csv (parser), stuk 13-Y; 'FINANDIERING' = tikfout in de bron; BO 2020 excl./incl. overflow 78.709"),
    _bu(RTH, 2024, B.UITV, "entiteit_begroting", 124_370_000, "vlpar-bbt-wvg-uitv-2024", PF.format(2162480), "BBT WVG begrotingsuitvoering 2024 — 23-T (2024-2025)", "p. 133, artikel GH0-AGGF2RC-WT", "(duizend euro) VAK VEK … BA 2024 124.370 124.370 BU 2024 124.370 124.370", GEC, D, VAK, "GH0-AGGF2RC-WT", "GG", PMB,
        "RTH (VAPH-begroting, uitvoering)", opm="uit kredieten.csv; BU = begrotingsuitvoering"),
    _bu(RTH, 2025, B.UITV, "entiteit_begroting", 116_723_000, "vlpar-bbt-wvg-uitv-2025", PF.format(2325132), "BBT WVG begrotingsuitvoering 2025 — 23-V (2025-2026)", "p. 124, artikel GH0-AGGF2RC-WT", "BA 2025 115.400 115.400 BA – JR 2025 116.800 116.800 BU 2025 116.723 116.723", GEC, D, VAK, "GH0-AGGF2RC-WT", "GG", PMB,
        "RTH (VAPH-begroting, uitvoering)", opm="uit kredieten.csv; krediet na BA 2025 met 1,4 mln verhoogd (spilindex)"),
    _bu(RTH, 2026, B.BO, "entiteit_begroting", 117_400_000, "vlpar-bbt-wvg-2026", PF.format(2227516), "BBT Welzijn en Armoedebestrijding 2026 — 13-Z (2025-2026)", "p. 186-187, artikel GH0-AGGF2RC-WT", "BA 2025 115.400 115.400 Index 2.000 2.000 BO 2026 117.400 117.400", GEC, D, VAK, "GH0-AGGF2RC-WT", "GG", PMB,
        "RTH (VAPH-begroting)", opm="uit kredieten.csv; artikelkop p. 186, tabel p. 187"),
    _bu(RTH, 2024, B.UITV, "entiteit_begroting", 35_151_000, "vlpar-bbt-wvg-uitv-2024", PF.format(2162480), "BBT WVG begrotingsuitvoering 2024 — 23-T (2024-2025)",
        "p. 133, artikel GH0-AGGF2RB-WT", "GH0-AGGF2RB-WT FINANCIERING VAN HULPMIDDELEN (duizend euro) … BA 2024 48.206 37.231 BU 2024 35.151 35.151", GEL, A, VAK, "GH0-AGGF2RB-WT", "GG", PMB,
        "hulpmiddelen (VAPH-begroting, uitvoering)", opm="BA 2024: VAK 48.206, VEK 37.231"),
    _bu(RTH, 2025, B.UITV, "entiteit_begroting", 35_115_000, "vlpar-bbt-wvg-uitv-2025", PF.format(2325132), "BBT WVG begrotingsuitvoering 2025 — 23-V (2025-2026)",
        "p. 124, artikel GH0-AGGF2RB-WT", "GH0-AGGF2RB-WT FINANCIERING VAN HULPMIDDELEN (duizend euro) … BA 2025 48.957 37.763 BA – JR 2025 48.957 37.763 BU 2025 35.115 35.115", GEL, A, VAK,
        "GH0-AGGF2RB-WT", "GG", PMB, "hulpmiddelen (VAPH-begroting, uitvoering)", opm="BA 2025: VAK 48.957, VEK 37.763"),
    _bu(RTH, 2025, B.BELEID, "uitbreidingsbeleid", 4_400_000, JV, JV25.format(45), TJV, "pages/45, tabel middelen uitbreidingsbeleid 2025",
        "Rechtstreeks toegankelijke hulp 4,4 miljoen … Totaal 102,4 miljoen … Tot slot werd ook voor rechtstreeks toegankelijke hulp (RTH) een uitbreiding voorzien voor preventieve, "
        "vroegtijdige en laagdrempelige ondersteuning aan ‑6-jarigen van 4,3 miljoen euro, die zijn opstart zal kennen vanaf 2026.", GEC, D, label="uitbreidingsbeleid RTH (−6-jarigen)",
        opm="tabel 4,4 mln, tekst 4,3 mln (verschil in de bron); dezelfde 4,4 mln zit in de rij vaph-pab-minderjarigen 'uitbreidingsbeleid MFC + RTH minderjarig' (12,9 mln) — niet optellen"),
    _bu(CAR, 2025, B.BA, "entiteit_begroting", 207_852_000, "vlpar-bbt-wvg-2026", PF.format(2227516), "BBT Welzijn en Armoedebestrijding 2026 — 13-Z (2025-2026)", "p. 105-106, artikel GM0-AGCF2LF-WT",
        "GM0-AGCF2LF-WT – Werking en Toelagen – Sociale Bescherming – Revalidatie Voorzieningen … (duizend euro) VAK VEK BA 2025 207.852 207.852 Index 4.157 4.157 … BO 2026 213.430 213.430", GEC, D, VAK, "GM0-AGCF2LF-WT", "GC", "GESPECIALISEERDE ZORG", "revalidatie VSB (CAR, verslavingszorg 7.73 e.a.)",
        opm="CAR-aandeel niet afgesplitst; de BBT noemt geen CAR — toewijzing via SV 624 (CAR sinds oktober 2023 in de VSB via revalidatieovereenkomst) en SV 568"),
    _bu(CAR, 2026, B.BO, "entiteit_begroting", 213_430_000, "vlpar-bbt-wvg-2026", PF.format(2227516), "BBT Welzijn en Armoedebestrijding 2026 — 13-Z (2025-2026)", "p. 105-106, artikel GM0-AGCF2LF-WT", "BO 2026 213.430 213.430", GEC, D, VAK, "GM0-AGCF2LF-WT", "GC", "GESPECIALISEERDE ZORG", "revalidatie VSB (CAR, verslavingszorg 7.73 e.a.)"),
    _bu(CAW, 2025, B.BA, "dept_artikel", 141_740_000, "vlpar-bbt-wvg-2026", PF.format(2227516), "BBT Welzijn en Armoedebestrijding 2026 — 13-Z (2025-2026)", "p. 59-60, artikel GB0-1GCF2EA-WT",
        "GB0-1GCF2EA-WT - WELZIJNSWERK Op dit begrotingsartikel zijn de subsidies opgenomen voor de CAW’s, de centra voor teleonthaal en de samenwerkingsverbanden voor schuldhulpverlening. "
        "(duizend euro) VAK VEK BA 2025 141.740 141.740 Index 2.793 2.793 Compensaties -1.477 -1.477 Andere bijstellingen -1.500 -1.500 BO 2026 141.556 141.556", GEC, D, VAK, "GB0-1GCF2EA-WT", "GC",
        "WELZIJNSWERK", "welzijnswerk (CAW e.a.)", opm="tabel p. 59, toelichting p. 60; ISE Welzijnswerk (p. 50)"),
    _bu(CAW, 2026, B.BO, "dept_artikel", 141_556_000, "vlpar-bbt-wvg-2026", PF.format(2227516), "BBT Welzijn en Armoedebestrijding 2026 — 13-Z (2025-2026)", "p. 59, artikel GB0-1GCF2EA-WT", "BO 2026 141.556 141.556", GEC, D, VAK, "GB0-1GCF2EA-WT", "GC", "WELZIJNSWERK", "welzijnswerk (CAW e.a.)",
        opm="CAW-subsidie-enveloppe ± 128 mln (1.468,93 VTE) staat op p. 51; artikel omvat ook teleonthaal en schuldhulpverlening"),
    _bu(FOR, 2023, B.BELEID, "realisatie", 2_075_000, S950, U950, T950, "antwoord 1b, PDF p. 4",
        "Voor 2024 waren er 3 projecten erkend. De jaarlijkse kostprijs bedroeg toen 2.075.000 € voor personeel en werkingsmiddelen.", GEC, D,
        label="VAPH-projecten ondersteuning in gevangenissen",
        opm="jaarlijkse kostprijs van de 3 projecten vóór de uitbreiding van 1 mei 2024 ('Voor 2024 … toen'), geen realisatie van 2024; begrotingsjaar 2023 = laatste volle jaar met 3 projecten"),
    _bu(FOR, 2025, B.BELEID, "realisatie", 3_200_000, S950, U950, T950, "antwoord 1b, PDF p. 4",
        "Na de uitbreiding in 2024 en rekening houdend met de indexering was de kostprijs in 2025 ongeveer 3.200.000 €.", GEC, D, label="VAPH-projecten ondersteuning in gevangenissen",
        opm="'ongeveer'; jaarlijkse kostprijs, 7 projecten"),
]


def main() -> None:
    nb = upsert("bronnen", BRONNEN)
    _update_voorzieningen()
    nv = upsert("bevindingen", BEVINDINGEN)
    nu = upsert("budgetten", BUDGETTEN)
    print(f"ronde 6: bronnen {nb}, bevindingen {nv}, budgetten {nu} (upsert); draai 'wachtlijst validate' en 'wachtlijst publish'")


if __name__ == "__main__":
    main()
