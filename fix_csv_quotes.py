#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script para remover aspas extras do CSV"""

import pandas as pd
import re

csv_path = "data/master_taf_consolidado.csv"

try:
    # Ler arquivo com baixa nível para manipular aspas
    with open(csv_path, 'r', encoding='utf-8') as f:
        linhas = f.readlines()
    
    linhas_corrigidas = []
    for linha in linhas:
        # Remover aspas extras: "XX""" -> XX
        linha_corrigida = re.sub(r'"(\d+)"""+', r'\1', linha)
        # Remover aspas extras em formatos de tempo: "XX'YY""" -> XX'YY ou 1'02""" -> 1'02
        linha_corrigida = re.sub(r'"([0-9\'\s]+)"""+', r'\1', linha_corrigida)
        linhas_corrigidas.append(linha_corrigida)
    
    # Salvar
    with open(csv_path, 'w', encoding='utf-8') as f:
        f.writelines(linhas_corrigidas)
    
    print("✅ Arquivo corrigido com sucesso!")
    
    # Validar leitura
    df = pd.read_csv(csv_path)
    print(f"Total de registros: {len(df)}")
    
    # Verificar GIGLAHERBETE
    gigl = df[df['Nome'].str.upper().str.contains('GIGLAHERBETE', na=False)]
    if len(gigl) > 0:
        print("\n✅ GIGLAHERBETE encontrado:")
        print(f"  Natacao: {gigl['Natacao'].values[0]}")
        print(f"  Barra: {gigl['Barra'].values[0]}")
    else:
        print("\n❌ GIGLAHERBETE não encontrado")

except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
