import pandas as pd

print("Carregando datasets...")
df_estab = pd.read_csv(r'D:/Análise_Empresas_Software/software_brasil_completo.csv', dtype=str)
df_simples = pd.read_csv(r'D:/Análise_Empresas_Software/simples_software.csv', dtype=str)

print(f"Estabelecimentos: {len(df_estab)} registros")
print(f"Simples: {len(df_simples)} registros")

# Cruzamento pelo cnpj_basico
df_final = df_estab.merge(df_simples, on='cnpj_basico', how='left')

# Preenche empresas sem registro no Simples
df_final['opcao_simples'] = df_final['opcao_simples'].fillna('N')
df_final['opcao_mei'] = df_final['opcao_mei'].fillna('N')

print(f"\nDataset final: {len(df_final)} registros")
print(f"\nDistribuição Simples Nacional:")
print(df_final['opcao_simples'].value_counts())
print(f"\nDistribuição MEI:")
print(df_final['opcao_mei'].value_counts())

df_final.to_csv(r'D:/Análise_Empresas_Software/dataset_final.csv', index=False)
print("\nDataset final salvo!")