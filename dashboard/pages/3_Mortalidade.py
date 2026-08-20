import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config import (
    REGIOES, UF_REGIAO,
    CORES, MAPA_CNAE, COORTES,
    LAYOUT_BASE, FONTE_DADOS, SUBTITULO_STYLE,
    carregar_dados_otimizado,
)

st.set_page_config(page_title="Mortalidade Empresarial", layout="wide")


@st.cache_data(max_entries=1, show_spinner=False)
def carregar_dados() -> pd.DataFrame:
    colunas = [
        "uf", "situacao_cadastral", "cnae_fiscal_principal",
        "data_inicio_atividade", "data_situacao_cadastral"
    ]
    df = carregar_dados_otimizado(colunas)
    df = df[df["uf"] != "EX"]
    df["regiao"] = df["uf"].map(UF_REGIAO)
    df["ano_abertura"] = pd.to_numeric(
        df["data_inicio_atividade"].astype(str).str[:4], errors="coerce", downcast="unsigned"
    )
    df["cnae_label"] = df["cnae_fiscal_principal"].map(MAPA_CNAE).fillna("Outros")
    df["data_inicio_atividade"] = pd.to_datetime(
        df["data_inicio_atividade"], format="%Y%m%d", errors="coerce"
    )
    df["data_situacao_cadastral"] = pd.to_datetime(
        df["data_situacao_cadastral"], format="%Y%m%d", errors="coerce"
    )
    return df


df = carregar_dados()

st.title("Mortalidade Empresarial")
st.markdown(
    f''
    'Análise de sobrevivência por corte de abertura e mortalidade por segmento de atuação. '
    'O Nordeste apresenta paradoxo: melhor taxa de sobrevivência que o Sudeste, '
    'mas cria muito menos empresas — o gargalo é de volume, não de resiliência.'
    '',
    unsafe_allow_html=True,
)

with st.expander("Filtros", expanded=True):
    reg_sel = st.multiselect("Regiões", list(REGIOES.keys()),
                             default=["Nordeste", "Sudeste", "Sul"])

ufs_sel = [uf for r in reg_sel for uf in REGIOES[r]]
df_f = df[df["uf"].isin(ufs_sel)]

if df_f.empty:
    st.warning("Nenhum dado para os filtros selecionados.")
    st.stop()

st.markdown("---")
st.subheader("Sobrevivência por corte de abertura", anchor=False)

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
    title="Taxa de sobrevivência por corte de abertura",
    xaxis_title="Corte (ano de abertura)", yaxis_title="% ainda ativas",
    height=400, hovermode="x unified",
    legend=dict(bgcolor="rgba(255,255,255,0.9)", bordercolor="#e5e7eb", borderwidth=1),
    **LAYOUT_BASE,
)
st.plotly_chart(fig_surv, use_container_width=True)
st.caption(FONTE_DADOS)

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
            surv_rows.append({"corte": c, "ne": ne_s, "se": se_s, "diff": round(ne_s - se_s, 1)})
    if surv_rows:
        best = max(surv_rows, key=lambda x: x["diff"])
        ne_vol_2008 = len(ne_r[ne_r["ano_abertura"] == 2008])
        se_vol_2008 = len(se_r[se_r["ano_abertura"] == 2008])
        sinal = "+" if best["diff"] >= 0 else ""
        st.markdown(
            f''
            f'Paradoxo da sobrevivência: '
            f'No corte de {best["corte"]}, o Nordeste'
            f' tem taxa de sobrevivência de {best["ne"]}% vs {best["se"]}%'
            f' no Sudeste ({sinal}{best["diff"]} pp de vantagem). Porém, o Sudeste abriu'
            f' {se_vol_2008 // max(ne_vol_2008, 1)}× mais empresas nesse corte.'
            f' O problema nordestino é de volume de criação, não de resiliência.'
            f'',
            unsafe_allow_html=True,
        )

st.markdown("---")
col_vida, col_cnae = st.columns(2)

with col_vida:
    st.subheader("Tempo mediano de vida — baixadas", anchor=False)
    df_bx = df_f[df_f["situacao_cadastral"] == "08"].copy()
    df_bx = df_bx.dropna(subset=["data_inicio_atividade", "data_situacao_cadastral"])
    df_bx["vida_anos"] = (df_bx["data_situacao_cadastral"] - df_bx["data_inicio_atividade"]).dt.days / 365.25
    df_bx = df_bx[df_bx["vida_anos"] > 0]
    med = (df_bx.groupby("regiao", observed=True)["vida_anos"].median()
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
    st.caption(FONTE_DADOS)

with col_cnae:
    st.subheader("Taxa de mortalidade por CNAE", anchor=False)
    mort = (
        df_f.groupby("cnae_label", observed=True)
        .apply(lambda g: (g["situacao_cadastral"] == "08").sum() / len(g) * 100,
               include_groups=False)
        .reset_index(name="pct").sort_values("pct")
    )
    fig_c = px.bar(mort, x="pct", y="cnae_label", orientation="h",
                   color_discrete_sequence=["#dc2626"],
                   labels={"pct": "% baixadas", "cnae_label": "Segmento"},
                   text="pct")
    fig_c.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_c.update_layout(**LAYOUT_BASE)
    fig_c.update_xaxes(range=[0, mort["pct"].max() * 1.2])
    st.plotly_chart(fig_c, use_container_width=True)
    st.caption(FONTE_DADOS)

if not med.empty:
    ne_med_row = med[med["regiao"] == "Nordeste"]
    se_med_row = med[med["regiao"] == "Sudeste"]
    if len(ne_med_row) > 0 and len(se_med_row) > 0:
        ne_med = float(ne_med_row["mediana"].values[0])
        se_med = float(se_med_row["mediana"].values[0])
        st.markdown(
            f''
            f'Insight: '
            f'O Nordeste tem tempo mediano de vida de'
            f' {ne_med:.1f} anos para empresas baixadas, contra'
            f' {se_med:.1f} anos no Sudeste. Mas sua taxa de sobrevivência'
            f' por corte é superior ao Sudeste — o problema é de volume,'
            f' não de resiliência.'
            f'',
            unsafe_allow_html=True,
        )

if not mort.empty:
    worst_cnae = mort.iloc[-1]
    best_cnae  = mort.iloc[0]
    st.markdown(
        f''
        f'Risco por segmento: '
        f'{worst_cnae["cnae_label"]} é o segmento de'
        f' maior mortalidade ({worst_cnae["pct"]:.1f}% de empresas baixadas), enquanto'
        f' {best_cnae["cnae_label"]} é o mais resiliente ({best_cnae["pct"]:.1f}%).'
        f' Segmentos com baixa barreira de entrada tendem a ter maior rotatividade.'
        f'',
        unsafe_allow_html=True,
    )
