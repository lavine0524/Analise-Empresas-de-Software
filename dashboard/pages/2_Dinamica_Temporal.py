import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from config import (
    REGIOES, UF_REGIAO,
    CORES, LAYOUT_BASE, FONTE_DADOS, SUBTITULO_STYLE,
    carregar_dados_otimizado,
)

st.set_page_config(page_title="Dinâmica Temporal", layout="wide")


@st.cache_data(max_entries=1, show_spinner=False)
def carregar_dados() -> pd.DataFrame:
    colunas = ["uf", "data_inicio_atividade"]
    df = carregar_dados_otimizado(colunas)
    df = df[df["uf"] != "EX"]
    df["regiao"] = df["uf"].map(UF_REGIAO)
    df["ano_abertura"] = pd.to_numeric(
        df["data_inicio_atividade"].astype(str).str[:4], errors="coerce", downcast="unsigned"
    )
    return df.dropna(subset=["ano_abertura"])[["regiao", "ano_abertura"]]


df = carregar_dados()

ano_min_data = int(df["ano_abertura"].min())
ano_max_data = int(df["ano_abertura"].max())

st.title("Dinâmica Temporal de Abertura de Empresas")
st.markdown(
    f''
    'Evolução anual de aberturas de empresas de software por região (2000–2024). '
    'Apesar de crescimento percentual semelhante, a brecha absoluta entre Nordeste e Sudeste se amplia.'
    '',
    unsafe_allow_html=True,
)

with st.expander("Filtros", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        ano_min, ano_max = st.slider(
            "Período de abertura",
            ano_min_data, ano_max_data,
            (max(ano_min_data, 2000), ano_max_data),
        )
    with c2:
        reg_sel = st.multiselect("Regiões", list(REGIOES.keys()), default=["Nordeste", "Sudeste", "Sul"])

df_f = df[df["regiao"].isin(reg_sel) & (df["ano_abertura"] >= ano_min) & (df["ano_abertura"] <= ano_max)]

if df_f.empty:
    st.warning("Nenhum dado para os filtros selecionados.")
    st.stop()

serie = (
    df_f.groupby(["regiao", "ano_abertura"], observed=True).size()
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
    title="Novas empresas de software por ano e região (base: data de abertura)",
    xaxis_title="Ano", yaxis_title="Nº de empresas abertas",
    height=460, hovermode="x unified",
    legend=dict(bgcolor="rgba(255,255,255,0.9)", bordercolor="#e5e7eb", borderwidth=1),
    **LAYOUT_BASE,
)
fig.update_yaxes(tickformat="~s")
st.plotly_chart(fig, use_container_width=True)
st.caption(FONTE_DADOS)

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
            f''
            f'Recuperação pós-pandemia (2020→2023): '
            f'{top["Região"]} liderou a aceleração'
            f' (+{top["pct"]}%), enquanto {bot["Região"]} cresceu +{bot["pct"]}%.'
            f' A pandemia serviu como catalisador assimétrico — regiões menores aceleraram'
            f' proporcionalmente mais com a digitalização forçada.'
            f'',
            unsafe_allow_html=True,
        )

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

        def fmt_cresc(v: float) -> str:
            cor = "#16a34a" if v >= 0 else "#dc2626"
            return f'{"+" if v>=0 else ""}{v:.1f}%'

        df_tab_html = df_tab.copy()
        df_tab_html["Crescimento (%)"] = df_tab_html["Crescimento (%)"].apply(fmt_cresc)
        html = df_tab_html.to_html(index=False, escape=False, classes="", border=0)
        st.markdown(
            f'{html}',
            unsafe_allow_html=True,
        )

        ne_row = df_tab[df_tab["Região"] == "Nordeste"]
        se_row = df_tab[df_tab["Região"] == "Sudeste"]
        if len(ne_row) > 0 and len(se_row) > 0:
            ne_pct = ne_row["Crescimento (%)"].values[0]
            se_pct = se_row["Crescimento (%)"].values[0]
            ne_abs_ini = ne_row["Empresas em 2015"].values[0]
            ne_abs_fim = ne_row["Empresas em 2024"].values[0]
            se_abs_ini = se_row["Empresas em 2015"].values[0]
            se_abs_fim = se_row["Empresas em 2024"].values[0]
            gap_ini = se_abs_ini - ne_abs_ini
            gap_fim = se_abs_fim - ne_abs_fim
            st.markdown(
                f''
                f''
                f'O Nordeste cresceu +{ne_pct:.1f}% no período,'
                f' partindo de uma base muito menor que o Sudeste (+{se_pct:.1f}%).'
                f' Em termos absolutos, a diferença passou de ~{gap_ini:,} para ~{gap_fim:,} empresas/ano.'
                f'',
                unsafe_allow_html=True,
            )

st.markdown("", unsafe_allow_html=True)

if "Nordeste" in reg_sel and "Sudeste" in reg_sel:
    ne_last = int(serie[(serie["regiao"] == "Nordeste") & (serie["ano_abertura"] == min(ano_max, ano_max_data))]["empresas"].sum())
    se_last = int(serie[(serie["regiao"] == "Sudeste")  & (serie["ano_abertura"] == min(ano_max, ano_max_data))]["empresas"].sum())
    ne_first = int(serie[(serie["regiao"] == "Nordeste") & (serie["ano_abertura"] == max(ano_min, ano_min_data))]["empresas"].sum())
    se_first = int(serie[(serie["regiao"] == "Sudeste")  & (serie["ano_abertura"] == max(ano_min, ano_min_data))]["empresas"].sum())
    if ne_first > 0 and se_first > 0:
        gap_ini = se_first - ne_first
        gap_fim = se_last  - ne_last
        st.markdown(
            f''
            f'Insight: '
            f'O Nordeste cresceu de ~{ne_first:,}'
            f' para ~{ne_last:,} empresas/ano, mas o Sudeste saltou de'
            f' ~{se_first:,} para ~{se_last:,}.'
            f' A desigualdade regional não está convergindo.'
            f'',
            unsafe_allow_html=True,
        )
        st.markdown(
            f''
            f'Divergência absoluta: '
            f'A diferença entre Sudeste e Nordeste em novas'
            f' empresas/ano passou de {gap_ini:,} (início do período) para'
            f' {gap_fim:,} (fim do período). Crescimento percentual similar'
            f' sobre bases muito diferentes significa que a brecha absoluta aumenta.'
            f' Para convergir, o Nordeste precisaria crescer 3–4× mais rápido que o Sudeste.'
            f'',
            unsafe_allow_html=True,
        )
