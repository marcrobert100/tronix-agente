import os
import sys
import json
import glob
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

SESSION_FILE = "session_instagram.json"
BASE = Path(__file__).parent

def login():
    from instagrapi import Client

    cl = Client()
    if os.path.exists(SESSION_FILE):
        try:
            cl.load_settings(SESSION_FILE)
            username = os.getenv("IG_USERNAME", "")
            password = os.getenv("IG_PASSWORD", "")
            if username and password:
                cl.login(username, password)
                return cl
        except:
            pass

    username = os.getenv("IG_USERNAME") or input("Instagram usuario: ")
    password = os.getenv("IG_PASSWORD") or input("Instagram senha: ")

    try:
        cl.login(username, password)
        cl.dump_settings(SESSION_FILE)
        print("  Login OK. Sessao salva.")
        return cl
    except Exception as e:
        print(f"  ERRO LOGIN: {e}")
        return None

def postar_reel(video_path, legenda="", hashtags=""):
    if not os.path.exists(video_path):
        print(f"  ERRO: Video nao encontrado: {video_path}")
        return False

    tamanho = os.path.getsize(video_path)
    if tamanho > 100 * 1024 * 1024:
        print(f"  ERRO: Video muito grande ({tamanho/1e6:.0f}MB). Max 100MB.")
        return False

    texto = legenda
    if hashtags:
        texto += f"\n\n{hashtags}"

    print(f"  Enviando: {os.path.basename(video_path)} ({tamanho/1e6:.1f}MB)...")
    cl = login()
    if not cl:
        return False

    try:
        result = cl.clip_upload(video_path, caption=texto)
        print(f"  SUCESSO! Reel publicado.")
        return True
    except Exception as e:
        print(f"  ERRO: {e}")
        return False

def postar_tudo_da_pasta(pasta="videos_saida"):
    padroes = [os.path.join(pasta, "cena*.mp4"), os.path.join(pasta, "*.mp4")]
    videos = []
    for p in padroes:
        videos.extend(sorted(glob.glob(str(BASE / p))))
    videos = [v for v in videos if "_super" not in os.path.basename(v) and "_voz" not in os.path.basename(v)]

    if not videos:
        print(f"  Nenhum video encontrado em {pasta}")
        return

    print(f"  Encontrados {len(videos)} videos para postar.")
    for v in videos:
        nome = os.path.basename(v)
        print(f"\n  --- {nome} ---")
        postar_reel(v, legenda=f"Video gerado por Tronix IA", hashtags="#tronix #pcsolucoes #ia")
        import time
        time.sleep(10)

def postar_pendentes():
    try:
        from tronix_logger import listar_pendentes, marcar_postado
    except ImportError:
        print("  ERRO: tronix_logger nao encontrado")
        return

    pendentes = listar_pendentes()
    if not pendentes:
        print("  Nenhum conteudo pendente.")
        return

    print(f"  Postando {len(pendentes)} itens pendentes...")
    for item in pendentes:
        caminho = os.path.join(BASE, item.get("pasta", "videos_saida"), item["arquivo"])
        if os.path.exists(caminho):
            ok = postar_reel(caminho, item.get("legenda", ""), item.get("hashtags", ""))
            if ok:
                marcar_postado(item["id"], "instagram")
            import time
            time.sleep(10)
        else:
            print(f"  Arquivo nao encontrado: {caminho}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Tronix - Postagem Instagram v2")
    parser.add_argument("--video", help="Video especifico")
    parser.add_argument("--legenda", "-l", default="Gerado por Tronix IA")
    parser.add_argument("--hashtags", default="#tronix #pcsolucoes #ia")
    parser.add_argument("--pendentes", action="store_true", help="Postar pendentes do banco")
    parser.add_argument("--pasta", help="Postar TODOS os videos de uma pasta")
    args = parser.parse_args()

    if args.pendentes:
        postar_pendentes()
    elif args.pasta:
        postar_tudo_da_pasta(args.pasta)
    elif args.video:
        postar_reel(args.video, args.legenda, args.hashtags)
    else:
        print("Opcoes:")
        print("  --video arquivo.mp4            Posta um video")
        print("  --pasta videos_saida           Posta todos da pasta")
        print("  --pendentes                    Posta pendentes do banco")
