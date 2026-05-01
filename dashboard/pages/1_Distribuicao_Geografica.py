import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
from config import (
    REGIOES, UF_REGIAO,
    CORES, COR_NE, COR_OUTR,
    MAPA_SITUACAO, LAYOUT_BASE, FONTE_DADOS, SUBTITULO_STYLE,
)

DATA_PATH = Path(__file__).parent.parent / "dataset_final.parquet"

st.set_page_config(page_title="Distribuição Geográfica", layout="wide")


@st.cache_data
def carregar_dados() -> pd.DataFrame:
    df = pd.read_parquet(DATA_PATH)
    df = df[df["uf"] != "EX"]
    df["regiao"] = df["uf"].map(UF_REGIAO)
    df["situacao_nome"] = df["situacao_cadastral"].map(MAPA_SITUACAO).fillna(df["situacao_cadastral"])
    return df


df = carregar_dados()

st.title("Distribuição Geográfica")
st.markdown(
    f'<p style="{SUBTITULO_STYLE}">'
    'Mapeamento das empresas de software por estado e região brasileira. '
    'O Nordeste concentra ~8% do total apesar de 28% da população — '
    'com forte hiperprimazia das capitais estaduais.'
    '</p>',
    unsafe_allow_html=True,
)

with st.expander("Filtros", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        opts_sit = sorted(df["situacao_nome"].dropna().unique().tolist())
        sit_sel = st.multiselect("Situação cadastral", opts_sit, default=["Ativa"])
    with c2:
        reg_sel = st.multiselect("Regiões", list(REGIOES.keys()), default=list(REGIOES.keys()))

ufs_sel = [uf for r in reg_sel for uf in REGIOES[r]]
df_f = df[df["situacao_nome"].isin(sit_sel) & df["uf"].isin(ufs_sel)]

if df_f.empty:
    st.warning("Nenhum dado para os filtros selecionados.")
    st.stop()

st.markdown("---")

# ── Gráfico 1: Empresas por UF ──────────────────────────────────────────────
por_uf = df_f.groupby("uf").size().reset_index(name="total").sort_values("total")
por_uf["cor"] = por_uf["uf"].apply(lambda u: COR_NE if UF_REGIAO.get(u) == "Nordeste" else COR_OUTR)
por_uf["regiao"] = por_uf["uf"].map(UF_REGIAO)

fig1 = px.bar(
    por_uf, x="total", y="uf", orientation="h",
    title="Distribuição de empresas de software por estado",
    color="cor", color_discrete_map="identity",
    hover_data={"regiao": True, "cor": False},
    labels={"total": "Nº de empresas", "uf": "Estado", "regiao": "Região"},
)
fig1.update_layout(showlegend=False, height=580, **LAYOUT_BASE)
fig1.update_xaxes(tickformat="~s")
st.plotly_chart(fig1, use_container_width=True)
st.caption(FONTE_DADOS)

sp_total = int(df_f[df_f["uf"] == "SP"].shape[0]) if "Sudeste" in reg_sel else 0
ne_total = int(df_f[df_f["regiao"] == "Nordeste"].shape[0]) if "Nordeste" in reg_sel else 0
if sp_total > 0 and ne_total > 0:
    ratio = round(sp_total / ne_total, 1)
    st.markdown(
        f'<div style="border-left:4px solid #2563eb; background:#eff6ff;'
        f' padding:14px 18px; border-radius:6px; margin:8px 0;">'
        f'<span style="font-weight:700; color:#1a1a2e;">Perspectiva: </span>'
        f'<span style="color:#374151;">São Paulo sozinho (<strong>{sp_total:,}</strong> empresas)'
        f' equivale a <strong>{ratio}×</strong> o volume de todo o Nordeste'
        f' (<strong>{ne_total:,}</strong>). A concentração paulista supera'
        f' a soma das 9 UFs nordestinas.</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

st.markdown("---")
col_pie, col_cap = st.columns(2)

# ── Gráfico 2: Pizza por região ──────────────────────────────────────────────
with col_pie:
    por_reg = df_f.groupby("regiao").size().reset_index(name="total")
    fig2 = px.pie(
        por_reg, names="regiao", values="total",
        title="Participação regional no ecossistema de software",
        color="regiao", color_discrete_map=CORES,
        hole=0.35,
    )
    fig2.update_traces(textposition="outside", textinfo="percent+label")
    fig2.update_layout(
        paper_bgcolor="white",
        font=dict(size=13, color="#1a1a2e"),
        showlegend=True,
        legend=dict(orientation="v", x=1.02, y=0.5),
        margin=dict(l=10, r=120, t=40, b=10),
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.caption(FONTE_DADOS)

# ── Gráfico 3: Concentração no maior município por UF ───────────────────────
with col_cap:
    tot_uf = df_f.groupby("uf").size().rename("total_uf")
    maior = (
        df_f.groupby(["uf", "municipio"]).size().reset_index(name="n")
        .sort_values("n", ascending=False).drop_duplicates("uf")
        .set_index("uf")["n"].rename("n_capital")
    )
    conc = pd.concat([tot_uf, maior], axis=1).dropna().reset_index()
    conc["pct"] = (conc["n_capital"] / conc["total_uf"] * 100).round(1)
    conc = conc.sort_values("pct")
    conc["cor"] = conc["uf"].apply(lambda u: COR_NE if UF_REGIAO.get(u) == "Nordeste" else COR_OUTR)

    fig3 = px.bar(
        conc, x="pct", y="uf", orientation="h",
        title="Concentração no principal município (% do total estadual)",
        color="cor", color_discrete_map="identity",
        labels={"pct": "% no maior município", "uf": "Estado"},
    )
    fig3.update_layout(showlegend=False, **LAYOUT_BASE)
    st.plotly_chart(fig3, use_container_width=True)
    st.caption(FONTE_DADOS)

ne_ufs_present  = [u for u in REGIOES.get("Nordeste", []) if u in conc["uf"].values]
sul_ufs_present = [u for u in REGIOES.get("Sul",      []) if u in conc["uf"].values]
ne_conc_avg  = round(conc[conc["uf"].isin(ne_ufs_present)]["pct"].mean(),  1) if ne_ufs_present  else None
sul_conc_avg = round(conc[conc["uf"].isin(sul_ufs_present)]["pct"].mean(), 1) if sul_ufs_present else None

if ne_conc_avg and sul_conc_avg:
    se_row = conc[conc["uf"] == "SE"]
    ce_row = conc[conc["uf"] == "CE"]
    se_pct = f"{se_row['pct'].values[0]:.1f}%" if len(se_row) > 0 else "—"
    ce_pct = f"{ce_row['pct'].values[0]:.1f}%" if len(ce_row) > 0 else "—"
    st.markdown(
        f'<div style="border-left:4px solid #e05c2b; background:#fff8f5;'
        f' padding:16px 20px; border-radius:6px; margin-top:8px;">'
        f'<span style="font-weight:700; color:#1a1a2e;">Insight: </span>'
        f'<span style="color:#374151;">Estados nordestinos concentram em média <strong>{ne_conc_avg}%</strong>'
        f' das empresas no maior município, contra <strong>{sul_conc_avg}%</strong> no Sul —'
        f' Aracaju/SE ({se_pct}) e Fortaleza/CE ({ce_pct}) lideram a concentração.'
        f' Isso indica ausência de ecossistema de software fora das capitais.</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

st.markdown(
    '<div style="border-left:4px solid #94a3b8; background:#f8fafc;'
    ' padding:14px 18px; border-radius:6px; margin-top:8px;">'
    '<span style="font-weight:700; color:#1a1a2e;">Implicação: </span>'
    '<span style="color:#374151;">A hiperprimazia das capitais nordestinas cria um ecossistema frágil:'
    ' sem cidades secundárias com massa crítica de empresas, qualquer crise no polo central'
    ' compromete o setor inteiro. Contraste com o interior paulista e gaúcho, onde a distribuição'
    ' é mais equilibrada.</span>'
    '</div>',
    unsafe_allow_html=True,
)
