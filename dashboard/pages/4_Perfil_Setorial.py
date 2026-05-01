from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px
from config import (
    REGIOES, UF_REGIAO,
    CORES, MAPA_CNAE, LAYOUT_BASE, FONTE_DADOS, SUBTITULO_STYLE,
)

DATA_PATH = Path(__file__).parent.parent / "dataset_final.parquet"

st.set_page_config(page_title="Perfil Setorial", layout="wide")


@st.cache_data
def carregar_dados() -> pd.DataFrame:
    df = pd.read_parquet(DATA_PATH)
    df = df[df["uf"] != "EX"]
    df["regiao"] = df["uf"].map(UF_REGIAO)
    df["cnae_label"] = df["cnae_fiscal_principal"].map(MAPA_CNAE).fillna("Outros")
    df["tem_email"] = df["correio_eletronico"].fillna("").str.strip() != ""
    df["tem_telefone"] = df["telefone1"].fillna("").str.strip() != ""
    return df


df = carregar_dados()

st.title("Perfil Setorial")
st.markdown(
    f'<p style="{SUBTITULO_STYLE}">'
    'Comparação do mix de segmentos CNAE, formalização digital e regime tributário entre duas regiões. '
    'Use os seletores para explorar qualquer par de regiões do Brasil.'
    '</p>',
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

# ── Gráfico 1: Distribuição por CNAE ─────────────────────────────────────────
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

# insight dinâmico: CNAE com maior diferença entre regiões
dist["diff_abs"] = (dist[reg_a] - dist[reg_b]).abs()
dist["diff_ab"]  = dist[reg_a] - dist[reg_b]
if not dist.empty:
    max_row  = dist.loc[dist["diff_abs"].idxmax()]
    val_a    = round(max_row[reg_a], 1)
    val_b    = round(max_row[reg_b], 1)
    maior_reg = reg_a if val_a > val_b else reg_b
    menor_reg = reg_b if val_a > val_b else reg_a
    maior_val = max(val_a, val_b)
    menor_val = min(val_a, val_b)
    # segmento onde reg_a tem maior vantagem sobre reg_b
    adv_row  = dist.loc[dist["diff_ab"].idxmax()]
    dom_a    = dist.loc[dist[reg_a].idxmax()]
    dom_b    = dist.loc[dist[reg_b].idxmax()]
    st.markdown(
        f'<div style="border-left:4px solid #ca8a04; background:#fefce8;'
        f' padding:14px 18px; border-radius:6px; margin:8px 0;">'
        f'<span style="font-weight:700; color:#1a1a2e;">Maior diferença de mix: </span>'
        f'<span style="color:#374151;"><strong>{max_row["cnae_label"]}</strong> é o segmento'
        f' com maior divergência — <strong>{maior_reg}</strong> ({maior_val:.1f}%)'
        f' vs <strong>{menor_reg}</strong> ({menor_val:.1f}%). '
        f'O segmento dominante em {reg_a} é <em>{dom_a["cnae_label"]}</em>'
        f' ({dom_a[reg_a]:.1f}%) e em {reg_b} é <em>{dom_b["cnae_label"]}</em>'
        f' ({dom_b[reg_b]:.1f}%).</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

st.markdown("---")
st.markdown(
    '<p style="color:#6b7280; font-size:0.9rem; margin-bottom:4px;">'
    'Proxies de presença digital e formalização cadastral — quanto maior, mais formalizada tende a ser a empresa.'
    '</p>', unsafe_allow_html=True,
)

# ── Gráficos 2a e 2b: Formalização ──────────────────────────────────────────
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
    f'<div style="border-left:4px solid #7c3aed; background:#faf5ff;'
    f' padding:14px 18px; border-radius:6px; margin:8px 0;">'
    f'<span style="font-weight:700; color:#1a1a2e;">Formalização digital: </span>'
    f'<span style="color:#374151;"><strong>{maior_email}</strong> lidera em cadastro de e-mail'
    f' (gap de <strong>{gap_email:.1f} pp</strong>) e <strong>{maior_tel}</strong> em telefone'
    f' (gap de <strong>{gap_tel:.1f} pp</strong>). Ausência de contato cadastrado'
    f' é proxy de informalidade operacional — empresas sem dado de contato têm menor'
    f' probabilidade de acesso a crédito, licitações e parcerias.</span>'
    f'</div>',
    unsafe_allow_html=True,
)

st.markdown("---")

# ── Gráfico 3: Simples Nacional ───────────────────────────────────────────────
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

# insight dinâmico baseado nas regiões selecionadas
simp_a = next((r["Valor"] for r in rows_simp if r["Região"] == reg_a and r["Categoria"] == "Simples Nacional"), None)
simp_b = next((r["Valor"] for r in rows_simp if r["Região"] == reg_b and r["Categoria"] == "Simples Nacional"), None)
if simp_a is not None and simp_b is not None:
    maior_simp = reg_a if simp_a > simp_b else reg_b
    menor_simp = reg_b if simp_a > simp_b else reg_a
    val_maior  = max(simp_a, simp_b)
    val_menor  = min(simp_a, simp_b)
    # CNAE com maior diferença proporcional a favor de reg_a
    adv_cnae = dist.loc[dist["diff_ab"].idxmax()] if not dist.empty else None
    adv_text = ""
    if adv_cnae is not None and adv_cnae["diff_ab"] > 0:
        adv_text = (
            f" <strong>{reg_a}</strong> tem proporcionalmente mais"
            f" <em>{adv_cnae['cnae_label']}</em>"
            f" ({adv_cnae[reg_a]:.1f}% vs. {adv_cnae[reg_b]:.1f}% em {reg_b})."
        )
    st.markdown(
        f'<div style="border-left:4px solid #e05c2b; background:#fff8f5;'
        f' padding:16px 20px; border-radius:6px; margin-top:8px;">'
        f'<span style="font-weight:700; color:#1a1a2e;">Perfil setorial: </span>'
        f'<span style="color:#374151;">{adv_text}'
        f' <strong>{maior_simp}</strong> tem maior adesão ao Simples Nacional'
        f' ({val_maior:.1f}% vs. {val_menor:.1f}% em {menor_simp}),'
        f' refletindo predominância de micro e pequenas empresas no ecossistema regional.</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
