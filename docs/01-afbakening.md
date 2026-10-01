# Methodiek en afbakening

*Stand 1 oktober 2026. De scope (Vlaamse Gemeenschap én Vlaams Gewest) is bevestigd door het onderzoeksteam; alle
voorzieningen uit de inventaris zijn uitgewerkt of afgesloten. De tabellen onderaan deze pagina worden rechtstreeks
uit de gepubliceerde gegevens berekend.*

## Onderzoeksvraag

> Welke overheidsdiensten van de **Vlaamse overheid (Gemeenschap én Gewest)** beschikken over een wachtlijst voor het
> toekennen van voorzieningen van de sociale politiek, en welke budgetten horen daarbij?

De oorspronkelijke vraag sprak van het "Vlaamse Gewest". Om de redenen hieronder nemen we de Vlaamse Gemeenschap
uitdrukkelijk mee en registreren we per voorziening de **bevoegdheid** (`bevoegdheid`), zodat het dashboard alsnog op
Gewest of Gemeenschap kan filteren.

## 1. Scope: Vlaamse Gemeenschap én Vlaams Gewest

De term "sociale politiek" verwijst in de Belgische staatsstructuur grotendeels naar **persoonsgebonden
aangelegenheden**, en die zijn een bevoegdheid van de **Gemeenschappen**, niet van de Gewesten:

| Materie | Bevoegd | Grondslag |
|---|---|---|
| Gezondheidsbeleid, bijstand aan personen (gezinsbeleid, maatschappelijk welzijn, personen met een handicap, ouderenbeleid, jeugdhulp, onthaal en integratie van inwijkelingen, hulp aan gedetineerden en justitiehuizen) | **Vlaamse Gemeenschap** | GW art. 128 §1; BWHI 8-8-1980 art. 5 §1 |
| Onderwijs | **Vlaamse Gemeenschap** | GW art. 127 §1, 2° |
| Huisvesting (sociale huur, sociale koop, huurpremie, woonleningen), tewerkstelling (VDAB, sociale economie, wijk-werken), energie (premies, leningen) | **Vlaams Gewest** | GW art. 39; BWHI art. 6 §1 IV, VII, IX |
| Uitoefening van beide bevoegdheidspakketten door **één** Vlaams Parlement en **één** Vlaamse Regering | — | GW art. 137; BWHI art. 1 §1 |

Gevolgen:

1. Strikt "Vlaams Gewest" zou de grootste wachtlijsten (VAPH-PVB, jeugdhulp, woonzorg, CGG, kinderopvang, buitengewoon
   onderwijs) **uitsluiten** en enkel wonen, werk en energie overhouden. Daarom nemen we beide mee.
2. Omdat Parlement en Regering voor beide identiek zijn, splitst de bronnenkaart niet op instelling, wel op materie
   (thema-facet in de Parlement-API, beleidsdomein in de begroting).

## 2. Wat telt als "voorziening van de sociale politiek"?

Werkdefinitie: een **individueel toekenbaar recht, budget, plaats of dienst** die de Vlaamse overheid (rechtstreeks of
via erkende/gesubsidieerde aanbieders) toewijst aan burgers op grond van een sociale behoefte, en waarvan de toewijzing
door **schaarste** (budget, capaciteit, urencontingent, programmatie) wordt begrensd.

Domeinen in de inventaris: handicap (PVB, PAB, RTH en hulpmiddelen, COS), jeugdhulp (NRTJ, pleegzorg), gezin
(kinderopvang), ouderenzorg (woonzorg), geestelijke gezondheidszorg (CGG, CAW en verslavingszorg), revalidatie (CAR),
thuiszorg (gezinszorg), Vlaamse sociale bescherming (zorgbudgetten), justitie (justitiehuizen, forensische zorg),
wonen (sociale huur en koop, huurpremie, premies, woonlening), inburgering (maatschappelijke oriëntatie, NT2),
onderwijs (buitengewoon onderwijs) en werk (collectief maatwerk, IBO, art. 60 en wijk-werken).

Uitgesloten: federale materies (ziekteverzekering/RIZIV, pensioenen, leefloon-uitkering zelf, werkloosheid), lokale
OCMW-dienstverlening zonder Vlaamse toewijzingsregeling, Brusselse gemeenschapsinstellingen (VGC) tenzij ze Vlaamse
voorzieningen uitvoeren.

## 3. Wat is een "wachtlijst"? — typologie

Niet elke schaarste produceert een *lijst*. We onderscheiden vier types (`wachtlijst_type`):

| Type | Betekenis | Voorbeelden |
|---|---|---|
| `centraal_gepubliceerd` | Vlaamse entiteit beheert een register en publiceert periodiek cijfers | VAPH-PVB (prioriteitengroepen), Opgroeien-NRTJ, Centraal Inschrijvingsregister sociale huur, PAB minderjarigen |
| `centraal_niet_gepubliceerd` | Cijfers bestaan centraal maar komen enkel naar buiten via parlementaire vragen of een niet meer gepubliceerde KPI | CGG-wachttijden, collectief maatwerk, pleegzorg, justitiehuizen, forensische zorg, inburgering MO, NT2 |
| `decentraal` | Lijsten per voorziening of aanbieder; de Vlaamse overheid houdt **geen** centrale registratie bij | woonzorg, kinderopvang, buitengewoon onderwijs, COS, CAR, CAW en verslavingszorg, sociale koop |
| `geen` | Rechtsgebonden toekenning, enveloppe of contingent zonder lijst | zorgbudgetten VSB, huurpremie, Mijn VerbouwPremie/-Lening, woonlening, IBO, gezinszorg (urencontingent), VAPH RTH en hulpmiddelen, art. 60 en wijk-werken |

