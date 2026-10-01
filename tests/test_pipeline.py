from datetime import date
from pathlib import Path

from wachtlijst.models import Bevinding, Controlestatus, Krediet
from wachtlijst.publish import load_published, publish
from wachtlijst.sources.vaph import parse_prioriteitengroepen
from wachtlijst.store import load, pas_kredietcontroles_toe, upsert, validate_all, write_rows

ROOT = Path(__file__).resolve().parents[1]

VAPH_ZIN = (
    "Prioriteitengroepen Op 31 december 2024 waren 18.261 personen met in totaal 18.302 vragen geregistreerd in de "
    "prioriteitengroepen. Dat zijn 526 vragen in prioriteitengroep 1, 8091 vragen in prioriteitengroep 2 en 9685 vragen in "
    "prioriteitengroep 3. De eerstvolgende wachtende in elke prioriteitengroep had op 31 december 2024 de volgende "
    "prioriteringsdatum: prioriteitengroep 1: 1 januari 2024, prioriteitengroep 2: 1 oktober 2016, prioriteitengroep 3: 16 januari 2002."
)


def test_curated_data_valideert():
    r = validate_all(ROOT / "data" / "curated")
    assert r.ok, r.fouten
    assert r.aantallen["bevindingen"] > 0


def test_vaph_parser_haalt_alle_cijfers():
    uit = parse_prioriteitengroepen(VAPH_ZIN, "b", "http://x", "t", "p")
    d = {b.metriek: b.waarde for b in uit}
    assert d["wachtenden_personen"] == 18261
    assert d["wachtenden_vragen_totaal"] == 18302
    assert (d["wachtenden_vragen_pg1"], d["wachtenden_vragen_pg2"], d["wachtenden_vragen_pg3"]) == (526, 8091, 9685)
    assert d["wachtenden_vragen_pg1"] + d["wachtenden_vragen_pg2"] + d["wachtenden_vragen_pg3"] == d["wachtenden_vragen_totaal"]
    assert d["wachttijd_eerstvolgende_pg3_dagen"] == (date(2024, 12, 31) - date(2002, 1, 16)).days
    assert all(b.controlestatus == Controlestatus.ONGECONTROLEERD for b in uit)
    assert all(b.peildatum == date(2024, 12, 31) for b in uit)


def test_parser_geeft_leeg_bij_onbekend_patroon():
    assert parse_prioriteitengroepen("niets te zien hier", "b", "u", "t") == []


def test_som_prioriteitengroepen_klopt_in_curated():
    bev = load("bevindingen", ROOT / "data" / "curated")
    per_datum: dict[date, dict[str, float]] = {}
    for b in bev:
        if b.voorziening_id == "vaph-pvb" and b.metriek.startswith("wachtenden_vragen") and b.bron_id != "grip-wachtlijst-2022":
            per_datum.setdefault(b.peildatum, {})[b.metriek] = b.waarde
    for d, m in per_datum.items():
        if {"wachtenden_vragen_pg1", "wachtenden_vragen_pg2", "wachtenden_vragen_pg3", "wachtenden_vragen_totaal"} <= m.keys():
            assert m["wachtenden_vragen_pg1"] + m["wachtenden_vragen_pg2"] + m["wachtenden_vragen_pg3"] == m["wachtenden_vragen_totaal"], d


def test_store_roundtrip_en_upsert(tmp_path):
    b = Bevinding(bevinding_id="x:m:2024-01-01", voorziening_id="x", metriek="m", waarde=1, eenheid="n", peildatum=date(2024, 1, 1),
                  bron_id="s", bron_url="u", documenttitel="t")
    write_rows("bevindingen", [b], tmp_path)
    assert load("bevindingen", tmp_path)[0] == b
    b2 = b.model_copy(update={"waarde": 2.0})
    upsert("bevindingen", [b2], tmp_path)
    rows = load("bevindingen", tmp_path)
    assert len(rows) == 1 and rows[0].waarde == 2


