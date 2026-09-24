import os
import sys
import subprocess
import time
import re
import json
import shutil
import requests
from pathlib import Path
from urllib.parse import quote
from io import BytesIO

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = Path(__file__).parent
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

try:
    import tronix_logger as db
    db.inicializar()
except ImportError:
    db = None

try:
    from tronix_director import Director
    director = Director()
except ImportError:
    director = None
    print("[AVISO] tronix_director.py nao encontrado. Rodando sem Director.")

UPLOADS = BASE / "uploads"
VIDEOS_DIR = BASE / "videos_saida"
UPLOADS.mkdir(exist_ok=True)
VIDEOS_DIR.mkdir(exist_ok=True)

TEMA = "Mercadinho Bizu - cap. 1"

VERSAO = "vertical"  # vertical (9:16) = formato viral ReelShort/TikTok/IG
LARG = 1080
ALT = 1920

CENAS = [
    {
        "titulo": "A Porta",
        "plano": "medium",
        "movimento": "static",
        "prompt": "vertical 9:16 photorealistic cinematic still, hot morning in a small Brazilian northeast town, modest corner market with worn wooden sign, middle-aged Brazilian woman sweeping the doorway, dusty street, warm sunlight, realistic skin, film grain, 9:16 portrait",
        "legenda": "O Mercadinho Bizu era a alma da rua.",
    },
    {
        "titulo": "A Rival",
        "plano": "medium",
        "movimento": "static",
        "prompt": "vertical 9:16 photorealistic cinematic still, elegant middle-aged Brazilian woman in red dress standing at a market door holding documents, contemptuous expression, dramatic harsh sunlight, shallow depth of field, emotional tension, 9:16 portrait",
        "legenda": "Mas a vizinha Claudete queria aquele pedaco.",
    },
    {
        "titulo": "O Papel",
        "plano": "close_up",
        "movimento": "zoom_in",
        "prompt": "vertical 9:16 photorealistic close-up of weathered hands holding an eviction notice paper, trembling, dark corner grocery store background, single warm bulb light, dramatic shadows, melancholic mood, film still",
        "legenda": "Um papel... e a porta fechou.",
    },
    {
        "titulo": "O Choro",
        "plano": "close_up",
        "movimento": "zoom_in",
        "prompt": "vertical 9:16 photorealistic cinematic close-up, sad middle-aged Brazilian woman with tears at a dim market counter at night, single lamp glow, emotional portrait, bokeh shelves behind, touching mood, film still",
        "legenda": "E Severina achou que tudo tinha acabado.",
    },
    {
        "titulo": "A Virada",
        "plano": "wide",
        "movimento": "static",
        "prompt": "vertical 9:16 photorealistic cinematic still, renovated glowing corner market at golden hour, friendly white humanoid robot with blue eyes working as cashier, happy Brazilian customers in a queue smiling, neon sign new front, festive hopeful mood, 9:16 portrait",
        "legenda": "Ate que a rua inteira viu o novo caixa.",
    },
    {
        "titulo": "O Gancho",
        "plano": "medium",
        "movimento": "static",
        "prompt": "vertical 9:16 photorealistic cinematic still, shocked elegant Brazilian woman in red dress staring at a busy successful market across the street, mouth open in disbelief, golden sunrise, dramatic low angle foreground, suspense tone, 9:16 portrait",
        "legenda": "Claudete nao imaginava o que vinha por ai. CONTINUA...",
    },
]


def carregar_hf_token():
    for linha in (BASE / ".env").read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if linha.startswith("HF_TOKEN=") and len(linha) > 9:
            return linha.split("=", 1)[1].strip().strip('"').strip("'")
    return os.environ.get("HF_TOKEN", "").strip()


MODELOS_IMG = [
    "black-forest-labs/FLUX.1-schnell",
    "stabilityai/stable-diffusion-xl-base-1.0",
]


def gerar_imagem(prompt, output_path):
    token = carregar_hf_token()
    if not token:
        print("  ERRO: HF_TOKEN ausente")
        return False
    headers = {"Authorization": f"Bearer {token}"}
    for modelo in MODELOS_IMG:
        url = f"https://api-inference.huggingface.co/models/{modelo}"
        print(f"  Gerando imagem via HF ({modelo})...")
        print(f"  Prompt: {prompt[:100]}...")
        params = {"parameters": {"width": 1024, "height": 576}} if "flux" in modelo else {"inputs": prompt}
        payload = {"inputs": prompt}
        if "flux" in modelo:
            payload = {"inputs": prompt, "parameters": {"width": 1024, "height": 576}}
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=240)
        except Exception as e:
            print(f"  ERRO conexao ({modelo}): {e}")
            continue
        if r.status_code == 401:
            print("  ERRO 401: token invalido")
            return False
        if r.status_code == 503 or r.status_code == 429:
            print(f"  Modelo carregando/limitado ({r.status_code}); aguardando 20s...")
            time.sleep(20)
            try:
                r = requests.post(url, headers=headers, json=payload, timeout=240)
            except Exception as e:
                print(f"  ERRO retry: {e}")
                continue
        if r.status_code != 200:
            print(f"  ERRO API: {r.status_code} - {r.text[:120]}")
            continue
        dados = r.content
        if dados[:4] == b"\x89PNG" or b"image" in r.headers.get("Content-Type", ""):
            output_path.write_bytes(dados)
            print(f"  Imagem salva: {output_path.name}")
            return True
        print("  Formato inesperado (provavel JSON de erro)")
    return False


