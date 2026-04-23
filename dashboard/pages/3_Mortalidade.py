import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Mortalidade Empresarial", layout="wide")

DATASET_PATH = "D:/Análise_Empresas_Software/dataset_final.csv"

REGIOES = {
    "Norte":       ["AM", "RR", "AP", "PA", "TO", "RO", "AC"],
    "Nordeste":    ["MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA"],
    "Centro-Oeste":["MT", "MS", "GO", "DF"],
    "Sudeste":     ["SP", "RJ", "MG", "ES"],
    "Sul":         ["PR", "SC", "RS"],
}
UF_REGIAO = {uf: reg for reg, ufs in REGIOES.items() for uf in ufs}

CORES = {
    "Nordeste":     "#e05c2b",
    "Sudeste":      "#2563eb",
    "Sul":          "#16a34a",
    "Norte":        "#7c3aed",
    "Centro-Oeste": "#ca8a04",
}

MAPA_CNAE = {
    "6201500": "Desenv. sob encomenda", "6201501": "Desenv. sob encomenda",
    "6202300": "Software customizável",  "6203100": "Software não-customizável",
    "6204000": "Consultoria em TI",      "6209100": "Suporte técnico/TI",
    "6201502": "Web design",
}

COLUNAS = ["uf", "situacao_cadastral", "data_inicio_atividade",
           "data_situacao_cadastral", "cnae_fiscal_principal"]

COORTES = [2008, 2010, 2012, 2015, 2018, 2020, 2022]

LAYOUT_BASE = dict(
    plot_bgcolor="white", paper_bgcolor="white", font_color="#1a1a2e",
    xaxis=dict(gridcolor="#e5e7eb", linecolor="#e5e7eb"),
    yaxis=dict(gridcolor="#e5e7eb", linecolor="#e5e7eb"),
    hoverlabel=dict(font_size=15, bgcolor="white", bordercolor="#e5e7eb"),
)


@st.cache_data
def carregar_dados() -> pd.DataFrame:
    df = pd.read_csv(DATASET_PATH, usecols=COLUNAS, dtype=str)
    df = df[df["uf"] != "EX"]
    df["regiao"] = df["uf"].map(UF_REGIAO)
    df["ano_abertura"] = pd.to_numeric(
        df["data_inicio_atividade"].str[:4], errors="coerce"
    ).astype("Int64")
    df["cnae_label"] = df["cnae_fiscal_principal"].map(MAPA_CNAE).fillna("Outros")
    df["data_inicio_atividade"] = pd.to_datetime(
        df["data_inicio_atividade"], format="%Y%m%d", errors="coerce"
    )
    df["data_situacao_cadastral"] = pd.to_datetime(
        df["data_situacao_cadastral"], format="%Y%m%d", errors="coerce"
    )
    return df


df = carregar_dados()

st.title("💀 Mortalidade Empresarial")

with st.expander("🔧 Filtros", expanded=True):
    reg_sel = st.multiselect("Regiões", list(REGIOES.keys()),
                             default=["Nordeste", "Sudeste", "Sul"])

ufs_sel = [uf for r in reg_sel for uf in REGIOES[r]]
df_f = df[df["uf"].isin(ufs_sel)]

if df_f.empty:
    st.warning("Nenhum dado para os filtros selecionados.")
    st.stop()

st.markdown("---")

# ── Gráfico 1: Sobrevivência por coorte ─────────────────────────────────────
st.subheader("Sobrevivência por coorte de abertura")

fig_surv = go.Figure()
for regiao in reg_sel:
    df_r = df_f[df_f["regiao"] == regiao]
    xs, ys = [], []
    for c in COORTES:
        sub = df_r[df_r["ano_abertura"] == c]
        if len(sub) == 0:
            continue
        xs.append(c)
        ys.append(round((sub["situacao_cadastral"] == "02").sum() / len(sub) * 100, 1))
    ne = regiao == "Nordeste"
    fig_surv.add_trace(go.Scatter(
        x=xs, y=ys, name=regiao, mode="lines+markers",
        line=dict(color=CORES.get(regiao, "#94a3b8"), width=3 if ne else 2),
        marker=dict(size=8 if ne else 6),
    ))

fig_surv.update_layout(
    xaxis_title="Coorte (ano de abertura)", yaxis_title="% ainda ativas",
    height=380, hovermode="x unified",
    legend=dict(bgcolor="rgba(255,255,255,0.9)", bordercolor="#e5e7eb", borderwidth=1),
    **LAYOUT_BASE,
)
st.plotly_chart(fig_surv, use_container_width=True)

