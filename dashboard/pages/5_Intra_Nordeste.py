import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config import (
    DATASET_PATH, NORDESTE_ESTADOS, NOME_ESTADO,
    CORES_NE, LAYOUT_BASE, FONTE_DADOS, SUBTITULO_STYLE,
)

st.set_page_config(page_title="Intra-Nordeste", layout="wide")

COLUNAS = ["uf", "situacao_cadastral", "opcao_simples", "data_inicio_atividade"]


@st.cache_data
def carregar_dados() -> pd.DataFrame:
    df = pd.read_csv(DATASET_PATH, usecols=COLUNAS, dtype=str)
    df = df[df["uf"].isin(NORDESTE_ESTADOS.values())]
    df["ano_abertura"] = pd.to_numeric(
        df["data_inicio_atividade"].str[:4], errors="coerce"
    ).astype("Int64")
    return df.dropna(subset=["ano_abertura"])


df = carregar_dados()
df["estado_nome"] = df["uf"].map(NOME_ESTADO)

st.title("Análise Intra-Nordeste")
st.markdown(
    f'<p style="{SUBTITULO_STYLE}">'
    'Comparativo entre os 9 estados nordestinos em volume de empresas, taxa de atividade '
    'e trajetória de crescimento relativo. Volume e saúde do ecossistema nem sempre coincidem.'
    '</p>',
    unsafe_allow_html=True,
)

with st.expander("Filtros", expanded=True):
    estados_sel = st.multiselect(
        "Estados", list(NORDESTE_ESTADOS.keys()),
        default=list(NORDESTE_ESTADOS.keys()),
    )

ufs_sel = [NORDESTE_ESTADOS[n] for n in estados_sel]
df_f = df[df["uf"].isin(ufs_sel)].copy()

if df_f.empty:
    st.warning("Nenhum dado para os filtros selecionados.")
    st.stop()

st.markdown("---")
st.subheader("Comparativo entre estados nordestinos", anchor=False)

agg = (
    df_f.groupby("estado_nome")
    .agg(total=("uf", "count"),
         ativas=("situacao_cadastral", lambda x: (x == "02").sum()),
         simples=("opcao_simples", lambda x: (x == "S").sum()))
    .reset_index()
)
agg["pct_ativa"]   = (agg["ativas"]  / agg["total"] * 100).round(1)
agg["pct_simples"] = (agg["simples"] / agg["total"] * 100).round(1)

col_n, col_at, col_si = st.columns(3)

with col_n:
    d = agg.sort_values("total")
    d["cor"] = [CORES_NE[i % len(CORES_NE)] for i in range(len(d))]
    fig = px.bar(d, x="total", y="estado_nome", orientation="h",
                 color="cor", color_discrete_map="identity",
                 labels={"total": "Nº de empresas", "estado_nome": ""},
                 text="total", title="Volume de empresas")
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False, **LAYOUT_BASE)
    fig.update_xaxes(range=[0, d["total"].max() * 1.2], tickformat="~s")
    st.plotly_chart(fig, use_container_width=True)
    st.caption(FONTE_DADOS)

with col_at:
    d = agg.sort_values("pct_ativa")
    d["cor"] = [CORES_NE[i % len(CORES_NE)] for i in range(len(d))]
    fig = px.bar(d, x="pct_ativa", y="estado_nome", orientation="h",
                 color="cor", color_discrete_map="identity",
                 labels={"pct_ativa": "% ativas", "estado_nome": ""},
                 text="pct_ativa", title="Taxa de empresas ativas (%)")
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(showlegend=False, **LAYOUT_BASE)
    fig.update_xaxes(range=[0, 100])
    st.plotly_chart(fig, use_container_width=True)
    st.caption(FONTE_DADOS)

