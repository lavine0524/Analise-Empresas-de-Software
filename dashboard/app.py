import streamlit as st

st.set_page_config(
    page_title="Ecossistema de Software Brasileiro",
    page_icon="💻",
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

st.title("💻 Ecossistema de Software Brasileiro")
st.markdown("Análise de ~480 mil empresas de software com base nos dados abertos da Receita Federal.")
st.markdown("---")
st.subheader("Painel Geral")

kpis = [
    ("480.677", "Empresas de software"),
    ("57,6%", "Taxa de ativas"),
    ("8,4%", "Participação do Nordeste"),
    ("66,8%", "Concentração no Sudeste"),
    ("4,0 anos", "Vida mediana NE"),
]

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
    '<div style="border-left:4px solid #e05c2b; background-color:#fff8f5;'
    ' padding:16px 20px; border-radius:6px;">'
    '<span style="font-weight:700; color:#1a1a2e;">Contexto geral:</span>'
    '<span style="color:#1a1a2e;"> O Nordeste concentra apenas <strong>8,4%</strong> das empresas de software ativas,'
    ' apesar de representar 28% da população.'
    ' Contudo, apresenta taxa de sobrevivência superior ao Sudeste (57,4% vs. 52,9%),'
    ' indicando problema estrutural de <em>acesso</em>, não de <em>capacidade</em>.</span>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown("---")
st.markdown("Use o menu lateral para navegar pelas análises.")
