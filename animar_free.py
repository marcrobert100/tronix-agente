import os
import sys
import requests
import time
import json
import base64
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def animar_imagem(caminho_img, prompt=""):
    if not os.path.exists(caminho_img):
        print(f"ERRO: Imagem nao encontrada: {caminho_img}")
        return None

    saida_dir = "videos_saida"
    os.makedirs(saida_dir, exist_ok=True)

    # Servico 1: Upsampler (gratis, Wan 2.2, sem cadastro)
    print("\n[1/4] Tentando Upsampler (Wan 2.2, gratis)...")
    try:
        files = {"image": open(caminho_img, "rb")}
        r = requests.post(
            "https://api.upsampler.com/v1/video/generate",
            data={"prompt": prompt or "animate this image", "duration": 5},
            files=files, timeout=60
        )
        if r.status_code == 200 and len(r.content) > 1000:
            saida = f"{saida_dir}/tronix_upsampler_{int(time.time())}.mp4"
            with open(saida, "wb") as f: f.write(r.content)
            print(f"  SUCESSO via Upsampler!")
            return saida
        print(f"  Upsampler: {r.status_code}")
    except Exception as e:
        print(f"  Upsampler: {e}")

    # Servico 2: HuggingFace Inference (gratis, sem quota)
    print("\n[2/4] Tentando HuggingFace Inference...")
    try:
        with open(caminho_img, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        r = requests.post(
            "https://api-inference.huggingface.co/models/camenduru/stable-video-diffusion",
            json={"inputs": prompt or "animate this image", "image": img_b64},
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        if r.status_code == 200 and len(r.content) > 1000:
            saida = f"{saida_dir}/tronix_hf_{int(time.time())}.mp4"
            with open(saida, "wb") as f: f.write(r.content)
            print(f"  SUCESSO via HuggingFace!")
            return saida
        print(f"  HF: {r.status_code}")
    except Exception as e:
        print(f"  HF: {e}")

    # Servico 3: Replicate (Wan 2.2, tenta free)
    print("\n[3/4] Tentando Replicate (Wan 2.2 free)...")
    token = os.getenv("REPLICATE_API_TOKEN")
    if token:
        try:
            with open(caminho_img, "rb") as f:
                img_b64 = "data:image/png;base64," + base64.b64encode(f.read()).decode()
            r = requests.post(
                "https://api.replicate.com/v1/predictions",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={
                    "version": "wan-video/wan-2.2-i2v-fast",
                    "input": {"image": img_b64, "prompt": prompt or "smooth cinematic motion"}
                }, timeout=30
            )
            if r.status_code == 201:
                dados = r.json()
                url_get = dados["urls"]["get"]
                for _ in range(60):
                    r2 = requests.get(url_get, headers={"Authorization": f"Bearer {token}"})
                    status = r2.json()["status"]
                    if status == "succeeded":
                        video_url = r2.json()["output"]
                        if isinstance(video_url, list): video_url = video_url[0]
                        r3 = requests.get(video_url, timeout=120)
                        saida = f"{saida_dir}/tronix_replicate_{int(time.time())}.mp4"
                        with open(saida, "wb") as f: f.write(r3.content)
                        print(f"  SUCESSO via Replicate!")
                        return saida
                    elif status == "failed":
                        break
                    time.sleep(2)
            print(f"  Replicate: {r.status_code}")
        except Exception as e:
            print(f"  Replicate: {e}")
    else:
        print("  Token nao configurado")

    # Servico 4: Fallback - FFmpeg Ken Burns (sempre funciona)
    print("\n[4/4] Fallback: FFmpeg Ken Burns...")
    try:
        import subprocess
        ts = int(time.time())
        saida = f"{saida_dir}/tronix_kenburns_{ts}.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-loop", "1", "-i", caminho_img,
            "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,zoompan=z=zoom+0.003:fps=30:d=180",
            "-c:v", "libx264", "-t", "6", "-pix_fmt", "yuv420p", "-crf", "18",
            "-preset", "fast", saida
        ], check=True)
        if os.path.exists(saida):
            print(f"  SUCESSO via FFmpeg Ken Burns!")
            return saida
    except Exception as e:
        print(f"  FFmpeg: {e}")

    print("\nTodas as tentativas falharam.")
    return None

if __name__ == "__main__":
    img = "uploads/praia_1778570271.png"
    prompt = "aerial drone shot of tropical beach, waves, palm trees swaying, cinematic slow motion"
    if len(sys.argv) > 1:
        img = sys.argv[1]
    if len(sys.argv) > 2:
        prompt = " ".join(sys.argv[2:])
    resultado = animar_imagem(img, prompt)
    if resultado:
        print(f"\nVideo gerado: {resultado}")
        print(f"Tamanho: {os.path.getsize(resultado)/1024:.0f} KB")
