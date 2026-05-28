#!/usr/bin/env python3
"""
GORILA TALKING HEAD - Video do Gorila Humanizado com Opinioes
Pipeline completo: Roteirista -> Imagem -> TTS -> Video com Efeitos

Uso: python gorila_video.py
"""

import requests
import os
import sys
import json
import time
import subprocess
from pathlib import Path
import cv2
import numpy as np

# Credenciais Cloudflare
TOKEN = os.getenv("CF_API_TOKEN") or "cfut_nI8gZqUUHil8sG6xjjE1W26wbVHgDyU8PRQTdUV2e61edb64"
ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID") or "038280d984d9c936772700b7dbbc479e"

# Pastas
UPLOADS_DIR = Path(__file__).parent / "uploads"
OUTPUT_DIR = Path(__file__).parent / "uploads" / "gorila"
FONT_PATH = "C:/Windows/Fonts/arial.ttf"

# Garante diretorios
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


# ==================== AGENTE 1: ROTEIRISTA ====================

def agente_roteirista():
    print("=" * 60)
    print("[AGENTE 1 - ROTEIRISTA] Gerandoopinioes do Kong...")
    print("=" * 60)

    instrucao = """Voce e um roteirista criativo brasileiro. Crie um roteiro para um video de um GORILA HUMANIZADO
chamado 'Kong' que da opinioes filosoficas sobre a vida. Ele e engraado e tem personalidade forte.

Crie um roteiro com 4 a 5 falas curtas e impactantes.

REGRAS:
- Cada fala deve ter no maximo 20 palavras
- Tom: filosofia de vida, humor, opinioes fortes
- O gorila usa linguagem coloquial brasileira
- Inclua uma descricao de gesto entre [GESTO: ...]

Responda APENAS em JSON com este formato:
{
    "nome": "Kong",
    "falas": [
        {"texto": "Primeira frase do Kong", "gesto": "descricao do gesto"},
        {"texto": "Segunda frase", "gesto": "outro gesto"},
        ...
    ]
}"""

    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/@cf/meta/llama-3-8b-instruct"

    payload = {
        "messages": [
            {"role": "system", "content": instrucao},
            {"role": "user", "content": "Crie o roteiro do Kong, o gorila humanizado filosofico."}
        ],
        "max_tokens": 800,
    }

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    }

    print("Consultando IA para geraropinioes do Kong...")
    response = requests.post(url, headers=headers, json=payload, timeout=90)

    if response.status_code != 200:
        print(f"ERRO: Status {response.status_code}")
        return None

    data = response.json()
    conteudo = data.get("result", {}).get("response", "")

    try:
        texto = conteudo.strip()
        inicio_json = texto.find("{")
        if inicio_json != -1:
            texto = texto[inicio_json:]
        fim_json = texto.rfind("}") + 1
        if fim_json > 0:
            texto = texto[:fim_json]
        roteiro = json.loads(texto)
    except json.JSONDecodeError:
        print("AVISO: Resposta nao e JSON valido. Usando roteiro padrao.")
        roteiro = {
            "nome": "Kong",
            "falas": [
                {"texto": "A vida e como uma banana.", "gesto": "gesticula com mao"},
                {"texto": "Quanto mais voce sobe, mais banana.", "gesto": "ri alto"},
                {"texto": "Nao seja bom demais, asim come.", "gesto": "avisa com dedo"},
                {"texto": "O importante e ter musculos.", "gesto": "mostra forca"},
                {"texto": "E uma boa noite de sono.", "gesto": "boceja e dorme"},
            ]
        }

    arquivo_roteiro = OUTPUT_DIR / "roteiro_kong.json"
    with open(arquivo_roteiro, "w", encoding="utf-8") as f:
        json.dump(roteiro, f, ensure_ascii=False, indent=2)

    print(f"Roteiro salvo: {arquivo_roteiro}")
    print(f"Total de falas: {len(roteiro['falas'])}")
    for i, fala in enumerate(roteiro['falas']):
        print(f"  Fala {i+1}: {fala['texto']}")

    return roteiro


# ==================== AGENTE 2: GERADOR DE IMAGEM ====================

def agente_gerador_imagem():
    print("\n" + "=" * 60)
    print("[AGENTE 2 - GERADOR] Criando imagem do Kong...")
    print("=" * 60)

    prompt = (
        "A highly realistic anthropomorphic gorilla sitting in a modern cafe, "
        "wearing casual human clothes, holding a coffee cup, intelligent eyes, "
        "expressive human-like face, detailed fur texture, cinematic lighting, "
        "warm atmosphere, photorealistic, 8K quality, half-body portrait"
    )

    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/@cf/stabilityai/stable-diffusion-xl-base-1.0"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {"prompt": prompt}

    print(f"Prompt: {prompt[:80]}...")
    print("Enviando requisicao (pode demorar ate 3 minutos)...")

    response = requests.post(url, headers=headers, json=payload, timeout=300)

    if response.status_code != 200:
        print(f"ERRO: Status {response.status_code}")
        return None

    content_type = response.headers.get("Content-Type", "")

    if "image" in content_type or response.content[:4] == b"\x89PNG":
        image_data = response.content
    else:
        try:
            data = response.json()
            if "result" in data:
                import base64
                image_data = base64.b64decode(data["result"])
            else:
                print("ERRO: Resposta inesperada")
                return None
        except Exception:
            image_data = response.content

    arquivo_imagem = OUTPUT_DIR / "kong_imagem.png"
    with open(arquivo_imagem, "wb") as f:
        f.write(image_data)

    tamanho = len(image_data) / 1024
    print(f"SUCESSO! Imagem salva: {arquivo_imagem} ({tamanho:.1f} KB)")
    return str(arquivo_imagem)


