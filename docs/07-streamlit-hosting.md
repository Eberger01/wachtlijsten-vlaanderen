# Dashboard hosten op Streamlit Community Cloud

Gratis, één weblink, automatische herdeploy bij elke push. Vereist een **publieke GitHub-repository** en een
Streamlit-account gekoppeld aan GitHub.

## 1. Repository

```powershell
cd D:\MVPDev\Wachtlijst
git init
git add .
git commit -m "Wachtlijsten Vlaanderen: pipeline, dashboard, proef VAPH-PVB + sociale huur"
```

Maak op https://github.com/new een publieke repo (bv. `wachtlijsten-vlaanderen`), daarna:

```powershell
git remote add origin https://github.com/<account>/wachtlijsten-vlaanderen.git
git branch -M main
git push -u origin main
```

`data/published/` wordt mee gepusht — dat is de enige data die het dashboard leest. `data/raw` en `data/staging`
blijven lokaal (.gitignore).

## 2. Deploy

1. Ga naar https://share.streamlit.io → *Create app* → *Deploy a public app from GitHub*.
2. Repository: `<account>/wachtlijsten-vlaanderen`, branch `main`, **main file path: `dashboard/app.py`**.
3. *Advanced settings* → Python 3.11; **requirements file: `dashboard/requirements.txt`** (geen scrapers, licht).
4. App-URL kiezen (bv. `wachtlijsten-vlaanderen.streamlit.app`) → *Deploy*. Eerste build ± 2 min.

De app importeert `src/wachtlijst/publish.py` via `sys.path` in `dashboard/app.py`, dus geen `pip install -e .` nodig.

## 3. Bijwerken

Lokaal: `wachtlijst publish` → `git add data/published` → `git commit` → `git push`. Streamlit herbouwt automatisch;
de kop van het dashboard toont de nieuwe actualiseringsdatum uit `meta.json`.

## Beperkingen & alternatief

- Community Cloud slaapt na ± 12 uur zonder bezoek; de eerste bezoeker wekt de app (± 30 s).
- Beperkte CPU/RAM — daarom geen harvesting in de app.
- Later, voor een breed publiek: statische export (HTML + JSON uit `data/published`) op GitHub Pages; de Python-pipeline
  blijft identiek.
