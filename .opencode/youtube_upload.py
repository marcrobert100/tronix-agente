#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para upload de vídeos para o YouTube usando a API do YouTube Data API v3.
"""

import os
import json
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Configurações
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
CLIENT_SECRETS_FILE = 'client_secret.json'
CREDENTIALS_FILE = 'credentials.json'

def get_authenticated_service():
    """Autentica e retorna o serviço da API do YouTube."""
    credentials = None
    
    # Tenta carregar credenciais salvas
    if os.path.exists(CREDENTIALS_FILE):
        credentials = Credentials.from_authorized_user_file(CREDENTIALS_FILE, SCOPES)
    
    # Se não houver credenciais válidas, solicita nova autenticação
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRETS_FILE):
                print(f"Erro: Arquivo '{CLIENT_SECRETS_FILE}' não encontrado.")
                print("Baixe o arquivo de credenciais do Google Cloud Console.")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            credentials = flow.run_local_server(port=0)
        
        # Salva as credenciais para uso futuro
        with open(CREDENTIALS_FILE, 'w') as token:
            token.write(credentials.to_json())
    
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

def upload_video(youtube, file_path, title, description, category_id, privacy_status='private'):
    """Faz upload de um vídeo para o YouTube."""
    
    if not os.path.exists(file_path):
        print(f"Erro: Arquivo de vídeo não encontrado: {file_path}")
        return None
    
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': [],
            'categoryId': category_id
        },
        'status': {
            'privacyStatus': privacy_status,
            'selfDeclaredMadeForKids': False
        }
    }
    
    # Tamanho do arquivo em bytes
    size = os.path.getsize(file_path)
    
    media = MediaFileUpload(
        file_path,
        chunksize=-1,
        resumable=True,
        mimetype='video/*'
    )
    
    request = youtube.videos().insert(
        part='snippet,status',
        body=body,
        media_body=media
    )
    
    response = None
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                print(f"Progresso: {int(status.progress() * 100)}%")
        except Exception as e:
            print(f"Erro durante o upload: {e}")
            return None
    
    print(f"Upload concluído! ID do vídeo: {response['id']}")
    print(f"URL: https://www.youtube.com/watch?v={response['id']}")
    
    return response

def main():
    """Função principal."""
    # Configurações do vídeo
    VIDEO_PATH = r'C:\Users\CHCONTE RECPÇÃO\Desktop\frutas.mp4'
    TITLE = 'Frutas - Vídeo Demonstrativo'
    DESCRIPTION = 'Vídeo de demonstração sobre frutas.'
    CATEGORY_ID = '22'  # People & Blogs
    PRIVACY_STATUS = 'private'  # public, private, unlisted
    
    # Autenticação
    youtube = get_authenticated_service()
    if not youtube:
        print("Falha na autenticação.")
        return
    
    # Upload do vídeo
    print(f"Iniciando upload do vídeo: {VIDEO_PATH}")
    result = upload_video(youtube, VIDEO_PATH, TITLE, DESCRIPTION, CATEGORY_ID, PRIVACY_STATUS)
    
    if result:
        print("Upload realizado com sucesso!")
    else:
        print("Falha no upload do vídeo.")

if __name__ == '__main__':
    main()
