#!/usr/bin/env python3
"""
TRONIX NOVELINHA - Gerador de mini-novelas a partir de JSON.
Carrega roteiro JSON, usa Director para cada cena, gera video final.

Uso:
    python gerar_novelinha.py                          # usa novelinha_velho_estrela.json
    python gerar_novelinha.py --input minha.json      # roteiro custom
    python gerar_novelinha.py --somente-imagens       # so gera imagens
    python gerar_novelinha.py --sem-voz               # sem naracao
"""

import os
import sys
import json
import time
import shutil
import subprocess
import base64
import argparse
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

try:
    import requests
except ImportError:
    print("ERRO: pip install requests")
    sys.exit(1)

try:
    from tronix_director import Director
    director = Director()
except ImportError:
    print("ERRO: tronix_director.py nao encontrado")
    sys.exit(1)

GPT_IMAGE_2_TEMPLATES = {
    "extreme_wide": "epic wide concept scene, vast landscape, atmospheric perspective, golden hour, ultra-detailed, cinematic key art, 16:9 composition",
    "wide": "wide cinematic shot, environmental storytelling, deep focus, narrative scene, painterly composition, 16:9",
    "medium": "medium shot, character-centric, balanced composition, soft natural lighting, intimate atmosphere, emotional storytelling",
    "close_up": "intense close-up, shallow depth of field, bokeh background, dramatic chiaroscuro lighting, hyper-detailed skin texture, emotional intensity",
    "extreme_close_up": "extreme macro close-up, single element filling frame, soft bokeh, golden rim light, tactile texture, symbolic detail",
    "over_shoulder": "over-the-shoulder framing, foreground silhouette, subject in focus, conversational composition, depth layers",
    "top_down": "bird's eye view, geometric composition, pattern recognition, abstract landscape, high contrast aerial perspective",
    "low_angle": "low angle hero shot, towering subject, dramatic upward perspective, monumental scale, golden hour backlight",
}


def augmentar_prompt_gpt_image_2(prompt_base, tipo_plano, emocao="neutral", estilo="cinematic"):
    """
    Augmenta prompt com templates estruturados do gpt-image-2 skill.
    Inspirado em references/scenes-and-illustrations/*.md
    """
    base_template = GPT_IMAGE_2_TEMPLATES.get(tipo_plano, GPT_IMAGE_2_TEMPLATES["wide"])

    emocoes = {
        "neutral": "",
        "alegria": "warm golden light, joyful atmosphere, vibrant colors",
        "tristeza": "muted blue tones, melancholic atmosphere, soft shadows",
        "tensao": "high contrast, dramatic shadows, suspenseful mood, cool palette",
        "magia": "iridescent glow, ethereal light, mystical particles, otherworldly atmosphere",
        "nostalgia": "warm sepia tones, soft focus, faded film look, gentle haze",
        "romance": "soft pink and gold palette, intimate lighting, dreamy atmosphere",
        "acao": "dynamic composition, motion blur, intense energy, saturated colors",
    }

    estilo_director = emocoes.get(emocao, "")

    prompt_final = (
        f"{base_template}, "
        f"{estilo_director}, "
        f"masterpiece, professional photography, "
        f"{prompt_base}"
    )
    return prompt_final

try:
    import tronix_logger as db
    db.inicializar()
    DB_OK = True
except ImportError:
    DB_OK = False

BASE = Path(__file__).parent
UPLOADS = BASE / "uploads" / "novelinha"
VIDEOS_DIR = BASE / "videos_saida" / "novelinha"
TEMP_DIR = BASE / "_temp_novelinha"
UPLOADS.mkdir(parents=True, exist_ok=True)
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

CF_ACCOUNT = "038280d984d9c936772700b7dbbc479e"
CF_TOKEN = "cfut_nI8gZqUUHil8sG6xjjE1W26wbVHgDyU8PRQTdUV2e61edb64"
CF_URL = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT}/ai/run/@cf/stabilityai/stable-diffusion-xl-base-1.0"

POLLINATIONS_URL = "https://image.pollinations.ai/prompt/{prompt}?width={w}&height={h}&nologo=true&model={model}"


def gerar_imagem_pollinations(prompt, output_path, model="flux", w=1280, h=720):
    """Gera imagem via Pollinations.ai (FREE, sem API key, FLUX/SDXL)."""
    import urllib.parse
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={w}&height={h}&nologo=true&model={model}&seed={int(time.time())%99999}"
    try:
        r = requests.get(url, timeout=120)
        if r.status_code == 200 and len(r.content) > 1000:
            with open(output_path, "wb") as f:
                f.write(r.content)
            return True
        print(f"  [POLL] Status {r.status_code}, size {len(r.content)}")
        return False
    except Exception as e:
        print(f"  [POLL] ERRO: {e}")
        return False


