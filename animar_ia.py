import os
import sys
import requests
import time
import json
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def animar_imagem_zsky(caminho_img, prompt="", duracao=5):
    from gradio_client import Client, handle_file
    
    if not os.path.exists(caminho_img):
        print(f"ERRO: Imagem nao encontrada: {caminho_img}")
        return None

    print(f"  Tentando ZSky API (gratis)...")
    try:
        r = requests.post(
            "https://zsky.ai/api/v1/video/generate",
            json={
                "prompt": prompt or "Animate this image with smooth motion",
                "duration": duracao,
                "resolution": "1080p",
                "audio": True
            },
            timeout=120
        )
        if r.status_code == 200:
            saida_dir = "videos_saida"
            os.makedirs(saida_dir, exist_ok=True)
            ts = int(time.time())
            caminho_saida = os.path.join(saida_dir, f"tronix_{ts}.mp4")
            with open(caminho_saida, "wb") as f:
                f.write(r.content)
            print(f"SUCESSO|{caminho_saida}")
            return caminho_saida
        else:
            print(f"  ZSky falhou ({r.status_code}), tentando Replicate...")
    except:
        print(f"  ZSky indisponivel, tentando Replicate...")

    print(f"  Tentando Replicate (Wan 2.2 I2V)...")
    try:
        REPLICATE_TOKEN = os.getenv("REPLICATE_API_TOKEN")
        if not REPLICATE_TOKEN:
            print("  REPLICATE_API_TOKEN nao configurado. Pule para HuggingFace.")
            return None

        with open(caminho_img, "rb") as f:
            img_data = f.read()
        import base64
        img_b64 = "data:image/png;base64," + base64.b64encode(img_data).decode()

        r = requests.post(
            "https://api.replicate.com/v1/predictions",
            headers={
                "Authorization": f"Bearer {REPLICATE_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "version": "wan-video/wan-2.2-i2v-fast",
                "input": {
                    "image": img_b64,
                    "prompt": prompt or "smooth motion, cinematic"
                }
            },
            timeout=30
        )
        if r.status_code == 201:
            data = r.json()
            url_get = data["urls"]["get"]
            print(f"  Replicate processando...")
            for _ in range(60):
                r2 = requests.get(url_get, headers={"Authorization": f"Bearer {REPLICATE_TOKEN}"})
                status = r2.json()["status"]
                if status == "succeeded":
                    video_url = r2.json()["output"]
                    if isinstance(video_url, list):
                        video_url = video_url[0]
                    r3 = requests.get(video_url, timeout=60)
                    saida_dir = "videos_saida"
                    os.makedirs(saida_dir, exist_ok=True)
                    ts = int(time.time())
                    caminho_saida = os.path.join(saida_dir, f"tronix_{ts}.mp4")
                    with open(caminho_saida, "wb") as f:
                        f.write(r3.content)
                    print(f"SUCESSO|{caminho_saida}")
                    return caminho_saida
                elif status == "failed":
                    print(f"  Replicate falhou")
                    break
                time.sleep(3)
    except Exception as e:
        print(f"  Replicate erro: {e}")

    print(f"  Tentando HuggingFace SVD...")
    try:
        from gradio_client import Client, handle_file
        HF_TOKEN = "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"
        client = Client("multimodalart/stable-video-diffusion", token=HF_TOKEN)
        result = client.predict(
            image=handle_file(caminho_img),
            seed=0, randomize_seed=True,
            motion_bucket_id=127, fps_id=6,
            api_name="/video"
        )
        video_temp = result[0]['video'] if isinstance(result[0], dict) else result[0]
        saida_dir = "videos_saida"
        os.makedirs(saida_dir, exist_ok=True)
        ts = int(time.time())
        caminho_saida = os.path.join(saida_dir, f"tronix_{ts}.mp4")
        import shutil
        shutil.copy(video_temp, caminho_saida)
        print(f"SUCESSO|{caminho_saida}")
        return caminho_saida
    except Exception as e:
        print(f"  SVD erro: {e}")

    print(f"ERRO: Todas as APIs falharam.")
    return None

if __name__ == "__main__":
    img = "uploads/alien_cena1.png"
    if len(sys.argv) > 1:
        img = sys.argv[1]
    prompt = "cinematic motion, smooth camera movement, high quality"
    if len(sys.argv) > 2:
        prompt = " ".join(sys.argv[2:])
    animar_imagem_zsky(img, prompt)
