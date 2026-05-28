#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar se a API key do YouTube funciona.
"""

import requests

API_KEY = 'AIzaSyDMnQjY94YAKcOkJS9fG9q1TQMcj3sU9Hw'

def check_api_key():
    """Verifica se a API key é válida fazendo uma requisição simples."""
    url = 'https://www.googleapis.com/youtube/v3/videos'
    params = {
        'part': 'snippet',
        'id': 'dQw4w9WgXcQ',  # Um vídeo qualquer do YouTube
        'key': API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            print("API key válida!")
            data = response.json()
            if 'items' in data and len(data['items']) > 0:
                print(f"Título do vídeo: {data['items'][0]['snippet']['title']}")
            return True
        elif response.status_code == 403:
            print("API key inválida ou sem permissões.")
            return False
        else:
            print(f"Erro: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Erro ao verificar API key: {e}")
        return False

if __name__ == '__main__':
    check_api_key()