def gerar_imagem_cf(prompt, output_path):
    headers = {"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": "application/json"}
    r = requests.post(CF_URL, headers=headers, json={"prompt": prompt}, timeout=180)
    if r.status_code != 200:
        print(f"  [CF] ERRO API: {r.status_code}")
        return False
    dados = r.content
    ct = r.headers.get("Content-Type", "")
    if "image" not in ct and dados[:4] != b"\x89PNG":
        try:
            dados = base64.b64decode(r.json()["result"])
        except Exception as e:
            print(f"  [CF] ERRO decode: {e}")
            return False
    with open(output_path, "wb") as f:
        f.write(dados)
    return True


def gerar_imagem_pipeline(prompt, output_path, cena_id, modelo_preferido="flux"):
    """
    Pipeline inteligente: tenta Pollinations (FREE) -> Cloudflare -> Fallback.
    """
    print(f"  [IMG] Tentando Pollinations.ai ({modelo_preferido})...")
    if gerar_imagem_pollinations(prompt, output_path, model=modelo_preferido):
        size_kb = os.path.getsize(output_path) // 1024
        print(f"  [IMG] OK Pollinations ({size_kb} KB)")
        return "pollinations"

    print(f"  [IMG] Tentando Cloudflare SDXL...")
    if gerar_imagem_cf(prompt, output_path):
        size_kb = os.path.getsize(output_path) // 1024
        print(f"  [IMG] OK Cloudflare ({size_kb} KB)")
        return "cloudflare"

    print(f"  [IMG] Fallback Pillow placeholder...")
    gerar_imagem_fallback(prompt, output_path, cena_id)
    return "fallback"


def gerar_imagem_fallback(prompt, output_path, cena_id):
    try:
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new("RGB", (1920, 1080), color=(20, 30, 50))
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 60)
            font_small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 30)
        except:
            font = ImageFont.load_default()
            font_small = ImageFont.load_default()
        draw.text((100, 100), f"CENA {cena_id}", fill=(255, 215, 0), font=font)
        prompt_curto = prompt[:120] + "..." if len(prompt) > 120 else prompt
        draw.text((100, 250), prompt_curto, fill=(255, 255, 255), font=font_small)
        img.save(output_path)
        return True
    except Exception as e:
        print(f"  ERRO fallback: {e}")
        return False


def criar_video_cena(img_path, cena, idx):
    """Cria video Ken Burns com parametros do Director."""
    params = director.para_cena(cena["plano"], cena["movimento"])
    duracao = cena.get("duracao", 6)

    pasta_cena = TEMP_DIR / f"cena{idx}"
    pasta_cena.mkdir(exist_ok=True)
    img_temp = pasta_cena / "frame.png"
    shutil.copy2(img_path, img_temp)

    saida_raw = VIDEOS_DIR / f"cena{idx:02d}_raw.mp4"

    cmd = [
        "python", str(BASE / "gera_video.py"),
        "--pasta", str(pasta_cena),
        "--saida", str(saida_raw),
        "--duracao", str(duracao),
        "--animacao", "fade",
        "--zoom-inicial", str(params["zoom_inicial"]),
        "--zoom-final", str(params["zoom_final"]),
        "--pan-x", str(params["pan_x"]),
        "--pan-y", str(params["pan_y"]),
    ]

    print(f"  [DIRECTOR] {params['plano_nome']} + {params['movimento_nome']}")
    print(f"  [DIRECTOR] Zoom {params['zoom_inicial']}->{params['zoom_final']}, Pan ({params['pan_x']}, {params['pan_y']})")

    result = subprocess.run(cmd, cwd=str(BASE), capture_output=True, text=True, encoding='utf-8', errors='replace')

    if saida_raw.exists():
        return str(saida_raw)
    print(f"  ERRO gera_video: {result.stderr[-300:]}")
    return None


def aplicar_voz_cena(video_path, cena, idx):
    """Adiciona narração Edge-TTS ao vídeo."""
    legenda = cena.get("legenda", "")
    if not legenda:
        return video_path

    txt_file = TEMP_DIR / f"legenda_{idx}.txt"
    with open(txt_file, "w", encoding="utf-8") as f:
        f.write(legenda)

    saida_final = VIDEOS_DIR / f"cena{idx:02d}.mp4"

    result = subprocess.run(
        ["python", str(BASE / "tronix_super_editor.py"), video_path],
        cwd=str(BASE), capture_output=True, text=True, encoding='utf-8', errors='replace'
    )

    saida_comb = result.stdout + result.stderr
    import re
    m = re.search(r'SUCESSO TOTAL\|(.+?)$', saida_comb, re.MULTILINE)
    if m:
        final_path = m.group(1).strip()
        if os.path.exists(final_path):
            if saida_final.exists():
                saida_final.unlink()
            shutil.move(final_path, saida_final)
            return str(saida_final)

    # Fallback: usa ultimo video cena*.mp4
    candidates = sorted(VIDEOS_DIR.glob(f"cena*_super*.mp4"), key=os.path.getmtime, reverse=True)
    if candidates:
        if saida_final.exists():
            saida_final.unlink()
        shutil.copy2(candidates[0], saida_final)
        return str(saida_final)

    return video_path


