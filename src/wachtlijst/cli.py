"""Commandoregel: ``wachtlijst --help``.

  wachtlijst validate                      controleert data/curated
  wachtlijst publish                       bouwt data/published (+ meta.json)
  wachtlijst harvest vlpar wachtlijst      zoekt in de Vlaams Parlement Search API -> data/raw/vlpar/
  wachtlijst harvest vaph 2024 --pagina 25 parsed de VAPH-jaarverslagpagina -> data/staging/
  wachtlijst harvest codex wachtlijst      zoekt regelgeving in de Vlaamse Codex
  wachtlijst promote <staging-bestand>     neemt gecontroleerde staging-rijen op in data/curated
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import typer

from . import STAGING_DIR
from .models import Controlestatus
from .store import load, upsert, validate_all, write_rows

app = typer.Typer(help="Wachtlijsten en budgetten van Vlaamse sociale voorzieningen — onderzoekspipeline.")
harvest = typer.Typer(help="Ruwe data ophalen uit publieke bronnen.")
app.add_typer(harvest, name="harvest")


@app.command()
def validate() -> None:
    """Valideer data/curated (typen, sleutels, verwijzingen)."""
    r = validate_all()
    for w in r.waarschuwingen:
        typer.secho(f"WAARSCHUWING {w}", fg=typer.colors.YELLOW)
    for f in r.fouten:
        typer.secho(f"FOUT {f}", fg=typer.colors.RED)
    typer.echo(f"aantallen: {r.aantallen}")
    if not r.ok:
        raise typer.Exit(code=1)
    typer.secho("OK", fg=typer.colors.GREEN)


@app.command()
def publish(force: bool = typer.Option(False, help="Publiceer ook bij validatiefouten.")) -> None:
    """Bouw data/published voor het dashboard."""
    from .publish import publish as _publish

    meta = _publish(force=force)
    typer.echo(f"gepubliceerd op {meta['gepubliceerd_op']}: {meta['aantallen']}")


@harvest.command("vlpar")
def harvest_vlpar(
    term: str = typer.Argument("wachtlijst"),
    pages: int = typer.Option(2, help="Aantal pagina's van 50 hits."),
    sort: str = typer.Option("date", help="date | relevance"),
) -> None:
    """Zoek parlementaire documenten (schriftelijke vragen, Rekenhof, BBT's) op trefwoord."""
    from .sources import vlpar

    pad = vlpar.save_hits(vlpar.search(term, max_pages=pages, sort=sort), term.replace(" ", "_"))
    typer.echo(f"hits bewaard in {pad} (+ .csv)")


@harvest.command("vaph")
def harvest_vaph(
    editie: str = typer.Argument(..., help="bv. 2024 of 2024-eerste-jaarhelft"),
    pagina: int = typer.Option(25, help="Paginanummer van 'Prioriteitengroepen' in het HTML-jaarverslag."),
) -> None:
    """Parse de VAPH-jaarverslagpagina 'Prioriteitengroepen' naar kandidaat-bevindingen (staging)."""
    from .sources import vaph

    bron_id = f"vaph-jaarverslag-{editie}"
    titel = f"VAPH jaarverslag {editie} — Prioriteitengroepen"
    bevindingen = vaph.harvest_jaarverslag(editie, pagina, bron_id=bron_id, documenttitel=titel)
    if not bevindingen:
        typer.secho("patroon niet gevonden; controleer het paginanummer", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    base = STAGING_DIR / f"vaph_{editie}"
    base.mkdir(exist_ok=True)
    write_rows("bevindingen", bevindingen, base)
    typer.echo(f"{len(bevindingen)} kandidaat-bevindingen -> {base / 'bevindingen.csv'} (bron_id {bron_id!r}: voeg toe aan bronnen.csv indien nieuw)")


@harvest.command("codex")
def harvest_codex(zoekterm: str = typer.Argument("wachtlijst")) -> None:
    """Zoek regelgeving in de Vlaamse Codex."""
    from .sources import codex

    d = codex.zoek(zoekterm)
    docs = d.get("WetgevingDocumenten") or d.get("Documenten") or d
    typer.echo(str(docs)[:4000])


@harvest.command("bbt-download")
def harvest_bbt_download(
    domein: list[str] = typer.Option(None, help="WVG en/of WONEN (standaard: beide)."),
    jaar: list[int] = typer.Option(None, help="Begrotingsjaren (standaard: alle in config/bbt_documenten.yaml)."),
    force: bool = typer.Option(False, help="Opnieuw downloaden."),
) -> None:
    """Download de BBT-PDF's uit het register naar data/raw/bbt/."""
    from .sources import bbt

    paden = bbt.download_all(domeinen=domein or None, jaren=jaar or None, force=force)
    for p in paden:
        typer.echo(f"{p.name}  {p.stat().st_size // 1024} kB")
    typer.echo(f"{len(paden)} PDF's in data/raw/bbt/")


@harvest.command("bbt-parse")
def harvest_bbt_parse(
    domein: list[str] = typer.Option(None, help="WVG en/of WONEN."),
    jaar: list[int] = typer.Option(None, help="Begrotingsjaren."),
    alleen_relevant: bool = typer.Option(True, help="Enkel ISE's uit 'ise_relevant_voor_wachtlijsten' bewaren."),
) -> None:
    """Parse gedownloade BBT-PDF's naar data/staging/bbt/kredieten.csv (ISE-totalen + artikelen, k€)."""
    from .sources import bbt

    docs, domeinen = bbt.registry()
    alle = []
    for d in docs:
        if (domein and d.beleidsdomein not in domein) or (jaar and d.begrotingsjaar not in jaar):
            continue
        if not d.pad.exists():
            typer.secho(f"ontbreekt: {d.pad.name} (draai eerst harvest bbt-download)", fg=typer.colors.YELLOW)
            continue
        rijen = bbt.parse_pdf(d)
        if alleen_relevant:
            relevant = [x.upper() for x in domeinen[d.beleidsdomein]["ise_relevant_voor_wachtlijsten"]]
            rijen = [r for r in rijen if any(k in r.ise.upper() for k in relevant)]
        typer.echo(f"{d.pad.name}: {len(rijen)} rijen")
        alle += rijen
    if not alle:
        raise typer.Exit(code=1)
    base = STAGING_DIR / "bbt"
    base.mkdir(parents=True, exist_ok=True)
    write_rows("kredieten", alle, base)
    typer.echo(f"{len(alle)} kredietrijen -> {base / 'kredieten.csv'}; controleer steekproef en draai 'wachtlijst promote-kredieten'")


@app.command("promote-kredieten")
def promote_kredieten(
    staging_map: Path = typer.Argument(Path("data/staging/bbt")),
    status: Controlestatus = typer.Option(Controlestatus.BRON_GELEZEN),
    door: str = typer.Option(..., help="Wie heeft de steekproef gedaan (initialen)."),
) -> None:
    """Neem geparste kredieten op in data/curated/kredieten.csv (upsert op krediet_id)."""
    items = load("kredieten", staging_map)
    for it in items:
        it.controlestatus = status
        it.opmerking = f"steekproef {door} {date.today().isoformat()}; " + it.opmerking
    n = upsert("kredieten", items)
    typer.echo(f"{n} kredietrijen opgenomen; draai 'wachtlijst validate' en 'wachtlijst publish'.")


@app.command()
def promote(
    staging_map: Path = typer.Argument(..., help="bv. data/staging/vaph_2024"),
    status: Controlestatus = typer.Option(Controlestatus.BRON_GELEZEN, help="Controlestatus die je toekent."),
    door: str = typer.Option(..., help="Wie heeft gecontroleerd (initialen)."),
) -> None:
    """Neem gecontroleerde staging-bevindingen op in data/curated (upsert op bevinding_id)."""
    items = load("bevindingen", staging_map)
    for it in items:
        it.controlestatus = status
        it.gecontroleerd_door = door
        it.gecontroleerd_op = date.today()
        it.opmerking = it.opmerking.replace("automatisch geparsed; nog te controleren", "").strip()
    n = upsert("bevindingen", items)
    typer.echo(f"{n} bevindingen opgenomen; draai 'wachtlijst validate' en 'wachtlijst publish'.")


if __name__ == "__main__":
    app()
