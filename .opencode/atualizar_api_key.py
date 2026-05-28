#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para atualizar a API key nos scripts.
"""

import os
import re

def update_api_key_in_file(filename, new_api_key):
    """Atualiza a API key em um arquivo Python."""
    if not os.path.exists(filename):
        print(f"Arquivo não encontrado: {filename}")
        return False
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Encontra a linha com a API key atual
        pattern = r"API_KEY\s*=\s*['\"]([^'\"]+)['\"]"
        matches = re.findall(pattern, content)
        
        if matches:
            old_api_key = matches[0]
            # Substitui a API key antiga pela nova
            updated_content = re.sub(
                pattern,
                f"API_KEY = '{new_api_key}'",
                content
            )
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print(f"[OK] API key atualizada em {filename}")
            print(f"     Antiga: {old_api_key[:20]}...")
            print(f"     Nova: {new_api_key[:20]}...")
            return True
        else:
            print(f"[X] API key não encontrada em {filename}")
            return False
    except Exception as e:
        print(f"[X] Erro ao atualizar {filename}: {e}")
        return False

def main():
    print("=" * 60)
    print("ATUALIZAR API KEY NOS SCRIPTS")
    print("=" * 60)
    
    # Pedir nova API key
    new_api_key = input("\nDigite a nova API key: ").strip()
    
    if not new_api_key:
        print("Nenhuma API key fornecida.")
        return
    
    # Arquivos para atualizar
    files_to_update = [
        'youtube_check.py',
        'youtube_channel_info.py'
    ]
    
    print(f"\nAtualizando API key em {len(files_to_update)} arquivos...")
    
    success_count = 0
    for filename in files_to_update:
        if update_api_key_in_file(filename, new_api_key):
            success_count += 1
    
    print(f"\n{success_count} de {len(files_to_update)} arquivos atualizados com sucesso.")
    
    if success_count > 0:
        print("\n[OK] API key atualizada em todos os scripts!")
        print("Execute 'python youtube_check.py' para verificar a nova API key.")
    else:
        print("\n[X] Nenhum arquivo foi atualizado.")

if __name__ == '__main__':
    main()
