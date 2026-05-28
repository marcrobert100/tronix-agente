import os
import sys
import requests
import time
import json
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def animar_replicate(caminho_img, prompt="smooth cinematic motion"):
    token = os.getenv("REPLICATE_API_TOKEN")
    if not token:
        print("ERRO: Configure REPLICATE_API_TOKEN no .env")
        print("1. Crie conta em: https://replicate.com")
        print("2. Pegue o token em: https://replicate.com/account/api-tokens")
        print('3. Adicione no .env: "REPLICATE_API_TOKEN": "seu-token-aqui"')
        return None

    if not os.path.exists(caminho_img):
        print(f"ERRO: Imagem nao encontrada: {caminho_img}")
        return None

    import base64
    with open(caminho_img, "rb") as f:
        img_b64 = "data:image/png;base64," + base64.b64encode(f.read()).decode()

    print(f"  Enviando para Replicate (Wan 2.2 I2V)...")
    try:
        r = requests.post(
            "https://api.replicate.com/v1/predictions",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={
                "version": "wan-video/wan-2.2-i2v-fast",
                "input": {"image": img_b64, "prompt": prompt}
            },
            timeout=30
        )
        if r.status_code != 201:
            print(f"  ERRO: {r.status_code} - {r.text[:200]}")
            return None

        dados = r.json()
        url_get = dados["urls"]["get"]
        print(f"  Processando... (ate 60s)")

        for tentativa in range(60):
            r2 = requests.get(url_get, headers={"Authorization": f"Bearer {token}"})
            status = r2.json()["status"]
            if status == "succeeded":
                video_url = r2.json()["output"]
                if isinstance(video_url, list):
                    video_url = video_url[0]
                r3 = requests.get(video_url, timeout=120)
                saida_dir = "videos_saida"
                os.makedirs(saida_dir, exist_ok=True)
                ts = int(time.time())
                caminho = os.path.join(saida_dir, f"tronix_{ts}.mp4")
                with open(caminho, "wb") as f:
                    f.write(r3.content)
                print(f"SUCESSO|{caminho}")
                return caminho
            elif status == "failed":
                print(f"  FALHA: {r2.json().get('error', 'desconhecido')}")
                return None
            time.sleep(1)

        print("  TIMEOUT: Levou mais de 60s")
        return None
    except Exception as e:
        print(f"  ERRO: {e}")
        return None

if __name__ == "__main__":
    img = "uploads/cachorro_surf_1778565418.png"
    prompt = "golden retriever dog surfing on ocean wave, cinematic slow motion"
    if len(sys.argv) > 1:
        img = sys.argv[1]
    if len(sys.argv) > 2:
        prompt = " ".join(sys.argv[2:])
    animar_replicate(img, prompt)
