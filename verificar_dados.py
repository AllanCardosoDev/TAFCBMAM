import pandas as pd

df = pd.read_csv('master_taf_consolidado.csv')
print(f'✓ Registros carregados: {len(df)}')
print(f'✓ Colunas no arquivo: {len(df.columns)}')
print(f'✓ NOME: {df["NOME"].notna().sum()}/{len(df)}')
print(f'✓ CORRIDA: {df["CORRIDA"].notna().sum()}/{len(df)}')
print(f'✓ SEXO: {df["Sexo"].notna().sum()}/{len(df)}')
print(f'✓ IDADE: {df["Idade"].notna().sum()}/{len(df)}')
print(f'✓ DATA NASCIMENTO: {df["Data de Nascimento"].notna().sum()}/{len(df)}')
print(f'✓ CPF: {df["CPF"].notna().sum()}/{len(df)}')
