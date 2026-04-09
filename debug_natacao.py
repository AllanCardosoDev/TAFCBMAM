import pandas as pd

df = pd.read_csv('master_taf_consolidado.csv')
michel = df[df['Nome'].str.contains('MICHEL', case=False, na=False) & df['Posto'].str.contains('MAJOR', case=False, na=False)]

if len(michel) > 0:
    val = michel.iloc[0]['Natacao']
    print(f'Valor original (repr): {repr(val)}')
    print(f'Valor (str): {str(val)}')
    print(f'Caracteres: {[c for c in str(val)]}')
    print(f'Comprimento: {len(str(val))}')
    print()
    print(f'Após remover aspas duplas: {repr(str(val).replace(chr(34), ""))}')
    print(f'Após remover aspas simples: {repr(str(val).replace(chr(34), "").replace(chr(39), ""))}')