if "Nordeste" in reg_sel and "Sudeste" in reg_sel:
    ne_r = df_f[df_f["regiao"] == "Nordeste"]
    se_r = df_f[df_f["regiao"] == "Sudeste"]
    surv_rows = []
    for c in COORTES:
        ne_c = ne_r[ne_r["ano_abertura"] == c]
        se_c = se_r[se_r["ano_abertura"] == c]
        if len(ne_c) > 50 and len(se_c) > 50:
            ne_s = round((ne_c["situacao_cadastral"] == "02").sum() / len(ne_c) * 100, 1)
            se_s = round((se_c["situacao_cadastral"] == "02").sum() / len(se_c) * 100, 1)
            surv_rows.append({"coorte": c, "ne": ne_s, "se": se_s, "diff": round(ne_s - se_s, 1)})
    if surv_rows:
        best = max(surv_rows, key=lambda x: x["diff"])
        ne_vol_2008 = len(ne_r[ne_r["ano_abertura"] == 2008])
        se_vol_2008 = len(se_r[se_r["ano_abertura"] == 2008])
        sinal = "+" if best["diff"] >= 0 else ""
        st.markdown(
            f'<div style="border-left:4px solid #16a34a; background:#f0fdf4;'
            f' padding:14px 18px; border-radius:6px; margin:8px 0;">'
            f'<span style="font-weight:700; color:#1a1a2e;">Paradoxo da sobrevivência: </span>'
            f'<span style="color:#374151;">Na coorte de <strong>{best["coorte"]}</strong>, o Nordeste'
            f' tem taxa de sobrevivência de <strong>{best["ne"]}%</strong> vs <strong>{best["se"]}%</strong>'
            f' no Sudeste ({sinal}{best["diff"]} pp de vantagem). Porém, o Sudeste abriu'
            f' <strong>{se_vol_2008 // max(ne_vol_2008, 1)}×</strong> mais empresas nessa coorte.'
            f' O problema nordestino é de <em>volume de criação</em>, não de resiliência.</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown("---")
col_vida, col_cnae = st.columns(2)

# ── Gráfico 2: Tempo mediano de vida ────────────────────────────────────────
with col_vida:
    st.subheader("Tempo mediano de vida — baixadas")
    df_bx = df_f[df_f["situacao_cadastral"] == "08"].copy()
    df_bx = df_bx.dropna(subset=["data_inicio_atividade", "data_situacao_cadastral"])
    df_bx["vida_anos"] = (df_bx["data_situacao_cadastral"] - df_bx["data_inicio_atividade"]).dt.days / 365.25
    df_bx = df_bx[df_bx["vida_anos"] > 0]
    med = (df_bx.groupby("regiao")["vida_anos"].median()
           .reset_index(name="mediana").sort_values("mediana"))
    med["cor"] = med["regiao"].apply(lambda r: CORES.get(r, "#94a3b8"))
    fig_v = px.bar(med, x="mediana", y="regiao", orientation="h",
                   color="cor", color_discrete_map="identity",
                   labels={"mediana": "Mediana (anos)", "regiao": "Região"},
                   text="mediana")
    fig_v.update_traces(texttemplate="%{text:.1f} anos", textposition="outside")
    fig_v.update_layout(showlegend=False, **LAYOUT_BASE)
    fig_v.update_xaxes(range=[0, med["mediana"].max() * 1.25])
    st.plotly_chart(fig_v, use_container_width=True)

# ── Gráfico 3: Mortalidade por CNAE ─────────────────────────────────────────
with col_cnae:
    st.subheader("Taxa de mortalidade por CNAE")
    mort = (
        df_f.groupby("cnae_label")
        .apply(lambda g: (g["situacao_cadastral"] == "08").sum() / len(g) * 100,
               include_groups=False)
        .reset_index(name="pct").sort_values("pct")
    )
    fig_c = px.bar(mort, x="pct", y="cnae_label", orientation="h",
                   color_discrete_sequence=["#dc2626"],
                   labels={"pct": "% baixadas", "cnae_label": "CNAE"},
                   text="pct")
    fig_c.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_c.update_layout(**LAYOUT_BASE)
    fig_c.update_xaxes(range=[0, mort["pct"].max() * 1.2])
    st.plotly_chart(fig_c, use_container_width=True)

st.markdown(
    '<div style="border-left:4px solid #e05c2b; background:#fff8f5;'
    ' padding:16px 20px; border-radius:6px; margin-top:8px;">'
    '<span style="font-weight:700; color:#1a1a2e;">Insight: </span>'
    '<span style="color:#374151;">O Nordeste tem tempo mediano de vida de <strong>4,0 anos</strong>'
    ' para empresas baixadas, contra 5,6 anos no Sudeste. Mas sua taxa de sobrevivência por coorte'
    ' é superior ao Sudeste — o problema é de <em>volume</em>, não de <em>resiliência</em>.</span>'
    '</div>',
    unsafe_allow_html=True,
)

if not mort.empty:
    worst_cnae = mort.iloc[-1]
    best_cnae = mort.iloc[0]
    st.markdown(
        f'<div style="border-left:4px solid #dc2626; background:#fef2f2;'
        f' padding:14px 18px; border-radius:6px; margin-top:8px;">'
        f'<span style="font-weight:700; color:#1a1a2e;">Risco por segmento: </span>'
        f'<span style="color:#374151;"><strong>{worst_cnae["cnae_label"]}</strong> é o segmento de'
        f' maior mortalidade ({worst_cnae["pct"]:.1f}% de empresas baixadas), enquanto'
        f' <strong>{best_cnae["cnae_label"]}</strong> é o mais resiliente ({best_cnae["pct"]:.1f}%).'
        f' Segmentos com baixa barreira de entrada tendem a ter maior rotatividade —'
        f' quem entra sem capital ou diferenciação sai precocemente.</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
