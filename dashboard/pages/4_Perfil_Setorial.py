import streamlit as st
import pandas as pd
import plotly.express as px
from config import (
    REGIOES, UF_REGIAO,
    CORES, MAPA_CNAE, LAYOUT_BASE, FONTE_DADOS, SUBTITULO_STYLE,
    carregar_dados_otimizado,
)

st.set_page_config(page_title="Perfil Setorial", layout="wide")


@st.cache_data(max_entries=1, show_spinner=False)
def carregar_dados() -> pd.DataFrame:
    colunas = [
        "uf", "cnae_fiscal_principal", "correio_eletronico", 
        "telefone1", "opcao_simples"
    ]
    df = carregar_dados_otimizado(colunas)
    df = df[df["uf"] != "EX"]
    df["regiao"] = df["uf"].map(UF_REGIAO)
    df["cnae_label"] = df["cnae_fiscal_principal"].map(MAPA_CNAE).fillna("Outros")
    df["tem_email"] = df["correio_eletronico"].fillna("").astype(str).str.strip() != ""
    df["tem_telefone"] = df["telefone1"].fillna("").astype(str).str.strip() != ""
    return df[["regiao", "cnae_label", "tem_email", "tem_telefone", "opcao_simples"]]


df = carregar_dados()

st.title("Perfil Setorial")
st.markdown(
    f''
    'Comparação do mix de segmentos CNAE, formalização digital e regime tributário entre duas regiões. '
    'Use os seletores para explorar qualquer par de regiões do Brasil.'
    '',
    unsafe_allow_html=True,
)

with st.expander("Filtros", expanded=True):
    c1, c2 = st.columns(2)
    regioes_list = list(REGIOES.keys())
    with c1:
        reg_a = st.selectbox("Região A", regioes_list,
                             index=regioes_list.index("Nordeste"))
    with c2:
        reg_b = st.selectbox("Região B", regioes_list,
                             index=regioes_list.index("Sudeste"))

df_a = df[df["regiao"] == reg_a]
df_b = df[df["regiao"] == reg_b]

if df_a.empty or df_b.empty:
    st.warning("Dados insuficientes para uma das regiões selecionadas.")
    st.stop()

cor_a = CORES.get(reg_a, "#e05c2b")
cor_b = CORES.get(reg_b, "#2563eb")

st.markdown("---")
st.subheader("Distribuição percentual por CNAE", anchor=False)

dist_a = df_a["cnae_label"].value_counts(normalize=True).mul(100).rename(reg_a)
dist_b = df_b["cnae_label"].value_counts(normalize=True).mul(100).rename(reg_b)
dist = pd.concat([dist_a, dist_b], axis=1).fillna(0).reset_index()
dist.columns = ["cnae_label", reg_a, reg_b]
dist_melt = dist.melt(id_vars="cnae_label", var_name="Região", value_name="Percentual")
dist_melt = dist_melt.sort_values(["cnae_label", "Percentual"])

fig_cnae = px.bar(
    dist_melt, x="Percentual", y="cnae_label", color="Região",
    barmode="group", orientation="h",
    color_discrete_map={reg_a: cor_a, reg_b: cor_b},
    labels={"cnae_label": "Segmento", "Percentual": "% das empresas"},
    text="Percentual",
)
fig_cnae.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
fig_cnae.update_layout(height=380, legend=dict(orientation="h", y=1.08), **LAYOUT_BASE)
fig_cnae.update_xaxes(range=[0, dist_melt["Percentual"].max() * 1.2])
st.plotly_chart(fig_cnae, use_container_width=True)
st.caption(FONTE_DADOS)

dist["diff_abs"] = (dist[reg_a] - dist[reg_b]).abs()
dist["diff_ab"]  = dist[reg_a] - dist[reg_b]
if not dist.empty:
    max_row   = dist.loc[dist["diff_abs"].idxmax()]
    val_a     = round(max_row[reg_a], 1)
    val_b     = round(max_row[reg_b], 1)
    maior_reg = reg_a if val_a > val_b else reg_b
    menor_reg = reg_b if val_a > val_b else reg_a
    maior_val = max(val_a, val_b)
    menor_val = min(val_a, val_b)
    dom_a     = dist.loc[dist[reg_a].idxmax()]
    dom_b     = dist.loc[dist[reg_b].idxmax()]
    st.markdown(
        f''
        f'Maior diferença de mix: '
        f'{max_row["cnae_label"]} é o segmento'
        f' com maior divergência — {maior_reg} ({maior_val:.1f}%)'
        f' vs {menor_reg} ({menor_val:.1f}%). '
        f'O segmento dominante em {reg_a} é {dom_a["cnae_label"]}'
        f' ({dom_a[reg_a]:.1f}%) e em {reg_b} é {dom_b["cnae_label"]}'
        f' ({dom_b[reg_b]:.1f}%).'
        f'',
        unsafe_allow_html=True,
    )

st.markdown("---")
st.markdown(
    ''
    'Proxies de presença digital e formalização cadastral — quanto maior, mais formalizada tende a ser a empresa.'
    '', unsafe_allow_html=True,
)

col_email, col_tel = st.columns(2)