Ook zonder lijst verzamelen we **schaarste-indicatoren**: doorlooptijden (hulpmiddelen), urencontingenten
(gezinszorg), tekortramingen (kinderopvang, buitengewoon onderwijs) en **aanbodzijde-lijsten** (erkenningskalender
woonzorg, uitbreidingsrondes kinderopvang). Die laatste zijn wachtlijsten voor *organisatoren*, niet voor burgers; ze
staan als afzonderlijke metrieken in het dossier van de voorziening, met die nuance in de `definitie`, en niet als
apart wachtlijsttype.

## 4. Tijdsvenster en peildata

Startpunt 2019 (begin vorige legislatuur en hervorming begrotingsstructuur); oudere punten worden opgenomen waar ze een
reeks verduidelijken (bv. sociale huur vanaf 2018, sociale koop vanaf 2014). Halfjaarlijkse peildata waar de bron dat
toelaat (VAPH: 30/06 en 31/12), anders jaarlijks of de datum van de parlementaire vraag. Elk cijfer krijgt zijn eigen
`peildatum` én `publicatiedatum`; ramingen voor de toekomst (bv. tekort buitengewoon onderwijs 2030) dragen de
peildatum waarop ze slaan. **Definitiewissels** (bv. overgang naar het Centraal Inschrijvingsregister in 2023) worden
niet weggewerkt maar als reeksbreuk in de `opmerking` gemeld.

## 5. Bronnen

Voorrang voor primaire bronnen van de Vlaamse overheid: jaarverslagen en cijferrapporten van de agentschappen (VAPH,
Opgroeien, Wonen in Vlaanderen, AgII, Departement Zorg), open data (WEWIS, Codex), schriftelijke vragen en antwoorden
via de API van het Vlaams Parlement, en de Beleids- en Begrotingstoelichtingen (BBT's). Pers en middenveld gelden als
**secundaire** bron en worden als `ongecontroleerd` gemarkeerd. Het tabblad *Bronnen*
toont per bron het kanaal, de frequentie en hoe ze machinaal te bevragen is.

## 6. Controleprotocol

Elke bevinding en elke budgetrij draagt een `controlestatus`:

- `ongecontroleerd`: secundaire bron of nog niet nagelezen;
- `bron_gelezen`: één lezing van de primaire bron, met het letterlijke citaat in `passage` en de vindplaats in `pagina`;
- `gecontroleerd`: een tweede, onafhankelijke lezing bevestigt waarde, eenheid, peildatum en definitie;
- `betwist`: bronnen spreken elkaar tegen; de `opmerking` legt uit waarom.

`gecontroleerd_door` en `gecontroleerd_op` leggen vast wie las en wanneer (onderzoeksagent, tweede lezing, eigen
berekening goedgekeurd door de onderzoeker). Een eigen berekening, zoals het gewogen sectorgemiddelde van de
CGG-wachttijden, staat als zodanig gemarkeerd. Het dashboard toont ongecontroleerde en betwiste punten met open markers.

## 7. Budgetten

Per voorziening koppelen we budgetten (`budgetten.csv`) aan het **begrotingsartikel** (fase BO, BA of UITV;
vastleggings- en vereffeningskrediet, VAK/VEK), de **begroting van het agentschap** en **beleidsbedragen** zoals
uitbreidingsbeleid en realisaties. Daarnaast zijn alle kredietrijen van de 29 BBT's van Welzijn, Volksgezondheid en Gezin en van
Wonen (2020–2026) machinaal uit de PDF's gelezen (`kredieten.csv`, status `bron_gelezen`, steekproef 40/40 letterlijk
teruggevonden). VEK, niet VAK, is de maat voor wat in een jaar effectief wordt uitbetaald.

## 8. Stand van het onderzoek

Elke voorziening heeft een `scan_status`: `te_onderzoeken` → `in_onderzoek` → `proef_uitgewerkt` (tijdreeks, bronnen en
budget in de data) of `afgerond` (onderzocht; geen bruikbare Vlaamse reeks of geen wachtlijst). De eerste proeven waren
het persoonsvolgend budget (VAPH) en sociale huur; daarna volgden de overige voorzieningen in rondes. De dossiers per
voorziening staan in
[`docs/03-inventaris.md`](https://github.com/Eberger01/wachtlijsten-vlaanderen/blob/main/docs/03-inventaris.md), de
vaste updatecyclus in
[`docs/09-draaiboek.md`](https://github.com/Eberger01/wachtlijsten-vlaanderen/blob/main/docs/09-draaiboek.md).

## 9. Beperkingen

- Bij decentrale lijsten bestaat geen Vlaams cijfer; wat we tonen zijn schaarste-indicatoren, geen wachtenden.
- Cijfers uit parlementaire vragen zijn momentopnames met wisselende definities; reeksen lopen enkel door zolang
  dezelfde vraag terugkomt.
- Aantallen in verschillende voorzieningen zijn niet optelbaar: één persoon kan op meerdere lijsten staan, en lijsten
  tellen soms vragen, soms personen.
- De machinaal gelezen BBT-kredieten hebben één lezing; ISE-totaalregels van vóór 2022 zijn minder betrouwbaar dan de
  artikelregels.
