import pandas as pd
import streamlit as st
from config import FONTE_DADOS, UF_REGIAO, SUBTITULO_STYLE, fmt_br, carregar_dados_otimizado

st.set_page_config(
    page_title="Ecossistema de Software Brasileiro",
    page_icon=None,
    layout="wide",
)

st.markdown(
    """
    
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("---")
    st.markdown("**Fonte dos dados:**  \nReceita Federal do Brasil  \nEstabelecimentos CNPJ — fev/2026")


@st.cache_data(max_entries=1, show_spinner=False)
def carregar_kpis() -> tuple:
    colunas = ["uf", "situacao_cadastral", "data_inicio_atividade", "data_situacao_cadastral"]
    df = carregar_dados_otimizado(colunas)
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
    inicio = pd.to_datetime(df_bx_ne["data_inicio_atividade"], format="%Y%m%d", errors="coerce")
    fim = pd.to_datetime(df_bx_ne["data_situacao_cadastral"], format="%Y%m%d", errors="coerce")
    vida = (fim - inicio).dt.days / 365.25
    vida = vida[vida > 0].dropna()
    vida_ne = round(float(vida.median()), 1) if len(vida) > 0 else 0.0

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
    f''
    'Análise de ~480 mil empresas de software com base nos dados abertos da Receita Federal do Brasil.'
    '',
    unsafe_allow_html=True,
)
st.markdown("---")
st.subheader("Painel Geral", anchor=False)

cols = st.columns(5)
for col, (value, label) in zip(cols, kpis):
    with col:
        st.markdown(
            f''
            f'{value}'
            f'{label}'
            f'',
            unsafe_allow_html=True,
        )

st.markdown("", unsafe_allow_html=True)
st.markdown(
    f''
    f'Contexto geral:'
    f' O Nordeste concentra apenas {fmt_br(pct_ne)}%'
    f' das empresas de software, apesar de representar 28% da população.'
    f' Contudo, apresenta taxa de atividade superior ao Sudeste'
    f' ({fmt_br(ne_ativa_pct)}% vs. {fmt_br(se_ativa_pct)}%),'
    f' indicando problema estrutural de acesso, não de capacidade.'
    f'',
    unsafe_allow_html=True,
)

st.markdown("---")
st.caption(FONTE_DADOS)
st.markdown("Use o menu lateral para navegar pelas análises.")
