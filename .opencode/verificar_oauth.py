#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar se OAuth 2.0 foi configurado corretamente.
"""

import os
import json

def verificar_client_secret():
    """Verifica se o arquivo client_secret.json existe e é válido."""
    arquivo = 'client_secret.json'
    
    if not os.path.exists(arquivo):
        print(f"[X] Arquivo '{arquivo}' não encontrado.")
        return False
    
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Verifica se tem as chaves necessárias
        if 'installed' in data:
            client_id = data['installed'].get('client_id', '')
            if client_id:
                print(f"[OK] Arquivo '{arquivo}' encontrado e válido.")
                print(f"     Client ID: {client_id[:20]}...")
                return True
        elif 'web' in data:
            client_id = data['web'].get('client_id', '')
            if client_id:
                print(f"[OK] Arquivo '{arquivo}' encontrado e válido.")
                print(f"     Client ID: {client_id[:20]}...")
                return True
        else:
            print(f"[X] Arquivo '{arquivo}' inválido (formato desconhecido).")
            return False
    except json.JSONDecodeError:
        print(f"[X] Arquivo '{arquivo}' contém JSON inválido.")
        return False
    except Exception as e:
        print(f"[X] Erro ao ler arquivo: {e}")
        return False

def verificar_credenciais():
    """Verifica se as credenciais salvas existem."""
    arquivo = 'credentials.json'
    
    if os.path.exists(arquivo):
        print(f"[OK] Arquivo '{arquivo}' encontrado (credenciais salvas).")
        return True
    else:
        print(f"[X] Arquivo '{arquivo}' não encontrado (será criado após autorização).")
        return False

def main():
    print("=" * 60)
    print("VERIFICAÇÃO DO OAuth 2.0")
    print("=" * 60)
    
    print("\n1. Verificando client_secret.json:")
    client_secret_ok = verificar_client_secret()
    
    print("\n2. Verificando credentials.json:")
    credentials_ok = verificar_credenciais()
    
    print("\n" + "=" * 60)
    if client_secret_ok:
        print("STATUS: OAuth 2.0 configurado corretamente!")
        print("PRÓXIMO PASSO: Execute 'python youtube_upload.py'")
    else:
        print("STATUS: OAuth 2.0 não configurado.")
        print("PRÓXIMO PASSO: Execute 'python configurar_oauth.py'")
    print("=" * 60)

if __name__ == '__main__':
    main()
