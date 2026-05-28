#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testa a API key fornecida com diferentes endpoints da YouTube Data API v3.
"""

import requests
import os

API_KEY = os.getenv("YOUTUBE_API_KEY")
if not API_KEY:
    raise ValueError("YOUTUBE_API_KEY environment variable is not set")

def test_endpoint(url, params, name):
    """Testa um endpoint específico."""
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"\n{name}:")
        print(f"  URL: {url}")
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  Resultado: SUCESSO")
            data = response.json()
            if 'items' in data and len(data['items']) > 0:
                print(f"  Itens encontrados: {len(data['items'])}")
                if 'snippet' in data['items'][0]:
                    title = data['items'][0]['snippet'].get('title', 'N/A')
                    print(f"  Título: {title}")
        else:
            print(f"  Resultado: FALHA")
            if response.status_code == 403:
                print(f"  Motivo: API key inválida ou sem permissões")
            elif response.status_code == 400:
                print(f"  Motivo: Requisição inválida")
            else:
                print(f"  Motivo: {response.text[:100]}")
    except Exception as e:
        print(f"\n{name}:")
        print(f"  ERRO: {e}")

def main():
    print("=" * 70)
    print("TESTE DA API KEY DO YOUTUBE DATA API v3")
    print("=" * 70)
    print(f"\nAPI Key: {API_KEY[:20]}...")
    
    # Teste 1: Vídeo específico
    test_endpoint(
        'https://www.googleapis.com/youtube/v3/videos',
        {
            'part': 'snippet',
            'id': 'dQw4w9WgXcQ',
            'key': API_KEY
        },
        'Teste 1: Consultar vídeo específico'
    )
    
    # Teste 2: Canal
    test_endpoint(
        'https://www.googleapis.com/youtube/v3/channels',
        {
            'part': 'snippet,statistics',
            'id': 'UC_x5XG1OV2P6uZZ5FSM9Ttw',
            'key': API_KEY
        },
        'Teste 2: Consultar canal'
    )
    
    # Teste 3: Busca
    test_endpoint(
        'https://www.googleapis.com/youtube/v3/search',
        {
            'part': 'snippet',
            'q': 'frutas',
            'type': 'video',
            'maxResults': 5,
            'key': API_KEY
        },
        'Teste 3: Buscar vídeos'
    )
    
    # Teste 4: Categorias
    test_endpoint(
        'https://www.googleapis.com/youtube/v3/videoCategories',
        {
            'part': 'snippet',
            'regionCode': 'BR',
            'key': API_KEY
        },
        'Teste 4: Consultar categorias'
    )
    
    print("\n" + "=" * 70)
    print("ANÁLISE:")
    print("=" * 70)
    print("Se todos os testes falharem com HTTP 403:")
    print("  - API key inválida ou expirada")
    print("  - API YouTube Data API v3 não ativada no projeto")
    print("  - API key pertence a projeto diferente")
    print()
    print("SOLUÇÃO:")
    print("  1. Acesse: https://console.cloud.google.com/")
    print("  2. Selecione o projeto correto")
    print("  3. Ative 'YouTube Data API v3' em 'APIs & Services' > 'Library'")
    print("  4. Crie uma nova API key em 'Credentials'")
    print("  5. Use a nova API key nos scripts")
    print("=" * 70)

if __name__ == '__main__':
    main()
