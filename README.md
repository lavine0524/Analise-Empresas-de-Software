# Análise do Setor de Software Brasileiro

Projeto de extensão acadêmica que mapeia e analisa o setor de software brasileiro a partir dos dados abertos de CNPJ da Receita Federal, com foco na desigualdade regional entre o Nordeste e o restante do país.

**Vínculo:** Estruture Negócios | UFPB 2026
**Fonte dos dados:** Receita Federal do Brasil — Dados Abertos CNPJ (fev/2026)

---

## Contexto

O projeto investiga a hipótese central do programa Estruture Negócios: o Nordeste é estruturalmente sub-representado no ecossistema de software brasileiro, não por falta de resiliência dos empreendedores, mas por ausência de acesso a mercado, capital e infraestrutura.

---

## Principais Achados

### 1. Concentração Geográfica Extrema
São Paulo sozinho ultrapassa 120.000 empresas de software ativas — mais do que todos os outros estados somados. O bloco MG, PR, RJ, SC e RS forma um segundo grupo com 15.000–22.000 empresas cada.

### 2. O Nordeste Tem 28% da População, mas Apenas 8,4% das Empresas

| Região | % das empresas ativas |
|--------|----------------------|
| Sudeste | 66,8% |
| Sul | 17,0% |
| Nordeste | 8,4% |
| Centro-Oeste | 6,1% |
| Norte | 1,7% |

Nenhum estado nordestino entra no top 7 nacional. CE (8º), BA (10º) e PE (11º) são os mais representativos. A Paraíba aparece na 14ª posição.

### 3. Resultado Contraintuitivo: Empresas Nordestinas Sobrevivem Mais

| Região | % de empresas ativas |
|--------|---------------------|
| Sul | 58,5% |
| Norte | 58,5% |
| Nordeste | 57,4% |
| Centro-Oeste | 56,4% |
| Sudeste | 52,9% |

O problema do ecossistema nordestino **não é que as empresas fecham mais** — é que **poucas são abertas**. A questão é estrutural, não de competência.

### 4. O Nordeste Está Preso no Modelo de Serviço, Não de Produto
Os CNAEs dominantes na região são suporte técnico em TI, desenvolvimento sob encomenda e consultoria — modelos que não escalam. Software customizável e não-customizável (com potencial de produto) aparecem apenas em 4º e 5º lugar.

### 5. A Digitalização Pós-2020 Ampliou, Não Reduziu, a Desigualdade

| Período | Sudeste (aprox./ano) | Nordeste (aprox./ano) | Gap absoluto |
|---------|---------------------|----------------------|--------------|
| 2019 | ~8.000 | ~800 | ~7.200 |
| 2024 | ~21.000 | ~3.500 | ~17.500 |

A pandemia funcionou como catalisador para todas as regiões, mas o Sudeste cresceu proporcionalmente mais em termos absolutos — reforçando que a desigualdade é estrutural e persistente.

---

## CNAEs Considerados

| Código | Descrição |
|--------|-----------|
| 6201500 / 6201501 | Desenvolvimento de software sob encomenda |
| 6201502 | Web design |
| 6202300 | Desenvolvimento de software customizável |
| 6203100 | Desenvolvimento de software não-customizável |
| 6204000 | Consultoria em tecnologia da informação |
| 6209100 | Suporte técnico e manutenção em TI |

---

## Estrutura do Projeto

```
.
├── filtrar.py              # Filtra os arquivos brutos da Receita Federal pelos CNAEs de software
├── processar_simples.py    # Extrai dados do Simples Nacional para os CNPJs de software
├── consolidar.py           # Combina os datasets em dataset_final.csv
├── explorar.py             # Exploração inicial dos dados brutos
├── analise.ipynb           # Notebook principal com análises e visualizações
├── software_brasil_completo.csv   # Estabelecimentos de software filtrados
├── software_estabelecimentos.csv  # Dataset intermediário de estabelecimentos
└── simples_software.csv           # Dados do Simples Nacional para empresas de software
```

> **Não incluídos no repositório:** arquivos brutos da Receita Federal (Estabelecimentos0-9, Simples/) e o dataset final consolidado (dataset_final.csv) — totalizando ~20 GB. Precisam ser obtidos diretamente nos [Dados Abertos do CNPJ](https://dados.rfb.gov.br/CNPJ/).

---

## Como Executar

### Requisitos

```bash
pip install pandas matplotlib seaborn jupyter
```

### Pipeline de dados

Execute os scripts na ordem abaixo para gerar o dataset final a partir dos arquivos brutos:

```bash
python filtrar.py           # → software_brasil_completo.csv
python processar_simples.py # → simples_software.csv
python consolidar.py        # → dataset_final.csv
```

### Análise

```bash
jupyter notebook analise.ipynb
```

---

## Observações Técnicas

- Arquivos brutos da Receita Federal usam encoding `latin-1`; CSVs processados usam `UTF-8`
- A leitura dos arquivos brutos é feita em chunks de 100.000 linhas para controle de memória
- O join entre os datasets é feito pela coluna `cnpj_basico` (CNPJ sem sufixo de filial)
- O dado de 2025 no notebook deve ser tratado como parcial — empresas abertas recentemente podem não ter situação cadastral consolidada no dataset de fev/2026
