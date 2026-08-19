# Análise do Setor de Software Brasileiro

Projeto analítico e de extensão acadêmica que mapeia o ecossistema e a dinâmica das empresas de software no Brasil a partir dos microdados de Estabelecimentos CNPJ da Receita Federal, com foco analítico nas assimetrias regionais entre o Nordeste e os demais polos do país.

**Vínculo Acadêmico:** Projeto de Extensão Estruture Negócios — UFPB 2026  
**Fonte Primária:** Receita Federal do Brasil — Dados Abertos de Estabelecimentos CNPJ (Fevereiro/2026)  
**Aplicação Interativa:** [Acessar Dashboard no Render](https://analise-empresas-de-software-1.onrender.com)  

---

## 🎯 Contexto e Hipótese de Pesquisa

O projeto investiga a hipótese central do programa **Estruture Negócios**: o Nordeste brasileiro apresenta uma sub-representação quantitativa severa no ecossistema de base tecnológica nacional. Contudo, essa disparidade decorre de barreiras estruturais de acesso a capital, infraestrutura e mercados centrais, e **não** de menor resiliência ou eficiência operacional dos empreendimentos locais.

---

## 📊 Principais Indicadores e Achados Empíricos

O universo analisado compreende **479.071 estabelecimentos de software** registrados no território nacional (excluindo registros do exterior).

### 1. Panorama Geral Consolidado

| Indicador | Valor Nacional | Destaque Nordeste | Destaque Sudeste |
| :--- | :---: | :---: | :---: |
| **Total de Estabelecimentos** | 479.071 | 40.089 (8,4%) | 320.019 (66,8%) |
| **Taxa Média de Atividade** | 54,5% | 57,4% | 52,9% |
| **Adesão ao Simples Nacional** | — | 42,7% | 39,5% |
| **Tempo Mediano de Vida (Baixadas)** | — | 4,1 anos | 5,6 anos |

---

### 2. Concentração e Distribuição Regional

| Região | % das Empresas no Ecossistema | Taxa de Empresas Ativas (%) | Tempo Mediano de Vida (Baixadas) |
| :--- | :---: | :---: | :---: |
| **Sudeste** | 66,8% | 52,9% | 5,6 anos |
| **Sul** | 17,0% | 58,5% | 4,2 anos |
| **Nordeste** | 8,4% | 57,4% | 4,1 anos |
| **Centro-Oeste** | 6,1% | 56,4% | — |
| **Norte** | 1,7% | 58,5% | — |

* **Hiperconcentração em São Paulo:** O estado de São Paulo concentra sozinho um volume que supera em várias vezes a totalidade dos 9 estados nordestinos combinados.
* **Hiperprimazia das Capitais no Nordeste:** Enquanto estados do Sul distribuem empresas por polos regionais e cidades secundárias, os estados nordestinos concentram, em média, a maioria expressiva de seus negócios na capital (liderados por Aracaju/SE e Fortaleza/CE).

---

### 3. Análise Intra-Nordeste (Detalhamento por Estado)

Distribuição do ecossistema entre os 9 estados da região Nordeste:

| Estado (UF) | Volume de Empresas | Taxa de Atividade (%) | Adesão ao Simples Nacional (%) |
| :--- | :---: | :---: | :---: |
| **Bahia (BA)** | 9.603 | 50,0% | 38,2% |
| **Ceará (CE)** | 9.086 | 62,4% | 46,9% |
| **Pernambuco (PE)** | 8.483 | 53,9% | 38,3% |
| **Paraíba (PB)** | 3.242 | 63,7% | 48,0% |
| **Rio Grande do Norte (RN)** | 2.560 | 62,9% | 48,9% |
| **Maranhão (MA)** | 2.269 | 60,0% | 43,5% |
| **Sergipe (SE)** | 1.806 | 55,7% | 40,1% |
| **Alagoas (AL)** | 1.792 | 57,4% | 40,7% |
| **Piauí (PI)** | 1.472 | 69,2% | 52,9% |

> **Paradoxo da Sobrevivência:** O Nordeste exibe taxa de atividade e sobrevivência por coorte superior à do Sudeste (ex: na coorte histórica de 2008). No entanto, o volume de empresas abertas no Sudeste é expressivamente maior, demonstrando que o gargalo regional é de **capacidade de criação e acesso**, não de resiliência.

---

### 4. Perfil Setorial e Taxa de Mortalidade por Segmento (CNAE)

| Segmento / Atividade Econômica | Taxa de Mortalidade (% Baixadas) | Participação no Nordeste | Participação no Sudeste |
| :--- | :---: | :---: | :---: |
| **Software não-customizável** | 47,8% | 7,6% | 7,7% |
| **Suporte técnico em TI** | 38,8% | 31,0% | 33,5% |
| **Desenvolvimento sob encomenda** | 37,6% | 25,6% | 23,5% |
| **Consultoria em TI** | 34,9% | 20,5% | 25,7% |
| **Software customizável** | 24,1% | 13,4% | 8,2% |
| **Web design** | 22,3% | 1,9% | — |

* **Presença Digital e Formalização:** O Nordeste registra 79,5% de e-mail e 90,3% de telefone cadastrados na Receita Federal, comparado a 78,4% (e-mail) e 89,2% (telefone) no Sudeste.

---

## 🏷️ Classificação CNAE Utilizada

| Código CNAE | Denominação Oficial |
| :--- | :--- |
| **6201-5/00** | Desenvolvimento de programas de computador sob encomenda |
| **6201-5/01** | Desenvolvimento de programas de computador sob encomenda (detalhado) |
| **6201-5/02** | Web design |
| **6202-3/00** | Desenvolvimento e licenciamento de programas customizáveis |
| **6203-1/00** | Desenvolvimento e licenciamento de programas não-customizáveis |
| **6204-0/00** | Consultoria em tecnologia da informação |
| **6209-1/00** | Suporte técnico, manutenção e outros serviços em TI |

---

## 🛠️ Estrutura do Repositório

```text
.
├── app.py                     # Página principal da aplicação Streamlit (Home/KPIs)
├── config.py                  # Configurações globais, paletas e mapeamentos
├── dataset_final.parquet      # Base tratada e compactada (~479 mil registros)
├── requirements.txt           # Dependências de execução
└── pages/                     # Visões analíticas segmentadas
    ├── 1_Distribuicao_Geografica.py
    ├── 2_Dinamica_Temporal.py
    ├── 3_Mortalidade_Empresarial.py
    ├── 4_Perfil_Setorial.py
    └── 5_Intra_Nordeste.py
```

---

## 🚀 Arquitetura de Dados e Otimização em Produção

O dashboard analítico foi desenvolvido em **Python + Streamlit + Plotly** e disponibilizado em ambiente de produção por meio do **Render**.

Devido à volumetria do dataset (aproximadamente 479 mil registros) e às restrições de memória do ambiente gratuito utilizado (512 MB de RAM), foram implementadas estratégias de otimização para reduzir o consumo de memória e garantir a estabilidade da aplicação em produção.

### Principais estratégias adotadas

1. **Leitura seletiva por projeção (`Projection Pushdown`)**

   Cada página do dashboard realiza a leitura apenas das colunas necessárias para sua respectiva análise, utilizando a seleção de colunas durante a leitura do arquivo Parquet. Dessa forma, evita-se o carregamento desnecessário de informações na memória.

2. **Tipagem categórica e otimização dos tipos de dados**

   Campos textuais com valores repetitivos, como `uf`, `regiao`, `situacao_cadastral` e categorias de análise, foram convertidos para tipos mais eficientes, incluindo `category` quando aplicável. Também foram realizados ajustes nos tipos numéricos para reduzir o consumo de memória durante a execução.

3. **Controle de cache do Streamlit**

   O mecanismo de cache foi configurado de forma controlada, utilizando `@st.cache_data(max_entries=1)` nas rotinas de carregamento de dados, evitando a retenção excessiva de objetos em memória durante a utilização do dashboard.

4. **Otimização para ambiente de produção**

   As otimizações foram realizadas após a identificação de falhas de execução no Render relacionadas ao limite de memória da instância gratuita. A aplicação chegou a apresentar erros `502` e encerramentos por **Out of Memory (OOM)**. Após a refatoração da leitura e do tratamento dos dados, o dashboard passou a operar de forma estável dentro dos recursos disponíveis.

### Resultado

O dashboard encontra-se **implantado e operacional no Render**, com navegação pelas diferentes visões analíticas e execução dos filtros e gráficos.

🌐 **Dashboard online:**  
https://analise-empresas-de-software-1.onrender.com

---

## 💻 Como Executar Localmente

### 1. Clone o repositório

```bash
git clone https://github.com/lavine0524/Analise-Empresas-de-Software.git
cd Analise-Empresas-de-Software
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Execute a aplicação

```bash
streamlit run app.py
```

Após a execução, o Streamlit disponibilizará a aplicação localmente no endereço indicado pelo terminal.

---

## 🌐 Deploy

A aplicação está hospedada no **Render** como um Web Service e utiliza o repositório GitHub como fonte do código.

**Status:** 🟢 Em produção

**Acesso:** https://analise-empresas-de-software-1.onrender.com
