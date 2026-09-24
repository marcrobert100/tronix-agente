"""Copa 2026 — Video final com Pillow (texto garantido) + Edge-TTS."""
import subprocess, os, sys, asyncio
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = Path(__file__).parent
VIDEOS = BASE / "videos_saida"
FRAMES = BASE / "_copa_frames"
VIDEOS.mkdir(exist_ok=True)
FRAMES.mkdir(exist_ok=True)

SELECOES = [
    ("BRASIL", "#009c3b", "Selecao de 5 estrelas! Vinicius Jr e Rodrygo rumo ao sexto titulo!"),
    ("ARGENTINA", "#74acdf", "Bicampea mundial! Messi defende o titulo conquistado no Catar!"),
    ("FRANCA", "#002395", "Vice-campea 2022. Mbappe quer o titulo de volta!"),
    ("INGLATERRA", "#cf142b", "Bellingham e Saka lideram os Three Lions!"),
    ("ALEMANHA", "#1a1a1a", "4 vezes campea. Musiala inicia nova era!"),
    ("ESPANHA", "#aa151b", "Campea Euro 2024. Pedri e Yamal brilham!"),
    ("PORTUGAL", "#006600", "CR7 em provavel ultima Copa!"),
    ("URUGUAI", "#5b9aa0", "2 vezes campea. Nunez e Valverde!"),
    ("COLOMBIA", "#fcd116", "James Rodriguez e a festa sul-americana!"),
    ("MARROCOS", "#c1272d", "Sensacao 2022! Hakimi lidera de novo!"),
    ("JAPAO", "#bc002d", "Derrotou Alemanha e Espanha na Copa!"),
    ("EUA", "#002868", "Pais sede! Pulisic e Reyna em casa!"),
]

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def criar_imagem_copa(nome, cor_hex, desc, idx):
    """Cria imagem 1920x1080 com fundo colorido + texto."""
    img = Image.new("RGB", (1920, 1080), hex_to_rgb(cor_hex))
    draw = ImageDraw.Draw(img)
    
    # Fontes
    try:
        font_big = ImageFont.truetype("C:/Windows/Fonts/impact.ttf", 120)
        font_med = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 50)
        font_small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 36)
    except:
        font_big = ImageFont.load_default()
        font_med = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Barra preta topo
    draw.rectangle([0, 0, 1920, 180], fill=(0, 0, 0, 200))
    # Barra preta fundo
    draw.rectangle([0, 880, 1920, 1080], fill=(0, 0, 0, 200))
    
    # Sigla grande (fundo)
    bbox = draw.textbbox((0, 0), nome, font=font_big)
    tw = bbox[2] - bbox[0]
    draw.text(((1920 - tw) // 2, 400), nome, fill=(255, 255, 255, 40), font=font_big)
    
    # Nome da selecao (topo)
    bbox = draw.textbbox((0, 0), nome, font=font_big)
    tw = bbox[2] - bbox[0]
    draw.text(((1920 - tw) // 2, 30), nome, fill="white", font=font_big)
    
    # Copa 2026 (fundp)
    texto_copa = "COPA DO MUNDO 2026"
    bbox = draw.textbbox((0, 0), texto_copa, font=font_med)
    tw = bbox[2] - bbox[0]
    draw.text(((1920 - tw) // 2, 900), texto_copa, fill="#FFD700", font=font_med)
    
    # Descricao
    bbox = draw.textbbox((0, 0), desc, font=font_small)
    tw = bbox[2] - bbox[0]
    draw.text(((1920 - tw) // 2, 970), desc, fill="white", font=font_small)
    
    saida = FRAMES / f"copa_{idx:02d}.png"
    img.save(str(saida))
    return saida

def gerar_voz(texto, destino):
    import edge_tts
    async def _gen():
        c = edge_tts.Communicate(texto, "pt-BR-AntonioNeural", rate="+5%")
        await c.save(str(destino))
    asyncio.run(_gen())

# 1. Criar imagens
print("1. Criando imagens com Pillow...")
imagens = []
for i, (nome, cor, desc) in enumerate(SELECOES):
    img = criar_imagem_copa(nome, cor, desc, i+1)
    imagens.append(img)
    print(f"  {nome}: {img.name}")

# 2. Criar videos Ken Burns
print("\n2. Criando videos Ken Burns...")
videos_raw = []
for i, img in enumerate(imagens):
    out = VIDEOS / f"copa_{i+1:02d}.mp4"
    subprocess.run([
        "ffmpeg", "-loop", "1", "-i", str(img),
        "-t", "6", "-vf",
        "scale=1920:1080,zoompan=z='min(zoom+0.001,1.3)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=180:s=1920x1080:fps=30",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-y", str(out)
    ], capture_output=True, timeout=60)
    if out.exists():
        videos_raw.append(out)
        print(f"  Cena {i+1}: OK")

# 3. Gerar vozes
print("\n3. Gerando voces...")
finais = []
for i, (nome, cor, desc) in enumerate(SELECOES):
    if i >= len(videos_raw):
        break
    voz = VIDEOS / f"copa_voz_{i+1:02d}.mp3"
    final = VIDEOS / f"copa_f_{i+1:02d}.mp4"
    raw = videos_raw[i]
    
    voz_texto = f"{nome}! {desc}"
    gerar_voz(voz_texto, voz)
    
    if voz.exists():
        subprocess.run([
            "ffmpeg", "-i", str(raw), "-i", str(voz),
            "-c:v", "copy", "-c:a", "aac", "-shortest", "-y", str(final)
        ], capture_output=True, timeout=30)
        if final.exists():
            finais.append(final)
            voz.unlink(missing_ok=True)
            print(f"  {nome}: OK")

# 4. Concatenar
print(f"\n4. Juntando {len(finais)} cenas...")
concat = VIDEOS / "_concat.txt"
with open(concat, "w", encoding="utf-8") as f:
    for v in finais:
        f.write("file '" + os.path.abspath(v) + "'\n")

final = VIDEOS / "copa2026_selecoes.mp4"
subprocess.run([
    "ffmpeg", "-f", "concat", "-safe", "0",
    "-i", str(concat), "-c", "copy",
    "-movflags", "+faststart", "-y", str(final)
], capture_output=True, timeout=120)

concat.unlink(missing_ok=True)

# Limpar temporarios
for f in FRAMES.glob("*.png"):
    f.unlink()

if final.exists():
    mb = final.stat().st_size / (1024*1024)
    print(f"\n{'='*50}")
    print(f"COPA 2026 — VIDEO FINAL PRONTO!")
    print(f"Arquivo: {final}")
    print(f"Tamanho: {mb:.1f} MB")
    print(f"Duracao: ~{len(finais)*6}s")
    print(f"{'='*50}")
