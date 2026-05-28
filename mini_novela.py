import os
import sys
import subprocess
import glob

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def juntar_videos(pasta, saida="mini_novela.mp4", max_videos=3):
    videos = sorted(glob.glob(os.path.join(pasta, "*.mp4")))
    videos_filtrados = videos[:max_videos]

    if not videos_filtrados:
        print("ERRO: Nenhum video encontrado.")
        return

    print(f"Juntando {len(videos_filtrados)} videos:")
    for v in videos_filtrados:
        print(f"  - {os.path.basename(v)}")

    lista_txt = "_concat_list.txt"
    with open(lista_txt, "w", encoding="utf-8") as f:
        for v in videos_filtrados:
            f.write(f"file '{os.path.abspath(v)}'\n")

    comando = [
        'ffmpeg', '-f', 'concat', '-safe', '0',
        '-i', lista_txt,
        '-c:v', 'copy', '-c:a', 'aac', '-y', saida
    ]

    try:
        subprocess.run(comando, check=True)
        print(f"SUCESSO|{os.path.abspath(saida)}")
    except Exception as e:
        print(f"ERRO: {e}")
    finally:
        if os.path.exists(lista_txt):
            os.remove(lista_txt)

if __name__ == "__main__":
    pasta = "videos_saida"
    saida = "mini_novela.mp4"
    if len(sys.argv) > 1:
        pasta = sys.argv[1]
    if len(sys.argv) > 2:
        saida = sys.argv[2]

    if not os.path.isabs(pasta):
        pasta = os.path.join(os.path.dirname(__file__), pasta)

    juntar_videos(pasta, saida)
