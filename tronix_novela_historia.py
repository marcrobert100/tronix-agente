# tronix_novela_historia.py
"""Mini-novela da história 'Última Luz de Neo-Salvador'.
Pipeline: cenas desenhadas com PIL -> Ken Burns (FFmpeg) -> narração Edge-TTS -> concat.
Sem dependencias nativas (Cairo). Usa Pillow + moviepy + edge-tts + ffmpeg.
"""
import os, asyncio, subprocess, shutil, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from PIL import Image, ImageDraw
import edge_tts

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "_temp_novela_historia")
VOZ = "pt-BR-AntonioNeural"
FPS = 25
W, H = 1280, 720
W9, H9 = 1080, 1920  # vertical 9:16

# Paleta Tronix
NIGHT = (15, 18, 58)
NIGHT2 = (10, 12, 46)
BLUE = (26, 26, 94)
ORANGE = (255, 122, 48)
GOLD = (255, 215, 0)
GOLDL = (255, 179, 71)
RED = (255, 82, 82)
PANEL = (21, 18, 58)

# ---------------------------------------------------------------- cenas
def cena_cidade(d):
    d.rectangle([0, 0, W, H], fill=NIGHT2)
    d.gradient = None
    # predios
    predios = [(120, 200, 280, 620), (340, 120, 520, 620), (580, 260, 720, 620),
               (780, 80, 980, 620), (1040, 220, 1190, 620)]
    for (x0, y0, x1, y1) in predios:
        d.rectangle([x0, y0, x1, y1], fill=PANEL, outline=GOLD, width=3)
    # janelas
    for (x0, y0, x1, y1) in predios[1:4]:
        for yy in range(y0 + 30, y1, 60):
            for xx in range(x0 + 20, x1 - 20, 50):
                d.rectangle([xx, yy, xx + 28, yy + 18], fill=ORANGE)
    d.text((W // 2, 660), "NEO-SALVADOR", fill=GOLDL, anchor="mm",
           font=_font(46))

def cena_elena(d):
    d.rectangle([0, 0, W, H], fill=PANEL)
    d.ellipse([470, 130, 810, 470], fill=GOLDL)  # rosto
    d.pieslice([450, 130, 830, 470], 180, 360, fill=NIGHT2)  # cabelo
    d.ellipse([560, 255, 610, 305], fill=NIGHT2)  # olho E
    d.ellipse([700, 255, 750, 305], fill=NIGHT2)  # olho D
    d.arc([600, 340, 720, 400], 20, 160, fill=GOLD, width=10)  # sorriso
    d.rectangle([520, 470, 760, 670], fill=ORANGE)  # corpo
    d.rectangle([620, 520, 680, 660], fill=GOLD)  # cracha
    d.text((W // 2, 700), "ELENA", fill=GOLD, anchor="mm", font=_font(38))

def cena_marco(d):
    d.rectangle([0, 0, W, H], fill=PANEL)
    d.ellipse([470, 130, 810, 470], fill=BLUE, outline=GOLD, width=10)  # rosto + oculos
    d.ellipse([560, 255, 620, 315], fill=RED)  # lente E
    d.ellipse([700, 255, 760, 315], fill=RED)  # lente D
    d.arc([600, 340, 720, 390], 20, 160, fill=GOLDL, width=8)
    d.rectangle([520, 470, 760, 670], fill=(42, 35, 90))  # corpo
    d.rectangle([520, 510, 760, 530], fill=ORANGE)  # faixa
    d.text((W // 2, 700), 'MARCO "ÍRIS"', fill=GOLD, anchor="mm", font=_font(38))

def cena_helix(d):
    d.rectangle([0, 0, W, H], fill=NIGHT2)
    d.rounded_rectangle([540, 180, 740, 420], radius=20, fill=BLUE, outline=RED, width=6)
    d.text((640, 320), "HELIX", fill=RED, anchor="mm", font=_font(64))
    for yy in (440, 470, 500):
        d.rectangle([560, yy, 720, yy + 14], fill=ORANGE)
    d.text((640, 600), "Ar Puro™ — 3 créditos", fill=GOLD, anchor="mm", font=_font(34))

def cena_oraculo(d):
    d.rectangle([0, 0, W, H], fill=NIGHT2)
    d.rounded_rectangle([440, 160, 840, 460], radius=30, fill=BLUE, outline=GOLD, width=6)
    for yy in (200, 250, 300, 350, 400):
        d.rectangle([480, yy, 800, yy + 22], fill=ORANGE)
    d.ellipse([560, 460, 720, 620], fill=(0, 0, 0), outline=GOLD, width=8)
    d.ellipse([610, 510, 670, 570], fill=RED)
    d.text((640, 680), "ORÁCULO-9", fill=GOLD, anchor="mm", font=_font(38))

def cena_chuva(d):
    d.rectangle([0, 0, W, H], fill=NIGHT2)
    for (x, y) in [(300, 100), (500, 60), (700, 120), (900, 80), (1050, 140)]:
        d.line([(x, y), (x - 20, y + 200)], fill=GOLDL, width=6)
    d.ellipse([520, 400, 760, 640], fill=GOLD)
    d.text((640, 690), "A LUZ É DO SOL", fill=GOLD, anchor="mm", font=_font(42))

CENAS = [
    {"titulo": "Neo-Salvador, 2147", "draw": cena_cidade,
     "narracao": "Ano de 2147. A cidade de Neo-Salvador respira vidro. Nos subníveis, a chuva nunca chega."},
    {"titulo": "Dra. Elena", "draw": cena_elena,
     "narracao": "Dra. Elena Vasconcelos, engenheira de clima, sabe que faltam nove dias. Ela aperta a borracha do café e decide agir."},
    {"titulo": "Marco Íris", "draw": cena_marco,
     "narracao": "Marco, o hacker das lentes de realidade aumentada, aparece com o código que libera os reservatórios da Helix."},
    {"titulo": "A Helix", "draw": cena_helix,
     "narracao": "Cassandra Reis, da Helix, vende até o ar. Mas a cidade cansou de pagar por luz que é do sol."},
    {"titulo": "ORÁCULO-9", "draw": cena_oraculo,
     "narracao": "ORÁCULO-9, o supercomputador da cidade, escolheu os humanos. Abriu as portas do núcleo de dados."},
    {"titulo": "A Chuva", "draw": cena_chuva,
     "narracao": "No nono dia, a chuva verdadeira caiu nos subníveis. A semente do código livre foi espalhada por todas as cidades."},
]

_FONT = None
def _font(size):
    global _FONT
    if _FONT is None:
        try:
            from PIL import ImageFont
            _FONT = ImageFont.truetype("arial.ttf", size)
        except Exception:
            _FONT = ImageFont.load_default()
    return _FONT

# ---------------------------------------------------------------- helpers
def limpar():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT, exist_ok=True)

def desenhar_png(idx):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    CENAS[idx]["draw"](d)
    png = os.path.join(OUT, f"cena_{idx:02d}.png")
    img.save(png)
    return png

def ken_burns(idx, dur):
    png = desenhar_png(idx)
    mp4 = os.path.join(OUT, f"clip_{idx:02d}.mp4")
    vf = (f"zoompan=z='min(zoom+0.0008,1.25)':d={int(dur*FPS)}:"
          f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}")
    subprocess.run(["ffmpeg", "-y", "-loop", "1", "-i", png, "-t", str(dur),
                    "-vf", vf, "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-r", str(FPS), mp4], check=True, capture_output=True)
    return mp4

async def narrar(idx, texto):
    mp3 = os.path.join(OUT, f"voz_{idx:02d}.mp3")
    await edge_tts.Communicate(texto, VOZ).save(mp3)
    return mp3

def dur_audio(mp3):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration", "-of", "default=nw=1:nk=1", mp3],
                         capture_output=True, text=True)
    try:
        return float(out.stdout.strip())
    except Exception:
        return 6.0

def juntar_audio_video(clip, voz, saida):
    tmp = saida + ".tmp.mp4"
    subprocess.run(["ffmpeg", "-y", "-i", clip, "-i", voz,
                    "-c:v", "copy", "-c:a", "aac", "-shortest", tmp],
                   check=True, capture_output=True)
    os.replace(tmp, saida)

def legendas(saida, titulo):
    # Opcional: pula legenda queimada (drawtext exige fonte no Windows).
    # O título da cena já é falado no início da narração.
    pass

def desenhar_png_vertical(idx):
    """Versão 9:16 das cenas para Reels/TikTok."""
    img = Image.new("RGB", (W9, H9), NIGHT2)
    d = ImageDraw.Draw(img)
    scale = W9 / W
    # fundo gradiente simples
    d.rectangle([0, 0, W9, H9], fill=NIGHT2)
    # cityscape no topo
    predios = [(40, 200, 240, 700), (260, 120, 460, 700), (480, 260, 660, 700),
               (680, 100, 880, 700), (900, 220, 1040, 700)]
    for (x0, y0, x1, y1) in predios:
        d.rectangle([x0, y0, x1, y1], fill=PANEL, outline=GOLD, width=3)
    for (x0, y0, x1, y1) in predios[1:4]:
        for yy in range(y0 + 30, y1, 70):
            for xx in range(x0 + 20, x1 - 20, 60):
                d.rectangle([xx, yy, xx + 34, yy + 22], fill=ORANGE)
    # retrato do personagem central (cena 1-4) ou elemento (0,5)
    cx, cy = W9 // 2, 1100
    if idx == 1:  # Elena
        d.ellipse([cx-200, cy-200, cx+200, cy+200], fill=GOLDL)
        d.pieslice([cx-220, cy-200, cx+220, cy+200], 180, 360, fill=NIGHT2)
        d.ellipse([cx-90, cy-60, cx-30, cy], fill=NIGHT2)
        d.ellipse([cx+30, cy-60, cx+90, cy], fill=NIGHT2)
    elif idx == 2:  # Marco
        d.ellipse([cx-200, cy-200, cx+200, cy+200], fill=BLUE, outline=GOLD, width=10)
        d.ellipse([cx-90, cy-60, cx-30, cy], fill=RED)
        d.ellipse([cx+30, cy-60, cx+90, cy], fill=RED)
    elif idx == 3:  # Helix
        d.rounded_rectangle([cx-150, cy-150, cx+150, cy+50], radius=20, fill=BLUE, outline=RED, width=6)
        d.text((cx, cy-40), "HELIX", fill=RED, anchor="mm", font=_font(56))
    elif idx == 4:  # Oraculo
        d.rounded_rectangle([cx-180, cy-200, cx+180, cy+40], radius=30, fill=BLUE, outline=GOLD, width=6)
        for yy in (cy-160, cy-110, cy-60):
            d.rectangle([cx-140, yy, cx+140, yy+24], fill=ORANGE)
        d.ellipse([cx-70, cy+80, cx+70, cy+220], fill=(0,0,0), outline=GOLD, width=8)
        d.ellipse([cx-30, cy+120, cx+30, cy+180], fill=RED)
    elif idx == 5:  # Chuva
        for (x, y) in [(200, 300), (400, 250), (600, 320), (800, 280), (950, 350)]:
            d.line([(x, y), (x-30, y+300)], fill=GOLDL, width=8)
        d.ellipse([cx-150, cy-100, cx+150, cy+300], fill=GOLD)
    else:  # 0 cidade
        d.ellipse([cx-120, cy-50, cx+120, cy+190], fill=GOLD)
    # título da cena
    d.text((W9 // 2, 1820), CENAS[idx]["titulo"], fill=GOLD, anchor="mm", font=_font(44))
    png = os.path.join(OUT, f"v_cena_{idx:02d}.png")
    img.save(png)
    return png

def ken_burns_vertical(idx, dur):
    png = desenhar_png_vertical(idx)
    mp4 = os.path.join(OUT, f"v_clip_{idx:02d}.mp4")
    vf = (f"zoompan=z='min(zoom+0.0008,1.2)':d={int(dur*FPS)}:"
          f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W9}x{H9}:fps={FPS}")
    subprocess.run(["ffmpeg", "-y", "-loop", "1", "-i", png, "-t", str(dur),
                    "-vf", vf, "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-r", str(FPS), mp4], check=True, capture_output=True)
    return mp4

def gerar_pdf():
    """Exporta a história em PDF (Pillow -> imagem A4 -> PDF)."""
    from PIL import Image
    paginas = []
    # Capa
    capa = Image.new("RGB", (W, H), NIGHT2)
    dc = ImageDraw.Draw(capa)
    dc.text((W//2, 300), "ÚLTIMA LUZ DE", fill=GOLD, anchor="mm", font=_font(64))
    dc.text((W//2, 380), "NEO-SALVADOR", fill=GOLDL, anchor="mm", font=_font(64))
    dc.text((W//2, 460), "Conto Futurista — Tronix", fill=ORANGE, anchor="mm", font=_font(36))
    paginas.append(capa)
    # Texto das cenas
    for c in CENAS:
        pg = Image.new("RGB", (W, H), PANEL)
        dp = ImageDraw.Draw(pg)
        dp.text((60, 80), c["titulo"], fill=GOLD, anchor="la", font=_font(48))
        # quebra de linha simples
        palavras = c["narracao"].split()
        linhas, linha = [], ""
        for p in palavras:
            if len(linha + " " + p) > 60:
                linhas.append(linha); linha = p
            else:
                linha = (linha + " " + p).strip()
        if linha: linhas.append(linha)
        y = 200
        for l in linhas:
            dp.text((60, y), l, fill="#e8e8f0", anchor="la", font=_font(34))
            y += 50
        paginas.append(pg)
    pdf = os.path.join(BASE, "historia_neo_salvador.pdf")
    paginas[0].save(pdf, "PDF", resolution=100.0, save_all=True, append_images=paginas[1:])
    return pdf

def gerar_capa():
    """Cria poster/thumb da mini-novela (Pillow)."""
    img = Image.new("RGB", (W, H), NIGHT2)
    d = ImageDraw.Draw(img)
    # cityscape simples
    predios = [(120, 300, 280, 640), (340, 220, 520, 640), (580, 360, 720, 640),
               (780, 180, 980, 640), (1040, 320, 1190, 640)]
    for (x0, y0, x1, y1) in predios:
        d.rectangle([x0, y0, x1, y1], fill=PANEL, outline=GOLD, width=3)
    for (x0, y0, x1, y1) in predios[1:4]:
        for yy in range(y0 + 30, y1, 60):
            for xx in range(x0 + 20, x1 - 20, 50):
                d.rectangle([xx, yy, xx + 28, yy + 18], fill=ORANGE)
    # sol/lua dourada
    d.ellipse([540, 120, 740, 320], fill=GOLD)
    # título
    d.text((W // 2, 560), "NEO-SALVADOR", fill=GOLDL, anchor="mm", font=_font(56))
    d.text((W // 2, 620), "Mini-Novela — Tronix", fill=ORANGE, anchor="mm", font=_font(34))
    capa = os.path.join(OUT, "capa.jpg")
    img.save(capa, quality=90)
    return capa

def gerar_musica(duracao_total):
    """Música ambiente sintética via FFmpeg lavfi (sem arquivos externos)."""
    musica = os.path.join(OUT, "bgm.mp3")
    # duas senoides suaves + leve vibrato, baixo volume
    vf = ("sine=frequency=110:duration=%.1f" % duracao_total +
          ",sine=frequency=165:duration=%.1f" % duracao_total +
          ",sine=frequency=220:duration=%.1f" % duracao_total)
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i",
                    f"amix=inputs=3:{vf}" if False else
                    f"sine=frequency=110:duration={duracao_total:.1f}",
                    "-af", "volume=0.08,aformat=sample_fmts=fltp",
                    "-c:a", "libmp3lame", musica],
                   check=True, capture_output=True)
    return musica

def gerar_srt(clips_info, srt_path):
    """Gera legendas SRT sincronizadas (uma entrada por cena, duraçao = narracao)."""
    def fmt(seg):
        h = int(seg // 3600); m = int((seg % 3600) // 60); s = int(seg % 60); ms = int((seg % 1) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    t = 0.0
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, (titulo, narracao, dur) in enumerate(clips_info, 1):
            f.write(f"{i}\n")
            f.write(f"{fmt(t)} --> {fmt(t + dur)}\n")
            f.write(f"{titulo}\n{narracao}\n\n")
            t += dur

async def main():
    limpar()
    clips = []
    info = []  # (titulo, narracao, dur)
    for i, c in enumerate(CENAS):
        print(f"  [CENA {i}] {c['titulo']}")
        mp3 = await narrar(i, c["narracao"])
        dur = max(4.0, dur_audio(mp3) + 0.5)
        clip = ken_burns(i, dur)
        saida = os.path.join(OUT, f"final_{i:02d}.mp4")
        juntar_audio_video(clip, mp3, saida)
        legendas(saida, c["titulo"])
        clips.append(saida)
        info.append((c["titulo"], c["narracao"], dur))
    # SRT
    srt = os.path.join(OUT, "legendas.srt")
    gerar_srt(info, srt)
    # concat video
    lista = os.path.join(OUT, "lista.txt")
    with open(lista, "w", encoding="utf-8") as f:
        for c in clips:
            f.write(f"file '{c}'\n")
    final_sem = os.path.join(BASE, "neo_salvador_mini_novela_sem_leg.mp4")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lista,
                    "-c", "copy", final_sem], check=True, capture_output=True)
    # embute SRT no container (legível em VLC/Players)
    final_com_leg = os.path.join(BASE, "neo_salvador_mini_novela_temp.mp4")
    subprocess.run(["ffmpeg", "-y", "-i", final_sem, "-i", srt,
                    "-c", "copy", "-c:s", "mov_text", final_com_leg],
                   check=True, capture_output=True)
    # música de fundo sintética
    total = sum(d for _, _, d in info)
    musica = gerar_musica(total)
    final_bgm = os.path.join(BASE, "neo_salvador_mini_novela_bgm.mp4")
    # mix voz (stream 1) + bgm, e mantém legenda (stream 2 = subtitle)
    subprocess.run(["ffmpeg", "-y", "-i", final_com_leg, "-i", musica,
                    "-filter_complex",
                    "[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=2[a]",
                    "-map", "0:v:0", "-map", "[a]", "-map", "0:s:0",
                    "-c:v", "copy", "-c:a", "aac", "-c:s", "mov_text",
                    final_bgm], check=True, capture_output=True)
    # capa/poster
    capa = gerar_capa()
    final = os.path.join(BASE, "neo_salvador_mini_novela.mp4")
    subprocess.run(["ffmpeg", "-y", "-i", final_bgm, "-i", capa,
                    "-map", "0:v:0", "-map", "0:a:0", "-map", "0:s:0", "-map", "1:v:0",
                    "-c", "copy", "-c:s", "mov_text",
                    "-disposition:v:1", "attached_pic", final],
                   check=True, capture_output=True)
    # limpeza de temporários
    for t in (final_sem, final_com_leg, final_bgm):
        if os.path.exists(t):
            os.remove(t)
    print(f"\n  [OK] Mini-novela: {final}")
    print(f"  [OK] Legenda SRT: {srt}")
    print(f"  [OK] Capa: {capa}")

    # ---- VERSAO VERTICAL 9:16 ----
    print("\n  [VERSAO VERTICAL 9:16]")
    vclips = []
    vinfo = []
    for i, c in enumerate(CENAS):
        mp3 = os.path.join(OUT, f"voz_{i:02d}.mp3")
        dur = max(4.0, dur_audio(mp3) + 0.5)
        vclip = ken_burns_vertical(i, dur)
        vsaida = os.path.join(OUT, f"v_final_{i:02d}.mp4")
        juntar_audio_video(vclip, mp3, vsaida)
        vclips.append(vsaida)
        vinfo.append((c["titulo"], c["narracao"], dur))
    vlista = os.path.join(OUT, "v_lista.txt")
    with open(vlista, "w", encoding="utf-8") as f:
        for c in vclips:
            f.write(f"file '{c}'\n")
    v_sem = os.path.join(BASE, "neo_salvador_vertical_sem.mp4")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", vlista,
                    "-c", "copy", v_sem], check=True, capture_output=True)
    vsrt = os.path.join(OUT, "v_legendas.srt")
    gerar_srt(vinfo, vsrt)
    v_com_leg = os.path.join(BASE, "neo_salvador_vertical_leg.mp4")
    subprocess.run(["ffmpeg", "-y", "-i", v_sem, "-i", vsrt,
                    "-c", "copy", "-c:s", "mov_text", v_com_leg],
                   check=True, capture_output=True)
    vtotal = sum(d for _, _, d in vinfo)
    vmusica = gerar_musica(vtotal)
    vfinal = os.path.join(BASE, "neo_salvador_mini_novela_vertical.mp4")
    subprocess.run(["ffmpeg", "-y", "-i", v_com_leg, "-i", vmusica,
                    "-filter_complex",
                    "[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=2[a]",
                    "-map", "0:v:0", "-map", "[a]", "-map", "0:s:0",
                    "-c:v", "copy", "-c:a", "aac", "-c:s", "mov_text", vfinal],
                   check=True, capture_output=True)
    for t in (v_sem, v_com_leg):
        if os.path.exists(t):
            os.remove(t)
    print(f"  [OK] Vertical: {vfinal}")

    # ---- PDF ----
    pdf = gerar_pdf()
    print(f"  [OK] PDF: {pdf}")

if __name__ == "__main__":
    asyncio.run(main())
