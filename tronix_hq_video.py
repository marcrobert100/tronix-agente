#!/usr/bin/env python3
"""
Tronix HQ Video - Gerador de Videos de Alta Qualidade
Pipeline: Imagens locais/geradas -> Ken Burns -> Edge-TTS -> FFmpeg
Resolucao: 1920x1080 @ 30fps
"""
import os, sys, time, asyncio, subprocess, hashlib, math, random
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import colorsys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = Path(__file__).parent
UPLOADS = ROOT / "uploads"
OUTPUT = ROOT / "videos_saida"
TEMP = ROOT / "_temp_hq"
VOZ = "pt-BR-AntonioNeural"
FPS = 30
RESOLUCAO = (1920, 1080)

def log(msg):
    print(f"[HQ] {msg}", flush=True)

def ensure_dirs():
    for d in [UPLOADS, OUTPUT, TEMP]:
        d.mkdir(parents=True, exist_ok=True)

def gerar_paisagem_brasileira(tipo, width=1920, height=1080):
    """Gera paisagem brasileira estilizada com PIL."""
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)
    
    palettes = {
        "pôr do sol": {
            "sky_top": (25, 10, 60), "sky_mid": (180, 60, 20), "sky_bot": (255, 140, 30),
            "ground": (20, 40, 20), "accent": (255, 200, 50)
        },
        "montanha": {
            "sky_top": (10, 30, 80), "sky_mid": (60, 120, 200), "sky_bot": (150, 200, 240),
            "ground": (40, 80, 40), "accent": (255, 255, 255)
        },
        "praia": {
            "sky_top": (30, 100, 180), "sky_mid": (80, 160, 220), "sky_bot": (150, 210, 250),
            "ground": (240, 210, 150), "accent": (0, 150, 200)
        },
        "floresta": {
            "sky_top": (20, 60, 100), "sky_mid": (40, 100, 60), "sky_bot": (60, 140, 40),
            "ground": (30, 80, 20), "accent": (255, 220, 50)
        },
    }
    
    p = palettes.get(tipo, palettes["pôr do sol"])
    
    # Gradiente do céu
    for y in range(height):
        ratio = y / height
        if ratio < 0.6:
            t = ratio / 0.6
            r = int(p["sky_top"][0] * (1-t) + p["sky_mid"][0] * t)
            g = int(p["sky_top"][1] * (1-t) + p["sky_mid"][1] * t)
            b = int(p["sky_top"][2] * (1-t) + p["sky_mid"][2] * t)
        else:
            t = (ratio - 0.6) / 0.4
            r = int(p["sky_mid"][0] * (1-t) + p["sky_bot"][0] * t)
            g = int(p["sky_mid"][1] * (1-t) + p["sky_bot"][1] * t)
            b = int(p["sky_mid"][2] * (1-t) + p["sky_bot"][2] * t)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Elementos visuais
    ground_y = int(height * 0.65)
    draw.rectangle([(0, ground_y), (width, height)], fill=p["ground"])
    
    # Montanhas/serras
    points = [(0, ground_y)]
    for x in range(0, width + 50, 50):
        y_off = math.sin(x * 0.008) * 80 + math.sin(x * 0.003) * 120
        points.append((x, ground_y - 60 - abs(y_off)))
    points.append((width, ground_y))
    draw.polygon(points, fill=(p["ground"][0]+15, p["ground"][1]+25, p["ground"][2]+10))
    
    # Sol/lua
    sol_x, sol_y = int(width * 0.75), int(height * 0.3)
    for r in range(80, 0, -2):
        alpha = max(0, min(255, 255 - r * 3))
        color = tuple(min(255, c + alpha // 4) for c in p["accent"])
        draw.ellipse([sol_x - r, sol_y - r, sol_x + r, sol_y + r], fill=color)
    
    # Reflexo d'água
    water_y = int(height * 0.85)
    for y in range(water_y, height):
        for x in range(0, width, 3):
            offset = int(math.sin(x * 0.05 + y * 0.1) * 3)
            if (y + offset) % 4 == 0:
                draw.point((x, y), fill=p["accent"])
    
    # Nuvens
    for _ in range(5):
        cx = random.randint(0, width)
        cy = random.randint(30, int(height * 0.4))
        for dx in range(-40, 41, 8):
            for dy in range(-10, 11, 6):
                r = random.randint(8, 18)
                draw.ellipse([cx+dx-r, cy+dy-r, cx+dx+r, cy+dy+r], fill=(255, 255, 255, 30))
    
    # Vegetação
    for _ in range(15):
        tx = random.randint(0, width)
        ty = random.randint(ground_y + 10, height - 50)
        tree_h = random.randint(30, 80)
        draw.rectangle([tx-2, ty-tree_h, tx+2, ty], fill=(50, 30, 20))
        for r in range(15, 0, -2):
            draw.ellipse([tx-r, ty-tree_h-r*2, tx+r, ty-tree_h+r//2], fill=(20+random.randint(0,30), 80+random.randint(0,40), 20))
    
    # Texto overlay (sutil)
    try:
        font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 28)
        draw.text((30, height - 50), "TRONIX HQ", fill=(255, 255, 255, 180), font=font)
    except:
        pass
    
    # Aplicar blur leve para suavizar
    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
    
    return img

def gerar_todas_imagens():
    """Gera 4 paisagens brasileiras diferentes."""
    tipos = ["pôr do sol", "montanha", "praia", "floresta"]
    caminhos = []
    
    log("Gerando paisagens brasileiras...")
    for i, tipo in enumerate(tipos):
        img = gerar_paisagem_brasileira(tipo)
        path = UPLOADS / f"paisagem_{i:02d}_{tipo.replace(' ', '_')}.png"
        img.save(path, "PNG", quality=95)
        caminhos.append(str(path))
        log(f"Paisagem {i+1}/4: {tipo} -> {path.name}")
    
    return caminhos

def aplicar_ken_burns(imagem_path, duracao, saida_path, zoom_in=1.0, zoom_out=1.2, pan_x=0, pan_y=0):
    """Aplica efeito Ken Burns com alta qualidade via FFmpeg."""
    log(f"Ken Burns: {Path(imagem_path).name} -> {duracao}s")
    
    total_frames = int(duracao * FPS)
    
    vf_filters = []
    vf_filters.append(f"scale=8000:-1:flags=lanczos")
    vf_filters.append(
        f"zoompan=z='min({zoom_in}+(({zoom_out}-{zoom_in})*on/{total_frames}),{zoom_out})'"
        f":x='iw/2-(iw/zoom/2)+{pan_x}*on/{total_frames}'"
        f":y='ih/2-(ih/zoom/2)+{pan_y}*on/{total_frames}'"
        f":d={total_frames}:s={RESOLUCAO[0]}x{RESOLUCAO[1]}:fps={FPS}"
    )
    vf_filters.append("format=yuv420p")
    vf_filters.append("unsharp=5:5:0.8:3:3:0.4")
    
    vf = ",".join(vf_filters)
    
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", imagem_path,
        "-vf", vf,
        "-t", str(duracao),
        "-c:v", "libx264", "-preset", "slow", "-crf", "15",
        "-pix_fmt", "yuv420p",
        "-r", str(FPS),
        saida_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if result.returncode != 0:
        log(f"Erro Ken Burns: {result.stderr[-300:]}")
        return False
    log(f"Ken Burns pronto: {Path(saida_path).name}")
    return True

def gerar_voz(texto, saida_path):
    """Gera audio via Edge-TTS."""
    log(f"Gerando voz: {texto[:50]}...")
    try:
        import edge_tts
        communicate = edge_tts.Communicate(texto, VOZ)
        asyncio.run(communicate.save(saida_path))
        log(f"Voz pronta: {Path(saida_path).name}")
        return True
    except Exception as e:
        log(f"Erro voz: {e}")
        return False

def mixar_video_audio(video_path, audio_path, saida_path, legenda=None):
    """Mixa video + audio com FFmpeg."""
    log("Mixando video + audio...")
    
    cmd = ["ffmpeg", "-y", "-i", video_path, "-i", audio_path]
    
    vf_parts = []
    if legenda:
        safe_legenda = legenda.replace("'", "'\\''").replace(":", "\\:")
        vf_parts.append(
            f"drawtext=text='{safe_legenda}':"
            f"fontfile='C\\:/Windows/Fonts/arial.ttf':"
            f"fontcolor=white:fontsize=42:borderw=3:bordercolor=black:"
            f"x=(w-text_w)/2:y=h-90"
        )
    
    if vf_parts:
        cmd.extend(["-vf", ",".join(vf_parts)])
        cmd.extend(["-c:v", "libx264", "-preset", "slow", "-crf", "15"])
    else:
        cmd.extend(["-c:v", "copy"])
    
    cmd.extend([
        "-map", "0:v", "-map", "1:a",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        saida_path
    ])
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        log(f"Erro mix: {result.stderr[-300:]}")
        return False
    log(f"Video final: {Path(saida_path).name}")
    return True

def gerar_video_hq(tema, duracao_por_cena=6):
    """Gera video completo de alta qualidade."""
    ensure_dirs()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_clips = []
    
    tipos = ["pôr do sol", "montanha", "praia", "floresta"]
    narracoes = [
        "Bem-vindos ao Brasil. Um pais de belezas naturais incomparaveis.",
        "Das montanhas da Serra da Mantiqueira as praias do Nordeste.",
        "Cada paisagem conta uma historia de natureza e cultura.",
        "Tronix - transformando visoes em videos cinematograficos.",
    ]
    
    total_cenas = len(tipos)
    duracao_total = duracao_por_cena * total_cenas
    
    log(f"{'='*60}")
    log(f"TRONIX HQ VIDEO - {tema}")
    log(f"Cenas: {total_cenas} | Duracao: {duracao_total}s | Resolucao: {RESOLUCAO[0]}x{RESOLUCAO[1]}")
    log(f"{'='*60}")
    
    # 1. Gerar imagens
    log("\n[ETAPA 1/4] Gerando paisagens...")
    imagens = gerar_todas_imagens()
    
    # 2. Ken Burns
    log("\n[ETAPA 2/4] Aplicando Ken Burns...")
    for i, img_path in enumerate(imagens):
        clip_path = str(TEMP / f"clip_{timestamp}_{i:02d}.mp4")
        if i % 2 == 0:
            zoom_in, zoom_out = 1.0, 1.25
            pan_x, pan_y = -150, -80
        else:
            zoom_in, zoom_out = 1.25, 1.0
            pan_x, pan_y = 150, 80
        
        if aplicar_ken_burns(img_path, duracao_por_cena, clip_path, zoom_in, zoom_out, pan_x, pan_y):
            temp_clips.append(clip_path)
    
    if not temp_clips:
        log("ERRO: Nenhum clip gerado")
        return None
    
    # 3. Concatenar
    log("\n[ETAPA 3/4] Concatenando clips...")
    lista_concat = TEMP / f"concat_{timestamp}.txt"
    with open(lista_concat, "w") as f:
        for clip in temp_clips:
            f.write(f"file '{clip}'\n")
    
    video_concat = str(OUTPUT / f"tronix_hq_{timestamp}_concat.mp4")
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(lista_concat),
        "-c:v", "libx264", "-preset", "slow", "-crf", "15",
        "-pix_fmt", "yuv420p", "-r", str(FPS),
        video_concat
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        log(f"Erro concat: {result.stderr[-200:]}")
        return None
    log(f"Concatenado: {Path(video_concat).name}")
    
    # 4. Voz
    log("\n[ETAPA 4/4] Gerando narração...")
    texto_completo = " ".join(narracoes)
    audio_path = str(TEMP / f"voz_{timestamp}.mp3")
    
    if gerar_voz(texto_completo, audio_path):
        video_final = str(OUTPUT / f"tronix_hq_{timestamp}.mp4")
        if mixar_video_audio(video_concat, audio_path, video_final, legenda=tema):
            for clip in temp_clips:
                try: os.remove(clip)
                except: pass
            try: os.remove(video_concat)
            except: pass
            try: os.remove(str(lista_concat))
            except: pass
            try: os.remove(audio_path)
            except: pass
            
            tamanho = os.path.getsize(video_final) / (1024*1024)
            log(f"\n{'='*60}")
            log(f"VIDEO HQ PRONTO!")
            log(f"Arquivo: {video_final}")
            log(f"Tamanho: {tamanho:.1f} MB")
            log(f"Duracao: {duracao_total}s")
            log(f"Resolucao: {RESOLUCAO[0]}x{RESOLUCAO[1]} @ {FPS}fps")
            log(f"{'='*60}")
            return video_final
    
    log("ERRO: Falha na geracao")
    return None


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Tronix HQ Video")
    parser.add_argument("--tema", default="Paisagens epicas do Brasil, cinematografico, 4K")
    parser.add_argument("--duracao", type=float, default=6, help="Duracao por cena")
    args = parser.parse_args()
    
    resultado = gerar_video_hq(tema=args.tema, duracao_por_cena=args.duracao)
    
    if resultado:
        print(f"\nPronto! Video: {resultado}")
    else:
        print("\nFalha na geracao")
