# Bronnenkaart — publieke publicatiekanalen

*Stand 1 oktober 2026. ✅ = endpoint/pagina effectief opgehaald en structuur bevestigd; (nv) = niet geverifieerd. De machineleesbare versie staat in `data/curated/bronnen.csv`.*

## Kernconclusie

Er bestaat **geen open dataset "wachtlijsten"** in de Vlaamse datacatalogus (Datavindplaats: 0 treffers) en **geen open data van de begroting per begrotingsartikel**. Wachtlijstcijfers leven in (a) agentschapsrapporten (VAPH, Opgroeien, Wonen in Vlaanderen, AgII) en (b) antwoorden op schriftelijke vragen. Het **Vlaams Parlement Document Search API** is daarom de primaire machinale ingang; agentschapspagina's worden gericht gescrapet.

## 1. Vlaams Parlement

| Bron | Type | Bevragen | Opmerking |
|---|---|---|---|
| **Document Search API** ✅ `https://ws.vlpar.be/api/search/query/{term}?collection=vp_collection&page=1&max=50&sort=date` | JSON | Per hit `metatags`: zittingsjaar, nummer, soort (SCHV/VI/PI/JLN), aggregaattype (Schriftelijke vraag, Vraag om uitleg, Verslag van het Rekenhof, …), thema, minister, vraagsteller, publicatiedatum, **document** (PDF-URL), **opendata** (XML-URL). Facetten: minister, commissie, aggregaattype, thema, zittingsjaar, … | "wachtlijst" → 12.552 hits; Swagger `https://ws.vlpar.be/v3/api-docs`. Licentie: Modellicentie Gratis Hergebruik v1.0. Bulk = pagineren. |
| **Open data XML** ✅ `http://ws.vlpar.be/e/opendata/{schv|vi|jln|vv|verg}/{id}` | XML | Volledige metadata per entiteit incl. PDF-link | Docs: vlaamsparlement.be → dossiers → open data |
| **PDF** ✅ `https://docs.vlaamsparlement.be/files/pfile?id={id}` | PDF | pdfplumber; `wachtlijst.sources.vlpar.grep_pdf` | Vraag + antwoord, BBT's, begroting, Rekenhof |
| Website-zoekfunctie `…/documenten/alle-documenten?query=…&aggregaat[]=…` | HTML | scrape | API is betrouwbaarder |
| Dossier Begroting {jaar} ✅ `…/dossiers/dossiers/begroting-2026` | HTML→PDF | per jaar alle stukken | stuk 13-x BBT opmaak, 15 uitgaven (+Bijlage 2 rechtspersonen), 16 Rekenhof, 19 aanpassing, 23-x BBT uitvoering |
| flempar (R, UAntwerpen) | wrapper | referentie-implementatie bulk-harvest | zelfde endpoints |

Zoektermen die werken: `wachtlijst`, `wachtenden`, `wachttijd`, `prioriteitengroep`, `kandidaat-huurders`, `zorgbudget`, `urencontingent`, `"Verslag van het Rekenhof" wachtlijst`.

## 2. Vlaamse Regering & regelgeving

| Bron | Type | Bevragen |
|---|---|---|
| **Themis** ✅ `https://themis.vlaanderen.be/` (Kanselarij) | JSON:API + Turtle | `/catalogs` → `/datasets` (1 per ministerraad) → `/distributions`; PDF `…/files/{id}/download`. Bevat BBT's als mededeling aan de VR. |
| Beslissingen VR ✅ `vlaanderen.be/vlaamse-regering/beslissingen-van-de-vlaamse-regering` | HTML | scrape; geen API/RSS |
| **Vlaamse Codex API** ✅ `https://codex.opendata.api.vlaanderen.be/` | JSON | `/api/WetgevingDocument/Zoeken?Zoekterm=…`, `/api/WetgevingDocument/{id}/Structuur`; BWHI = id 1004736 |
| Belgisch Staatsblad / Justel | HTML (cgi) | robots blokkeert; Codex-API (met Numac) is de betere ingang |

## 3. Open data & statistiek

| Bron | Resultaat |
|---|---|
| Datavindplaats ✅ `vlaanderen.be/datavindplaats/catalogus?q=wachtlijst` | 0 datasets |
| metadata.vlaanderen.be (GeoNetwork) ✅ | record-API per uuid |
| Statistiek Vlaanderen ✅ | geen wachtlijststatistiek; wel COFOG-uitgaven (sociale bescherming ≈ 27 % van 64,7 mld, 2025) |
| WEWIS open data (Werk/Sociale Economie) ✅ | Opendatasoft; geen wachtlijstdata |
| publicaties.vlaanderen.be ✅ `view-file/{id}` | PDF's van agentschappen (bv. VAPH in cijfers 2025 = 85057) |

## 4. Agentschappen (cijferpublicaties)

| Entiteit | Bron | Formaat | Frequentie |
|---|---|---|---|
| VAPH | `extranet.vaph.be/jaarverslag/{jaar}/pages/{n}` ✅ (2023/2024: Prioriteitengroepen = pages/25); PDF "Het VAPH in cijfers"; Tableau Public `vaph8585` | HTML, PDF, Tableau | halfjaarlijks + jaarlijks. **www.vaph.be blokkeert bots (403)**, extranet niet |
| Opgroeien | `opgroeien.be/kennis/cijfers-en-onderzoek/aanvragen-crisisjeugdhulp-en-niet-rechtstreeks-toegankelijke-jeugdhulp` ✅ | Power BI | jaarlijks |
| Wonen in Vlaanderen | jaarverslag; CIR-cijfers via SV's (bv. pfile 2291613); statistiekpagina nog te lokaliseren (404) | PDF | jaarlijks |
| AgII | jaarverslag PDF ✅ (2023: KPI MO-aanbod) | PDF | jaarlijks |
| Departement Zorg / VSB | `departementzorg.be/nl/aantal-dossiers-zorgbudgetten-vlaamse-sociale-bescherming` ✅ | **Excel + ZIP** | jaarlijks |
| Departement Zorg (woonzorg) | erkenningskalender, aanbodcijfers | PDF/HTML | — |
| VDAB | toelichting maatwerk (pfile 2118435) | PDF | op vraag |

## 5. Rekenhof

ccrek.be blokkeert geautomatiseerde toegang. Alle verslagen aan het Vlaams Parlement zijn via de **Parlement-API** bereikbaar (aggregaattype "Verslag van het Rekenhof"), bv. stuk 16 (2025-2026) nr. 1 over de begroting 2026 = pfile 2235038. Geen recent themarapport over VAPH-wachtlijsten gevonden (nv).

## 6. Niet gelukt / open

Codex Swagger-spec (JS-only), Datavindplaats-API-endpoints, Themis SPARQL-URL, Parlement bulk-dump/RSS, Datawrapper-CSV van DFB, primaire statistiekpagina Wonen in Vlaanderen. **Let op**: vanuit sommige netwerken (proxy's) zijn ws.vlpar.be en vaph.be geblokkeerd; draai de harvesters op een gewone werkpost.