# ==================== AGENTE 3: NARRADOR (TTS) ====================

def agente_narrador(roteiro):
    print("\n" + "=" * 60)
    print("[AGENTE 3 - NARRADOR] Gerando audio das falas...")
    print("=" * 60)

    try:
        import edge_tts
        import asyncio
    except ImportError:
        print("ERRO: edge-tts nao instalado.")
        return None

    voces = [
        "pt-BR-AntonioNeural",
        "pt-BR-FranciscaNeural",
        "pt-BR-RobertoNeural",
    ]

    async def gerar_falas():
        arquivos_audio = []

        for i, fala in enumerate(roteiro['falas']):
            texto = fala['texto']
            voz = voces[i % len(voces)]
            arquivo_audio = OUTPUT_DIR / f"audio_fala_{i:02d}.mp3"
            arquivos_audio.append(str(arquivo_audio))

            print(f"  Fala {i+1}/{len(roteiro['falas'])}: '{texto}'")
            print(f"    Voz: {voz}")

            try:
                communicate = edge_tts.Communicate(texto, voz)
                await communicate.save(str(arquivo_audio))
                tamanho = arquivo_audio.stat().st_size / 1024
                print(f"    OK! ({tamanho:.1f} KB)")
            except Exception as e:
                print(f"    ERRO: {e}")
                arquivos_audio.pop()

            await asyncio.sleep(0.3)

        return arquivos_audio

    arquivos = asyncio.run(gerar_falas())

    if not arquivos:
        print("ERRO: Nenhum audio gerado.")
        return None

    # Concatena audios (apenas os validos)
    print("\nCombinando todos os audios...")

    # Filtra apenas arquivos validos (> 1KB)
    arquivos_validos = [a for a in arquivos if a and Path(a).exists() and Path(a).stat().st_size > 1024]
    print(f"  Arquivos validos: {len(arquivos_validos)}/{len(arquivos)}")

    if not arquivos_validos:
        print("ERRO: Nenhum audio valido encontrado.")
        return None

    lista_arquivos = OUTPUT_DIR / "lista_audios.txt"
    with open(lista_arquivos, "w", encoding="utf-8") as f:
        for arq in arquivos_validos:
            f.write(f"file '{arq.replace(chr(92), '/')}'\n")

    audio_unificado = OUTPUT_DIR / "kong_audio_unificado.mp3"

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(lista_arquivos).replace("\\", "/"),
        "-c", "copy",
        str(audio_unificado).replace("\\", "/")
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            tamanho = audio_unificado.stat().st_size / 1024
            print(f"Audio unificado: {tamanho:.1f} KB")
        else:
            print(f"FFmpeg concat falhou, usando primeiro audio valido.")
            import shutil
            shutil.copy(arquivos_validos[0], audio_unificado)
    except FileNotFoundError:
        print("FFmpeg nao encontrado.")
        import shutil
        shutil.copy(arquivos_validos[0], audio_unificado)
    except Exception as e:
        print(f"Erro concatenacao: {e}")
        import shutil
        shutil.copy(arquivos_validos[0], audio_unificado)

    return str(audio_unificado)


# ==================== AGENTE 4: EDITOR (Video com Efeitos) ====================

