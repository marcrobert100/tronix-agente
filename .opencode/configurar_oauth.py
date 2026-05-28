#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para configurar OAuth 2.0 para a API do YouTube.
"""

import os
import webbrowser

def create_oauth_config():
    """Cria um arquivo de configuração OAuth 2.0 simulado."""
    
    # Instruções detalhadas
    instructions = """
=== CONFIGURAÇÃO DO OAuth 2.0 PARA API DO YOUTUBE ===

PARA FAZER UPLOAD DE VÍDEOS, VOCÊ PRECISA CONFIGURAR OAuth 2.0:

1. Acesse o Google Cloud Console:
   https://console.cloud.google.com/

2. Crie um novo projeto ou selecione um existente:
   - Clique no seletor de projetos no topo
   - Clique em "Novo Projeto"
   - Nome: "YouTube Upload Tool"
   - Clique em "Criar"

3. Ative a API do YouTube Data API v3:
   - Vá para "APIs & Services" > "Library"
   - Pesquise por "YouTube Data API v3"
   - Clique em "Enable"

4. Crie credenciais OAuth 2.0:
   - Vá para "APIs & Services" > "Credentials"
   - Clique em "Create Credentials" > "OAuth client ID"
   - Selecione "Desktop app" como tipo de aplicativo
   - Nome: "YouTube Upload Desktop"
   - Clique em "Create"

5. Baixe o arquivo de credenciais:
   - Após criar, clique em "Download JSON"
   - Salve o arquivo como 'client_secret.json' na pasta:
     C:\\xampp\\htdocs\\agente\\.opencode

6. Execute o script de upload:
   - Abra o terminal nesta pasta
   - Execute: python youtube_upload.py
   - Siga as instruções no navegador para autorizar o acesso

=== IMPORTANTE ===
- NUNCA compartilhe o arquivo client_secret.json
- Mantenha-o seguro e não commit no repositório
- A API key fornecida é apenas para consultas, não para upload

=== VERIFICAÇÃO APÓS CONFIGURAÇÃO ===
Após baixar o client_secret.json, execute:
   python youtube_upload.py

Se tudo estiver correto, o navegador abrirá para autorizar o acesso.
"""

    print(instructions)
    
    # Salva as instruções em um arquivo
    with open('OAUTH_CONFIG_PASSOS.txt', 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print("\n[OK] Instrucoes salvas em: OAUTH_CONFIG_PASSOS.txt")
    
    # Abre o Google Cloud Console no navegador
    try:
        webbrowser.open('https://console.cloud.google.com/')
        print("[OK] Abrindo Google Cloud Console no navegador...")
    except:
        print("[X] Nao foi possivel abrir o navegador automaticamente")
        print("     Abra manualmente: https://console.cloud.google.com/")

def check_files():
    """Verifica os arquivos necessários."""
    print("\n=== VERIFICAÇÃO DE ARQUIVOS ===")
    
    files_to_check = [
        ('youtube_upload.py', 'Script principal para upload'),
        ('client_secret.json', 'Credenciais OAuth 2.0 (NÃO ENCONTRADO)'),
        ('OAUTH_CONFIG_PASSOS.txt', 'Instruções de configuração')
    ]
    
    for filename, description in files_to_check:
        if os.path.exists(filename):
            print(f"[OK] {filename} - {description}")
        else:
            print(f"[X] {filename} - {description}")

def main():
    print("=" * 60)
    print("CONFIGURAÇÃO DO OAuth 2.0 PARA UPLOAD NO YOUTUBE")
    print("=" * 60)
    
    create_oauth_config()
    check_files()
    
    print("\n" + "=" * 60)
    print("PRÓXIMOS PASSOS:")
    print("1. Siga as instruções no arquivo OAUTH_CONFIG_PASSOS.txt")
    print("2. Baixe o client_secret.json do Google Cloud Console")
    print("3. Salve na pasta atual")
    print("4. Execute: python youtube_upload.py")
    print("=" * 60)

if __name__ == '__main__':
    main()
