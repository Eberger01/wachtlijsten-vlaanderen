# Onderzoeksafbakening (voorstel)

*Status: **bevestigd door het onderzoeksteam op 1 oktober 2026** — scope = Vlaamse Gemeenschap + Vlaams Gewest, `bevoegdheid` als filterattribuut; tweede proefvoorziening = sociale huur.*

## Onderzoeksvraag

> Welke overheidsdiensten van het Vlaamse Gewest beschikken over een wachtlijst voor het toekennen van voorzieningen van de sociale politiek?

## 1. Scope-check: "Vlaams Gewest" dekt de bedoelde scope niet — neem de Vlaamse Gemeenschap mee

De term "sociale politiek" verwijst in de Belgische staatsstructuur grotendeels naar **persoonsgebonden aangelegenheden**, en die zijn een bevoegdheid van de **Gemeenschappen**, niet van de Gewesten:

| Materie | Bevoegd | Grondslag |
|---|---|---|
| Gezondheidsbeleid, bijstand aan personen (gezinsbeleid, maatschappelijk welzijn, personen met een handicap, ouderenbeleid, jeugdbescherming/jeugdhulp, onthaal en integratie van inwijkelingen, hulp aan gedetineerden) | **Vlaamse Gemeenschap** | GW art. 128 §1; BWHI 8-8-1980 art. 5 §1 |
| Onderwijs | **Vlaamse Gemeenschap** | GW art. 127 §1, 2° |
| Huisvesting (sociale huur, sociale koop, huurpremie, woonleningen), tewerkstelling (VDAB, sociale economie), energie (premies, leningen) | **Vlaams Gewest** | GW art. 39; BWHI art. 6 §1 IV, VII, IX |
| Uitoefening van beide bevoegdheidspakketten door **één** Vlaams Parlement en **één** Vlaamse Regering | — | GW art. 137; BWHI art. 1 §1 |

Gevolgen voor het onderzoek:

1. Strikt "Vlaams Gewest" zou de grootste wachtlijsten (VAPH-PVB, jeugdhulp, woonzorg, CGG, kinderopvang, buitengewoon onderwijs) **uitsluiten** en enkel sociale huisvesting, maatwerk en energiepremies overhouden. Dat is vrijwel zeker niet wat bedoeld wordt.
2. **Voorstel**: formuleer de vraag als *"overheidsdiensten van de Vlaamse overheid (Gemeenschap én Gewest)"* en registreer per voorziening de **bevoegdheid** als attribuut (`bevoegdheid` in `voorzieningen.csv`). Het dashboard kan dan alsnog op Gewest filteren.
3. Omdat Parlement en Regering voor beide identiek zijn, hoeft de **bronnenkaart niet te splitsen** op instelling — wel op materie (thema-facet in de Parlement-API, beleidsdomein in de begroting).

## 2. Wat telt als "voorziening van de sociale politiek"?

Werkdefinitie: een **individueel toekenbaar recht, budget, plaats of dienst** die de Vlaamse overheid (rechtstreeks of via erkende/gesubsidieerde aanbieders) toewijst aan burgers op grond van een sociale behoefte, en waarvan de toewijzing door **schaarste** (budget, capaciteit, urencontingent, programmatie) wordt begrensd.

Inbegrepen domeinen (brede scan): handicap, jeugdhulp, gezin/kinderopvang, ouderenzorg, geestelijke gezondheidszorg, thuiszorg, Vlaamse sociale bescherming, wonen (sociale huur/koop, premies, leningen), inburgering/NT2, onderwijs (capaciteit, buitengewoon onderwijs), werk (sociale economie), justitiehuizen.

Uitgesloten: federale materies (ziekteverzekering/RIZIV, pensioenen, leefloon-uitkering zelf, werkloosheid), lokale OCMW-dienstverlening zonder Vlaamse toewijzingsregeling, Brusselse gemeenschapsinstellingen (VGC) tenzij ze Vlaamse voorzieningen uitvoeren.

