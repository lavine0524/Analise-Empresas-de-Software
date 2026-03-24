import pandas as pd

df = pd.read_csv(r'D:/Análise_Empresas_Software/software_estabelecimentos.csv', dtype=str)

print(f"Total de registros: {len(df)}")
print(f"\nDistribuição por UF:")
print(df['uf'].value_counts())
print(f"\nDistribuição por situação cadastral:")
print(df['situacao_cadastral'].value_counts())
print(f"\nDistribuição por CNAE:")
print(df['cnae_fiscal_principal'].value_counts())