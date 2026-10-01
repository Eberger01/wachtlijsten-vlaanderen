# Fase 3 — resultaten: budgetten per ISE uit de BBT's (uitgevoerd 1-10-2026)

Bron: 29 Beleids- en Begrotingstoelichtingen (WVG 2020–2026 en Wonen 2020–2026; opmaak, aanpassing 2020, uitvoering)
gedownload van docs.vlaamsparlement.be en geparsed met `wachtlijst.sources.bbt` → **3.958 kredietrijen** in
`data/curated/kredieten.csv` (eenheid duizend euro; elke rij met stuknummer, pfile-id, pagina, kolomkop, VAK/VEK).
Steekproef: 40 willekeurige en gerichte bedragen letterlijk teruggevonden op de vermelde PDF-pagina (40/40).
Controlestatus van alle rijen: `bron_gelezen` (één machinale lezing + steekproef); tweede menselijke lezing van de
sleutelreeksen hieronder wordt aanbevolen vóór publicatie naar buiten.

## 1. Personen met een handicap (ISE "Personen met een beperking", programma GG) — mln €

Dotatie aan het VAPH (artikel GB0-1GGF2RX-IS = volledige ISE):

| Jaar | BO VAK | BA VAK | Uitvoering VAK | BO VEK | BA VEK | Uitvoering VEK |
|---|---|---|---|---|---|---|
| 2020 | — | 1.752,1 | 1.810,3 | — | 1.752,1 | 1.810,3 |
| 2021 | — | 1.882,8 | 1.965,9 | — | 1.882,8 | 1.965,5 |
| 2022 | 1.994,1 | 2.013,6 | 2.213,8 | 1.994,1 | 2.013,6 | 2.213,8 |
| 2023 | 2.547,7 | 2.625,4 | 2.617,5 | 2.387,0 | 2.422,2 | 2.414,0 |
| 2024 | 2.751,0 | 2.799,1 | 2.827,5 | 2.541,9 | 2.091,9 | 2.117,7 |
| 2025 | 2.991,7 | 2.988,6 | 3.034,4 | 2.726,2 | 2.720,4 | 2.762,0 |
| 2026 | 3.121,8 | — | — | 2.819,6 | — | — |

"BA VAK" = kolom "BA jaar" uit de BBT van het volgende jaar (opmaak) of uit de uitvoerings-BBT; beide bronnen geven
identieke waarden (bv. BA 2024 = 2.799.113 in 13-V én in 23-T), wat de parser valideert. BO 2020/2021 ontbreekt: in
die stukken staat de kolom "BO" voor het artikel op een afwijkend opgemaakte regel (handmatig na te lezen).

Binnen de VAPH-begroting (Bijlage 2, entiteit onder gezag) is het artikel **GH0-AGGF2RD-WT "Financiering van niet
rechtstreeks toegankelijke zorg en ondersteuning"** (PVB, PAB, MFC) de post die rechtstreeks met de wachtlijst
samenhangt: BO VAK 1.553,5 (2019) → 1.629,7 (2021) → 2.322,7 (2023) → 2.514,1 (2024) → 2.745,5 (2025) → **2.898,3
(2026)**; uitvoering VAK 2.577,2 (2024), 2.811,5 (2025).

**Interpretatie (voorlopig)**: het VAPH-budget groeide 2020→2025 met ± 68 % in vastleggingen (1.810 → 3.034 mln
uitvoering), terwijl het aantal vragen in de prioriteitengroepen in dezelfde periode steeg van ± 16,6 k (eind 2020,
jaarreekstabel) naar 17,9 k (eind 2025; +8 %) en het aantal budgethouders tot 31,3 k. De kloof VAK–VEK vanaf 2023
(± 160–700 mln) weerspiegelt de meerjarige vastleggingen (zorginvesteringsplan) en de "afroming saldo" bij BA 2024
(zie toelichting p. 116 van 13-V): VEK, niet VAK, is de maat voor wat in een jaar effectief wordt uitbetaald.

## 2. Sociale huur (Wonen, ISE "Aanbodzijde woningmarkt" en "Vraagzijde woningmarkt", programma QD) — mln €

Vraagzijde (huursubsidie en huurpremie, artikel QF0-1QD?2PA-WT "Een betaalbare woningmarkt met woonzekerheid"):
BA 100,2 (2020) → 118,8 (2021) → 112,4 (2022) → 112,9 (2023) → 132,4 (2024) → 140,8 (2025) → BO **152,1 (2026)**;
uitvoering 102,3 / 107,1 / — / 131,8 / 134,0 (2021–2025). Groei ± 50 % in vijf jaar, gedreven door de huurpremie
voor wie ≥ 4 jaar wacht (23.353 gerechtigden, 63,5 mln in 2025).