def agente_editor(caminho_imagem, caminho_audio):
    print("\n" + "=" * 60)
    print("[AGENTE 4 - EDITOR] Criando video com efeitos e gestos...")
    print("=" * 60)

    try:
        from moviepy import (
            ImageClip, AudioFileClip, CompositeVideoClip,
            ColorClip, TextClip
        )
    except ImportError as e:
        print(f"ERRO: moviepy nao instalado: {e}")
        return None

    # Carrega audio para duracao
    try:
        audio_clip = AudioFileClip(caminho_audio)
        duracao_total = audio_clip.duration
        audio_clip.close()
        print(f"Duracao do audio: {duracao_total:.1f}s")
    except Exception as e:
        print(f"ERRO ao carregar audio: {e}")
        duracao_total = 15.0

    largura = 1280
    altura = 720

    # Carrega e processa imagem com OpenCV para efeitos
    img = cv2.imread(caminho_imagem)
    if img is None:
        print(f"ERRO: Nao foi possivel carregar imagem: {caminho_imagem}")
        return None

    h_img, w_img = img.shape[:2]
    print(f"Imagem original: {w_img}x{h_img}")

    # Cria video com efeito Ken Burns (pan + zoom simulado)
    # Salva frames processados
    print("Processando frames com efeito de movimento...")

    frames_dir = OUTPUT_DIR / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    fps = 30
    total_frames = int(duracao_total * fps)

    for i in range(total_frames):
        t = i / fps
        progresso = t / duracao_total

        # Ken Burns: pan e zoom suaves
        zoom = 1.0 + 0.06 * np.sin(progresso * np.pi * 2.5)
        pan_x = int(25 * np.sin(progresso * np.pi * 3))
        pan_y = int(15 * np.cos(progresso * np.pi * 2))

        # Calcula crop
        crop_w = int(w_img / zoom)
        crop_h = int(h_img / zoom)

        center_x = w_img // 2 + pan_x
        center_y = h_img // 2 + pan_y

        x1 = max(0, min(center_x - crop_w // 2, w_img - crop_w))
        y1 = max(0, min(center_y - crop_h // 2, h_img - crop_h))

        # Crop
        crop = img[y1:y1+crop_h, x1:x1+crop_w]

        # Resize
        frame = cv2.resize(crop, (largura, altura), interpolation=cv2.INTER_LANCZOS4)

        # Adiciona vinheta sutil
        vignette = criar_vinheta(largura, altura, intensidade=0.25)
        frame = cv2.addWeighted(frame, 1, vignette, 0.25, 0)

        # Adiciona barra dourada no topo
        frame[0:8, :] = [255, 215, 0]

        # Salva frame
        frame_path = str(frames_dir / f"frame_{i:05d}.png").replace("\\", "/")
        cv2.imwrite(frame_path, frame)

        if i % 100 == 0:
            print(f"  Processando frame {i}/{total_frames} ({100*i//total_frames}%)")

    print(f"Frames salvos em: {frames_dir}")

    # Cria video com FFmpeg dos frames
    arquivo_video = OUTPUT_DIR / "kong_video.mp4"

    # Windows: usa caminho com barra normalizada
    import platform
    if platform.system() == "Windows":
        frames_pattern = str(frames_dir / "frame_%05d.png").replace("\\", "/")
        audio_path = str(caminho_audio).replace("\\", "/")
        video_path = str(arquivo_video).replace("\\", "/")
    else:
        frames_pattern = str(frames_dir / "frame_%05d.png")
        audio_path = str(caminho_audio)
        video_path = str(arquivo_video)

    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", frames_pattern,
        "-i", audio_path,
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        video_path
    ]

    print("\nCodificando video (FFmpeg)...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

    if result.returncode != 0:
        print(f"ERRO FFmpeg: {result.stderr[-300:]}")
        return None

    # Limpa frames para economizar espaco
    import shutil
    try:
        shutil.rmtree(frames_dir)
        print("Frames temporarios removidos.")
    except:
        pass

    tamanho = arquivo_video.stat().st_size / (1024 * 1024)
    print(f"\n" + "=" * 60)
    print(f"SUCESSO! VIDEO DO KONG CRIADO!")
    print(f"Arquivo: {arquivo_video}")
    print(f"Tamanho: {tamanho:.2f} MB")
    print(f"Duracao: {duracao_total:.1f}s")
    print("=" * 60)

    return str(arquivo_video)


def criar_vinheta(w, h, intensidade=0.25):
    """Cria efeito de vinheta para as bordas."""
    kernel_x = cv2.getGaussianKernel(w, w // 2)
    kernel_y = cv2.getGaussianKernel(h, h // 2)
    kernel = kernel_y * kernel_x.T
    mask = kernel / kernel.max()
    mask = 1 - (1 - mask) * intensidade

    vinheta = np.zeros((h, w, 3), dtype=np.float32)
    for c in range(3):
        vinheta[:, :, c] = mask * 255

    return vinheta.astype(np.uint8)


# ==================== PIPELINE PRINCIPAL ====================

def main():
    print("=" * 60)
    print("  GORILA TALKING HEAD - Pipeline de Video IA")
    print("  Agente: Kong - O Gorila com Opinioes")
    print("=" * 60)

    # ETAPA 1: Roteirista
    roteiro = agente_roteirista()
    if not roteiro:
        print("FALHA: Nao foi possivel criar o roteiro.")
        sys.exit(1)

    # ETAPA 2: Gerador de Imagem
    caminho_imagem = agente_gerador_imagem()
    if not caminho_imagem:
        print("FALHA: Nao foi possivel gerar a imagem.")
        sys.exit(1)

    # ETAPA 3: Narrador (TTS)
    caminho_audio = agente_narrador(roteiro)
    if not caminho_audio:
        print("FALHA: Nao foi possivel gerar o audio.")
        sys.exit(1)

    # ETAPA 4: Editor (Video)
    caminho_video = agente_editor(caminho_imagem, caminho_audio)
    if not caminho_video:
        print("FALHA: Nao foi possivel criar o video.")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETO! Video do Kong pronto!")
    print(f"Arquivo final: {caminho_video}")
    print("=" * 60)


if __name__ == "__main__":
    main()
