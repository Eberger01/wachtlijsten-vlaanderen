# Budgetbronnen en begrippen (voorbereiding fase 3)

*Stand 1 oktober 2026. Doel: budgetten per voorziening en per jaar machinaal koppelen aan wachtlijstcijfers.*

## Kernbevinding

De Vlaamse begroting per begrotingsartikel bestaat **enkel als PDF** (ontwerpdecreet + bijlagen, beleids- en begrotingstoelichtingen). Geen CSV/Excel/API bij Financiën en Begroting, niet op data.vlaanderen.be, niet bij Statistiek Vlaanderen. Koppelen vereist dus **PDF-tabelextractie** (pdfplumber/camelot) — de ISE-tabellen in de BBT's zijn daarvoor regelmatig genoeg.

Beste koppelingsniveau: het **inhoudelijk structuurelement (ISE)** binnen de BBT van het beleidsdomein (bv. WVG: "Personen met een handicap", "Jeugdhulp", "Woonzorg", "Zorgbudgetten", "Geïntegreerd gezinsbeleid"), aangevuld met de **eigen begroting van de rechtspersoon** (Bijlage 2 bij de uitgavenbegroting: VAPH, Opgroeien Regie, VSB, VMSW/Wonen in Vlaanderen, VIPA) en de **jaarverslagen/financiële verslagen** van de agentschappen als realisatie- en detaillaag.

## Bronnen

| Bron | URL / patroon | Formaat | Dekking |
|---|---|---|---|
| Dossier Begroting {jaar} (Vlaams Parlement) | `vlaamsparlement.be/nl/parlementair-werk/dossiers/dossiers/begroting-2026` | HTML → PDF | per jaar |
| Uitgavenbegroting = stuk 15 (zj) nr. 1 | 2026: ontwerp pfile 2225770; Bijlage 1 (departementen/IVA's/DAB's) 2225118; **Bijlage 2 (rechtspersonen)** 2225120; aangenomen 2255728. 2025: pfile 2078969 | PDF | VAK/VEK per artikel (k€) |
| BBT begrotingsopmaak = stuk **13-x** (zj) nr. 1 | 13-W (2022-23) WVG pfile 1887474; 13-V (2024-25) WVG+Armoede pfile 2081035; **letter per beleidsveld wisselt per zittingsjaar** → zoeken op titel | PDF | tabellen per ISE: BA vorig jaar / BO dit jaar, VAK en VEK |
| BBT begrotingsuitvoering = stuk **23-x** | bv. 23-M (2024-25) pfile 2162439 | PDF | uitvoering vorig jaar |
| Begrotingsaanpassing = stuk 19 | 2026: commissieverslag pfile 2347447 | PDF | BA |
| Rekenhof begrotingsonderzoek = stuk 16 | 2026: pfile 2235038 (§5.3 WVG p. 52-53; financiering VMSW 798,8 → 920,5 M€, VWF 1.356,7 M€) | PDF | jaarlijks |
| Themis (BBT als mededeling VR) | BBT WVG BO 2026 = VR 2025 2410 MED.0443-1 → `themis.vlaanderen.be/files/e9b10360-…/download` | PDF | alternatieve vindplaats |
| DFB "begroting in cijfers" | `vlaanderen.be/departement-financien-en-begroting/begroting/in-cijfers/uitgaven` | Datawrapper | totalen per beleidsdomein (BA 2026: 67,1 mld) |
| Algemene rekening (DFB) | `…/uitvoering/algemene-rekening` | PDF | 2014–2025 |
| Statistiek Vlaanderen uitgaven (COFOG) | `…/statistiek-vlaanderen/overheidsfinancien/uitgaven-vlaamse-overheid` | HTML | macro-check |
| Begrotingsinstructies (codestructuur) | VR 2024 2604 MED.0145-2BIS | PDF | definities |
| VAPH | "Het VAPH in cijfers" (hfst. Budget), financieel verslag (extranet), Meerjarenplanning 2025-2029 | PDF/HTML | 2019– |
| VSB | jaarverslag (publicaties.vlaanderen.be 78033 / 69463); Excel dossiers per zorgbudget | PDF + Excel | 2017– |
| Opgroeien | cijferrapporten (volumes, geen euro) → budget via BBT/Bijlage 2 | Power BI | — |

## Structuur begrotingsartikelcode

`GB0-1GGF2RX-IS` → `GB0` entiteit (Departement WVG; `GH0` = VAPH, `GM0` = VSB) · `1` uitgaven (0 = ontvangsten) · `GG` programma (eerste letter = beleidsdomein: G WVG, T Werk & SE, F Onderwijs) · `F2` kredietlijn · `RX` ISE + volgletter · suffix ESR-aggregaat: `WT` werking en toelagen, `LO` lonen, `PR` provisies, `IS` interne stromen (dotaties aan agentschappen), `LE` leningen, `PA` participaties.