Aanbodzijde (dotaties en machtigingen aan VMSW/Wonen in Vlaanderen, FS3-financiering, SSI-subsidies): de
ISE-totalen springen tussen ± 30 mln (2020) en 1,3–1,5 mld VAK (2021–2026) omdat de **machtigingen** voor
projectfinanciering (artikel QF0-1QD?5QK-IS, geen ESR-uitgave) vanaf 2021 in het ISE zitten; VEK blijft ± 75–120
mln. Vergelijk daarom op artikelniveau (tabblad Budget → tabel) en lees `docs/04-budgetbronnen.md` §begrippen.
Primaire investeringsmaat blijft de FS3-toekenning uit het jaarverslag (997 mln 2024; 742 mln 2025).

## 3. Jeugdhulp en kinderopvang (Opgroeien) — gekoppeld op 1-10-2026

Jeugdhulp (ISE Jeugdhulp, GE-M, artikel GB0-1GEF2MX-IS): BA VAK 607,8 (2022) → 830,2 (2023) → 878,0 (2024) → 940,5 (2025); BO 2026
945,5; uitvoering 693,9 / 948,3 / 949,4 (2022/2024/2025). Tegenover wachtenden NRTJ 7.448 → 9.748 (+31 % 2022→2025) staat +56 %
budget (BA 2022 → BO 2026). Vóór 2022 zat jeugdhulp in een ander artikel (ISE-totaal 2019–2021 ≈ 0 in de parser: niet gebruiken).

Kinderopvang zit in ISE Geïntegreerd gezinsbeleid (GE-U, GB0-1GEF2UX-IS) samen met preventieve gezinsondersteuning, adoptie en het
Groeipakket-apparaat; de BBT splitst kinderopvang niet af. Gebruik voor kinderopvang de beleidsenveloppes (masterplan 200 mln/jaar
tegen 2029; 115 mln 2023) en de uitvoeringscijfers van GDF-AGEF2UA-WT uit `budgetten.csv`.

## 3b. Andere wachtlijst-ISE's (beschikbaar in `kredieten.csv`, nog niet geïnterpreteerd)

Jeugdhulp (GE-M): BA VAK 607,8 (2022) → 830,2 (2023) → 878,0 (2024) → 940,5 (2025); BO 2026 945,5. Geïntegreerd
gezinsbeleid/kinderopvang (GE-U), Woonzorg en eerste lijn (GD-K; vanaf 2026 GC-V), Gespecialiseerde zorg/CGG (GD-L),
Sociale bescherming/zorgbudgetten (GH-T): rijen aanwezig voor 2020–2026 (artikelniveau betrouwbaar; ISE-totaalregels
vóór 2022 soms verkeerd gelezen — zie §4).

## 4. Bekende beperkingen van de parser

- **ISE-totaalregel** ("Totaal" van de synthesetabel): betrouwbaar vanaf BO 2022 (WVG) en voor de meeste
  Wonen-stukken; in 2020–2021 en in Wonen BO 2024 (ontbrekende ISE-kop, afgebroken getallen) kan de eerste "Totaal"
  na een ISE-kop een andere tabel zijn. Het dashboard gebruikt daarom de **som van de uitgavenartikelen op
  departementsniveau** als ISE-reeks; de ISE-totaalregels staan wel in de tabel.
- **Artikelregels** krijgen hun ISE via de artikelcode (programma + ISE-letter, `config/bbt_documenten.yaml` →
  `ise_codes`), niet via de kop in de PDF; dat is robuust over alle 29 stukken.
- Oudere opmaak (13-Y 2020, 13-X 2021): de regel "BO jaar" van sommige artikelen wordt niet herkend; "Index" en
  "Andere bijstellingen" wel. Handmatig aanvullen waar nodig.
- Begrotingsaanpassing: aparte BBT's bestaan enkel voor 2020 (17-A); voor 2021–2022 niet gevonden; vanaf 2023 niet
  meer vereist. BA-waarden komen dus uit de "BA jaar"-kolom van de opmaak- en uitvoerings-BBT's.
- 13-AB Armoedebestrijding (2024) bevat geen wachtlijst-ISE's (0 relevante rijen, verwacht).

## 5. Reproduceren

```powershell
python scripts\harvest_bbt.py            # 29 PDF's -> data\raw\bbt (± 60 MB)
wachtlijst harvest bbt-parse             # -> data\staging\bbt\kredieten.csv
wachtlijst promote-kredieten --door EB   # -> data\curated\kredieten.csv
wachtlijst validate ; wachtlijst publish
```
