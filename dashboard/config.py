from pathlib import Path

ROOT = Path(__file__).parent.parent
DATASET_PATH = ROOT / "dataset_final.csv"

REGIOES: dict[str, list[str]] = {
    "Norte":        ["AM", "RR", "AP", "PA", "TO", "RO", "AC"],
    "Nordeste":     ["MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA"],
    "Centro-Oeste": ["MT", "MS", "GO", "DF"],
    "Sudeste":      ["SP", "RJ", "MG", "ES"],
    "Sul":          ["PR", "SC", "RS"],
}
UF_REGIAO: dict[str, str] = {uf: reg for reg, ufs in REGIOES.items() for uf in ufs}

NORDESTE_ESTADOS: dict[str, str] = {
    "Maranhão":     "MA", "Piauí":      "PI", "Ceará":      "CE",
    "Rio G. Norte": "RN", "Paraíba":    "PB", "Pernambuco": "PE",
    "Alagoas":      "AL", "Sergipe":    "SE", "Bahia":      "BA",
}
NOME_ESTADO: dict[str, str] = {v: k for k, v in NORDESTE_ESTADOS.items()}

CORES: dict[str, str] = {
    "Nordeste":     "#e05c2b",
    "Sudeste":      "#2563eb",
    "Sul":          "#16a34a",
    "Norte":        "#7c3aed",
    "Centro-Oeste": "#ca8a04",
}
COR_NE   = "#e05c2b"
COR_OUTR = "#94a3b8"

CORES_NE: list[str] = [
    "#e05c2b", "#f97316", "#eab308", "#22c55e",
    "#14b8a6", "#3b82f6", "#8b5cf6", "#ec4899", "#64748b",
]

MAPA_CNAE: dict[str, str] = {
    "6201500": "Desenv. sob encomenda",
    "6201501": "Desenv. sob encomenda",
    "6202300": "Software customizável",
    "6203100": "Software não-customizável",
    "6204000": "Consultoria em TI",
    "6209100": "Suporte técnico/TI",
    "6201502": "Web design",
}

MAPA_SITUACAO: dict[str, str] = {
    "01": "Nula", "02": "Ativa", "03": "Suspensa",
    "04": "Inapta", "08": "Baixada",
}

COORTES: list[int] = [2008, 2010, 2012, 2015, 2018, 2020, 2022]

LAYOUT_BASE: dict = dict(
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(size=13, color="#1a1a2e"),
    xaxis=dict(gridcolor="#e5e7eb", linecolor="#e5e7eb"),
    yaxis=dict(gridcolor="#e5e7eb", linecolor="#e5e7eb"),
    margin=dict(l=10, r=10, t=40, b=10),
    hoverlabel=dict(font_size=15, bgcolor="white", bordercolor="#e5e7eb"),
)

SUBTITULO_STYLE = (
    'color:#6b7280; font-size:0.93rem; margin-top:-8px; margin-bottom:4px;'
)

FONTE_DADOS = "Fonte: Receita Federal do Brasil — Estabelecimentos CNPJ, fev/2026"


def fmt_br(valor: float, dec: int = 1) -> str:
    """Formata número no locale pt-BR (vírgula como separador decimal)."""
    return f"{valor:.{dec}f}".replace(".", ",")
