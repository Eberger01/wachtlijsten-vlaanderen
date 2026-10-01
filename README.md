# Wachtlijst — wachtlijsten voor sociale voorzieningen in Vlaanderen

Onderzoeksproject: *welke overheidsdiensten van de Vlaamse overheid (Gemeenschap én Gewest) beschikken over een wachtlijst voor het toekennen van voorzieningen van de sociale politiek, en welke budgetten horen daarbij?*

Python-pipeline voor verzamelen en controleren, los van een Streamlit-dashboard dat enkel gepubliceerde, gecontroleerde gegevens toont.

**Dashboard:** https://wachtlijsten-vlaanderen.streamlit.app

## Snel starten (volledige handleiding: `docs/06-harvesters-lokaal.md`, vaste werkwijze: `docs/09-draaiboek.md`)

```powershell
git clone https://github.com/Eberger01/wachtlijsten-vlaanderen.git
cd wachtlijsten-vlaanderen
python -m venv .venv ; .\.venv\Scripts\Activate.ps1
pip install -e ".[dashboard,dev]"
pytest                                # alle tests moeten slagen
wachtlijst validate
wachtlijst publish                    # bouwt data\published + meta.json
streamlit run dashboard\app.py
```

`data\curated` zit in de repo; `python scripts\seed_proef.py` (daarna `python scripts\seed_opgroeien.py`) bouwt bevindingen, bronnen en budgetten opnieuw op uit de scripts.

## Wat zit erin

| Map | Inhoud |
|---|---|
| `docs/01-afbakening.md` | scope-voorstel incl. **Gewest vs Gemeenschap** (conclusie: beide meenemen, bevoegdheid als attribuut) |
| `docs/02-bronnenkaart.md` | publicatiekanalen: Vlaams Parlement Search API (geverifieerd), open-data XML, Codex-API, Themis, agentschappen, Rekenhof |
| `docs/03-inventaris.md` | brede scan van 20 voorzieningen, getypeerd als centraal gepubliceerd / niet gepubliceerd / decentraal / geen lijst |
| `docs/04-budgetbronnen.md` | waar budgetten per voorziening en jaar te vinden zijn (enkel PDF), codestructuur, VAK/VEK/ISE-begrippen, aanpak fase 3 |
| `docs/05-datamodel.md` | tabellen, sleutels, controlestatus, datastroom, checklist nieuwe voorziening |
| `docs/06-harvesters-lokaal.md` | **stap-voor-stap PowerShell-handleiding** voor alle harvesters (Parlement-API, VAPH, BBT's, Codex) |
| `docs/07-streamlit-hosting.md` | deploy op Streamlit Community Cloud (GitHub-repo, main file, requirements) |
| `docs/08-fase3-resultaten.md` | **resultaten fase 3**: budgetreeksen 2020–2026 per ISE (VAPH, sociale huur, jeugdhulp), interpretatie, parserbeperkingen |
| `docs/09-draaiboek.md` | eenmalige en terugkerende stappen: publicatiekalender van de bronnen, vaste updatecyclus, beheer |
| `config/bbt_documenten.yaml` | register van 29 BBT's (WVG + Wonen, 2020–2026) met pfile-id's |
| `config/kredieten_controles.csv` | tweede lezingen van individuele kredietrijen (audittrail; overleeft een nieuwe BBT-parse) |
| `data/curated/*.csv` | bronnen (69), voorzieningen (20), bevindingen (153: VAPH-PVB, sociale huur, jeugdhulp NRTJ, kinderopvang), budgetten (40), kredieten (3.958 BBT-rijen 2020–2026) |
| `src/wachtlijst/` | `models` (pydantic), `store` (CSV + validatie), `sources/{vlpar,vaph,codex,bbt,opgroeien}`, `publish`, `cli` |
| `dashboard/app.py` | Streamlit: inventaris, voorziening (tijdreeks + herkomst), budget, bronnen, methodiek |
| `scripts/seed_opgroeien.py` | proefdossiers jeugdhulp NRTJ en kinderopvang (upsert, ná seed_proef) |
| `scripts/seed_proef.py` | reproduceerbare seed van de gecureerde data |
| `scripts/harvest_bbt.py` | downloadt de BBT-PDF's (alleen stdlib) |

## Principes

- **Elk cijfer draagt zijn herkomst**: bron, documenttitel, pagina/passage (letterlijk citaat), peildatum, publicatiedatum, definitie, controlestatus (`ongecontroleerd` → `bron_gelezen` → `gecontroleerd`, of `betwist`).
- **Verzamelen ≠ tonen**: harvesters schrijven naar `data/raw` en `data/staging`; een mens promoveert naar `data/curated`; `publish` maakt `data/published`; het dashboard leest alleen dat en toont de actualiseringsdatum.
- **Budget vanaf dag één gekoppeld**: `budgetten.csv` per voorziening, jaar, fase (BO/BA/UITV/AGENTSCHAP/BELEID), niveau en kredietsoort (VAK/VEK).
- **Downloads/API's eerst, scraping waar nodig**: Parlement-API en Codex-API zijn JSON; VAPH-jaarverslag is HTML met stabiele zinsstructuur; begroting is PDF.

## Gratis hosten

Streamlit Community Cloud: repository publiek maken, *main file* `dashboard/app.py`, *requirements* `dashboard/requirements.txt`; `data/published` mee committen. Alternatief later: statische export naar GitHub Pages vanuit dezelfde `published`-map.

## Bekende beperkingen

- `www.vaph.be` en `ccrek.be` blokkeren bots; gebruik `extranet.vaph.be`, `publicaties.vlaanderen.be` en de Parlement-API. De BBT-, Parlement-API- en VAPH-harvesters zijn alle drie live gedraaid (1-10-2026) — zie `docs/06-harvesters-lokaal.md`.
- Geen open data van de begroting per artikel: fase 3 is uitgevoerd via PDF-extractie van de 29 BBT's (`data/raw/bbt`, niet in git); ISE-totaalregels van vóór 2022 zijn minder betrouwbaar dan de artikelregels (zie `docs/08-fase3-resultaten.md` §4).

## Licentie en bronvermelding

De code valt onder de [MIT-licentie](LICENSE). De cijfers in `data/` zijn overgenomen uit publicaties van de Vlaamse overheid
(o.a. VAPH, Wonen in Vlaanderen) en het Vlaams Parlement, die hergebruik toestaan onder de *Modellicentie Gratis Hergebruik*
met bronvermelding. Elke rij vermeldt haar bron (`bron_url`, documenttitel, pagina); vermeld bij hergebruik die oorspronkelijke bron.
Secundaire bronnen (pers, middenveld) zijn als zodanig gemarkeerd.