Proef: **GB0-1GGF2RX-IS** = dotatie aan het VAPH, programma GG "Personen met een beperking", 2025 BO: VAK 2.991.680 k€ / VEK 2.726.246 k€ (stuk 15 (2024-2025) nr. 1, p. 4).

## Begrippen → datamodel (`budgetten.csv`)

| Begrip | Betekenis | Kolom |
|---|---|---|
| **VAK** vastleggingskrediet | mag in het jaar juridisch worden vastgelegd | `kredietsoort=VAK` |
| **VEK** vereffeningskrediet | mag in het jaar effectief betaald worden (kasvergelijking) | `kredietsoort=VEK` |
| **VRK** variabel krediet | begrotingsfonds, niet-limitatief | `kredietsoort=VRK` |
| Begrotingsartikel / basisallocatie (pre-2019) | fijnste kredietlijn | `artikel_code` |
| ESR-code/aggregaat | economische classificatie (ESR 2010) | suffix in `artikel_code` |
| Programma / ISE / beleidsdomein | beleidsmatige indeling; **ISE = koppelsleutel naar voorziening** | `programma`, `ise` |
| Fase BO / BA / UITV | opmaak (okt), aanpassing (apr), uitvoering (rekening, stuk 23) — 3 waarden per artikel per jaar | `fase` |
| AGENTSCHAP / BELEID | cijfer uit jaarverslag/financieel verslag resp. beleidsenveloppe (uitbreidingsbeleid, meerjarenplan) | `fase` |
| Niveau | `dept_artikel` (dotatie), `entiteit_begroting` (Bijlage 2), `uitbreidingsbeleid`, `realisatie`, `meerjarenplan` | `niveau` |
| Herverdelingsbesluit | kredietverschuiving door VR; verklaart BO→uitvoering | `opmerking` / later eigen fase |

**Interpretatieregel**: vergelijk nooit bedragen over niveaus heen. Uitbreidingsbeleid (± 40–120 M€/jaar) is een *groei-enveloppe*; de dotatie aan het VAPH (± 2,7–3,0 mld) is het *totale* budget; realisatie PVB (± 1,35–1,40 mld) is de *uitgave* voor één instrument.

## Fase 3 — status (1-10-2026)

**Gebouwd**: register `config/bbt_documenten.yaml` (29 BBT's: WVG 2020–2026 BO/BA/UITV + Wonen 2020–2026, met pfile-id's en
indieningsdata, geverifieerd via de open-data-fiches), downloader `scripts/harvest_bbt.py` (stdlib), parser
`wachtlijst.sources.bbt` (ISE-totalen + artikelregels, getest op de letterlijke tekststructuur van 13-V (2024-2025) en op
een gegenereerde PDF), tabel `kredieten.csv`, CLI `harvest bbt-download` / `harvest bbt-parse` / `promote-kredieten`,
dashboardsectie "Kredieten per ISE". **Uitgevoerd op 1-10-2026**: 29 PDF's gedownload en geparsed → 3.958 kredietrijen in `data/curated/kredieten.csv`,
steekproef 40/40 correct. Resultaten en beperkingen: `08-fase3-resultaten.md`. Vaststellingen uit het bronnenonderzoek: BBT's bij de begrotingsaanpassing
bestaan enkel voor 2020 (reeks 17-A) en zijn vanaf 2023 niet meer vereist; de letter per beleidsveld wisselt per
zittingsjaar; vanaf BO 2026 heet de WVG-BBT "Welzijn en Armoedebestrijding" (13-Z) en zijn beleidsvelden Welzijn en
Gezondheids-/Woonzorg samengevoegd tot "Zorg". ISE-lijst WVG (BO 2025): Beleidsondersteuning, Armoedebeleid, Welzijnswerk,
VIA, Preventie, Woonzorg en eerste lijn, Gespecialiseerde zorg, Algemeen gezondheidsbeleid, Jeugdhulp, Groeipakket,
Geïntegreerd gezinsbeleid, Personen met een beperking, Sociale bescherming, Zorginfrastructuur. ISE-lijst Wonen:
Vraagzijde woningmarkt, Aanbodzijde woningmarkt, Woningkwaliteit, Thema-overschrijdend instrumentarium.

## Aanpak fase 3 (oorspronkelijk voorstel)

1. Per begrotingsjaar 2019→2026: BBT WVG (13-x / 23-x) en Bijlage 2 van stuk 15 als PDF ophalen via de Parlement-API (`aggregaattype` begroting) → tabellen per ISE extraheren naar `artikel_code, label, jaar, fase, VAK, VEK`.
2. ISE-codes mappen op voorzieningen in `voorzieningen.csv` (nieuwe kolom `ise_codes`).
3. Uitvoering toevoegen (stuk 23-x + algemene rekening) als fase `UITV`.
4. Agentschapsdata (VAPH in cijfers, VSB-Excel, VMSW-financiering) als controlelaag.
5. Macro-check met COFOG "sociale bescherming" (Statistiek Vlaanderen).
6. Interpretatie: budget per wachtende, groei budget vs groei wachtlijst, VAK/VEK-kloof als indicator van onderbenutting.
