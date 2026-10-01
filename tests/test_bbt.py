from pathlib import Path

import pytest

from wachtlijst.sources.bbt import BbtDoc, parse_pdf, parse_tekst, registry

ROOT = Path(__file__).resolve().parents[1]

# Tekst zoals pdfplumber die oplevert uit 13-V (2024-2025), pfile 2081035 (passages letterlijk overgenomen).
BBT_TEKST = """IV. BELEIDSVELD I: WELZIJN
ISE: BELEIDSONDERSTEUNING, MVG excl. DAB
1.7. Budgettair kader voor het begrotingsjaar
(duizend euro)
VAK VEK
BA 2024 evolutie BO 2025 BA 2024 evolutie BO 2025
ESR-uitgaven (werking en toelagen (WT), lonen (LO), provisies (PR))
331.740 -37.565 294.175 343.519 -40.728 302.791
Toelagen (interne stromen (IS))
25 1 26 25 1 26
Overige (leningen (LE), participaties (PA); geen ESR-impact)
0 0 0 0 0 0
Totaal 331.765 -37.564 294.201 343.544 -40.727 302.817
1.7.1. Departement Zorg
Uitgavenartikelen
GB0-1GCF2BA-WT - BELEIDSONTWIKKELING EN -ONDERSTEUNING
Korte inhoud begrotingsartikel: De middelen op dit begrotingsartikel worden aangewend voor de ondersteuning.
Kredietevolutie:
(duizend euro) VAK VEK
BA 2024 327.710 337.924
Index 5.547 5.547
Compensaties -4.917 -4.755
Andere bijstellingen -38.219 -39.923
BO 2025 290.121 298.793
VII. BELEIDSVELD IV: PERSONEN MET EEN BEPERKING
ISE: PERSONEN MET EEN BEPERKING, MVG excl. DAB
1.7. Budgettair kader voor het begrotingsjaar
(duizend euro)
VAK VEK
BA 2024 evolutie BO 2025 BA 2024 evolutie BO 2025
Totaal 2.800.000 191.680 2.991.680 2.600.000 126.246 2.726.246
GB0-1GGF2RX-IS - VAPH
Kredietevolutie:
(duizend euro) VAK VEK
BA 2024 2.800.000 2.600.000
Index 50.000 50.000
Andere bijstellingen 141.680 76.246
BO 2025 2.991.680 2.726.246
"""

DOC = BbtDoc(beleidsdomein="WVG", begrotingsjaar=2025, fase="BO", stuk="13-V (2024-2025) nr. 1", doc_id=1841767, pfile_id=2081035, ingediend="2024-11-15")


def test_registry_laadt_en_is_consistent():
    docs, dom = registry(ROOT / "config" / "bbt_documenten.yaml")
    assert len(docs) >= 28
    ids = [d.pfile_id for d in docs]
    assert len(ids) == len(set(ids)), "dubbele pfile-id's in register"
    assert {d.beleidsdomein for d in docs} == {"WVG", "WONEN"}
    assert "PERSONEN MET EEN BEPERKING" in dom["WVG"]["ise_relevant_voor_wachtlijsten"]


def test_parser_ise_totaal_en_artikel():
    rijen = parse_tekst(DOC, BBT_TEKST)
    d = {(r.ise, r.artikel_code, r.kolom, r.kredietsoort): r.bedrag_keur for r in rijen}
    assert d[("BELEIDSONDERSTEUNING", "", "BO 2025", "VAK")] == 294201
    assert d[("BELEIDSONDERSTEUNING", "", "BA 2024", "VEK")] == 343544
    assert d[("BELEIDSONDERSTEUNING", "GB0-1GCF2BA-WT", "BO 2025", "VAK")] == 290121
    assert d[("BELEIDSONDERSTEUNING", "GB0-1GCF2BA-WT", "Andere bijstellingen", "VEK")] == -39923
    assert d[("PERSONEN MET EEN BEPERKING", "", "BO 2025", "VAK")] == 2991680
    assert d[("PERSONEN MET EEN BEPERKING", "GB0-1GGF2RX-IS", "BO 2025", "VEK")] == 2726246
    r = next(x for x in rijen if x.artikel_code == "GB0-1GGF2RX-IS" and x.kolom == "BO 2025" and x.kredietsoort == "VAK")
    assert r.programma == "GG" and r.beleidsveld == "PERSONEN MET EEN BEPERKING" and r.controlestatus == "ongecontroleerd"
    assert len({x.krediet_id for x in rijen}) == len(rijen)


def test_parser_op_echte_pdf(tmp_path):
    reportlab = pytest.importorskip("reportlab")
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    pad = tmp_path / "bbt.pdf"
    c = canvas.Canvas(str(pad), pagesize=A4)
    y = 820
    for regel in BBT_TEKST.splitlines():
        if y < 40:
            c.showPage(); y = 820
        c.setFont("Helvetica", 8); c.drawString(30, y, regel); y -= 11
    c.save()
    rijen = parse_pdf(DOC, pad)
    d = {(r.ise, r.artikel_code, r.kolom, r.kredietsoort): r.bedrag_keur for r in rijen}
    assert d[("PERSONEN MET EEN BEPERKING", "GB0-1GGF2RX-IS", "BO 2025", "VAK")] == 2991680
    assert all(r.pagina for r in rijen)