with col_si:
    d = agg.sort_values("pct_simples")
    d["cor"] = [CORES_NE[i % len(CORES_NE)] for i in range(len(d))]
    fig = px.bar(d, x="pct_simples", y="estado_nome", orientation="h",
                 color="cor", color_discrete_map="identity",
                 labels={"pct_simples": "% Simples", "estado_nome": ""},
                 text="pct_simples", title="Adesão ao Simples Nacional (%)")
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(showlegend=False, **LAYOUT_BASE)
    fig.update_xaxes(range=[0, 100])
    st.plotly_chart(fig, use_container_width=True)
    st.caption(FONTE_DADOS)

# insight dinâmico — computado do agg atual
if len(agg) >= 2:
    ne_avg_ativa = round(agg["ativas"].sum() / agg["total"].sum() * 100, 1)
    top_ativa    = agg.loc[agg["pct_ativa"].idxmax()]
    bot_ativa    = agg.loc[agg["pct_ativa"].idxmin()]
    top_vol      = agg.loc[agg["total"].idxmax()]
    gap_vol_ativa = round(top_ativa["pct_ativa"] - bot_ativa["pct_ativa"], 1)
    st.markdown(
        f'<div style="border-left:4px solid #16a34a; background:#f0fdf4;'
        f' padding:14px 18px; border-radius:6px; margin:8px 0;">'
        f'<span style="font-weight:700; color:#1a1a2e;">Contraste interno: </span>'
        f'<span style="color:#374151;"><strong>{top_ativa["estado_nome"]}</strong> lidera em'
        f' qualidade de ecossistema (<strong>{top_ativa["pct_ativa"]}%</strong> de ativas),'
        f' enquanto <strong>{bot_ativa["estado_nome"]}</strong> tem a menor taxa'
        f' (<strong>{bot_ativa["pct_ativa"]}%</strong>) — gap de <strong>{gap_vol_ativa} pp</strong>'
        f' dentro de uma mesma região. <strong>{top_vol["estado_nome"]}</strong> lidera em volume'
        f' (média regional: {ne_avg_ativa}%).</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

st.markdown("---")
st.subheader("Crescimento relativo 2015–2024 (base 2015 = 100)", anchor=False)

ano_min_data = int(df_f["ano_abertura"].min())
ano_max_data = int(df_f["ano_abertura"].max())

with st.expander("Período de análise", expanded=True):
    periodo = st.slider("Período", ano_min_data, ano_max_data, (max(ano_min_data, 2015), ano_max_data))

df_p = df_f[(df_f["ano_abertura"] >= periodo[0]) & (df_f["ano_abertura"] <= periodo[1])]
serie = (
    df_p.groupby(["estado_nome", "ano_abertura"]).size()
    .reset_index(name="n").sort_values("ano_abertura")
)

fig_rel = go.Figure()
for i, nome in enumerate(estados_sel):
    dados = serie[serie["estado_nome"] == nome].sort_values("ano_abertura")
    base_rows = dados[dados["ano_abertura"] == periodo[0]]
    if dados.empty or base_rows.empty:
        continue
    base = base_rows["n"].values[0]
    if base == 0:
        continue
    dados = dados.copy()
    dados["indice"] = (dados["n"] / base * 100).round(1)
    fig_rel.add_trace(go.Scatter(
        x=dados["ano_abertura"], y=dados["indice"],
        name=nome, mode="lines+markers",
        line=dict(color=CORES_NE[i % len(CORES_NE)], width=2),
        marker=dict(size=5),
    ))

fig_rel.add_hline(y=100, line_dash="dot", line_color="#9ca3af",
                  annotation_text=f"Base {periodo[0]}", annotation_font_color="#6b7280")
fig_rel.update_layout(
    xaxis_title="Ano", yaxis_title=f"Índice (base {periodo[0]} = 100)",
    height=420, hovermode="x unified",
    legend=dict(bgcolor="rgba(255,255,255,0.9)", bordercolor="#e5e7eb", borderwidth=1),
    **LAYOUT_BASE,
)
st.plotly_chart(fig_rel, use_container_width=True)
st.caption(FONTE_DADOS)

# ── Tabela de crescimento ─────────────────────────────────────────────────────
rows_tab = []
for nome in estados_sel:
    dados = serie[serie["estado_nome"] == nome]
    vi = dados[dados["ano_abertura"] == periodo[0]]["n"].sum()
    vf = dados[dados["ano_abertura"] == periodo[1]]["n"].sum()
    if vi > 0:
        rows_tab.append({"Estado": nome, str(periodo[0]): int(vi),
                         str(periodo[1]): int(vf),
                         "Crescimento (%)": round((vf / vi - 1) * 100, 1)})

if rows_tab:
    st.markdown("#### Crescimento acumulado")
    df_tab     = pd.DataFrame(rows_tab)
    df_tab_raw = df_tab.copy()

    def fmt(v: float) -> str:
        c = "#16a34a" if v >= 0 else "#dc2626"
        return f'<span style="color:{c};font-weight:600">{"+" if v>=0 else ""}{v:.1f}%</span>'

    df_tab["Crescimento (%)"] = df_tab["Crescimento (%)"].apply(fmt)
    html = df_tab.to_html(index=False, escape=False, border=0)
    st.markdown(
        f'<style>table{{border-collapse:collapse;width:100%}}'
        f'th{{background:#f0f2f6;color:#1a1a2e;padding:9px 14px;text-align:left;'
        f'border-bottom:2px solid #e5e7eb;font-size:0.87rem}}'
        f'td{{padding:8px 14px;border-bottom:1px solid #f3f4f6;color:#1a1a2e;font-size:0.88rem}}'
        f'tr:hover td{{background:#f9fafb}}</style>{html}',
        unsafe_allow_html=True,
    )

    # insight dinâmico baseado no agg filtrado e na tabela de crescimento
    if len(agg) >= 2:
        med_ativa = agg["pct_ativa"].median()
        agg_copy = agg.copy()
        agg_copy["dist_med"] = (agg_copy["pct_ativa"] - med_ativa).abs()
        mid_state = agg_copy.loc[agg_copy["dist_med"].idxmin()]
        st.markdown(
            f'<div style="border-left:4px solid #e05c2b; background:#fff8f5;'
            f' padding:16px 20px; border-radius:6px; margin-top:16px;">'
            f'<span style="font-weight:700; color:#1a1a2e;">Insight: </span>'
            f'<span style="color:#374151;">'
            f'<strong>{top_vol["estado_nome"]}</strong> lidera em volume mas tem taxa de'
            f' atividade de <strong>{top_vol["pct_ativa"]:.1f}%</strong>.'
            f' <strong>{top_ativa["estado_nome"]}</strong> tem a maior taxa de atividade'
            f' (<strong>{top_ativa["pct_ativa"]:.1f}%</strong>).'
            f' <strong>{mid_state["estado_nome"]}</strong> apresenta posição intermediária'
            f' ({mid_state["pct_ativa"]:.1f}% de atividade,'
            f' {mid_state["pct_simples"]:.1f}% no Simples).</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    fastest = df_tab_raw.loc[df_tab_raw["Crescimento (%)"].idxmax()]
    slowest = df_tab_raw.loc[df_tab_raw["Crescimento (%)"].idxmin()]
    ano_ini, ano_fim = str(periodo[0]), str(periodo[1])
    st.markdown(
        f'<div style="border-left:4px solid #3b82f6; background:#eff6ff;'
        f' padding:14px 18px; border-radius:6px; margin-top:8px;">'
        f'<span style="font-weight:700; color:#1a1a2e;">Dinâmica de crescimento: </span>'
        f'<span style="color:#374151;"><strong>{fastest["Estado"]}</strong> foi o estado de'
        f' maior crescimento no período ({fastest[ano_ini]}→{fastest[ano_fim]} empresas,'
        f' +{fastest["Crescimento (%)"]:.1f}%). <strong>{slowest["Estado"]}</strong> cresceu'
        f' mais devagar (+{slowest["Crescimento (%)"]:.1f}%). Estados com crescimento'
        f' acelerado e baixa base inicial representam janelas de oportunidade para'
        f' políticas de fomento.</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