## 3. Wat is een "wachtlijst"? — typologie

Niet elke schaarste produceert een *lijst*. We onderscheiden vier types (`wachtlijst_type`):

| Type | Betekenis | Voorbeelden |
|---|---|---|
| `centraal_gepubliceerd` | Vlaamse entiteit beheert een register en publiceert periodiek cijfers | VAPH-PVB (prioriteitengroepen), Opgroeien-NRTJ, Centraal Inschrijvingsregister sociale huur, AgII-KPI maatschappelijke oriëntatie |
| `centraal_niet_gepubliceerd` | Cijfers bestaan centraal maar komen enkel naar buiten via parlementaire vragen | CGG-wachttijden, collectief maatwerk (VDAB) |
| `decentraal` | Lijsten per voorziening/aanbieder; de Vlaamse overheid stelt expliciet dat ze **geen** centrale registratie bijhoudt | woonzorgcentra, kinderopvang (lokale loketten), buitengewoon onderwijs (LOP), gezinszorg (urencontingent), NT2, sociale koop, COS |
| `geen` | Rechtsgebonden toekenning of enveloppe zonder lijst | zorgbudgetten VSB, huurpremie, Mijn VerbouwPremie, woonlening, IBO |

Bijkomende aandachtspunten: **aanbodzijde-lijsten** (erkenningskalender woonzorg, uitbreidingsrondes kinderopvang) zijn wachtlijsten voor *organisatoren*, niet voor burgers — apart labelen. **Doorlooptijd** (VSB) is geen wachtlijst maar wel een schaarste-indicator.

## 4. Tijdsvenster en peildata

Startpunt 2019 (begin vorige legislatuur en hervorming begrotingsstructuur VCO); halfjaarlijkse peildata waar de bron dat toelaat (VAPH: 30/06 en 31/12). Elk cijfer krijgt zijn eigen `peildatum` én `publicatiedatum`.

## 5. Controleprotocol

Elke bevinding draagt `controlestatus`: `ongecontroleerd` (secundaire bron of nog niet nagelezen) → `bron_gelezen` (één onderzoeker las de primaire bron en citeerde de passage) → `gecontroleerd` (tweede onafhankelijke lezing). `betwist` wanneer bronnen elkaar tegenspreken; de `opmerking` legt uit waarom. Het dashboard toont ongecontroleerde/betwiste punten met open markers.

## 6. Proefvoorziening

Het **persoonsvolgend budget (VAPH)** is als proef volledig uitgewerkt: tijdreeks 2019–2025 per prioriteitengroep, wachttijd van de eerstvolgende wachtende, terbeschikkingstellingen, en budget (uitbreidingsbeleid, realisatie, begrotingsartikel GB0-1GGF2RX-IS). Zie `data/curated/` en het dashboard.

## 6b. Tweede proefvoorziening: sociale huur (Vlaams Gewest)

Uitgewerkt op 1 oktober 2026: reeks kandidaat-huurders 2018–2025 (met breuk in 2023 door de overgang naar het Centraal
Inschrijvingsregister en drie opeenvolgende definities), toewijzingen, wachttijd bij toewijzing, patrimonium, huurpremie,
en budget op drie niveaus (FS3-financiering, begrotingsartikelen QF0-1QDB2PA-WT / QF0-1QDB5PJ-IS, nettofinanciering
VMSW/VWF volgens het Rekenhof). Zie `docs/03-inventaris.md` §E.

## 7. Beslist / nog open

- **Beslist**: scope Gemeenschap + Gewest; `bevoegdheid` als filter; proeven VAPH-PVB en sociale huur; fase 3 via BBT per ISE.
- Open: nemen we aanbodzijde-lijsten (erkenningskalender woonzorg, uitbreidingsrondes kinderopvang) op als aparte categorie `aanbodzijde`?
- Open: derde voorziening — NRTJ jeugdhulp (Power BI) of inburgering (AgII-jaarverslag)?