def concatenar_videos(video_paths, saida_final):
    """Concatena videos com ffmpeg."""
    if not video_paths:
        return False
    lista = TEMP_DIR / "_concat.txt"
    with open(lista, "w", encoding="utf-8") as f:
        for v in video_paths:
            f.write(f"file '{os.path.abspath(v)}'\n")

    cmd = [
        "ffmpeg", "-f", "concat", "-safe", "0",
        "-i", str(lista),
        "-c:v", "copy", "-c:a", "aac", "-y", str(saida_final)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if lista.exists():
        lista.unlink()
    return saida_final.exists()


def processar_novelinha(json_path, somente_imagens=False, sem_voz=False):
    print("="*70)
    print("TRONIX NOVELINHA - GERADOR COMPLETO")
    print("="*70)

    with open(json_path, "r", encoding="utf-8") as f:
        roteiro = json.load(f)

    titulo = roteiro.get("titulo", "Novelinha")
    cenas = roteiro.get("cenas", [])
    print(f"Titulo: {titulo}")
    print(f"Cenas: {len(cenas)}")
    print()

    print("ROTEIRO DE DIRECAO:")
    print(director.roteiro_direcao([
        {"titulo": c["titulo"], "plano": c["plano"], "movimento": c["movimento"]} for c in cenas
    ]))
    print()

    videos_finais = []
    for i, cena in enumerate(cenas):
        idx = i + 1
        print(f"\n--- CENA {idx}/{len(cenas)}: {cena['titulo']} ---")

        params = director.para_cena(cena["plano"], cena["movimento"])
        emocao = cena.get("emocao", "neutral")
        prompt_director = f"{params['prompt_prefixo']} {cena['prompt']}"
        prompt_final = augmentar_prompt_gpt_image_2(
            prompt_director,
            cena["plano"],
            emocao=emocao,
        )

        img_path = UPLOADS / f"cena{idx:02d}.png"
        if not img_path.exists():
            print(f"  Gerando imagem...")
            gerar_imagem_pipeline(prompt_final, img_path, idx, modelo_preferido="flux")
        else:
            print(f"  Imagem ja existe: {img_path.name}")

        if somente_imagens:
            continue

        video_raw = criar_video_cena(img_path, cena, idx)
        if not video_raw:
            print(f"  FALHA no video cena {idx}")
            continue

        if sem_voz:
            video_final = video_raw
        else:
            video_final = aplicar_voz_cena(video_raw, cena, idx)

        if video_final and os.path.exists(video_final):
            videos_finais.append(video_final)
            print(f"  OK: {os.path.basename(video_final)}")

        time.sleep(1)

    if somente_imagens:
        print(f"\n{somente_imagens} imagens geradas em {UPLOADS}")
        return

    if len(videos_finais) < 2:
        print(f"\nApenas {len(videos_finais)} cena(s) pronta(s).")
        return

    print(f"\n{'='*70}")
    print(f"Concatenando {len(videos_finais)} cenas...")
    slug = Path(json_path).stem
    saida_final = BASE / f"{slug}.mp4"

    if concatenar_videos(videos_finais, saida_final):
        tamanho_mb = saida_final.stat().st_size / (1024 * 1024)
        print(f"\n{'='*70}")
        print(f"NOVELINHA PRONTA!")
        print(f"Arquivo: {saida_final}")
        print(f"Tamanho: {tamanho_mb:.1f} MB")
        print(f"Abra: http://localhost/agente/{saida_final.name}")
        print(f"Ou direto: file:///{saida_final}")
        print(f"{'='*70}")

        if DB_OK:
            db.registrar("novelinha", titulo, saida_final.name, "videos_saida/novelinha",
                        legenda=" | ".join(c.get("legenda", "")[:50] for c in cenas),
                        hashtags="#tronix #novelinha #realismoMagico",
                        voz_usada="AntonioNeural",
                        tamanho_kb=int(tamanho_mb * 1024),
                        duracao_seg=sum(c.get("duracao", 6) for c in cenas))

        return saida_final
    else:
        print(f"ERRO na concatenacao")
        return None


def main():
    parser = argparse.ArgumentParser(description="Tronix Novelinha - gerador de mini-novelas")
    parser.add_argument("--input", "-i", default=str(BASE / "novelinha_velho_estrela.json"),
                        help="Arquivo JSON do roteiro")
    parser.add_argument("--somente-imagens", action="store_true", help="So gera imagens, sem videos")
    parser.add_argument("--sem-voz", action="store_true", help="Gera video sem narração")
    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"ERRO: Arquivo nao encontrado: {args.input}")
        sys.exit(1)

    processar_novelinha(args.input, args.somente_imagens, args.sem_voz)


if __name__ == "__main__":
    main()
