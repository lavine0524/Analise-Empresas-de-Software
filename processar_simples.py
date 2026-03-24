import pandas as pd

# Colunas do arquivo Simples Nacional
colunas_simples = [
    'cnpj_basico',
    'opcao_simples',
    'data_opcao_simples',
    'data_exclusao_simples',
    'opcao_mei',
    'data_opcao_mei',
    'data_exclusao_mei'
]

# Lê os CNPJs do nosso dataset de software
print("Carregando dataset de software...")
df_software = pd.read_csv(
    r'D:/Análise_Empresas_Software/software_brasil_completo.csv',
    dtype=str,
    usecols=['cnpj_basico']
)
cnpjs_software = set(df_software['cnpj_basico'].unique())
print(f"{len(cnpjs_software)} CNPJs únicos no dataset de software")

# Filtra o Simples só para empresas de software
print("\nProcessando arquivo do Simples...")
chunks = []
for i, chunk in enumerate(pd.read_csv(
    r'D:/Análise_Empresas_Software/Simples/F.K03200$W.SIMPLES.CSV.D60214',
    sep=';',
    names=colunas_simples,
    encoding='latin-1',
    chunksize=100000,
    dtype=str
)):
    filtrado = chunk[chunk['cnpj_basico'].isin(cnpjs_software)]
    chunks.append(filtrado)
    print(f"Chunk {i+1} processado...")

resultado = pd.concat(chunks)
resultado.to_csv(r'D:/Análise_Empresas_Software/simples_software.csv', index=False)
print(f"\nConcluído! {len(resultado)} registros encontrados.")