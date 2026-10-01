# Draaiboek — eenmalige en terugkerende stappen

*Stand 1 oktober 2026. Dashboard draait op Streamlit Community Cloud vanuit `Eberger01/wachtlijsten-vlaanderen`.*

## A. Eenmalig nog te doen (lokale werkpost)

| # | Stap | Commando / actie | Waarom |
|---|---|---|---|
| A1 | Lokale omgeving | `python -m venv .venv` · `.\.venv\Scripts\Activate.ps1` · `pip install -e ".[dashboard,dev]"` · `pytest` | Zonder dit werken `wachtlijst …`-commando's niet. Alle tests moeten groen zijn. |
| A2 | Lokale rookproef | `wachtlijst validate` · `wachtlijst publish` · `streamlit run dashboard\app.py` | Bevestigt dat de lokale kopie identiek is aan wat online staat. |
| A3 | Steekproef VAPH-PVB en sociale huur | Open 5 rijen in `data\curated\bevindingen.csv`, klik de `bron_url`, vergelijk de `passage` | Jouw tweede lezing: wijzig `controlestatus` naar `gecontroleerd` en `gecontroleerd_door` naar je initialen (in `scripts\seed_proef.py`, daarna `python scripts\seed_proef.py` · `python scripts\seed_opgroeien.py` · `python scripts\seed_aanvullingen.py`). |
| A4 | Steekproef kredieten (fase 3) | Open `data\curated\kredieten.csv`, kies 5 rijen van ISE "Personen met een beperking" en "Aanbodzijde woningmarkt", open de PDF in `data\raw\bbt\` op de vermelde `pagina` | Bevestigt de parser voor de reeksen die je naar buiten brengt. Status blijft `bron_gelezen` tot jij `gecontroleerd` zet: regel toevoegen in `config\kredieten_controles.csv`, dan `wachtlijst controleer-kredieten`. |
| A5 | Reeks sociale huur 2018–2022 | Download Excel "Tabel 1 Totaal kandidaat-huurders per jaar" (link in `06-harvesters-lokaal.md` §6) en vergelijk met de VRT-cijfers | Die vijf rijen zijn nu `ongecontroleerd` (secundaire bron). |
| A6 | Eerste live-run Parlement-API en VAPH-harvester | `wachtlijst harvest vlpar wachtlijst --pages 2` · `wachtlijst harvest vaph 2025` | Zonder `--pagina` zoekt `vaph` zelf de pagina Prioriteitengroepen (2024: 25, 2025: 27). |
| A7 | GitHub-repo opschonen | README nalezen; eventueel LICENSE toevoegen; `data\raw` en `data\staging` blijven buiten git (.gitignore) | Repo is publiek. |

## B. Terugkerend — bij elke nieuwe publicatie van een bron

Kalender van de bronnen:

| Wanneer | Bron | Wat |
|---|---|---|
| ± juni | VAPH "Het VAPH in cijfers" (PDF) en HTML-jaarverslag | PG-stand 31/12 vorig jaar, terbeschikkingstellingen, uitbreidingsbeleid |
| ± oktober/november | VAPH halfjaarverslag (`…/jaarverslag/<jaar>-eerste-jaarhelft/`) | PG-stand 30/06 |
| ± juni/juli | Wonen in Vlaanderen jaarverslag (HTML) | CIR-stand 31/12, toewijzingen, wachttijd, patrimonium, huurpremie |
| januari–juli | Opgroeien cijferrapport NRTJ (HTML) | wachtenden 31/12, aanmeldingen, hulpvragen (`harvest opgroeien nrtj`) |
| ± juni + per kwartaal | Opgroeien Excel kinderopvang | vergunde plaatsen (`harvest opgroeien kinderopvang`) |
| ± juli | SV 'Lokaal loket kinderopvang – registratie' (Schryvers/Warnez) | opvangvragen en onbeantwoorde vragen vorig jaar |
| februari–mei | SV-reeks CGG (Wouters/Mertens/Vaneeckhout) met Excel-bijlage | wachttijden, zorgperiodes, enveloppes vorig-vorig jaar |
| ± mei | AgII jaarverslag | contracten, MO-cursussen (wacht-KPI niet meer gepubliceerd; via commissie/SV) |
| ± mei | BBT begrotingsuitvoering (stuk 23-x) | kolom "Uitvoering <vorig jaar>" |
| ± eind oktober | BBT begrotingsopmaak (stuk 13-x) | kolom "BO <volgend jaar>" en "BA <dit jaar>" |
| doorlopend | Schriftelijke vragen Vlaams Parlement | nieuwe cijfers voor decentrale lijsten (CGG, buitengewoon onderwijs, kinderopvang, …) |

Vaste cyclus per update (± 30 min, alles in de projectmap (je clone van de repo) met geactiveerde venv):

```powershell
# 1. verzamelen
wachtlijst harvest vaph 2026                             # of: harvest vlpar <term>, python scripts\harvest_bbt.py
# 2. nalezen in data\staging\…  (passage + cijfer tegen de bron)
#    staat dezelfde peildatum al gecontroleerd in curated (bv. uit "VAPH in cijfers")? dan niet promoveren:
#    promote vervangt de rij op bevinding_id
# 3. promoveren
wachtlijst promote data\staging\vaph_2026 --door EB      # kredieten: wachtlijst promote-kredieten --door EB
# 4. controleren en publiceren
wachtlijst validate
wachtlijst publish
# 5. online zetten (Streamlit herbouwt automatisch binnen enkele minuten)
git add data\curated data\published
git commit -m "Update <bron> <peildatum>"
git push
```

Voor BBT's: eerst de nieuwe stukken toevoegen aan `config\bbt_documenten.yaml` (stuknummer, doc_id, pfile_id —
op te zoeken via de dossierpagina `vlaamsparlement.be/…/dossiers/begroting-<jaar>` of `ws.vlpar.be/e/opendata/pi/<doc_id>`),
dan `python scripts\harvest_bbt.py WVG <jaar>` → `wachtlijst harvest bbt-parse --jaar <jaar>` → steekproef → `promote-kredieten`
(past `config\kredieten_controles.csv` automatisch opnieuw toe; nieuwe controles: regel toevoegen + `wachtlijst controleer-kredieten`).

Voor cijfers die geen harvester hebben (sociale huur, AgII, Opgroeien): rij toevoegen in `scripts\seed_proef.py`
(zelfde velden: bron, url, documenttitel, pagina, passage, peildatum, definitie, controlestatus), `python scripts\seed_proef.py`,
dan stap 4–5. Nieuwe bron eerst in `BRONNEN`.

## C. Terugkerend — onderzoekswerk (per nieuwe voorziening)

1. Rij in `voorzieningen.csv` (bevoegdheid, wachtlijst_type, ise_koppeling) via `seed_proef.py`.
2. Bronnen inventariseren (`bronnen.csv`) — begin met `wachtlijst harvest vlpar "<naam voorziening> wachtlijst"`.
3. Bevindingen met letterlijke passage; tweede lezing door een collega.
4. Budget: ISE-koppeling zetten → kredieten verschijnen automatisch in het dashboard; aanvullen met jaarverslagcijfers in `budgetten.csv`.
5. `validate` → `publish` → commit → push.

Kandidaten in volgorde van bronkwaliteit: jeugdhulp NRTJ (Opgroeien, ISE Jeugdhulp al in kredieten), inburgering MO
(AgII-jaarverslag), CGG (bijlage SV 379), collectief maatwerk (VDAB).

## D. Beheer

- **Streamlit** slaapt na ± 12 u zonder bezoek; eerste bezoeker wekt de app (± 30 s). Logs: share.streamlit.io → *Manage app*.
- **Afhankelijkheden**: dashboard leest alleen `dashboard\requirements.txt`; pipeline via `pyproject.toml`. Versies verhogen = één commit.
- **Back-up**: de GitHub-repo bevat alles behalve `data\raw` (PDF's, reproduceerbaar via `harvest_bbt.py`) — bewaar `data\raw\bbt` lokaal of in OneDrive.
- **Teamwerk**: collega's clonen de repo, draaien A1, en werken via pull requests; `controlestatus` en `gecontroleerd_door` zijn de audittrail.
