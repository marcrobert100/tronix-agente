#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para configurar OAuth 2.0 para a API do YouTube.
"""

import os
import webbrowser
import json

def create_oauth_instructions():
    """Cria instruções para configurar OAuth 2.0."""
    
    instructions = """
=== CONFIGURAÇÃO DO OAuth 2.0 PARA API DO YOUTUBE ===

Para fazer upload de vídeos para o YouTube, você precisa configurar OAuth 2.0:

1. Acesse o Google Cloud Console:
   https://console.cloud.google.com/

2. Crie um novo projeto ou selecione um existente.

3. Ative a API do YouTube Data API v3:
   - Vá para "APIs & Services" > "Library"
   - Pesquise por "YouTube Data API v3"
   - Clique em "Enable"

4. Crie credenciais OAuth 2.0:
   - Vá para "APIs & Services" > "Credentials"
   - Clique em "Create Credentials" > "OAuth client ID"
   - Selecione "Desktop app" como tipo de aplicativo
   - Dê um nome ao cliente OAuth (ex: "YouTube Upload Tool")
   - Clique em "Create"

5. Baixe o arquivo de credenciais:
   - Após criar, clique em "Download JSON"
   - Salve o arquivo como 'client_secret.json' na pasta atual

6. Execute o script de upload:
   - Execute: python youtube_upload.py
   - Siga as instruções no navegador para autorizar o acesso

=== IMPORTANTE ===
- NUNCA compartilhe o arquivo client_secret.json
- Mantenha-o seguro e não commit no repositório
- A API key que você forneceu é apenas para consultas, não para upload

=== ARQUIVOS NECESSÁRIOS ===
- client_secret.json (do Google Cloud Console)
- youtube_upload.py (já criado)
"""
    
    print(instructions)
    
    # Salva as instruções em um arquivo
    with open('YOUTUBE_OAUTH_SETUP.txt', 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print("\nInstruções salvas em: YOUTUBE_OAUTH_SETUP.txt")

def check_required_files():
    """Verifica se os arquivos necessários existem."""
    files = {
        'youtube_upload.py': 'Script principal para upload',
        'youtube_check.py': 'Script para verificar API key'
    }
    
    print("\n=== VERIFICACAO DE ARQUIVOS ===")
    for file, description in files.items():
        if os.path.exists(file):
            print(f"[OK] {file} - {description}")
        else:
            print(f"[X] {file} - NAO ENCONTRADO")
    
    if not os.path.exists('client_secret.json'):
        print(f"[X] client_secret.json - NAO ENCONTRADO (necessario para OAuth)")
    else:
        print(f"[OK] client_secret.json - Encontrado")

if __name__ == '__main__':
    create_oauth_instructions()
    check_required_files()
