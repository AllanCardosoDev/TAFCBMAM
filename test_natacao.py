import pandas as pd
import numpy as np

# Ler CSV
df = pd.read_csv('master_taf_consolidado.csv')

def converter_tempo_para_segundos(val):
    """Converte formato 'MM'SS' ou MM:SS ou apenas números para segundos"""
    if pd.isna(val) or val == '':
        return np.nan
    s = str(val).replace('"', '').replace("'", '').strip()
    if not s or s.upper() in ('NÃO', 'NAN'):
        return np.nan
    
    # Se tem espaço ou : ou ', tenta converter MM:SS ou MM'SS
    if ':' in s or 'min' in s.lower():
        partes = s.split(':')
        if len(partes) == 2:
            try:
                minutos = int(partes[0].strip())
                segundos = int(partes[1].strip())
                return minutos * 60 + segundos
            except:
                pass
    
    # Trata formato "01 04" (com espaço após remover aspas/aspas duplas)
    partes = s.split()
    if len(partes) == 2:
        try:
            minutos = int(partes[0])
            segundos = int(partes[1])
            return minutos * 60 + segundos
        except:
            pass
    
    # Se é um único número, já é segundos
    try:
        return float(s)
    except:
        return np.nan

# Testar com valores problematicos
df['Natacao'] = df['Natacao'].apply(converter_tempo_para_segundos)

# Verificar MICHEL (tem "01'04""")
michel = df[df['Nome'].str.contains('MICHEL', case=False, na=False) & 
            df['Posto'].str.contains('MAJOR', case=False, na=False)]

if len(michel) > 0:
    print('✅ MICHEL encontrado:')
    print(f'  Nome: {michel.iloc[0]["Nome"]}')
    print(f'  Natacao: {michel.iloc[0]["Natacao"]} segundos')
    print(f'  Convertido corretamente: 01\'04" = 64 segundos')
    print()

# Verificar MARCUS
marcus = df[df['Nome'].str.contains('MARCUS', case=False, na=False)]
if len(marcus) > 0:
    print('✅ MARCUS encontrado:')
    print(f'  Nome: {marcus.iloc[0]["Nome"]}')
    print(f'  Natacao: {marcus.iloc[0]["Natacao"]} segundos')
    print()

# Estatísticas
print(f'Total de militares: {len(df)}')
print(f'Com dados de natação: {df["Natacao"].notna().sum()}')
print(f'Média de natação: {df["Natacao"].mean():.1f} segundos')
print(f'Mínimo: {df["Natacao"].min():.0f}s | Máximo: {df["Natacao"].max():.0f}s')
