#!/usr/bin/env python3
"""
Gerador de imagens via Cloudflare Workers AI.
Uso: python gera_imagem.py "seu prompt aqui"
"""

import requests
import sys
import os
import time
from pathlib import Path

# Configuracoes - use variaveis de ambiente
CF_API_TOKEN = os.getenv("CF_API_TOKEN")
CF_ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID")
UPLOADS_DIR = Path(__file__).parent / "uploads"

# Modelo de geracao de imagem (Stable Diffusion)
MODEL = "@cf/stabilityai/stable-diffusion-xl-base-1.0"


def gerar_imagem(prompt: str, output_path: str = None) -> str:
    """Gera uma imagem usando Cloudflare Workers AI e salva no disco."""

    if not CF_API_TOKEN or not CF_ACCOUNT_ID:
        print("ERRO: Defina as variaveis de ambiente CF_API_TOKEN e CF_ACCOUNT_ID")
        sys.exit(1)

    # Garante que a pasta uploads existe
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    # Nome do arquivo de saida
    if not output_path:
        timestamp = int(time.time())
        # Limita o nome do arquivo
        safe_prompt = "".join(c if c.isalnum() or c in " -_" else "_" for c in prompt[:30])
        output_path = UPLOADS_DIR / f"imagem_{timestamp}_{safe_prompt}.png"

    # Monta a URL da API
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/{MODEL}"

    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "prompt": prompt,
    }

    print(f"Gerando imagem com prompt: '{prompt}'...")
    print(f"Modelo: {MODEL}")

    print(f"Enviando requisicao (timeout: 120s)...")
    response = requests.post(url, headers=headers, json=payload, timeout=180)

    if response.status_code != 200:
        print(f"ERRO: Status {response.status_code}")
        print(response.text[:500])
        sys.exit(1)

    # Cloudflare Workers AI pode retornar:
    # 1. Imagem direta em binary (Content-Type: image/png)
    # 2. JSON com base64 em data.result
    content_type = response.headers.get("Content-Type", "")

    if "image" in content_type or response.content[:4] == b"\x89PNG":
        # Resposta binaria direta
        image_data = response.content
    else:
        # Resposta em JSON base64
        try:
            data = response.json()
            if "result" in data:
                import base64
                image_data = base64.b64decode(data["result"])
            else:
                print("ERRO: Resposta inesperada da API")
                print(data)
                sys.exit(1)
        except Exception:
            # Tenta usar o conteudo direto
            image_data = response.content

    with open(output_path, "wb") as f:
        f.write(image_data)

    print(f"SUCESSO! Imagem salva em: {output_path}")
    return str(output_path)


def main():
    if len(sys.argv) < 2:
        print("Uso: python gera_imagem.py \"seu prompt aqui\"")
        sys.exit(1)

    prompt = " ".join(sys.argv[1:])
    gerar_imagem(prompt)


if __name__ == "__main__":
    main()
