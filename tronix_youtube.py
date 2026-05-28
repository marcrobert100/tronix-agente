import os
import sys
import json
import pickle
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

TOKEN_FILE = "token_youtube.pickle"
CLIENT_SECRETS = "client_secrets.json"

TAGS = ["Tronix", "PCsolucoes", "Vicosa", "Alagoas", "IA"]

def autenticar():
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    import google.auth

    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRETS):
                print("="*60)
                print("PRECISA DO ARQUIVO client_secrets.json")
                print("="*60)
                print("1. Acesse: https://console.cloud.google.com/")
                print("2. Crie um projeto -> Ative YouTube Data API v3")
                print("3. Crie credenciais OAuth 2.0 -> Desktop app")
                print("4. Baixe o JSON e renomeie para client_secrets.json")
                print("5. Coloque na pasta: " + os.path.dirname(__file__))
                print("="*60)
                return None

            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS, SCOPES)
            creds = flow.run_local_server(port=8080)

        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)

    return creds

def upload_youtube(video_path, titulo, descricao, tags=None, privacidade="public"):
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    if not os.path.exists(video_path):
        print(f"ERRO: Video nao encontrado: {video_path}")
        return None

    creds = autenticar()
    if not creds:
        return None

    youtube = build("youtube", "v3", credentials=creds)
    body = {
        "snippet": {
            "title": titulo,
            "description": descricao,
            "tags": tags or TAGS,
            "categoryId": "22",  # 22 = People & Blogs
        },
        "status": {
            "privacyStatus": privacidade,
            "selfDeclaredMadeForKids": False,
        }
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    print(f"Enviando: {titulo}...")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  Progresso: {int(status.progress() * 100)}%")

    video_id = response.get("id")
    url = f"https://youtu.be/{video_id}"
    print(f"SUCESSO! Publicado em: {url}")
    return video_id

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Tronix - Upload YouTube")
    parser.add_argument("video", help="Caminho do video")
    parser.add_argument("--titulo", "-t", default="Mini Novela Tronix", help="Titulo do video")
    parser.add_argument("--descricao", "-d", default="Gerado por Tronix IA - PCsoluções", help="Descricao")
    parser.add_argument("--privado", action="store_true", help="Marcar como nao listado")
    args = parser.parse_args()

    upload_youtube(
        args.video,
        args.titulo,
        args.descricao,
        privacidade="unlisted" if args.privado else "public"
    )