pct_email_a = round(df_a["tem_email"].mean() * 100, 1)
pct_email_b = round(df_b["tem_email"].mean() * 100, 1)
pct_tel_a   = round(df_a["tem_telefone"].mean() * 100, 1)
pct_tel_b   = round(df_b["tem_telefone"].mean() * 100, 1)

with col_email:
    st.subheader("% com e-mail cadastrado", anchor=False)
    df_em = pd.DataFrame({"Região": [reg_a, reg_b], "valor": [pct_email_a, pct_email_b],
                           "cor": [cor_a, cor_b]}).sort_values("valor")
    fig_em = px.bar(df_em, x="valor", y="Região", orientation="h",
                    color="cor", color_discrete_map="identity",
                    labels={"valor": "%", "Região": ""},
                    text="valor")
    fig_em.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_em.update_layout(showlegend=False, **LAYOUT_BASE)
    fig_em.update_xaxes(range=[0, max(pct_email_a, pct_email_b) * 1.25])
    st.plotly_chart(fig_em, use_container_width=True)
    st.caption(FONTE_DADOS)

with col_tel:
    st.subheader("% com telefone cadastrado", anchor=False)
    df_tel = pd.DataFrame({"Região": [reg_a, reg_b], "valor": [pct_tel_a, pct_tel_b],
                            "cor": [cor_a, cor_b]}).sort_values("valor")
    fig_tel = px.bar(df_tel, x="valor", y="Região", orientation="h",
                     color="cor", color_discrete_map="identity",
                     labels={"valor": "%", "Região": ""},
                     text="valor")
    fig_tel.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_tel.update_layout(showlegend=False, **LAYOUT_BASE)
    fig_tel.update_xaxes(range=[0, max(pct_tel_a, pct_tel_b) * 1.25])
    st.plotly_chart(fig_tel, use_container_width=True)
    st.caption(FONTE_DADOS)

gap_email = abs(pct_email_a - pct_email_b)
gap_tel   = abs(pct_tel_a   - pct_tel_b)
maior_email = reg_a if pct_email_a > pct_email_b else reg_b
maior_tel   = reg_a if pct_tel_a   > pct_tel_b   else reg_b
st.markdown(
    f''
    f'Formalização digital: '
    f'{maior_email} lidera em cadastro de e-mail'
    f' (gap de {gap_email:.1f} pp) e {maior_tel} em telefone'
    f' (gap de {gap_tel:.1f} pp). Ausência de contato cadastrado'
    f' é proxy de informalidade operacional — empresas sem dado de contato têm menor'
    f' probabilidade de acesso a crédito, licitações e parcerias.'
    f'',
    unsafe_allow_html=True,
)

st.markdown("---")
st.subheader("Composição por regime tributário", anchor=False)

rows_simp = []
for reg, dfreg in [(reg_a, df_a), (reg_b, df_b)]:
    total = len(dfreg)
    if total == 0:
        continue
    ps = round((dfreg["opcao_simples"] == "S").sum() / total * 100, 1)
    rows_simp += [
        {"Região": reg, "Categoria": "Simples Nacional", "Valor": ps},
        {"Região": reg, "Categoria": "Fora do Simples",  "Valor": round(100 - ps, 1)},
    ]

df_simp = pd.DataFrame(rows_simp)
fig_simp = px.bar(
    df_simp, x="Região", y="Valor", color="Categoria", barmode="stack",
    text="Valor",
    color_discrete_map={"Simples Nacional": "#e05c2b", "Fora do Simples": "#2563eb"},
    labels={"Valor": "%"},
)
fig_simp.update_traces(texttemplate="%{text:.1f}%", textposition="inside", insidetextanchor="middle")
fig_simp.update_layout(legend=dict(orientation="h", y=1.08), **LAYOUT_BASE)
fig_simp.update_yaxes(range=[0, 105])
st.plotly_chart(fig_simp, use_container_width=True)
st.caption(FONTE_DADOS)

simp_a = next((r["Valor"] for r in rows_simp if r["Região"] == reg_a and r["Categoria"] == "Simples Nacional"), None)
simp_b = next((r["Valor"] for r in rows_simp if r["Região"] == reg_b and r["Categoria"] == "Simples Nacional"), None)
if simp_a is not None and simp_b is not None:
    maior_simp = reg_a if simp_a > simp_b else reg_b
    menor_simp = reg_b if simp_a > simp_b else reg_a
    val_maior  = max(simp_a, simp_b)
    val_menor  = min(simp_a, simp_b)
    adv_cnae = dist.loc[dist["diff_ab"].idxmax()] if not dist.empty else None
    adv_text = ""
    if adv_cnae is not None and adv_cnae["diff_ab"] > 0:
        adv_text = (
            f" {reg_a} tem proporcionalmente mais"
            f" {adv_cnae['cnae_label']}"
            f" ({adv_cnae[reg_a]:.1f}% vs. {adv_cnae[reg_b]:.1f}% em {reg_b})."
        )
    st.markdown(
        f''
        f'Perfil setorial: '
        f'{adv_text}'
        f' {maior_simp} tem maior adesão ao Simples Nacional'
        f' ({val_maior:.1f}% vs. {val_menor:.1f}% em {menor_simp}),'
        f' refletindo predominância de micro e pequenas empresas no ecossistema regional.'
        f'',
        unsafe_allow_html=True,
    )
