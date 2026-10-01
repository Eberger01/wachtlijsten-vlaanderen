# Datamodel en werkwijze

## Vier tabellen (CSV in `data/curated/`)

```
bronnen ──┐
          ├──< bevindingen   (één rij per cijfer, per peildatum, per metriek)
voorzieningen ─┤
          └──< budgetten     (één rij per bedrag, per jaar, per fase/niveau/kredietsoort)
```

| Tabel | Sleutel | Verplichte herkomst per rij |
|---|---|---|
| `bronnen` | `bron_id` | url, type (api/download/html/pdf/dashboard), licentie, hoe machinaal te bevragen |
| `voorzieningen` | `voorziening_id` | domein, entiteit, **bevoegdheid** (Gemeenschap/Gewest), **wachtlijst_type**, scan_status |
| `bevindingen` | `bevinding_id` = `<voorziening>:<metriek>:<peildatum>` | bron_id, bron_url, documenttitel, **pagina, passage (letterlijk), peildatum, definitie, publicatiedatum, controlestatus** |
| `budgetten` | `budget_id` = `<voorziening>:<jaar>:<fase>:<niveau>:<krediet>:<artikel|label>` | idem + begrotingsjaar, fase, niveau, kredietsoort, artikel_code, ISE |
| `kredieten` | `krediet_id` = `<pfile>:<ise>:<artikel|ISE>:<kolom>:<krediet>` | BBT-bedragen (k€) per ISE-totaal en per artikel: beleidsdomein, begrotingsjaar, fase, stuk, kolomkop, VAK/VEK, pagina. Gekoppeld aan voorzieningen via `voorzieningen.ise_koppeling`. |

Controlestatus (enum): `ongecontroleerd` → `bron_gelezen` → `gecontroleerd`; `betwist` bij tegenspraak. `validate` weigert rijen zonder bron of met afwijkende sleutel; `publish` weigert te publiceren bij fouten.

Metrieken (proef VAPH-PVB): `wachtenden_personen`, `wachtenden_vragen_totaal`, `wachtenden_vragen_pg{1,2,3}`, `wachttijd_eerstvolgende_pg{1,2,3}_dagen` (peildatum − prioriteringsdatum), `terbeschikkingstellingen_budgetten|personen`, `budgethouders_pvb`. Nieuwe voorzieningen voegen eigen metrieken toe; gebruik `snake_case` en zet de eenheid in `eenheid`.

## Datastroom (verzamelen los van tonen)

```
publieke bron ──harvest──> data/raw/        (ruwe JSON/HTML/PDF, niet in git)
                 parse ──> data/staging/    (kandidaat-bevindingen, controlestatus=ongecontroleerd)
        mens: promote ──> data/curated/     (CSV in git; status bron_gelezen/gecontroleerd)
             validate
              publish ──> data/published/   (CSV + meta.json met actualiseringsdatum)
                                   └──> dashboard/app.py (Streamlit; leest alleen published)
```

Het dashboard doet geen webverkeer. Publiceren = `data/published` committen (of mee uploaden naar Streamlit Community Cloud). Later kan een uitgebreidere webinterface dezelfde `published`-map lezen.

## Commando's

```
pip install -e ".[dashboard,dev]"
python scripts/seed_proef.py            # (her)genereert data/curated met bronnenkaart, inventaris en proef
wachtlijst validate
wachtlijst publish
streamlit run dashboard/app.py

wachtlijst harvest vlpar wachtlijst --pages 3        # Parlement-API -> data/raw/vlpar/wachtlijst.{jsonl,csv}
wachtlijst harvest vaph 2025                         # VAPH-jaarverslag (pagina wordt gezocht) -> data/staging/vaph_2025/bevindingen.csv
wachtlijst promote data/staging/vaph_2025 --door EB  # na nalezen -> data/curated (status bron_gelezen)
wachtlijst harvest codex wachtlijst                  # regelgeving
python scripts/harvest_bbt.py                        # BBT-PDF's -> data/raw/bbt (fase 3)
wachtlijst harvest bbt-parse                         # -> data/staging/bbt/kredieten.csv
wachtlijst promote-kredieten --door EB               # -> data/curated/kredieten.csv
pytest
```

## Toevoegen van een voorziening (checklist)

1. Rij in `voorzieningen.csv` (bevoegdheid, wachtlijst_type, publicatie_bron_id).
2. Bron(nen) in `bronnen.csv` met `machinaal`-beschrijving.
3. Connector in `src/wachtlijst/sources/` die kandidaat-bevindingen oplevert (hergebruik `Bevinding`).
4. Bevindingen met letterlijke passage; tweede lezing door een collega → `gecontroleerd`.
5. Budgetrijen op minstens twee niveaus (dept_artikel/ISE + realisatie of uitbreidingsbeleid).
6. `wachtlijst validate && wachtlijst publish`; het dashboard pikt de voorziening automatisch op.
