#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para o erro 'str' object has no attribute 'get'
"""

import sys
import traceback

def diagnosticar_erro():
    print("=== DIAGNOSTICO DE ERRO ===")
    print(f"Versao Python: {sys.version}")
    print()
    
    # Exemplo de codigo que causa o erro
    try:
        # ERRADO: Tentar usar .get() em uma string
        texto = "Hello World"
        valor = texto.get("chave")  # Isso vai falhar!
    except AttributeError as e:
        print("[OK] Erro identificado:")
        print(f"  {e}")
        print()
        print("Causa: Tentou usar .get() em uma string, mas .get() e para dicionarios.")
        print()
        print("Solucao:")
        print("  1. Se voce quer acessar um dicionario, use:")
        print("     dicionario = {'chave': 'valor'}")
        print("     valor = dicionario.get('chave')")
        print()
        print("  2. Se voce quer acessar um caractere em uma string:")
        print("     texto = 'Hello'")
        print("     caracter = texto[0]  # 'H'")
        print()
        print("  3. Se voce quer verificar se uma chave existe em um dicionario:")
        print("     if 'chave' in dicionario:")
        print("         valor = dicionario['chave']")
    
    print()
    print("=== VERIFICANDO SEU CÓDIGO ===")
    
    # Verificar se há arquivos Python problemáticos
    import os
    python_files = []
    for root, dirs, files in os.walk(r"C:\xampp\htdocs\agente"):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    
    print(f"Encontrados {len(python_files)} arquivos Python no diretório agente")
    
    # Procurar por .get() em strings
    problematic_files = []
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Procurar por padrões problemáticos
                if '.get(' in content:
                    # Verificar se é em uma string
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if '.get(' in line and ('"' in line or "'" in line):
                            problematic_files.append((file_path, i, line.strip()))
        except:
            pass
    
    if problematic_files:
        print("\n⚠ Arquivos com potencial problema de .get():")
        for file_path, line_num, line in problematic_files[:5]:  # Mostrar apenas 5
            print(f"  {file_path}:{line_num}")
            print(f"    {line}")
    else:
        print("\n✓ Nenhum arquivo problemático encontrado")

if __name__ == "__main__":
    diagnosticar_erro()