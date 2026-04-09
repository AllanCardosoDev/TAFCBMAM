import pandas as pd
import numpy as np

# Ler CSV
df = pd.read_csv('master_taf_consolidado.csv')

# Limpar NATACAO_SEG (mesmo código que no taf.py)
df['Natacao'] = df['Natacao'].astype(str).str.replace('"', '', regex=False).str.replace("'", '', regex=False).str.strip()
df['Natacao'] = df['Natacao'].str.extract(r'(\d+)', expand=False)
df['Natacao'] = pd.to_numeric(df['Natacao'], errors='coerce')

# Verificar MARCUS
marcus = df[df['Nome'].str.contains('MARCUS', case=False, na=False)]
if len(marcus) > 0:
    print('✅ MARCUS encontrado:')
    print(f'  Nome: {marcus.iloc[0]["Nome"]}')
    print(f'  Corrida: {marcus.iloc[0]["Corrida"]}')
    print(f'  Abdominal: {marcus.iloc[0]["Abdominal"]}')
    print(f'  Flexao: {marcus.iloc[0]["Flexao"]}')
    print(f'  Natacao (segundos): {marcus.iloc[0]["Natacao"]}')
    print(f'  Barra: {marcus.iloc[0]["Barra"]}')
    print()

# Estatísticas
print(f'Total de militares: {len(df)}')
print(f'Com dados da natação: {df["Natacao"].notna().sum()}')
print(f'Média de natação: {df["Natacao"].mean():.1f} segundos')
print(f'Primeiros valores de Natacao: {df["Natacao"].dropna().head(10).tolist()}')
