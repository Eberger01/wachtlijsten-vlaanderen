"""Streamlit-dashboard — leest uitsluitend ``data/published`` (geen web, geen PDF's).

Starten:  streamlit run dashboard/app.py
Hosten:   Streamlit Community Cloud (main file: dashboard/app.py, requirements: dashboard/requirements.txt)
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wachtlijst.publish import load_published  # noqa: E402

# Palet (dataviz-referentie): categorische slots in vaste volgorde, nooit per rang herverdeeld.
SERIES = {"pg1": "#2a78d6", "pg2": "#eb6834", "pg3": "#1baf7a", "totaal": "#4a3aa7"}
INK = {"primary": "#0b0b0b", "secondary": "#52514e", "muted": "#898781", "grid": "#e1e0d9", "surface": "#fcfcfb"}
STATUS_LABEL = {
    "gecontroleerd": "✔ gecontroleerd (2 lezingen)",
    "bron_gelezen": "◐ bron gelezen (1 lezing)",
    "ongecontroleerd": "○ ongecontroleerd / secundair",
    "betwist": "⚠ betwist",
}

st.set_page_config(page_title="Wachtlijsten Vlaanderen", page_icon="📋", layout="wide")


@st.cache_data
def data(publicatie: str):
    # Cachesleutel = inhoud van meta.json: Streamlit Cloud trekt nieuwe commits binnen zonder het proces
    # te herstarten, dus zonder sleutel bleef de oude publicatie in de cache staan.
    return load_published()


_meta_p = ROOT / "data" / "published" / "meta.json"
D = data(_meta_p.read_text(encoding="utf-8") if _meta_p.exists() else "")
meta = D["meta"]
voorz, bev, bud, bronnen = D["voorzieningen"], D["bevindingen"], D["budgetten"], D["bronnen"]

st.title("Wachtlijsten voor sociale voorzieningen in Vlaanderen")
st.caption(
    f"Onderzoeksdashboard · laatste actualisering van de gegevens: **{meta.get('gepubliceerd_op', 'onbekend')[:16].replace('T', ' ')}** · "
    "elk cijfer draagt zijn bron, passage, peildatum, definitie en controlestatus."
)

tab_overzicht, tab_totalen, tab_detail, tab_budget, tab_bronnen, tab_methode = st.tabs(
    ["Inventaris", "Totalen", "Voorziening", "Budget", "Bronnen", "Methodiek"]
)

# ------------------------------------------------------------------------------------------ Inventaris
with tab_overzicht:
    c1, c2, c3 = st.columns(3)
    c1.metric("Voorzieningen gescand", len(voorz))
    c2.metric("Met centraal gepubliceerde wachtlijst", int((voorz["wachtlijst_type"] == "centraal_gepubliceerd").sum()))
    c3.metric("Decentrale lijsten (geen Vlaams cijfer)", int((voorz["wachtlijst_type"] == "decentraal").sum()))

    f1, f2, f3 = st.columns(3)
    bevoegd = f1.multiselect("Bevoegdheid", sorted(voorz["bevoegdheid"].unique()), default=list(voorz["bevoegdheid"].unique()))
    domein = f2.multiselect("Domein", sorted(voorz["domein"].unique()), default=sorted(voorz["domein"].unique()))
    wtype = f3.multiselect("Type wachtlijst", sorted(voorz["wachtlijst_type"].unique()), default=sorted(voorz["wachtlijst_type"].unique()))
    sel = voorz[voorz["bevoegdheid"].isin(bevoegd) & voorz["domein"].isin(domein) & voorz["wachtlijst_type"].isin(wtype)]
    st.dataframe(
        sel[["naam", "domein", "entiteit", "bevoegdheid", "wachtlijst_naam", "wachtlijst_type", "frequentie", "laatste_peildatum", "scan_status", "opmerking"]],
        width="stretch", hide_index=True, height=560,
    )

# ------------------------------------------------------------------------------------------ Totalen
with tab_totalen:
    # Eén kerncijfer per voorziening, bewust gekozen (zoals REEKS_LABELS): een 'hoeveel wachten er'-metriek (aantal)
    # en/of een wachttijdmetriek. Enkel aantal-metrieken worden opgeteld; wachttijden en voorzieningen zonder cijfer
    # staan ernaast met de reden. Het totaal zegt dus altijd wat erin zit — eenheden en peildata verschillen.
    KERN = {
        "vaph-pvb": dict(aantal="wachtenden_personen", wachttijd="wachttijd_eerstvolgende_pg2_dagen",
                         noot="personen met minstens één actieve vraag; wachttijd = eerstvolgende wachtende PG2"),
        "opgroeien-nrtj": dict(aantal="wachtenden_nrtj", noot="excl. PAB (apart geteld onder PAB minderjarigen)"),
        "wonen-sociale-huur": dict(aantal="wachtenden_kandidaten", wachttijd="wachttijd_bij_toewijzing_jaren", budget="nettofinanciering VMSW",
                                   noot="eenheid wisselt per bron (kandidaat-huurders / kandidaten / huishoudens)"),
        "wonen-huurpremie": dict(noot="rechtsgebonden, geen wachtlijst"),
        "wonen-sociale-koop": dict(noot="afgesloten: enkel verkoopcijfers, geen wachtlijst"),
        "agii-mo": dict(aantal="wachtenden_6_maanden", noot="KPI: > 6 maanden na contract nog niet gestart"),
        "vdab-collectief-maatwerk": dict(aantal="wachtenden_advies_cmw", noot="werkzoekenden met advies, zonder plaats"),
        "zorg-woonzorgcentra": dict(noot="geen wachtlijst, enkel erkenningskalender (zie Voorziening)"),
        "zorg-cgg": dict(wachttijd="wachttijd_ftf1_0_17_dagen", budget="enveloppe-subsidie CGG", noot="wachttijd tot 1e contact 0-17 j; geen wachtlijsttelling"),
        "zorg-cos": dict(wachttijd="wachttijd_antwerpen_maanden", noot="enkel per centrum (hier Antwerpen), geen Vlaams cijfer"),
        "opgroeien-kinderopvang": dict(aantal="onbeantwoorde_opvangvragen", noot="vragen via lokale loketten, niet-unieke kinderen"),
        "opgroeien-pleegzorg": dict(aantal="wachtenden_pleeggezin", noot="kinderen wachtend op een pleeggezin"),
        "onderwijs-buitengewoon": dict(noot="decentraal; enkel lokale LOP-cijfers (bv. Antwerpen)"),
        "nt2": dict(aantal="wachtenden_cbe_cvo", noot="afgesloten: geen wachtenden gemeld"),
        "zorg-gezinszorg": dict(noot="rantsoenering via urencontingent, geen lijst"),
        "vsb-zorgbudget": dict(noot="rechtsgebonden, geen wachtlijst"),
        "ajh-justitiehuizen": dict(wachttijd="wachttijd_werkstraf_aanstelling_dagen", noot="wachttijd tot aanstelling justitieassistent (werkstraf)"),
        "wonen-premies": dict(noot="afgesloten: premies op aanvraag, geen wachtlijst"),
        "vwf-woonlening": dict(noot="afgesloten: geen wachtlijst"),
        "vdab-ibo": dict(noot="afgesloten: geen wachtlijst"),
        "vaph-pab-minderjarigen": dict(aantal="wachtenden_pab", noot="minderjarigen wachtend op PAB (Opgroeien-telling)"),
        "vaph-rth-hulpmiddelen": dict(noot="geen lijst; deels verplaatste PVB-wachtlijst (zie PVB: onder cesuur)"),
        "zorg-car": dict(noot="geen cijfers beschikbaar"),
        "zorg-caw-verslavingszorg": dict(wachttijd="wachttijd_cgg_verslavingsteams_dagen", noot="geen wachtlijsttelling"),
        "zorg-forensisch": dict(aantal="caw_wachtenden_gevangenissen", wachttijd="wachttijd_cgg_forensisch_dagen",
                                noot="CAW in gevangenis, onvolledig (Oost-Vlaanderen zonder lijst)"),
        "dwse-art60-wijkwerken": dict(noot="rantsoenering zonder lijst"),
    }
    # Referentiebudget per voorziening: één bedrag, geen som — meest recente begrotingsjaar, bij voorkeur het
    # begrotingsartikel (VAK), anders de eigen begroting van de entiteit, anders een beleidsenveloppe, anders realisatie.
    # Waar het grootste artikel niet de voorziening dekt (sociale huur, CGG), kiest KERN[...]["budget"] de budgetlijn op label.
    NIVEAU_VOORKEUR = ["dept_artikel", "entiteit_begroting", "beleidsenveloppe", "realisatie"]

    def _laatste(vid: str, metriek: str | None):
        if not metriek:
            return None, None
        r = bev[(bev["voorziening_id"] == vid) & (bev["metriek"] == metriek)].dropna(subset=["peildatum"]).sort_values("peildatum")
        return (r.iloc[0], r.iloc[-1]) if len(r) else (None, None)

    def _budgetkandidaten(vid: str):
        kand = bud[(bud["voorziening_id"] == vid) & bud["niveau"].isin(NIVEAU_VOORKEUR) & bud["kredietsoort"].isin(["VAK", "n.v.t."])].dropna(subset=["begrotingsjaar"])
        label = KERN.get(vid, {}).get("budget")
        return kand[kand["label"].str.contains(label, case=False, regex=False)] if label else kand

    def _referentiebudget(vid: str):
        kand = _budgetkandidaten(vid)
        if not len(kand):
            return None
        kand = kand[kand["begrotingsjaar"] == kand["begrotingsjaar"].max()].copy()
        kand["rang"] = kand["niveau"].map(NIVEAU_VOORKEUR.index)
        return kand.sort_values(["rang", "bedrag_eur"], ascending=[True, False]).iloc[0]

    def _budgetreeks(vid: str):
        """Langste reeks met gelijk niveau en gelijke budgetlijn (≥ 2 jaren) — voor budgetgroei. Fases mogen mengen
        (BA 2025 → BO 2026 is de gangbare vergelijking); het label wordt ontdaan van een suffix als '(uitvoering)'.
        Uitbreidingsbeleid is uitgesloten: dat is een jaarlijkse enveloppe, geen stand."""
        kand = _budgetkandidaten(vid).copy()
        kand["lijn"] = kand["label"].str.replace(r"\s*\((uitvoering|realisatie)\)\s*$", "", regex=True).str.strip()
        beste = None
        FASE_RANG = {"BA": 0, "BO": 1, "AGENTSCHAP": 2, "BELEID": 3, "UITV": 4}  # per jaar één fase: begroting vóór uitvoering
        kand["fase_rang"] = kand["fase"].map(FASE_RANG).fillna(9)
        for (niveau, lijn), g in kand.groupby(["niveau", "lijn"]):
            g = g.sort_values(["begrotingsjaar", "fase_rang"]).drop_duplicates("begrotingsjaar", keep="first")
            if len(g) < 2:
                continue
            sleutel = (len(g), -NIVEAU_VOORKEUR.index(niveau), g["bedrag_eur"].iloc[-1])
            if beste is None or sleutel > beste[0]:
                beste = (sleutel, g)
        return None if beste is None else beste[1]

    rijen = []
    for _, v in voorz.iterrows():
        vid, k = v["voorziening_id"], KERN.get(v["voorziening_id"], {})
        e0, e1 = _laatste(vid, k.get("aantal"))
        w0, w1 = _laatste(vid, k.get("wachttijd"))
        rb, br = _referentiebudget(vid), _budgetreeks(vid)
        uitbr = bud[(bud["voorziening_id"] == vid) & (bud["niveau"] == "uitbreidingsbeleid")].dropna(subset=["begrotingsjaar"]).sort_values(["begrotingsjaar", "bedrag_eur"])
        rijen.append({
            "voorziening_id": vid, "voorziening": v["naam"], "domein": v["domein"],
            "wachtenden": e1["waarde"] if e1 is not None else None,
            "eenheid": e1["eenheid"] if e1 is not None else "",
            "peildatum": e1["peildatum"] if e1 is not None else pd.NaT,
            "status": STATUS_LABEL.get(e1["controlestatus"], "") if e1 is not None else "",
            "eerste_waarde": e0["waarde"] if e0 is not None and e0["peildatum"] != e1["peildatum"] else None,
            "eerste_peildatum": e0["peildatum"] if e0 is not None and e0["peildatum"] != e1["peildatum"] else pd.NaT,
            "wachttijd": w1["waarde"] if w1 is not None else None,
            "wachttijd_eenheid": w1["eenheid"] if w1 is not None else "",
            "wachttijd_peildatum": w1["peildatum"] if w1 is not None else pd.NaT,
            "wachttijd_eerste": w0["waarde"] if w0 is not None and w0["peildatum"] != w1["peildatum"] else None,
            "budget_mln": rb["bedrag_eur"] / 1e6 if rb is not None else None,
            "budget_jaar": int(rb["begrotingsjaar"]) if rb is not None else None,
            "budget_niveau": f"{rb['niveau']} · {rb['fase']}" if rb is not None else "",
            "budget_label": rb["label"] if rb is not None else "",
            "budget_status": STATUS_LABEL.get(rb["controlestatus"], "") if rb is not None else "",
            "uitbreiding_mln": uitbr["bedrag_eur"].iloc[-1] / 1e6 if len(uitbr) else None,
            "uitbreiding_jaar": int(uitbr["begrotingsjaar"].iloc[-1]) if len(uitbr) else None,
            "budgetreeks": br,
            "noot": k.get("noot", ""),
        })
    T = pd.DataFrame(rijen)
    T["groei_pct"] = (T["wachtenden"] / T["eerste_waarde"] - 1) * 100
    T["budgetgroei_pct"] = T["budgetreeks"].map(lambda g: (g["bedrag_eur"].iloc[-1] / g["bedrag_eur"].iloc[0] - 1) * 100 if g is not None else None)
    T["budgetperiode"] = T["budgetreeks"].map(lambda g: f"{int(g['begrotingsjaar'].iloc[0])}→{int(g['begrotingsjaar'].iloc[-1])}" if g is not None else "")
    T["budgetreeks_label"] = T["budgetreeks"].map(lambda g: f"{g['niveau'].iloc[0]} · {g['lijn'].iloc[0]} ({' / '.join(dict.fromkeys(g['fase']))})" if g is not None else "")

    met_aantal = T[T["wachtenden"].notna()]
    met_budget = T[T["budget_mln"].notna()]
    stijgend = met_aantal[met_aantal["groei_pct"] > 0]

    st.markdown(
        "Eén kerncijfer per voorziening: **hoeveel wachten er** (aantal) en/of **hoe lang** (wachttijd), plus één **referentiebudget** "
        "(meest recente begrotingsjaar, bij voorkeur het begrotingsartikel). De totalen tellen enkel aantallen op; eenheden, definities en "
        "peildata verschillen per voorziening — open *wat zit erin* vóór u een totaal citeert."
    )
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Wachtenden, som", f"{met_aantal['wachtenden'].sum():,.0f}".replace(",", "."),
              help=f"{len(met_aantal)} van {len(T)} voorzieningen met een telbaar kerncijfer; eenheden verschillen (zie 'wat zit erin').")
    c2.metric("Voorzieningen met telbaar cijfer", f"{len(met_aantal)} / {len(T)}")
    c3.metric("Lijsten die groeien", f"{len(stijgend)} / {int(met_aantal['groei_pct'].notna().sum())}",
              help="Kerncijfer laatste peildatum hoger dan eerste peildatum in de reeks.")
    c4.metric("Referentiebudget, som (mln €)", f"{met_budget['budget_mln'].sum():,.0f}".replace(",", "."),
              help=f"{len(met_budget)} voorzieningen; niveaus verschillen en overlappen deels (bv. PAB binnen VAPH, pleegzorg binnen jeugdhulp). Indicatief.")

    with st.expander("Wat zit erin — en wat niet"):
        a, bcol = st.columns(2)
        a.markdown("**In de som wachtenden**")
        a.dataframe(
            met_aantal.sort_values("wachtenden", ascending=False)[["voorziening", "wachtenden", "eenheid", "peildatum", "status", "noot"]],
            hide_index=True, width="stretch",
            column_config={"wachtenden": st.column_config.NumberColumn(format="localized"), "peildatum": st.column_config.DateColumn(format="DD-MM-YYYY")},
        )
        bcol.markdown("**Niet in de som** (geen telbaar cijfer)")
        bcol.dataframe(T[T["wachtenden"].isna()][["voorziening", "wachttijd", "wachttijd_eenheid", "noot"]], hide_index=True, width="stretch",
                       column_config={"wachttijd": st.column_config.NumberColumn(format="localized")})
        st.caption("Overlap bewust vermeden: NRTJ telt excl. PAB; RTH-gebruikers onder de PVB-cesuur worden niet apart geteld. "
                   "Kinderopvang telt vragen (niet-unieke kinderen); sociale huur telt huishoudens volgens de laatste bron.")

    # ---- Tabel per voorziening
    st.markdown("**Per voorziening** — kerncijfer, trend, wachttijd en referentiebudget")
    toon_t = T[["voorziening", "domein", "wachtenden", "eenheid", "peildatum", "groei_pct", "eerste_peildatum", "status",
                "wachttijd", "wachttijd_eenheid", "wachttijd_peildatum", "budget_mln", "budget_jaar", "budget_niveau", "budget_label",
                "uitbreiding_mln", "uitbreiding_jaar", "noot"]]
    st.dataframe(
        toon_t.sort_values("wachtenden", ascending=False, na_position="last"), hide_index=True, width="stretch", height=560,
        column_config={
            "wachtenden": st.column_config.NumberColumn("wachtenden", format="localized"),
            "peildatum": st.column_config.DateColumn("peildatum", format="DD-MM-YYYY"),
            "groei_pct": st.column_config.NumberColumn("groei sinds eerste meting (%)", format="%+.0f %%"),
            "eerste_peildatum": st.column_config.DateColumn("eerste meting", format="DD-MM-YYYY"),
            "wachttijd": st.column_config.NumberColumn("wachttijd", format="localized"),
            "wachttijd_eenheid": "eenheid ", "wachttijd_peildatum": st.column_config.DateColumn("peildatum ", format="DD-MM-YYYY"),
            "budget_mln": st.column_config.NumberColumn("referentiebudget (mln €)", format="%.1f"),
            "budget_jaar": st.column_config.NumberColumn("jaar", format="%d"),
            "budget_niveau": "niveau · fase", "budget_label": "budgetlijn",
            "uitbreiding_mln": st.column_config.NumberColumn("uitbreidingsbeleid (mln €)", format="%.1f"),
            "uitbreiding_jaar": st.column_config.NumberColumn("jaar ", format="%d"),
        },
    )

    # ---- Figuur 1: wachtenden per voorziening (log-as: sociale huur is 10× de rest)
    g1 = met_aantal[met_aantal["wachtenden"] > 0].sort_values("wachtenden")
    if len(g1):
        fig_t1 = go.Figure(go.Bar(
            x=g1["wachtenden"], y=g1["voorziening"], orientation="h", marker_color=SERIES["pg1"], marker_line_width=0,
            text=[f"{x:,.0f}".replace(",", ".") + f" {e}" for x, e in zip(g1["wachtenden"], g1["eenheid"])], textposition="outside",
            customdata=list(zip(g1["peildatum"].dt.strftime("%d-%m-%Y"), g1["status"], g1["noot"])),
            hovertemplate="<b>%{y}</b><br>%{x:,.0f} (peildatum %{customdata[0]})<br>%{customdata[1]}<br><i>%{customdata[2]}</i><extra></extra>",
        ))
        fig_t1.update_layout(
            title="Wachtenden per voorziening, laatste peildatum (logaritmische as — eenheden verschillen)",
            plot_bgcolor=INK["surface"], paper_bgcolor=INK["surface"], font=dict(color=INK["primary"], family="system-ui, Segoe UI, sans-serif"),
            margin=dict(l=40, r=160, t=60, b=40), height=60 + 38 * len(g1), showlegend=False,
        )
        fig_t1.update_xaxes(type="log", gridcolor=INK["grid"], tickfont=dict(color=INK["muted"]), separatethousands=True)
        fig_t1.update_yaxes(showgrid=False, tickfont=dict(color=INK["primary"]))
        st.plotly_chart(fig_t1, width="stretch")

    # ---- Figuur 2: groei wachtlijst vs groei budget — de eigenlijke 'big picture'
    g2 = T[T["groei_pct"].notna() | T["budgetgroei_pct"].notna()].copy()
    g2 = g2[g2["wachtenden"].notna()].sort_values("groei_pct", ascending=False)
    if len(g2):
        lijstper = [f"{a:%Y}→{b:%Y}" if pd.notna(a) else "" for a, b in zip(g2["eerste_peildatum"], g2["peildatum"])]
        fig_t2 = go.Figure()
        fig_t2.add_trace(go.Bar(
            name="wachtlijst (kerncijfer)", x=g2["voorziening"], y=g2["groei_pct"], marker_color=SERIES["pg2"], marker_line_width=0,
            customdata=list(zip(lijstper, g2["eenheid"])),
            hovertemplate="<b>%{x}</b><br>wachtlijst %{y:+.0f} % (%{customdata[0]}, %{customdata[1]})<extra></extra>",
        ))
        fig_t2.add_trace(go.Bar(
            name="budget (langste gelijksoortige reeks)", x=g2["voorziening"], y=g2["budgetgroei_pct"], marker_color=SERIES["pg1"], marker_line_width=0,
            customdata=list(zip(g2["budgetperiode"], g2["budgetreeks_label"])),
            hovertemplate="<b>%{x}</b><br>budget %{y:+.0f} % (%{customdata[0]})<br><i>%{customdata[1]}</i><extra></extra>",
        ))
        fig_t2.update_layout(
            title="Groei van de wachtlijst versus groei van het budget (%) — periodes verschillen per voorziening, zie hover",
            barmode="group", bargap=0.3, plot_bgcolor=INK["surface"], paper_bgcolor=INK["surface"],
            font=dict(color=INK["primary"], family="system-ui, Segoe UI, sans-serif"),
            legend=dict(orientation="h", y=-0.45), margin=dict(l=40, r=20, t=60, b=140), height=480,
        )
        fig_t2.update_xaxes(showgrid=False, tickangle=-30, tickfont=dict(color=INK["primary"]))
        fig_t2.update_yaxes(gridcolor=INK["grid"], zeroline=True, zerolinecolor=INK["muted"], ticksuffix=" %", tickfont=dict(color=INK["muted"]))
        st.plotly_chart(fig_t2, width="stretch")
        st.caption(
            "Lezing: staat de oranje balk boven de blauwe, dan groeit de lijst sneller dan het budget (of krimpt het budget niet mee). "
            "Budgetgroei is gemeten op de langste reeks met gelijk niveau en gelijke budgetlijn, begroting vóór uitvoering (uitbreidingsbeleid uitgesloten: een jaarlijkse "
            "enveloppe, geen stand). Wachttijd-voorzieningen (CGG, justitiehuizen, forensische zorg) staan hier niet: een wachttijd is geen lijst."
        )

    # ---- Wachttijden apart: eerste vs laatste meting
    wt = T[T["wachttijd"].notna()].copy()
    if len(wt):
        st.markdown("**Wachttijden** — eerste en laatste meting van het kerncijfer")
        st.dataframe(
            wt[["voorziening", "wachttijd_eerste", "wachttijd", "wachttijd_eenheid", "wachttijd_peildatum", "noot"]].sort_values("voorziening"),
            hide_index=True, width="stretch",
            column_config={"wachttijd_eerste": st.column_config.NumberColumn("eerste meting", format="localized"),
                           "wachttijd": st.column_config.NumberColumn("laatste meting", format="localized"),
                           "wachttijd_peildatum": st.column_config.DateColumn("peildatum", format="DD-MM-YYYY")},
        )

# ------------------------------------------------------------------------------------------ Voorziening
with tab_detail:
    met_data = sorted(bev["voorziening_id"].unique())
    keuze = st.selectbox("Voorziening", met_data, format_func=lambda i: voorz.set_index("voorziening_id").loc[i, "naam"])
    v = voorz.set_index("voorziening_id").loc[keuze]
    st.markdown(f"**{v['naam']}** — {v['entiteit']} · {v['bevoegdheid']} · wachtlijst: *{v['wachtlijst_naam']}*")
    b = bev[bev["voorziening_id"] == keuze].sort_values("peildatum")

    statussen = st.multiselect("Toon controlestatus", list(STATUS_LABEL), default=list(STATUS_LABEL), format_func=STATUS_LABEL.get)
    b = b[b["controlestatus"].isin(statussen)]

    # Reeksen in de hoofdgrafiek: vaste kleur per metriek (entiteit), nooit per rang herverdeeld.
    # Metrieken die hier niet staan (bv. wachttijden, terbeschikkingstellingen, capaciteit) blijven in de tabel.
    REEKS_LABELS = {
        "wachtenden_vragen_pg1": "Prioriteitengroep 1", "wachtenden_vragen_pg2": "Prioriteitengroep 2",
        "wachtenden_vragen_pg3": "Prioriteitengroep 3", "wachtenden_vragen_totaal": "Totaal vragen",
        "wachtenden_kandidaten": "Kandidaat-huurders / kandidaten (CIR)",
        "wachtenden_actieve_inschrijvingen": "Actieve inschrijvingen (CIR, incl. zittende huurders)",
        "wachtenden_nrtj": "Wachtenden NRTJ (excl. PAB)", "wachtenden_nrtj_zonder_hulp": "Wachtenden zonder enige NRTJ-hulp",
        "wachtenden_pab": "Wachtenden PAB (minderjarigen)", "wachtenden_nrtj_sector_jho": "Sector jeugdhulp Opgroeien (JHO)",
        "wachtenden_nrtj_sector_vaph": "Sector VAPH (MFC)",
        "opvangvragen_lokale_loketten": "Opvangvragen lokale loketten", "onbeantwoorde_opvangvragen": "Onbeantwoorde opvangvragen",
        "onvervulde_behoefte_kinderen": "Kinderen met onvervulde behoefte (onderzoek)",
        "wachtenden_geen_passend_aanbod": "Geen passend MO-aanbod", "wachtenden_6_maanden": "> 6 maanden na contract niet gestart",
        "wachttijd_ftf1_0_17_dagen": "Wachttijd tot 1e contact, 0-17 j (dagen)", "wachttijd_ftf1_18_59_dagen": "Wachttijd tot 1e contact, 18-59 j (dagen)",
        "wachttijd_ftf1_60plus_dagen": "Wachttijd tot 1e contact, 60+ (dagen)", "wachttijd_ftf1_18_64_dagen": "Wachttijd tot 1e contact, 18-64 j (dagen, vanaf 2024)",
        "wachttijd_ftf1_65plus_dagen": "Wachttijd tot 1e contact, 65+ (dagen, vanaf 2024)",
        "wachtenden_advies_cmw": "Werkzoekenden met advies collectief maatwerk (VDAB)", "contingent_open_vte": "Openstaand contingent maatwerkbedrijven (VTE)",
        "contingent_toegekend_vte": "Toegekend contingent (VTE)", "contingent_ingevuld_vte": "Ingevuld contingent (VTE)", "werknemers_cmw": "Werknemers collectief maatwerk (personen)",
        "kalender_nog_te_realiseren_wzc": "Kalender wzc nog te realiseren", "kalender_uitgesteld_wzc_cum": "Kalender wzc uitgesteld (cumulatief)",
        "kalender_gerealiseerd_wzc_cum": "Kalender wzc gerealiseerd (cumulatief)", "kalender_vervallen_wzc_cum": "Kalender wzc vervallen (cumulatief)",
        "kalender_uitstel_gevraagd_wzc": "Uitstel gevraagd in het jaar (wzc)",
        "leerlingen_buo": "Leerlingen buitengewoon onderwijs", "verkochte_sociale_koopwoningen_nieuw": "Verkochte nieuwe sociale koopwoningen",
        "uren_gezinszorg_gepresteerd": "Gepresteerde uren gezinszorg", "gebruikers_gezinszorg": "Gebruikers gezinszorg (gezinnen)", "urencontingent_toegekend": "Toegekend urencontingent (uren)",
        "wachttijd_antwerpen_maanden": "Wachttijd COS Antwerpen (maanden)", "wachttijd_brussel_maanden": "Wachttijd COS Brussel (maanden)", "wachttijd_gent_maanden": "Wachttijd COS Gent (maanden)", "wachttijd_leuven_maanden": "Wachttijd COS Leuven (maanden)",
        "wachtenden_pleeggezin": "Kinderen wachtend op een pleeggezin", "wachttijd_werkstraf_aanstelling_dagen": "Wachttijd werkstraf → justitieassistent (dagen)", "doorlooptijd_werkstraf_opstart_dagen": "Aanstelling → opstart werkstraf (dagen)",
        "daders_in_begeleiding": "Daders in begeleiding justitiehuizen", "wachtenden_pab_vaph_incl_prior": "Wachtenden PAB (VAPH-telling incl. prior)", "nieuwe_vragen_pab": "Nieuwe PAB-vragen", "toekenningen_pab": "Toegekende PAB's", "budgethouders_pab": "PAB-budgethouders",
        "wachttijd_cgg_forensisch_dagen": "Wachttijd CGG forensische zorg (dagen)", "wachttijd_cgg_gevangenis_dagen": "Wachttijd CGG hulp in gevangenis (dagen)", "forensische_zorgperiodes_actief": "Actieve forensische zorgperiodes (CGG)",
        "wachttijd_cgg_verslavingsteams_dagen": "Wachttijd CGG-verslavingsteams (dagen)", "twe_ocmw_trajecten_tijdig_werk": "TWE-OCMW-trajecten met tijdig werk (art. 60)", "wijkwerkers_actief": "Actieve wijk-werkers",
        "gebruikers_rth": "Gebruikers rechtstreeks toegankelijke hulp", "goedkeuringen_hulpmiddelen": "Goedkeuringen hulpmiddelen en aanpassingen", "mediaan_doorlooptijd_hulpmiddelen_sda_dagen": "Mediaan doorlooptijd hulpmiddelen SDA (dagen)",
        "caw_bereikte_clienten_totaal": "CAW bereikte cliënten (totaal)", "caw_bereikte_clienten_begeleiding": "CAW cliënten in begeleiding", "vaph_ondersteund_in_gevangenis": "VAPH-ondersteuning in de gevangenis (personen)",
        "caw_gedetineerden_onthaal": "Gedetineerden onthaald door CAW", "caw_gedetineerden_begeleiding": "Gedetineerden in begeleiding CAW",
    }
    PALET = [SERIES["pg1"], SERIES["pg2"], SERIES["pg3"], "#eda100", "#e87ba4", "#008300", SERIES["totaal"], "#e34948"]
    REEKS_KLEUR = {
        "wachtenden_vragen_pg1": PALET[0], "wachtenden_vragen_pg2": PALET[1], "wachtenden_vragen_pg3": PALET[2], "wachtenden_vragen_totaal": PALET[6],
        "wachtenden_kandidaten": PALET[0], "wachtenden_actieve_inschrijvingen": PALET[1],
        "wachtenden_nrtj": PALET[0], "wachtenden_nrtj_zonder_hulp": PALET[1], "wachtenden_pab": PALET[2], "wachtenden_nrtj_sector_jho": PALET[3], "wachtenden_nrtj_sector_vaph": PALET[4],
        "opvangvragen_lokale_loketten": PALET[0], "onbeantwoorde_opvangvragen": PALET[1], "onvervulde_behoefte_kinderen": PALET[2],
        "wachtenden_geen_passend_aanbod": PALET[0], "wachtenden_6_maanden": PALET[1],
        "wachttijd_ftf1_0_17_dagen": PALET[0], "wachttijd_ftf1_18_59_dagen": PALET[1], "wachttijd_ftf1_60plus_dagen": PALET[2],
        "wachttijd_ftf1_18_64_dagen": PALET[3], "wachttijd_ftf1_65plus_dagen": PALET[4],
        "wachtenden_advies_cmw": PALET[0], "contingent_open_vte": PALET[1], "contingent_toegekend_vte": PALET[2], "contingent_ingevuld_vte": PALET[3], "werknemers_cmw": PALET[4],
        "kalender_nog_te_realiseren_wzc": PALET[0], "kalender_uitgesteld_wzc_cum": PALET[1], "kalender_gerealiseerd_wzc_cum": PALET[2], "kalender_vervallen_wzc_cum": PALET[7],
        "kalender_uitstel_gevraagd_wzc": PALET[3],
        "leerlingen_buo": PALET[0], "verkochte_sociale_koopwoningen_nieuw": PALET[0],
        "uren_gezinszorg_gepresteerd": PALET[0], "gebruikers_gezinszorg": PALET[1], "urencontingent_toegekend": PALET[2],
        "wachttijd_antwerpen_maanden": PALET[0], "wachttijd_brussel_maanden": PALET[1], "wachttijd_gent_maanden": PALET[2], "wachttijd_leuven_maanden": PALET[3],
        "wachtenden_pleeggezin": PALET[0], "wachttijd_werkstraf_aanstelling_dagen": PALET[0], "doorlooptijd_werkstraf_opstart_dagen": PALET[1], "daders_in_begeleiding": PALET[2],
        "wachtenden_pab_vaph_incl_prior": PALET[1], "nieuwe_vragen_pab": PALET[2], "toekenningen_pab": PALET[3], "budgethouders_pab": PALET[4],
        "wachttijd_cgg_forensisch_dagen": PALET[0], "wachttijd_cgg_gevangenis_dagen": PALET[1], "forensische_zorgperiodes_actief": PALET[2],
        "wachttijd_cgg_verslavingsteams_dagen": PALET[0], "twe_ocmw_trajecten_tijdig_werk": PALET[0], "wijkwerkers_actief": PALET[1],
        "gebruikers_rth": PALET[0], "goedkeuringen_hulpmiddelen": PALET[1], "mediaan_doorlooptijd_hulpmiddelen_sda_dagen": PALET[2],
        "caw_bereikte_clienten_totaal": PALET[1], "caw_bereikte_clienten_begeleiding": PALET[2], "vaph_ondersteund_in_gevangenis": PALET[3],
        "caw_gedetineerden_onthaal": PALET[4], "caw_gedetineerden_begeleiding": PALET[5],
    }
    reeks = b[b["metriek"].isin(list(REEKS_LABELS))]
    if len(reeks):
        fig = go.Figure()
        for m in [k for k in REEKS_LABELS if k in set(reeks["metriek"])]:
            naam, kleur = REEKS_LABELS[m], REEKS_KLEUR[m]
            r = reeks[reeks["metriek"] == m]
            # Ongecontroleerde/betwiste punten: open marker, zodat status nooit alleen via kleur verschilt.
            symbolen = ["circle" if s in ("gecontroleerd", "bron_gelezen") else "circle-open" for s in r["controlestatus"]]
            fig.add_trace(go.Scatter(
                x=r["peildatum"], y=r["waarde"], mode="lines+markers", name=naam,
                line=dict(color=kleur, width=2), marker=dict(size=9, symbol=symbolen, line=dict(width=2, color=kleur)),
                customdata=list(zip(r["controlestatus"].map(STATUS_LABEL), r["documenttitel"], r["pagina"])),
                hovertemplate="%{x|%d-%m-%Y}: <b>%{y:,.0f}</b><br>%{customdata[0]}<br>%{customdata[1]} (%{customdata[2]})<extra>" + naam + "</extra>",
            ))
        fig.update_layout(
            title="Reeks per peildatum — open markers = ongecontroleerd of betwist; let op definitiewissels (zie opmerking)",
            plot_bgcolor=INK["surface"], paper_bgcolor=INK["surface"], font=dict(color=INK["primary"], family="system-ui, Segoe UI, sans-serif"),
            legend=dict(orientation="h", y=-0.2), margin=dict(l=40, r=20, t=60, b=40), hovermode="x unified", height=440,
        )
        fig.update_xaxes(showgrid=False, linecolor=INK["grid"], tickfont=dict(color=INK["muted"]))
        fig.update_yaxes(gridcolor=INK["grid"], zeroline=False, tickfont=dict(color=INK["muted"]), rangemode="tozero", separatethousands=True)
        st.plotly_chart(fig, width="stretch")

    wacht = b[b["metriek"].str.startswith("wachttijd_eerstvolgende")].copy()
    if len(wacht):
        wacht["jaren"] = (wacht["waarde"] / 365.25).round(1)
        piv = wacht.pivot_table(index="peildatum", columns="metriek", values="jaren").rename(
            columns=lambda c: c.replace("wachttijd_eerstvolgende_", "").replace("_dagen", " (jaar)"))
        st.markdown("**Wachttijd van de eerstvolgende wachtende** (peildatum − prioriteringsdatum, in jaren)")
        st.dataframe(piv, width="stretch")

    st.markdown("**Alle bevindingen met herkomst**")
    toon = b[["metriek", "waarde", "eenheid", "peildatum", "controlestatus", "documenttitel", "pagina", "passage", "definitie", "bron_url", "gecontroleerd_door", "opmerking"]]
    st.dataframe(
        toon, width="stretch", hide_index=True, height=420,
        column_config={"bron_url": st.column_config.LinkColumn("bron"), "peildatum": st.column_config.DateColumn(format="DD-MM-YYYY"),
                       "waarde": st.column_config.NumberColumn(format="localized")},
    )

# ------------------------------------------------------------------------------------------ Budget
with tab_budget:
    st.markdown(
        "Budgetten per voorziening en jaar. **Niveau** zegt waar het bedrag vandaan komt (begrotingsartikel, eigen begroting van het agentschap, "
        "uitbreidingsbeleid of realisatie); **fase** of het om opmaak (BO), aanpassing (BA), uitvoering (UITV), agentschapsverslag of beleidsuitspraak gaat; "
        "**kredietsoort** VAK (vastleggen) of VEK (vereffenen). Vergelijk nooit bedragen over niveaus heen zonder deze kolommen te lezen."
    )
    if len(bud):
        keuze_b = st.selectbox("Voorziening ", sorted(bud["voorziening_id"].unique()), format_func=lambda i: voorz.set_index("voorziening_id").loc[i, "naam"])
        bb = bud[bud["voorziening_id"] == keuze_b].sort_values(["begrotingsjaar", "niveau"])
        groei = bb[bb["niveau"] == "uitbreidingsbeleid"]
        if len(groei):
            fig2 = go.Figure(go.Bar(
                x=groei["begrotingsjaar"].astype(int).astype(str), y=groei["bedrag_eur"] / 1e6, marker_color=SERIES["pg1"],
                marker_line_width=0, text=[f"{x:,.1f}" for x in groei["bedrag_eur"] / 1e6], textposition="outside",
                customdata=list(zip(groei["controlestatus"].map(STATUS_LABEL), groei["documenttitel"])),
                hovertemplate="%{x}: <b>%{y:,.1f} mln €</b><br>%{customdata[0]}<br>%{customdata[1]}<extra></extra>",
            ))
            fig2.update_layout(title="Uitbreidingsbeleid per jaar (mln €) — jaarlijkse groei-enveloppe, geen totaalbudget",
                               plot_bgcolor=INK["surface"], paper_bgcolor=INK["surface"], font=dict(color=INK["primary"]), bargap=0.35,
                               margin=dict(l=40, r=20, t=60, b=40), height=380, showlegend=False)
            fig2.update_yaxes(gridcolor=INK["grid"], zeroline=False, tickfont=dict(color=INK["muted"]))
            fig2.update_xaxes(showgrid=False, tickfont=dict(color=INK["muted"]))
            st.plotly_chart(fig2, width="stretch")
        st.dataframe(
            bb[["begrotingsjaar", "fase", "niveau", "kredietsoort", "artikel_code", "ise", "label", "bedrag_eur", "controlestatus", "documenttitel", "pagina", "passage", "bron_url", "opmerking"]],
            width="stretch", hide_index=True, height=480,
            column_config={"bedrag_eur": st.column_config.NumberColumn("bedrag (€)", format="%d"), "bron_url": st.column_config.LinkColumn("bron"),
                           "begrotingsjaar": st.column_config.NumberColumn(format="%d")},
        )
    else:
        st.info("Nog geen budgetten gepubliceerd.")

    # ---- Fase 3: kredieten uit de BBT's per ISE (geparsed uit de PDF's, k€)
    st.markdown("---")
    st.markdown("**Kredieten per ISE uit de Beleids- en Begrotingstoelichtingen (BBT)** — duizend euro, geparsed uit de PDF's; "
                "kolom = kolomkop in het document (BO = opmaak, BA = aanpassing, Uitvoering = rekening).")
    kred = D["kredieten"]
    if len(kred) and len(bud):
        ise_k = voorz.set_index("voorziening_id").loc[keuze_b, "ise_koppeling"] if "ise_koppeling" in voorz.columns else ""
        kk = kred[kred["ise"].str.upper().str.contains(ise_k.upper(), regex=False)] if ise_k else kred.iloc[0:0]
        if ise_k and len(kk):
            # Som van de uitgavenartikelen op departementsniveau (code ..0-1....) per kolom: robuuster dan de
            # 'Totaal'-regel van de synthesetabel, die in oudere/afwijkend opgemaakte BBT's soms verkeerd gelezen wordt.
            art = kk[kk["artikel_code"].str.match(r"^[A-Z]{2}0-1") & kk["kolom"].str.match(r"^(BO|BA|Uitvoering|Realisatie)\s*\d{4}", case=False)].copy()
            # Eerst per document sommeren (een kolom als 'BA 2024' staat in twee stukken: opmaak 2025 én uitvoering 2024),
            # daarna één waarde per kolom houden — anders worden BA-bedragen dubbel geteld.
            per_doc = art.groupby(["pfile_id", "stuk", "kolom", "kredietsoort"], as_index=False).agg(
                bedrag_keur=("bedrag_keur", "sum"), pagina=("pagina", "first"), controlestatus=("controlestatus", "first"))
            tot = per_doc.sort_values("stuk").drop_duplicates(["kolom", "kredietsoort"], keep="first")
            tot["kolomjaar"] = tot["kolom"].str.extract(r"(\d{4})").astype(int)
            tot["kolomtype"] = tot["kolom"].str.extract(r"^(\w+)")[0].str.upper()
            # Per begrotingsjaar één waarde: BO uit de BBT van dat jaar; BA/uitvoering uit het document van het jaar zelf of erna.
            fig3 = go.Figure()
            for i, (kt, kleur) in enumerate((("BO", SERIES["pg1"]), ("BA", SERIES["pg2"]), ("UITVOERING", SERIES["pg3"]))):
                for ks, dash in (("VAK", "solid"), ("VEK", "dot")):
                    r = tot[(tot["kolomtype"] == kt) & (tot["kredietsoort"] == ks)].sort_values("kolomjaar").drop_duplicates("kolomjaar", keep="last")
                    if not len(r):
                        continue
                    fig3.add_trace(go.Scatter(x=r["kolomjaar"], y=r["bedrag_keur"] / 1000, mode="lines+markers", name=f"{kt} {ks}",
                                              line=dict(color=kleur, width=2, dash=dash), marker=dict(size=8),
                                              customdata=list(zip(r["stuk"], r["pagina"], r["controlestatus"].map(STATUS_LABEL))),
                                              hovertemplate="%{x}: <b>%{y:,.1f} mln €</b><br>%{customdata[0]} p. %{customdata[1]}<br>%{customdata[2]}<extra>" + f"{kt} {ks}" + "</extra>"))
            fig3.update_layout(title=f"ISE '{ise_k}' — som uitgavenartikelen departement per begrotingsjaar (mln €), VAK doorgetrokken / VEK gestippeld",
                               plot_bgcolor=INK["surface"], paper_bgcolor=INK["surface"], font=dict(color=INK["primary"]),
                               legend=dict(orientation="h", y=-0.2), margin=dict(l=40, r=20, t=60, b=40), height=400, hovermode="x unified")
            fig3.update_yaxes(gridcolor=INK["grid"], zeroline=False, tickfont=dict(color=INK["muted"]), rangemode="tozero")
            fig3.update_xaxes(showgrid=False, tickfont=dict(color=INK["muted"]), dtick=1)
            st.plotly_chart(fig3, width="stretch")
            st.dataframe(kk[["begrotingsjaar", "fase", "stuk", "beleidsveld", "ise", "artikel_code", "label", "kolom", "kredietsoort", "bedrag_keur", "pagina", "controlestatus", "bron_url"]]
                         .sort_values(["begrotingsjaar", "artikel_code", "kolom", "kredietsoort"]),
                         width="stretch", hide_index=True, height=420,
                         column_config={"bedrag_keur": st.column_config.NumberColumn("bedrag (k€)", format="%d"), "bron_url": st.column_config.LinkColumn("bron"),
                                        "begrotingsjaar": st.column_config.NumberColumn(format="%d")})
        else:
            st.info("Geen ISE-koppeling of geen geparste kredieten voor deze voorziening.")
    else:
        st.info("Nog geen BBT-kredieten gepubliceerd. Draai lokaal: `wachtlijst harvest bbt-download`, `wachtlijst harvest bbt-parse`, "
                "`wachtlijst promote-kredieten --door <initialen>`, `wachtlijst publish` (zie docs/06-harvesters-lokaal.md).")

# ------------------------------------------------------------------------------------------ Bronnen
with tab_bronnen:
    st.markdown("Bronnenkaart: publicatiekanalen, type (API / download / HTML / PDF / dashboard) en hoe ze machinaal te bevragen zijn.")
    st.dataframe(
        bronnen[["naam", "organisatie", "bron_type", "frequentie", "machinaal", "licentie", "url", "opmerking"]],
        width="stretch", hide_index=True, height=640, column_config={"url": st.column_config.LinkColumn("url")},
    )

# ------------------------------------------------------------------------------------------ Methodiek
with tab_methode:
    st.markdown((ROOT / "docs" / "01-afbakening.md").read_text(encoding="utf-8") if (ROOT / "docs" / "01-afbakening.md").exists() else "Zie docs/.")
    m1, m2 = st.columns(2)
    m1.markdown("**Voorzieningen per wachtlijsttype en bevoegdheid**")
    m1.dataframe(pd.crosstab(voorz["wachtlijst_type"], voorz["bevoegdheid"], margins=True, margins_name="totaal"), width="stretch")
    m2.markdown("**Stand van het onderzoek (`scan_status`)**")
    m2.dataframe(pd.crosstab(voorz["scan_status"], voorz["bevoegdheid"], margins=True, margins_name="totaal"), width="stretch")
    verdeling = meta.get("controlestatus_verdeling", {})
    if verdeling:
        st.markdown("**Controlestatus van de gepubliceerde cijfers**")
        st.dataframe(pd.DataFrame(verdeling).fillna(0).astype(int).rename(index=STATUS_LABEL), width="stretch")
