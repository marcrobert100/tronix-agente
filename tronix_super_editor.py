import os
import sys
import asyncio
import subprocess
import argparse

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import edge_tts
from pathlib import Path

try:
    import tronix_logger as db
    db.inicializar()
except ImportError:
    db = None

VOZ = "pt-BR-AntonioNeural"

async def gerar_voz_edge(texto, arquivo_saida):
    tts = edge_tts.Communicate(texto, VOZ)
    await tts.save(arquivo_saida)

def super_producao_tronix(video_input, texto, adicionar_texto=False):
    video_output = video_input.replace(".mp4", "_voz.mp4")
    audio_temp = "temp_audio.mp3"

    try:
        print(f"Gerando voz AntonioNeural para: '{texto}'...")
        asyncio.run(gerar_voz_edge(texto, audio_temp))

        cmd = ['ffmpeg', '-i', video_input, '-i', audio_temp]

        if adicionar_texto:
            print(f"Adicionando legenda na tela...")
            cmd.extend([
                '-vf',
                f"drawtext=text='{texto}':fontfile=_font.ttf:fontcolor=yellow:fontsize=40:"
                f"x=(w-text_w)/2:y=h-80:box=1:boxcolor=black:boxborderw=5"
            ])

        cmd.extend([
            '-map', '0:v', '-map', '1:a',
            '-c:v', 'libx264', '-c:a', 'aac', '-shortest', '-y', video_output
        ])

        subprocess.run(cmd, check=True)
        print(f"SUCESSO TOTAL|{video_output}")

        if db:
            tamanho = os.path.getsize(video_output) // 1024
            nome = os.path.basename(video_output)
            db.registrar("video", nome, nome, "videos_saida",
                         legenda=texto, tamanho_kb=tamanho, duracao_seg=4,
                         hashtags="#tronix", voz_usada=VOZ)

        if os.path.exists(audio_temp):
            os.remove(audio_temp)

    except Exception as e:
        print(f"ERRO NO PIPELINE DE VOZ: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tronix Super Editor - Adiciona voz IA a videos")
    parser.add_argument("video", nargs="?", default="videos_saida/tronix_1778515500.mp4", help="Caminho do video")
    parser.add_argument("--texto", help="Texto da legenda na tela (opcional, sem texto = so voz)")
    args = parser.parse_args()

    texto = ""
    if args.texto:
        texto = args.texto
        adicionar_texto = True
    elif os.path.exists("texto_promocao.txt"):
        with open("texto_promocao.txt", "r", encoding="utf-8") as f:
            texto = f.read().strip()
        adicionar_texto = False
    else:
        adicionar_texto = False

    if not texto:
        print("ERRO: Informe o texto com --texto ou crie texto_promocao.txt")
        sys.exit(1)

    super_producao_tronix(args.video, texto, adicionar_texto)
