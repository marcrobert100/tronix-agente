import os
import sys
import subprocess
import time
import re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

try:
    import tronix_logger as db
    db.inicializar()
except ImportError:
    db = None

BASE = Path(__file__).parent
UPLOADS = BASE / "uploads"
VIDEOS_DIR = BASE / "videos_saida"
UPLOADS.mkdir(exist_ok=True)
VIDEOS_DIR.mkdir(exist_ok=True)

CENAS = [
    {
        "titulo": "A Chegada",
        "prompt": "Cinematic shot of a massive alien spaceship hovering over a small Brazilian city at night, glowing blue lights, people looking up in awe, hyper-realistic, epic atmosphere",
        "legenda": "Eles chegaram... Algo grande esta vindo.",
    },
    {
        "titulo": "O Plano",
        "prompt": "Close-up of a tall alien creature with big black eyes inside a high-tech spacecraft, holographic map of Earth projected in front, dramatic lighting, sci-fi cinematic",
        "legenda": "O plano de invasao esta em andamento.",
    },
    {
        "titulo": "A Invasao",
        "prompt": "Aliens walking down a main street in a Brazilian town, beams of light from spaceships, dramatic sunrise sky, people running, epic sci-fi movie scene, highly detailed",
        "legenda": "A invasao comecou! A humanidade precisa de herois.",
    },
]

def gerar_imagem(prompt, output_path):
    import requests
    url = f"https://api.cloudflare.com/client/v4/accounts/038280d984d9c936772700b7dbbc479e/ai/run/@cf/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": "Bearer cfut_nI8gZqUUHil8sG6xjjE1W26wbVHgDyU8PRQTdUV2e61edb64", "Content-Type": "application/json"}
    print(f"  Gerando imagem via Cloudflare...")
    r = requests.post(url, headers=headers, json={"prompt": prompt}, timeout=180)
    if r.status_code != 200:
        print(f"  ERRO API: {r.status_code}")
        return False
    ct = r.headers.get("Content-Type", "")
    dados = r.content
    if "image" not in ct and r.content[:4] != b"\x89PNG":
        try:
            import base64
            dados = base64.b64decode(r.json()["result"])
        except:
            print(f"  ERRO: formato inesperado")
            return False
    with open(output_path, "wb") as f:
        f.write(dados)
    print(f"  Imagem salva: {output_path.name}")
    return True

def criar_video_kenburns(caminho_img, cena_id, legenda):
    pasta_temp = BASE / "_temp_cenas"
    pasta_temp.mkdir(exist_ok=True)
    
    import shutil
    img_temp = pasta_temp / f"cena{cena_id}.png"
    shutil.copy2(caminho_img, img_temp)
    
    saida = VIDEOS_DIR / f"cena{cena_id}_raw.mp4"
    
    print(f"  Criando video Ken Burns...")
    subprocess.run([
        "python", str(BASE / "gera_video.py"),
        "--pasta", str(pasta_temp),
        "--saida", str(saida),
        "--texto", legenda,
        "--duracao", "6",
        "--animacao", "fade"
    ], cwd=str(BASE), capture_output=True, text=True, encoding='utf-8', errors='replace')
    
    if saida.exists():
        return str(saida)
    return None

def aplicar_voz(video_path, legenda, cena_id):
    print(f"  Adicionando voz AntonioNeural...")
    txt_file = BASE / "texto_promocao.txt"
    with open(txt_file, "w", encoding="utf-8") as f:
        f.write(legenda)
    
    result = subprocess.run(
        ["python", str(BASE / "tronix_super_editor.py"), video_path],
        cwd=str(BASE), capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    
    saida = result.stdout + result.stderr
    m = re.search(r'SUCESSO TOTAL\|(.+?)$', saida, re.MULTILINE)
    if m:
        final_path = m.group(1).strip()
        if os.path.exists(final_path):
            novo_nome = str(VIDEOS_DIR / f"cena{cena_id}.mp4")
            if os.path.exists(novo_nome):
                os.remove(novo_nome)
            os.rename(final_path, novo_nome)
            return novo_nome
    
    videos = sorted(VIDEOS_DIR.glob("cena*.mp4"), key=os.path.getmtime)
    if videos:
        return str(videos[-1])
    return None

def main():
    print("="*60)
    print("TRONIX - MINI NOVELA GERADOR")
    print("Tema: Extraterrestre invade a Terra")
    print("="*60)
    
    videos_finais = []
    
    for i, cena in enumerate(CENAS):
        cena_id = i + 1
        print(f"\n--- CENA {cena_id}: {cena['titulo']} ---")
        
        img_path = UPLOADS / f"alien_cena{cena_id}.png"
        if not gerar_imagem(cena["prompt"], img_path):
            print(f"  Pulando...")
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
    
    pasta_temp = BASE / "_temp_cenas"
    if pasta_temp.exists():
        import shutil
        shutil.rmtree(pasta_temp)
    
    if len(videos_finais) < 2:
        print(f"\nApenas {len(videos_finais)} cena(s).")
        return
    
    print(f"\n{'='*60}")
    print(f"Juntando {len(videos_finais)} cenas...")
    for v in videos_finais:
        print(f"  - {os.path.basename(v)}")
    
    lista_txt = BASE / "_concat_list.txt"
    with open(lista_txt, "w", encoding="utf-8") as f:
        for v in videos_finais:
            f.write(f"file '{os.path.abspath(v)}'\n")
    
    final_mp4 = BASE / "mini_novela.mp4"
    subprocess.run([
        "ffmpeg", "-f", "concat", "-safe", "0",
        "-i", str(lista_txt),
        "-c:v", "copy", "-c:a", "aac", "-y", str(final_mp4)
    ], check=True)
    
    if lista_txt.exists():
        lista_txt.unlink()
    
    if final_mp4.exists():
        tamanho = final_mp4.stat().st_size // 1024
        print(f"\n{'='*60}")
        print(f"MINI NOVELA PRONTA: {final_mp4}")
        print(f"Tamanho: {tamanho / 1000:.1f} MB")
        print(f"Abra em: http://localhost/agente/")
        print(f"{'='*60}")

        if db:
            titulo = f"Mini Novela - {CENAS[0]['titulo']}"
            hashtags = "#tronix #pcsolucoes #miniNovela"
            db.registrar("mininovela", titulo, "mini_novela.mp4", "raiz",
                         legenda=" | ".join(c["legenda"] for c in CENAS),
                         hashtags=hashtags, voz_usada="AntonioNeural",
                         tamanho_kb=tamanho, duracao_seg=len(videos_finais) * 6)

if __name__ == "__main__":
    main()
