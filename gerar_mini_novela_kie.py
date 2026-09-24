import os
import sys
import time
import argparse
import subprocess
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = Path(__file__).parent
VIDEOS_DIR = BASE / "videos_saida"
VIDEOS_DIR.mkdir(exist_ok=True)

import tronix_kie as kie

try:
    import tronix_logger as db
    db.inicializar()
except ImportError:
    db = None

CENAS = [
    {
        "titulo": "A Chegada",
        "prompt": (
            "Cinematic extreme wide shot of a massive alien spaceship hovering over a small "
            "Brazilian city at night, glowing blue lights, people looking up in awe, "
            "hyper-realistic, epic atmosphere. The alien narrator speaks in Portuguese: "
            "'Eles chegaram... algo grande está vindo.' Native audio with the voice."
        ),
        "duracao": 8,
    },
    {
        "titulo": "O Plano",
        "prompt": (
            "Cinematic close-up of a tall alien creature with big black eyes inside a "
            "high-tech spacecraft, holographic map of Earth projected in front, dramatic "
            "lighting, sci-fi. The alien narrator speaks in Portuguese: 'O plano de invasão "
            "está em andamento.' Native audio with the voice."
        ),
        "duracao": 8,
    },
    {
        "titulo": "A Invasao",
        "prompt": (
            "Cinematic low angle shot of aliens walking down a main street in a Brazilian "
            "town, beams of light from spaceships, dramatic sunrise sky, people running, "
            "epic sci-fi movie scene, highly detailed. Narrator says in Portuguese: 'A "
            "invasão começou! A humanidade precisa de heróis!' Native audio with the voice."
        ),
        "duracao": 8,
    },
]


def gerar_cena(cena, i):
    print(f"\n--- CENA {i}: {cena['titulo']} ---")
    ts = int(time.time())
    saida = VIDEOS_DIR / f"kie_cena{i}_{ts}.mp4"
    tid = kie.criar_tarefa(
        "grok-imagine/text-to-video",
        {
            "prompt": cena["prompt"],
            "duration": cena["duracao"],
            "resolution": "720p",
            "aspect_ratio": "16:9",
        },
    )
    if not tid:
        return None
    data = kie.aguardar(tid, timeout=600)
    if not data:
        return None
    urls = kie.extrair_urls(data)
    if not urls:
        print(f"  SEM URL. Dados: {str(data)[:400]}")
        return None
    salvo = kie.baixar(urls[0], saida)
    return salvo


def main():
    print("=" * 60)
    print("TRONIX - MINI NOVELA (Grok Imagine via Kie.ai)")
    print("=" * 60)

    saldo = kie.creditos()
    if saldo is None:
        return 1

    videos = []
    for i, cena in enumerate(CENAS, 1):
        v = gerar_cena(cena, i)
        if v:
            videos.append(v)
            print(f"  CENA {i} PRONTA: {os.path.basename(v)}")
        else:
            print(f"  CENA {i} FALHOU")
        time.sleep(2)

    if len(videos) < 2:
        print(f"\nApenas {len(videos)} cena(s). Abortando concat.")
        return 1

    print(f"\nJuntando {len(videos)} cenas com FFmpeg...")
    lista = BASE / "_kie_concat_list.txt"
    with open(lista, "w", encoding="utf-8") as f:
        for v in videos:
            f.write(f"file '{os.path.abspath(v)}'\n")

    final = BASE / "mini_novela_kie.mp4"
    subprocess.run(
        ["ffmpeg", "-f", "concat", "-safe", "0", "-i", str(lista),
         "-c", "copy", "-y", str(final)],
        check=True, capture_output=True, text=True,
    )
    if lista.exists():
        lista.unlink()

    if final.exists():
        kb = final.stat().st_size // 1024
        print(f"\n{'=' * 60}")
        print(f"MINI NOVELA PRONTA: {final}")
        print(f"Tamanho: {kb / 1000:.1f} MB")
        print(f"{'=' * 60}")
        if db:
            db.registrar(
                "video", "Mini Novela Kie - Extraterrestre",
                final.name, "raiz",
                legenda=" | ".join(c["titulo"] for c in CENAS),
                hashtags="#tronix #kie #grokImagine #miniNovela",
                tamanho_kb=kb, duracao_seg=sum(c["duracao"] for c in CENAS),
            )
    return 0


if __name__ == "__main__":
    main()
