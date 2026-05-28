#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para obter informações do canal usando a API key do YouTube.
"""

import requests

API_KEY = 'AIzaSyDMnQjY94YAKcOkJS9fG9q1TQMcj3sU9Hw'

def get_channel_info():
    """Obtém informações do canal usando a API key."""
    # Primeiro, precisamos do ID do canal. Vamos usar um canal popular para teste.
    channel_id = 'UC_x5XG1OV2P6uZZ5FSM9Ttw'  # Canal do Google Developers
    
    url = 'https://www.googleapis.com/youtube/v3/channels'
    params = {
        'part': 'snippet,statistics',
        'id': channel_id,
        'key': API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if 'items' in data and len(data['items']) > 0:
                channel = data['items'][0]
                print("Informações do canal:")
                print(f"  Título: {channel['snippet']['title']}")
                print(f"  Descrição: {channel['snippet']['description'][:100]}...")
                print(f"  Inscritos: {channel['statistics']['subscriberCount']}")
                print(f"  Vídeos: {channel['statistics']['videoCount']}")
                print(f"  Visualizações: {channel['statistics']['viewCount']}")
                return True
        elif response.status_code == 403:
            print("API key inválida ou sem permissões.")
            return False
        else:
            print(f"Erro: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Erro ao obter informações do canal: {e}")
        return False

def search_videos():
    """Busca vídeos usando a API key."""
    url = 'https://www.googleapis.com/youtube/v3/search'
    params = {
        'part': 'snippet',
        'q': 'frutas',
        'type': 'video',
        'maxResults': 5,
        'key': API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if 'items' in data and len(data['items']) > 0:
                print("\nVídeos encontrados sobre 'frutas':")
                for item in data['items']:
                    print(f"  - {item['snippet']['title']}")
                    print(f"    Canal: {item['snippet']['channelTitle']}")
                    print(f"    ID: {item['id']['videoId']}")
                return True
        elif response.status_code == 403:
            print("API key inválida ou sem permissões.")
            return False
        else:
            print(f"Erro: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Erro ao buscar vídeos: {e}")
        return False

if __name__ == '__main__':
    print("Verificando API key do YouTube...")
    if get_channel_info():
        print("\nAPI key funciona para leitura!")
        search_videos()
    else:
        print("\nAPI key não funciona.")
