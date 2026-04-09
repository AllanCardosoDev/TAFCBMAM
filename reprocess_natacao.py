import pandas as pd
import numpy as np

def converter_tempo_para_segundos(val):
    """Converte formato 'MM'SS' ou MM:SS ou apenas números para segundos"""
    if pd.isna(val) or val == '':
        return np.nan
    s = str(val).strip()
    if not s or s.upper() in ('NÃO', 'NAN'):
        return np.nan
    
    # Remove aspas
    s = s.replace('"', '').replace("'", '')
    
    # Trata formato "01 04" (minutos e segundos separados)
    partes = s.split()
    if len(partes) >= 2:
        try:
            minutos = int(partes[0])
            segundos = int(partes[1])
            return minutos * 60 + segundos
        except:
            pass
    
    # Se tem 4 dígitos, pode ser "0104" = 1 min 4 seg
    if len(s) == 4 and s.isdigit():
        try:
            minutos = int(s[:2])
            segundos = int(s[2:])
            if minutos < 60 and segundos < 60:
                return minutos * 60 + segundos
        except:
            pass
    
    # Senão, é número puro (segundos)
    try:
        return float(s)
    except:
        return np.nan

# Ler o CSV consolidado
print("Lendo master_taf_consolidado.csv...")
df = pd.read_csv('master_taf_consolidado.csv')

# Reprocess Natacao com a função corrigida
print("Reprocessando coluna Natacao...")
df['Natacao'] = df['Natacao'].apply(converter_tempo_para_segundos)

# Verificar o resultado
print(f"Valores únicos de Natacao (primeiros 20): {sorted(df['Natacao'].dropna().unique())[:20]}")

# MICHEL agora deve ter 64
michel = df[df['Nome'].str.contains('MICHEL', case=False, na=False) & df['Posto'].str.contains('MAJOR', case=False, na=False)]
if len(michel) > 0:
    print(f"✅ MICHEL: {michel.iloc[0]['Natacao']} segundos (esperado: 64)")

# Salvar
print("Salvando...")
df.to_csv('master_taf_consolidado.csv', index=False)
print("✅ master_taf_consolidado.csv atualizado!")
