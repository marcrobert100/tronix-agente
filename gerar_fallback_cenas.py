import os
import sys
import time
import subprocess
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = Path(__file__).parent
VIDEOS_DIR = BASE / "videos_saida"
UPLOADS = BASE / "uploads"

import gerar_mini_novela as novela
import tronix_kie as kie


def gerar_fallback(cenas_ids):
    videos = []
    for cena_id in cenas_ids:
        cena = novela.CENAS[cena_id - 1]
        print(f"\n--- CENA {cena_id} (Kie img + Ken Burns + voz): {cena['titulo']} ---")

        img_path = UPLOADS / f"alien_cena{cena_id}.png"
        tid = kie.criar_tarefa(
            "grok-imagine/text-to-image",
            {"prompt": cena["prompt"], "aspect_ratio": "16:9"},
        )
        if not tid:
            continue
        data = kie.aguardar(tid, timeout=300)
        if not data:
            continue
        urls = kie.extrair_urls(data)
        if not urls:
            print(f"  SEM URL. Dados: {str(data)[:400]}")
            continue
        if not kie.baixar(urls[0], img_path):
            continue

        video_raw = novela.criar_video_kenburns(img_path, cena_id, cena["legenda"])
        if not video_raw:
            print(f"  Falha video cena {cena_id}")
            continue

        video_final = novela.aplicar_voz(video_raw, cena["legenda"], cena_id)
        if video_final and os.path.exists(video_final):
            print(f"  CENA {cena_id} PRONTA: {os.path.basename(video_final)}")
            videos.append(video_final)
        time.sleep(2)
    return videos


def concat(lista_videos, saida):
    lista_txt = BASE / "_final_concat_list.txt"
    with open(lista_txt, "w", encoding="utf-8") as f:
        for v in lista_videos:
            f.write(f"file '{os.path.abspath(v)}'\n")
    subprocess.run(
        ["ffmpeg", "-f", "concat", "-safe", "0", "-i", str(lista_txt),
         "-c", "copy", "-y", str(saida)],
        check=True, capture_output=True, text=True,
    )
    if lista_txt.exists():
        lista_txt.unlink()


def main():
    kie_cena1 = sorted(VIDEOS_DIR.glob("kie_cena1_*.mp4"), key=os.path.getmtime)
    if not kie_cena1:
        print("ERRO: cena 1 Kie nao encontrada.")
        return 1
    cena1 = str(kie_cena1[-1])
    print(f"Cena 1 (Kie): {os.path.basename(cena1)}")

    cenas_ken = gerar_fallback([2, 3])
    if not cenas_ken:
        print("ERRO: nenhuma cena Ken Burns gerada.")
        return 1

    todos = [cena1] + cenas_ken
    final = BASE / "mini_novela_kie.mp4"
    concat(todos, final)

    if final.exists():
        kb = final.stat().st_size // 1024
        print(f"\n{'='*60}")
        print(f"MINI NOVELA COMPLETA: {final}")
        print(f"Tamanho: {kb/1000:.1f} MB | Cenas: {len(todos)}")
        print(f"{'='*60}")
        try:
            import tronix_logger as db
            db.inicializar()
            db.registrar("video", "Mini Novela Completa - Extraterrestre",
                         final.name, "raiz",
                         legenda="Kie + Ken Burns",
                         hashtags="#tronix #miniNovela #kie #pcsolucoes",
                         tamanho_kb=kb, duracao_seg=24)
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    main()
