import pandas as pd
import streamlit as st
from config import DATASET_PATH, FONTE_DADOS, UF_REGIAO, SUBTITULO_STYLE, fmt_br

st.set_page_config(
    page_title="Ecossistema de Software Brasileiro",
    page_icon=None,
    layout="wide",
)

st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] { background-color: #f0f2f6; }
    section[data-testid="stSidebar"] * { color: #1a1a2e !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## Estruture Negócios")
    st.markdown("**Projeto de Extensão — UFPB 2026**")
    st.markdown("---")
    st.markdown("**Fonte dos dados:**  \nReceita Federal do Brasil  \nEstabelecimentos CNPJ — fev/2026")


@st.cache_data
def carregar_kpis() -> tuple:
    """Carrega colunas mínimas e calcula os 5 KPIs da home."""
    colunas = ["uf", "situacao_cadastral", "data_inicio_atividade", "data_situacao_cadastral"]
    df = pd.read_parquet(DATASET_PATH, columns=colunas)
    df = df[df["uf"] != "EX"]
    df["regiao"] = df["uf"].map(UF_REGIAO)

    total = len(df)
    pct_ativas = round((df["situacao_cadastral"] == "02").mean() * 100, 1)
    pct_ne = round((df["regiao"] == "Nordeste").sum() / total * 100, 1)
    pct_se = round((df["regiao"] == "Sudeste").sum() / total * 100, 1)

    ne_ativa_pct = round(
        (df[df["regiao"] == "Nordeste"]["situacao_cadastral"] == "02").mean() * 100, 1
    )
    se_ativa_pct = round(
        (df[df["regiao"] == "Sudeste"]["situacao_cadastral"] == "02").mean() * 100, 1
    )

    df_bx_ne = df[(df["situacao_cadastral"] == "08") & (df["regiao"] == "Nordeste")].copy()
    df_bx_ne["inicio"] = pd.to_datetime(
        df_bx_ne["data_inicio_atividade"], format="%Y%m%d", errors="coerce"
    )
    df_bx_ne["fim"] = pd.to_datetime(
        df_bx_ne["data_situacao_cadastral"], format="%Y%m%d", errors="coerce"
    )
    df_bx_ne = df_bx_ne.dropna(subset=["inicio", "fim"])
    df_bx_ne["vida"] = (df_bx_ne["fim"] - df_bx_ne["inicio"]).dt.days / 365.25
    df_bx_ne = df_bx_ne[df_bx_ne["vida"] > 0]
    vida_ne = round(df_bx_ne["vida"].median(), 1) if len(df_bx_ne) > 0 else 0.0

    return total, pct_ativas, pct_ne, pct_se, ne_ativa_pct, se_ativa_pct, vida_ne


total, pct_ativas, pct_ne, pct_se, ne_ativa_pct, se_ativa_pct, vida_ne = carregar_kpis()

kpis = [
    (f"{total:,}".replace(",", "."),  "Empresas de software"),
    (f"{fmt_br(pct_ativas)}%",        "Taxa de ativas"),
    (f"{fmt_br(pct_ne)}%",            "Participação do Nordeste"),
    (f"{fmt_br(pct_se)}%",            "Concentração no Sudeste"),
    (f"{fmt_br(vida_ne)} anos",       "Vida mediana NE"),
]

st.title("Ecossistema de Software Brasileiro")
st.markdown(
    f'<p style="{SUBTITULO_STYLE}">'
    'Análise de ~480 mil empresas de software com base nos dados abertos da Receita Federal do Brasil. '
    'Projeto de extensão acadêmica — Estruture Negócios | UFPB 2026.'
    '</p>',
    unsafe_allow_html=True,
)
st.markdown("---")
st.subheader("Painel Geral", anchor=False)

cols = st.columns(5)
for col, (value, label) in zip(cols, kpis):
    with col:
        st.markdown(
            f'<div style="background:#ffffff; border-left:4px solid #e05c2b; border-radius:6px;'
            f' padding:16px 18px; box-shadow:0 1px 4px rgba(0,0,0,0.08);">'
            f'<div style="font-size:1.7rem; font-weight:700; color:#1a1a2e; line-height:1.1;">{value}</div>'
            f'<div style="font-size:0.82rem; color:#6b7280; margin-top:5px;">{label}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    f'<div style="border-left:4px solid #e05c2b; background-color:#fff8f5;'
    f' padding:16px 20px; border-radius:6px;">'
    f'<span style="font-weight:700; color:#1a1a2e;">Contexto geral:</span>'
    f'<span style="color:#1a1a2e;"> O Nordeste concentra apenas <strong>{fmt_br(pct_ne)}%</strong>'
    f' das empresas de software, apesar de representar 28% da população.'
    f' Contudo, apresenta taxa de atividade superior ao Sudeste'
    f' ({fmt_br(ne_ativa_pct)}% vs. {fmt_br(se_ativa_pct)}%),'
    f' indicando problema estrutural de <em>acesso</em>, não de <em>capacidade</em>.</span>'
    f'</div>',
    unsafe_allow_html=True,
)

st.markdown("---")
st.caption(FONTE_DADOS)
st.markdown("Use o menu lateral para navegar pelas análises.")
