import sys
sys.path.insert(0, 'c:\\Users\\User\\Desktop\\TAF\\TAFCBMAM-main')

# Simular a função exata do taf.py
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
    print(f"  Após remover aspas: {repr(s)}")
    
    # Trata formato "01 04" (minutos e segundos separados)
    partes = s.split()
    print(f"  Split por espaço: {partes}")
    if len(partes) >= 2:
        try:
            # Tenta se é "01 04" ou "01'04" (tem 1 min e 4 seg)
            minutos = int(partes[0])
            segundos = int(partes[1])
            resultado = minutos * 60 + segundos
            print(f"  → Interpretado como {minutos} min + {segundos} seg = {resultado} seg")
            return resultado
        except Exception as e:
            print(f"  → Erro no split: {e}")
            pass
    
    # Se tem dois dígitos separados por espaço após limpar
    # Exemplo: "0104" pode ser "01 04" = 1 min 4 seg
    print(f"  Checando len={len(s)} isdigit={s.isdigit()}")
    if len(s) == 4 and s.isdigit():
        try:
            minutos = int(s[:2])
            segundos = int(s[2:])
            if minutos < 60 and segundos < 60:  # Validar
                resultado = minutos * 60 + segundos
                print(f"  → Interpretado como {minutos} min + {segundos} seg = {resultado} seg")
                return resultado
        except Exception as e:
            print(f"  → Erro no parse: {e}")
            pass
    
    # Se é um único número, já é segundos
    try:
        resultado = float(s)
        print(f"  → Interpretado como {resultado} seg (número puro)")
        return resultado
    except:
        print(f"  → Não conseguiu parsear")
        return np.nan

# Testar com MICHEL
print("Testando: \"01'04\"")
val = "01'04\""
resultado = converter_tempo_para_segundos(val)
print(f"Resultado final: {resultado} segundos")
print()

# Testar com MARCUS
print("Testando: 32")
val = "32"
resultado = converter_tempo_para_segundos(val)
print(f"Resultado final: {resultado} segundos")
