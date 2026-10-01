# Harvesters lokaal draaien (Windows / PowerShell)

De verzamelstap draait op een werkpost met gewone internettoegang. Vanuit sommige bedrijfs- of agentproxy's zijn
`docs.vlaamsparlement.be`, `ws.vlpar.be`, `extranet.vaph.be`, `publicaties.vlaanderen.be`, `assets.vlaanderen.be`
en `themis.vlaanderen.be` geblokkeerd — dan mislukt elke download met een 403/`CONNECT`-fout.

## 0. Eenmalige installatie

```powershell
cd D:\MVPDev\Wachtlijst
python --version                      # 3.10 of hoger
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # bij 'running scripts is disabled': Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
python -m pip install --upgrade pip
pip install -e ".[dashboard,dev]"
wachtlijst --help                     # toont: validate, publish, promote, promote-kredieten, harvest …
pytest                                # 9 tests groen
```

## 1. Basisdata (her)genereren en controleren

```powershell
python scripts\seed_proef.py          # schrijft data\curated\*.csv (bronnen, voorzieningen, bevindingen, budgetten)
wachtlijst validate                   # typen, sleutels, verwijzingen
wachtlijst publish                    # data\published + meta.json (dit leest het dashboard)
streamlit run dashboard\app.py        # http://localhost:8501
```

## 2. Vlaams Parlement — documenten zoeken op trefwoord

```powershell
wachtlijst harvest vlpar wachtlijst --pages 3          # 150 recentste hits
wachtlijst harvest vlpar prioriteitengroep --pages 2
wachtlijst harvest vlpar kandidaat-huurders --pages 2
wachtlijst harvest vlpar "zorgbudget wachttijd" --sort relevance
```

Resultaat: `data\raw\vlpar\<term>.jsonl` (volledige metatags) en `data\raw\vlpar\<term>.csv` (index: zittingsjaar,
nummer, aggregaattype, thema, titel, vraagsteller, minister, publicatiedatum, displayurl, **document** = PDF-URL,
**opendata** = XML-URL). Open de CSV in Excel, filter op `aggregaattype` (Schriftelijke vraag / Verslag van het
Rekenhof / …) en `thema` (Welzijn, Wonen, …). Een PDF lezen en doorzoeken in Python:

```python
from wachtlijst.sources import vlpar
p = vlpar.fetch_pdf("https://docs.vlaamsparlement.be/files/pfile?id=2291613")
for t in vlpar.grep_pdf(p, r"wachttijd|toewijzing"): print(t["pagina"], t["passage"][:200])
```

## 3. VAPH — prioriteitengroepen uit het HTML-jaarverslag

```powershell
wachtlijst harvest vaph 2024 --pagina 25                      # 31-12-2024
wachtlijst harvest vaph 2024-eerste-jaarhelft --pagina 25     # 30-06-2024
wachtlijst harvest vaph 2025 --pagina 25                      # controleer het paginanummer in de sitemap van het jaarverslag
```

Resultaat: `data\staging\vaph_<editie>\bevindingen.csv` met `controlestatus = ongecontroleerd`. Lees de passage na,
voeg zo nodig de bron toe aan `data\curated\bronnen.csv` (bron_id `vaph-jaarverslag-<editie>`), en neem op:

```powershell
wachtlijst promote data\staging\vaph_2025 --door EB           # status bron_gelezen; --status gecontroleerd na 2e lezing
wachtlijst validate ; wachtlijst publish
```

Als "patroon niet gevonden" verschijnt: open de pagina in de browser, zoek de zin "Op 31 december … waren … personen
met in totaal … vragen geregistreerd" en geef het juiste `--pagina`.

## 4. BBT's (fase 3) — kredieten per ISE en per begrotingsartikel

*Al uitgevoerd op 1-10-2026 (resultaat in `data/curated/kredieten.csv`, PDF's in `data/raw/bbt`). Herhalen wanneer nieuwe BBT's verschijnen (mei: uitvoering; oktober: opmaak) na toevoeging aan `config/bbt_documenten.yaml`.*

```powershell
python scripts\harvest_bbt.py                 # 29 PDF's (WVG + Wonen, 2020-2026) -> data\raw\bbt\  (alleen stdlib)
python scripts\harvest_bbt.py WVG 2025        # of één domein/jaar
wachtlijst harvest bbt-parse                  # -> data\staging\bbt\kredieten.csv (enkel wachtlijst-relevante ISE's)
wachtlijst harvest bbt-parse --no-alleen-relevant   # alle ISE's
```

Steekproef (verplicht vóór promotie): open 3–5 rijen uit `kredieten.csv`, ga naar de PDF op de vermelde `pagina`
en vergelijk `bedrag_keur` met de tabel. Daarna:

```powershell
wachtlijst promote-kredieten --door EB
wachtlijst validate ; wachtlijst publish
```

Het dashboard toont dan in het tabblad **Budget** per voorziening de ISE-totalen (BO/BA/Uitvoering, VAK/VEK) en de
artikelregels. De koppeling voorziening ↔ ISE staat in `voorzieningen.csv`, kolom `ise_koppeling`.

Parser-beperkingen: de BBT-lay-out is sinds 2020 stabiel, maar oudere stukken (2020-2021) of de uitvoerings-BBT's (23-x)
kunnen andere kolomkoppen hebben ("Uitvoering 2024"). De parser bewaart de kolomkop letterlijk in `kolom`; onbekende
regels worden overgeslagen. Controleer per document het aantal rijen in de uitvoer van `bbt-parse`; 0 rijen = lay-out
afwijkend → meld het document in `docs/04-budgetbronnen.md`.

## 5. Vlaamse Codex — regelgeving

```powershell
wachtlijst harvest codex wachtlijst
wachtlijst harvest codex "centraal inschrijvingsregister"
```

## 6. Sociale huur — Excel-tabellen Wonen in Vlaanderen (handmatig)

De reeks 2018–2022 (unieke kandidaat-huurders) staat in *Tabel 1* op
https://www.vlaanderen.be/sociaal-woonbeleid/cijfers/oudere-cijfers-over-sociaal-wonen/kandidaat-huurders-cijfers-tot-2023
(Excel op assets.vlaanderen.be). Download, lees de jaartotalen af en zet in `scripts/seed_proef.py` de status van de
rijen `wonen-sociale-huur:wachtenden_kandidaten:2018..2022` op `bron_gelezen` met de Excel als bron.

## Werkafspraken

- Alles wat harvesters schrijven is `ongecontroleerd`; alleen een mens promoveert naar `curated`.
- `data\raw` en `data\staging` staan in `.gitignore`; `data\curated` en `data\published` wél committen.
- Na elke `publish`: commit + push → Streamlit Community Cloud herlaadt automatisch (zie `07-streamlit-hosting.md`).