def gerar_imagem_pol(prompt, output_path, cena_id):
    """Imagem fotorealista gratuita via Pollinations (ganhos: sem chave, imagem real)."""
    url = ("https://image.pollinations.ai/prompt/" + quote(prompt)
           + "?width=" + str(LARG) + "&height=" + str(ALT)
           + "&seed=" + str(100 + cena_id) + "&nologo=true&model=flux")
    print("  Gerando imagem via Pollinations (flux, fotorealista)...")
    try:
        r = requests.get(url, timeout=240)
    except Exception as e:
        print(f"  ERRO conexao Pollinations: {e}")
        return False
    if r.status_code != 200 or len(r.content) < 10000:
        print(f"  ERRO Pollinations: HTTP {r.status_code}, {len(r.content)} bytes")
        return False
    raw = r.content
    if raw[:3] == b"\xff\xd8\xff":  # JPEG -> converte p/ PNG
        from PIL import Image as PILImage
        img = PILImage.open(BytesIO(raw)).convert("RGB")
        img.save(output_path, "PNG")
    else:
        output_path.write_bytes(raw)
    print(f"  Imagem salva: {output_path.name}")
    return True


def gerar_imagem_local(output_path, cena_id, seed=7):
    """Cenas cinematograficas offline via PIL (fallback sem internet/DNS)."""
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
    import random
    rnd = random.Random(seed + cena_id)
    W, H = 1024, 576

    def grad(c1, c2, vertical=True):
        img = Image.new("RGB", (W, H))
        p = img.load()
        for y in range(H):
            t = y / (H - 1) if vertical else 0
            c = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
            for x in range(W):
                p[x, y] = c
        return img

    def estrelas(img, n=90):
        d = ImageDraw.Draw(img)
        for _ in range(n):
            x, y = rnd.randint(0, W - 1), rnd.randint(0, int(H * 0.45))
            r = rnd.choice([1, 1, 2])
            d.ellipse((x, y, x + r, y + r), fill=(255, 255, 255, 220))
        return img

    if cena_id == 1:  # O Despertar - cidade a noite, loja acesa, servidores
        img = estrelas(grad((8, 10, 34), (26, 26, 94)))
        d = ImageDraw.Draw(img)
        d.ellipse((W - 180, 70, W - 60, 190), fill=(230, 230, 200))
        for i in range(9):  # predios silhueta
            bw, bh = rnd.randint(70, 130), rnd.randint(120, 260)
            bx = i * (W // 9)
            d.rectangle((bx, H - bh, bx + bw, H), fill=(10, 12, 24))
        # loja de computadores
        d.rectangle((400, 330, 640, H), fill=(14, 16, 30))
        d.rectangle((415, 355, 625, 420), fill=(255, 170, 60))
        for j in range(4):
            d.rectangle((430 + j * 50, 370, 475 + j * 50, 410), fill=(20, 24, 46))
        # racks de servidor brilhando
        for k in range(6):
            ry = 180 + k * 22
            d.rectangle((130 + k * 28, ry, 150 + k * 28, ry + 12), fill=(6, 182, 212))
        # feixes de luz subindo
        for s in range(5):
            sx = rnd.randint(80, W - 80)
            r = rnd.randint(8, 22)
            d.ellipse((sx - r, H - 40, sx + r, H - 40), fill=(140, 220, 255))
        v = 60
        d.ellipse((sx - v, 60, sx + v, 60), fill=(140, 220, 255))
    elif cena_id == 2:  # A Mente - cerebro neural holografico
        img = grad((4, 5, 14), (9, 30, 52))
        lay = Image.new("RGB", (W, H))
        dl = ImageDraw.Draw(lay)
        # chao em perspectiva
        for y in range(360, H):
            t = (y - 360) / (H - 360)
            c = tuple(int(6 + (18 - 6) * t) for _ in range(3))
            dl.line((0, y, W, y), fill=c)
        cx, cy = W // 2, 300
        nos = [(int(cx + rnd.uniform(-1, 1) * 170), int(cy + rnd.uniform(-0.6, 0.6) * 170))
               for _ in range(26)]
        core = (cx, cy)
        # grafo neural
        for i, a in enumerate(nos):
            dist = ((a[0] - core[0]) ** 2 + (a[1] - core[1]) ** 2) ** 0.5
            if dist < 175:
                pass
            for b in nos[i + 1:]:
                if rnd.random() < 0.28:
                    dl.line((a[0], a[1], b[0], b[1]), fill=(6, 182, 212, 120), width=2)
                dl.line((a[0], a[1], core[0], core[1]), fill=(6, 182, 212, 70), width=1)
            dl.ellipse((a[0] - 4, a[1] - 4, a[0] + 4, a[1] + 4), fill=(6, 182, 212))
        # nucleo pulsante
        glow = Image.new("RGB", (W, H))
        dg = ImageDraw.Draw(glow)
        dg.ellipse((cx - 60, cy - 60, cx + 60, cy + 60), fill=(80, 220, 255))
        glow = glow.filter(ImageFilter.GaussianBlur(30))
        img = Image.blend(img, glow, 0.55)
        d = ImageDraw.Draw(img)
        d.ellipse((cx - 22, cy - 22, cx + 22, cy + 22), fill=(200, 245, 255))
        # mapinha de cidade
        for gx in range(0, W, 48):
            for gy in range(400, H, 34):
                d.rectangle((gx, gy, gx + 18, gy + 10), outline=(255, 180, 80))
    else:  # O Auxilio - amanhecer, cidade e robo amigo
        img = grad((30, 18, 9), (80, 48, 20))
        top = grad((80, 48, 20), (255, 179, 71))
        img = Image.blend(img.resize((W, H)), top, 0.55)
        d = ImageDraw.Draw(img)
        for yy in range(150, 320, 8):
            c = tuple(int(255 - (yy - 150) * 0.9) for _ in range(3))
            d.ellipse((W - 420, yy - 260, W - 420 + 480, yy - 260 + 380), fill=c)
        sol = Image.new("RGB", (W, H))
        ds = ImageDraw.Draw(sol)
        ds.ellipse((130, 250, 290, 410), fill=(255, 215, 130))
        sol = sol.filter(ImageFilter.GaussianBlur(26))
        img = Image.blend(img, sol, 0.85)
        d = ImageDraw.Draw(img)
        d.ellipse((150, 270, 270, 390), fill=(255, 224, 150))
        for i in range(8):
            bw, bh = rnd.randint(70, 130), rnd.randint(100, 240)
            d.rectangle((i * (W // 8), H - bh, i * (W // 8) + bw, H), fill=(20, 16, 12))
        # robo assistente (silhueta)
        rx, ry = W // 2 - 60, H - 300
        d.rounded_rectangle((rx, ry + 80, rx + 120, ry + 290), 34, fill=(28, 24, 20))
        d.rounded_rectangle((rx + 26, ry, rx + 94, ry + 100), 18, fill=(28, 24, 20))
        d.ellipse((rx + 40, ry + 26, rx + 56, ry + 42), fill=(255, 210, 130))
        d.ellipse((rx + 64, ry + 26, rx + 80, ry + 42), fill=(255, 210, 130))
        d.rounded_rectangle((rx + 26, ry + 58, rx + 94, ry + 74), 6, fill=(255, 190, 90))
        # bracinho acenando
        d.polygon([(rx + 120, ry + 130), (rx + 150, ry + 150), (rx + 140, ry + 170), (rx + 116, ry + 155)],
                  fill=(28, 24, 20))
        # passaros
        for bd in range(4):
            bx, by = 420 + bd * 60, 200 + bd * 22
            d.arc((bx, by, bx + 22, by + 14), 200, 340, fill=(40, 30, 24), width=2)
            d.arc((bx + 12, by, bx + 34, by + 14), 200, 340, fill=(40, 30, 24), width=2)

    img = img.resize((W, H))
    img.save(output_path, "PNG")
    print(f"  [local] cena {cena_id} desenhada: {output_path.name}")
    return True


def criar_video_kenburns(caminho_img, cena_id, legenda):
    pasta_temp = BASE / "_temp_cenas_ia"
    pasta_temp.mkdir(exist_ok=True)
    img_temp = pasta_temp / f"cena{cena_id}.png"
    shutil.copy2(caminho_img, img_temp)
    saida = VIDEOS_DIR / f"ia_cena{cena_id}_raw.mp4"
    print("  Criando video Ken Burns...")
    subprocess.run(
        ["python", str(BASE / "gera_video.py"),
         "--pasta", str(pasta_temp),
         "--saida", str(saida),
         "--texto", legenda,
         "--duracao", "6",
         "--largura", str(LARG),
         "--altura", str(ALT),
         "--animacao", "fade"],
        cwd=str(BASE), capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return str(saida) if saida.exists() else None


def aplicar_voz(video_path, legenda, cena_id):
    print("  Adicionando voz AntonioNeural...")
    txt_file = BASE / "texto_promocao.txt"
    txt_file.write_text(legenda, encoding="utf-8")
    result = subprocess.run(
        ["python", str(BASE / "tronix_super_editor.py"), video_path],
        cwd=str(BASE), capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    saida = result.stdout + result.stderr
    m = re.search(r"SUCESSO TOTAL\|(.+?)$", saida, re.MULTILINE)
    if m:
        final_path = m.group(1).strip()
        if os.path.exists(final_path):
            novo_nome = str(VIDEOS_DIR / f"ia_cena{cena_id}.mp4")
            if os.path.exists(novo_nome):
                os.remove(novo_nome)
            os.rename(final_path, novo_nome)
            return novo_nome
    videos = sorted(VIDEOS_DIR.glob("ia_cena*.mp4"), key=os.path.getmtime)
    if videos:
        return str(videos[-1])
    return None


def main():
    print("=" * 60)
    print("TRONIX - MINI NOVELA GERADOR (HF)")
    print(f"Tema: {TEMA}")
    print("=" * 60)

    videos_finais = []
    if director:
        print(director.roteiro_direcao(CENAS))
        print()

    for i, cena in enumerate(CENAS):
        cena_id = i + 1
        print(f"\n--- CENA {cena_id}: {cena['titulo']} ---")
        if director and "plano" in cena:
            params = director.para_cena(cena["plano"], cena.get("movimento", "static"))
            print(f"  [DIRECTOR] {params['plano_nome']} + {params['movimento_nome']}")
            prompt_final = f"{params['prompt_prefixo']} {cena['prompt']}"
        else:
            prompt_final = cena["prompt"]

        img_path = UPLOADS / f"tronix_cena{cena_id}.png"
        if not gerar_imagem_pol(prompt_final, img_path, cena_id):
            print("  [fallback] HF/huggingface...")
            if not gerar_imagem(prompt_final, img_path):
                print("  [fallback] gerador local PIL...")
                if not gerar_imagem_local(img_path, cena_id):
                    print("  Pulando cena...")
                    continue

        video_raw = criar_video_kenburns(img_path, cena_id, cena["legenda"])
        if not video_raw:
            print(f"  ERRO: falha ao criar video cena {cena_id}")
            continue
        print(f"  Video criado: {os.path.basename(video_raw)}")

        video_final = aplicar_voz(video_raw, cena["legenda"], cena_id)
        if video_final and os.path.exists(video_final):
            print(f"  CENA {cena_id} PRONTA: {os.path.basename(video_final)}")
            videos_finais.append(video_final)
        time.sleep(2)

    pasta_temp = BASE / "_temp_cenas_ia"
    if pasta_temp.exists():
        shutil.rmtree(pasta_temp)

    if len(videos_finais) < 2:
        print(f"\nApenas {len(videos_finais)} cena(s).")
        return

    print(f"\n{'='*60}\nJuntando {len(videos_finais)} cenas...")
    lista_txt = BASE / "_concat_ia.txt"
    with open(lista_txt, "w", encoding="utf-8") as f:
        for v in videos_finais:
            f.write(f"file '{os.path.abspath(v)}'\n")

    final_mp4 = BASE / "mini_novela_Bizu.mp4"
    subprocess.run(
        ["ffmpeg", "-f", "concat", "-safe", "0", "-i", str(lista_txt),
         "-c:v", "copy", "-c:a", "aac", "-y", str(final_mp4)],
        check=True,
    )
    if lista_txt.exists():
        lista_txt.unlink()

    if final_mp4.exists():
        tamanho = final_mp4.stat().st_size // 1024
        print(f"\n{'='*60}")
        print(f"MINI NOVELA PRONTA: {final_mp4} ({tamanho / 1000:.1f} MB)")
        print(f"{'='*60}")
        if db:
            db.registrar(
                "mininovela",
                f"Mini Novela - {TEMA}",
                "mini_novela_IA.mp4", "raiz",
                legenda=" | ".join(c["legenda"] for c in CENAS),
                hashtags="#tronix #pcsolucoes #inteligenciaartificial #vicosa",
                voz_usada="AntonioNeural",
                tamanho_kb=tamanho, duracao_seg=len(videos_finais) * 6,
            )


if __name__ == "__main__":
    main()