def test_publish_schrijft_meta(tmp_path):
    meta = publish(base=ROOT / "data" / "curated", dest=tmp_path)
    assert (tmp_path / "meta.json").exists()
    assert meta["aantallen"]["bevindingen"] > 0
    d = load_published(tmp_path)
    assert "waarde" in d["bevindingen"].columns and d["bevindingen"]["waarde"].notna().all()


def test_kredietcontroles_overleven_herhaald_toepassen():
    k = Krediet(krediet_id="1:x:ISE:bo-2025:Kredietsoort.VAK", beleidsdomein="WVG", begrotingsjaar=2025, fase="BO", stuk="13-A",
                pfile_id=1, kolom="BO 2025", kredietsoort="VAK", bedrag_keur=10.0, bron_url="http://x",
                controlestatus=Controlestatus.BRON_GELEZEN, opmerking="automatisch geparsed")
    controles = {k.krediet_id: {"gecontroleerd_door": "EB", "gecontroleerd_op": "2026-10-01", "opmerking": "p. 3"}}
    assert pas_kredietcontroles_toe([k], controles) == 1
    assert pas_kredietcontroles_toe([k], controles) == 1
    assert k.controlestatus == Controlestatus.GECONTROLEERD
    assert k.opmerking == "gecontroleerd EB 2026-10-01 (p. 3); automatisch geparsed"


def test_vaph_passage_zonder_menutekst_en_volledig():
    uit = parse_prioriteitengroepen("Menu Jaarverslag Zoeken Prioriteitengroepen " + VAPH_ZIN + " Volgende hoofdstuk", "b", "u", "t")
    passage = uit[0].passage
    assert passage.startswith("Op 31 december 2024 waren 18.261 personen")
    assert passage.endswith("prioriteitengroep 3: 16 januari 2002")


NRTJ_TEKST = ("Wachtenden niet-rechtstreeks toegankelijke jeugdhulp Op 31 december 2025 stonden in totaal 9.748 kinderen en jongeren op een "
              "NRTJ-wachtlijst (inclusief wachtend op zorg door een MFC, exclusief Persoonlijke assistentiebudget (PAB)). Dat zijn er 6 procent "
              "meer dan in 2024 (9.194). Die stijging is te verklaren door een stabiele instroom. Het aantal kinderen en jongeren met een "
              "aanmelding bij de intersectorale toegangspoort door middel van een A document is in 2025 gestegen naar 15.446 (+3,9%). "
              "Het aantal kinderen en jongeren met een nieuwe hulpvraag is toegenomen (+ 4,9%, 12.897 in 2025).")


def test_opgroeien_nrtj_parser():
    from wachtlijst.sources.opgroeien import parse_nrtj

    d = {(b.metriek, b.peildatum.year): b.waarde for b in parse_nrtj(NRTJ_TEKST)}
    assert d[("wachtenden_nrtj", 2025)] == 9748
    assert d[("wachtenden_nrtj", 2024)] == 9194
    assert d[("aanmeldingen_a_document", 2025)] == 15446
    assert d[("nieuwe_hulpvraag", 2025)] == 12897


def test_cgg_gewogen_gemiddelde():
    import importlib.util

    import pandas as pd

    spec = importlib.util.spec_from_file_location("cgg_gewogen", ROOT / "scripts" / "cgg_gewogen.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    sleutel = {"leeftijd": "0-17", "jaar": 2023}
    wacht = pd.DataFrame([{**sleutel, "cgg": "F1", "geslacht": "M", "waarde": 10.0}, {**sleutel, "cgg": "F2", "geslacht": "M", "waarde": 40.0}])
    gewicht = pd.DataFrame([{**sleutel, "cgg": "F1", "geslacht": "M", "waarde": 300}, {**sleutel, "cgg": "F2", "geslacht": "M", "waarde": 100}])
    r = mod.gewogen(wacht, gewicht, "ftf1").iloc[0]
    assert r.gewogen == 17.5 and r.ongewogen == 25.0 and r.dekking_pct == 100.0
