#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para corrigir indentação do arquivo taf.py
Procura por linhas que não estão corretamente indentadas (múltiplos de 4) e tenta corrigir.
"""

import re
from pathlib import Path

file_path = Path("taf.py")

# Ler o arquivo
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Analisar indentação
print(f"Analisando {len(lines)} linhas...\n")

problemas = []
for i, line in enumerate(lines, 1):
    if not line.strip():  # Linhas vazias
        continue
    if line[0] not in (' ', '\t'):  # Sem indentação
        continue
    
    # Contar espaços no início
    match = re.match(r'^(\s+)', line)
    if match:
        spaces = len(match.group(1))
        # Verificar se é múltiplo de 4
        if spaces % 4 != 0:
            problemas.append({
                'lineno': i,
                'spaces': spaces,
                'content': line.strip()[:60],
                'line': line
            })

print(f"Encontradas {len(problemas)} linhas problemáticas:")
for p in problemas[:20]:
    print(f"  Linha {p['lineno']}: {p['spaces']} espaços - {p['content']}")

# Tentar corrigir automaticamente: arredondar para múltiplo de 4
if problemas:
    print(f"\nTentando corrigir automaticamente...")
    for p in problemas:
        # Arredondar para múltiplo de 4
        novo_spaces = (p['spaces'] // 4) * 4
        if novo_spaces != p['spaces'] and novo_spaces > 0:
            lineno = p['lineno'] - 1  # 0-indexed
            old_line = lines[lineno]
            # Remover espaços e re-adicionar quantidade correta
            stripped = old_line.lstrip()
            lines[lineno] = ' ' * novo_spaces + stripped
            print(f"  Linha {p['lineno']}: {p['spaces']} -> {novo_spaces} espaços")

# Salvar arquivo corrigido
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"\n✅ Arquivo salvo com {len(problemas)} correções!")
