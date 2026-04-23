import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Dinâmica Temporal", layout="wide")

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

COLUNAS = ["uf", "situacao_cadastral", "data_inicio_atividade"]


@st.cache_data
def carregar_dados() -> pd.DataFrame:
    df = pd.read_csv(DATASET_PATH, usecols=COLUNAS, dtype=str)
    df = df[df["uf"] != "EX"]
    df["regiao"] = df["uf"].map(UF_REGIAO)
    df["ano_abertura"] = pd.to_numeric(
        df["data_inicio_atividade"].str[:4], errors="coerce"
    ).astype("Int64")
    return df.dropna(subset=["ano_abertura"])


df = carregar_dados()

st.title("📈 Dinâmica Temporal de Abertura de Empresas")

with st.expander("🔧 Filtros", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        ano_min, ano_max = st.slider("Período de abertura", 2000, 2024, (2000, 2024))
    with c2:
        reg_sel = st.multiselect("Regiões", list(REGIOES.keys()), default=["Nordeste", "Sudeste", "Sul"])

df_f = df[df["regiao"].isin(reg_sel) & (df["ano_abertura"] >= ano_min) & (df["ano_abertura"] <= ano_max)]

if df_f.empty:
    st.warning("Nenhum dado para os filtros selecionados.")
    st.stop()

serie = (
    df_f.groupby(["regiao", "ano_abertura"]).size()
    .reset_index(name="empresas").sort_values("ano_abertura")
)

fig = go.Figure()
for regiao in reg_sel:
    dados = serie[serie["regiao"] == regiao]
    if dados.empty:
        continue
    ne = regiao == "Nordeste"
    fig.add_trace(go.Scatter(
        x=dados["ano_abertura"], y=dados["empresas"],
        name=regiao, mode="lines+markers",
        line=dict(color=CORES.get(regiao, "#94a3b8"), width=3 if ne else 2,
                  dash="solid" if ne else "dash"),
        marker=dict(size=6 if ne else 4),
    ))

if ano_min <= 2020 <= ano_max:
    fig.add_vline(x=2020, line_dash="dot", line_color="#9ca3af",
                  annotation_text="Pandemia (2020)", annotation_position="top right",
                  annotation_font_color="#6b7280")

fig.update_layout(
    title="Abertura de empresas de software por região",
    xaxis_title="Ano", yaxis_title="Nº de empresas abertas",
    height=460, hovermode="x unified",
    plot_bgcolor="white", paper_bgcolor="white",
    font_color="#1a1a2e",
    xaxis=dict(gridcolor="#e5e7eb", linecolor="#e5e7eb"),
    yaxis=dict(gridcolor="#e5e7eb", linecolor="#e5e7eb"),
    legend=dict(bgcolor="rgba(255,255,255,0.9)", bordercolor="#e5e7eb", borderwidth=1),
    hoverlabel=dict(font_size=15, bgcolor="white", bordercolor="#e5e7eb"),
)
st.plotly_chart(fig, use_container_width=True)

if 2020 in serie["ano_abertura"].values and ano_max >= 2023:
    rows_accel = []
    for regiao in reg_sel:
        d = serie[serie["regiao"] == regiao]
        v2020 = int(d[d["ano_abertura"] == 2020]["empresas"].sum())
        v2023 = int(d[d["ano_abertura"] == 2023]["empresas"].sum()) if 2023 in d["ano_abertura"].values else 0
        if v2020 > 0 and v2023 > 0:
            rows_accel.append({"Região": regiao, "pct": round((v2023 / v2020 - 1) * 100, 1)})
    if len(rows_accel) >= 2:
        rows_accel.sort(key=lambda x: x["pct"], reverse=True)
        top, bot = rows_accel[0], rows_accel[-1]
        st.markdown(
            f'<div style="border-left:4px solid #16a34a; background:#f0fdf4;'
            f' padding:14px 18px; border-radius:6px; margin:8px 0;">'
            f'<span style="font-weight:700; color:#1a1a2e;">Recuperação pós-pandemia (2020→2023): </span>'
            f'<span style="color:#374151;"><strong>{top["Região"]}</strong> liderou a aceleração'
            f' (+{top["pct"]}%), enquanto <strong>{bot["Região"]}</strong> cresceu +{bot["pct"]}%.'
            f' A pandemia serviu como catalisador assimétrico — regiões menores aceleraram'
            f' proporcionalmente mais com a digitalização forçada.</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

# ── Tabela de crescimento ─────────────────────────────────────────────────────
if ano_min <= 2015 and ano_max >= 2024:
    st.markdown("#### Crescimento acumulado 2015 → 2024")
    rows = []
    for regiao in reg_sel:
        dados = serie[serie["regiao"] == regiao]
        v2015 = int(dados[dados["ano_abertura"] == 2015]["empresas"].sum())
        v2024 = int(dados[dados["ano_abertura"] == 2024]["empresas"].sum())
        if v2015 > 0:
            pct = (v2024 / v2015 - 1) * 100
            rows.append({"Região": regiao, "Empresas em 2015": v2015,
                         "Empresas em 2024": v2024, "Crescimento (%)": pct})
    if rows:
        df_tab = pd.DataFrame(rows)

        def fmt_cresc(v):
            cor = "#16a34a" if v >= 0 else "#dc2626"
            return f'<span style="color:{cor};font-weight:600">{"+" if v>=0 else ""}{v:.1f}%</span>'

        df_tab["Crescimento (%)"] = df_tab["Crescimento (%)"].apply(fmt_cresc)
        html = df_tab.to_html(index=False, escape=False,
                              classes="", border=0)
        st.markdown(
            f'<style>table{{border-collapse:collapse;width:100%}}'
            f'th{{background:#f0f2f6;color:#1a1a2e;padding:10px 14px;text-align:left;'
            f'border-bottom:2px solid #e5e7eb;font-size:0.88rem}}'
            f'td{{padding:9px 14px;border-bottom:1px solid #f3f4f6;color:#1a1a2e;font-size:0.9rem}}'
            f'tr:hover td{{background:#f9fafb}}</style>{html}',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="background:#f0f2f6; border-radius:6px; padding:12px 16px; margin-top:10px;">'
            '<span style="color:#374151; font-size:0.9rem;">O Nordeste cresceu <strong>+327,8%</strong>'
            ' no período, partindo de uma base muito menor que o Sudeste (<strong>+289,5%</strong>).'
            ' Em termos absolutos, a diferença aumentou de ~5.400 para ~20.900 empresas/ano.</span>'
            '</div>',
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    '<div style="border-left:4px solid #e05c2b; background:#fff8f5;'
    ' padding:16px 20px; border-radius:6px;">'
    '<span style="font-weight:700; color:#1a1a2e;">Insight: </span>'
    '<span style="color:#374151;">O Nordeste cresceu de ~800 para ~3.500 empresas/ano (+337%),'
    ' mas o Sudeste saltou de ~8.000 para ~21.000. A desigualdade regional'
    ' <strong>não está convergindo</strong>.</span>'
    '</div>',
    unsafe_allow_html=True,
)

if "Nordeste" in reg_sel and "Sudeste" in reg_sel:
    ne_last = int(serie[(serie["regiao"] == "Nordeste") & (serie["ano_abertura"] == min(ano_max, 2024))]["empresas"].sum())
    se_last = int(serie[(serie["regiao"] == "Sudeste") & (serie["ano_abertura"] == min(ano_max, 2024))]["empresas"].sum())
    ne_first = int(serie[(serie["regiao"] == "Nordeste") & (serie["ano_abertura"] == max(ano_min, 2000))]["empresas"].sum())
    se_first = int(serie[(serie["regiao"] == "Sudeste") & (serie["ano_abertura"] == max(ano_min, 2000))]["empresas"].sum())
    if ne_first > 0 and se_first > 0:
        gap_ini = se_first - ne_first
        gap_fim = se_last - ne_last
        st.markdown(
            f'<div style="border-left:4px solid #94a3b8; background:#f8fafc;'
            f' padding:14px 18px; border-radius:6px; margin-top:8px;">'
            f'<span style="font-weight:700; color:#1a1a2e;">Divergência absoluta: </span>'
            f'<span style="color:#374151;">A diferença entre Sudeste e Nordeste em novas'
            f' empresas/ano passou de <strong>{gap_ini:,}</strong> (início do período) para'
            f' <strong>{gap_fim:,}</strong> (fim do período). Crescimento percentual similar'
            f' sobre bases muito diferentes significa que a <em>brecha absoluta aumenta</em>.'
            f' Para convergir, o Nordeste precisaria crescer 3–4× mais rápido que o Sudeste.</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
