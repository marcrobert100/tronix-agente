import os
import sys
import requests
import json
import time
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

NCA_URL = "http://localhost:8080"
NCA_KEY = "tronix_key_2026"

def imagem_para_video(caminho_img, duracao=5, zoom=1.05):
    if not os.path.exists(caminho_img):
        print(f"ERRO: Imagem nao encontrada: {caminho_img}")
        return None

    print(f"  [NCA] Convertendo imagem para video...")
    try:
        r = requests.post(f"{NCA_URL}/v1/image/convert/video", 
            headers={"X-API-Key": NCA_KEY},
            json={"image_url": os.path.abspath(caminho_img), "duration": duracao, "zoom": zoom},
            timeout=120
        )
        if r.status_code == 200:
            data = r.json()
            video_url = data.get("response", {}).get("output_url") or data.get("output_url")
            print(f"  [NCA] Video gerado: {video_url}")
            return video_url
        else:
            print(f"  [NCA] Erro {r.status_code}: {r.text[:200]}")
            return None
    except requests.exceptions.ConnectionError:
        print(f"  [NCA] Servidor nao iniciado. Rode: python nca-toolkit/app.py")
        return None
    except Exception as e:
        print(f"  [NCA] Erro: {e}")
        return None

def concatenar_videos(lista_videos, saida="concat.mp4"):
    if not lista_videos:
        return None

    print(f"  [NCA] Concatenando {len(lista_videos)} videos...")
    try:
        r = requests.post(f"{NCA_URL}/v1/video/concatenate",
            headers={"X-API-Key": NCA_KEY},
            json={"video_urls": [os.path.abspath(v) for v in lista_videos]},
            timeout=300
        )
        if r.status_code == 200:
            data = r.json()
            saida_path = os.path.join(os.path.dirname(__file__), saida)
            print(f"  [NCA] Videos concatenados: {saida}")
            return saida
        else:
            print(f"  [NCA] Erro {r.status_code}: {r.text[:200]}")
            return None
    except Exception as e:
        print(f"  [NCA] Erro: {e}")
        return None

def adicionar_legenda(video_path, texto, estilo="yellow"):
    if not os.path.exists(video_path):
        print(f"ERRO: Video nao encontrado: {video_path}")
        return None

    print(f"  [NCA] Adicionando legenda...")
    try:
        r = requests.post(f"{NCA_URL}/v1/video/caption",
            headers={"X-API-Key": NCA_KEY},
            json={
                "video_url": os.path.abspath(video_path),
                "text": texto,
                "font_color": estilo,
                "position": "bottom"
            },
            timeout=300
        )
        if r.status_code == 200:
            data = r.json()
            saida = video_path.replace(".mp4", "_legendado.mp4")
            print(f"  [NCA] Legenda adicionada")
            return saida
        else:
            print(f"  [NCA] Erro: {r.status_code}")
            return None
    except Exception as e:
        print(f"  [NCA] Erro: {e}")
        return None

def status():
    try:
        r = requests.post(f"{NCA_URL}/v1/toolkit/test",
            headers={"X-API-Key": NCA_KEY}, timeout=5)
        return r.status_code == 200
    except:
        return False

if __name__ == "__main__":
    if status():
        print("NCA-ToolKit: CONECTADO")
    else:
        print("NCA-ToolKit: DESCONECTADO (rode nca-toolkit/app.py primeiro)")
