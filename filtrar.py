import pandas as pd
import os

colunas = [
    'cnpj_basico', 'cnpj_ordem', 'cnpj_dv', 'identificador_matriz_filial',
    'nome_fantasia', 'situacao_cadastral', 'data_situacao_cadastral',
    'motivo_situacao_cadastral', 'nome_cidade_exterior', 'pais',
    'data_inicio_atividade', 'cnae_fiscal_principal', 'cnae_fiscal_secundaria',
    'tipo_logradouro', 'logradouro', 'numero', 'complemento', 'bairro',
    'cep', 'uf', 'municipio', 'ddd1', 'telefone1', 'ddd2', 'telefone2',
    'ddd_fax', 'fax', 'correio_eletronico', 'situacao_especial',
    'data_situacao_especial'
]

cnaes_software = [
    '6201500', '6201501', '6201502',
    '6202300', '6203100', '6204000', '6209100'
]

pasta_base = r'D:/Análise_Empresas_Software'
todos_chunks = []

for n in range(10):
    pasta = os.path.join(pasta_base, f'Estabelecimentos{n}')
    arquivo = [f for f in os.listdir(pasta) if f.endswith('ESTABELE')][0]
    caminho = os.path.join(pasta, arquivo)
    
    print(f"\n--- Processando Estabelecimentos{n} ---")
    for i, chunk in enumerate(pd.read_csv(
        caminho, sep=';', names=colunas,
        encoding='latin-1', chunksize=100000, dtype=str
    )):
        filtrado = chunk[chunk['cnae_fiscal_principal'].isin(cnaes_software)]
        todos_chunks.append(filtrado)
        print(f"Chunk {i+1} processado...")

resultado = pd.concat(todos_chunks)
saida = os.path.join(pasta_base, 'software_brasil_completo.csv')
resultado.to_csv(saida, index=False)
print(f"\nConcluído! {len(resultado)} empresas encontradas no total.")