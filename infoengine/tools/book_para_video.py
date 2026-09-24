#!/usr/bin/env python3
"""Converte book.html em video com narracao — Playwright + Edge-TTS + FFmpeg."""

import argparse
import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path

# ------------------------------------------------------------
async def capturar_paginas(url_html: str, saida_dir: str, largura=1920, altura=1080):
    """Abre HTML com Playwright, captura cada pagina como PNG em Full HD."""
    from playwright.async_api import async_playwright

    saida = Path(saida_dir)
    saida.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(
            viewport={"width": largura, "height": altura},
            device_scale_factor=1,
        )
        page = await ctx.new_page()

        print(f"[captura] Abrindo {url_html}...")
        await page.goto(url_html, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(1500)

        # Esconde toolbar, nav, pageno para captura limpa
        await page.evaluate("""() => {
            document.querySelector('.toolbar')?.remove();
            document.querySelector('.nav')?.remove();
            document.querySelector('.auto-read-overlay')?.remove();
            document.querySelectorAll('.pageno').forEach(e => e.remove());
            document.querySelectorAll('.btn-play').forEach(e => e.remove());
            // Remove page number from SVG
            document.querySelectorAll('.page-number').forEach(e => e.remove());
            // Fundo do body combinando com o fundo da pagina ativa
        }""")

        total = await page.evaluate("LIVRO.paginas.length + 2")
        print(f"[captura] Total paginas: {total}")

        arquivos = []
        for i in range(total):
            await page.evaluate(f"show({i})")
            await page.wait_for_timeout(500)

            path_png = saida / f"pagina_{i:03d}.png"
            # Captura viewport inteiro com fundo escuro
            await page.screenshot(path=str(path_png), full_page=False)
            arquivos.append(str(path_png))
            print(f"[captura] Pagina {i+1}/{total} -> {path_png.name} (OK)")

        await browser.close()

    print(f"[captura] OK — {len(arquivos)} paginas em Full HD")
    return arquivos


# ------------------------------------------------------------
async def gerar_audio(book_json: str, saida_dir: str, voz="pt-BR-AntonioNeural"):
    """Gera audio MP3 para cada pagina com Edge-TTS."""
    from edge_tts import Communicate

    with open(book_json, encoding="utf-8") as f:
        livro = json.load(f)

    saida = Path(saida_dir)
    saida.mkdir(parents=True, exist_ok=True)

    # Pagina 0 = capa (sem audio)
    # Paginas 1..N = story pages
    # Pagina N+1 = final

    audios = []
    textos = [
        f"{livro['titulo']}. {livro.get('subtitulo', '')}",  # capa
    ]
    for p in livro["paginas"]:
        txt = " ".join(filter(None, [p.get("texto", ""), p.get("dialogo", "")]))
        textos.append(txt)
    textos.append(livro.get("texto_final", "Fim!"))

    for i, txt in enumerate(textos):
        if not txt.strip():
            audios.append("")
            continue
        path_mp3 = saida / f"audio_{i:03d}.mp3"
        if path_mp3.exists():
            print(f"[audio] Pagina {i+1} ja existe, pulando")
            audios.append(str(path_mp3))
            continue

        communicate = Communicate(txt, voz)
        await communicate.save(str(path_mp3))
        audios.append(str(path_mp3))
        print(f"[audio] Pagina {i+1}/{len(textos)} -> {path_mp3.name}")

    return audios


# ------------------------------------------------------------
def criar_video(arquivos_png: list, arquivos_mp3: list, saida_mp4: str):
    """Cria video Full HD com Ken Burns + audio usando moviepy + FFmpeg."""
    from moviepy import ImageClip, AudioFileClip, concatenate_videoclips

    clips = []
    dur_total = 0

    for i, (png, mp3) in enumerate(zip(arquivos_png, arquivos_mp3)):
        if not os.path.isfile(png):
            continue

        if mp3 and os.path.isfile(mp3):
            try:
                audio = AudioFileClip(mp3)
                duracao = audio.duration + 1.0
            except Exception:
                duracao = 5.0
                audio = None
        else:
            duracao = 5.0
            audio = None

        clip = ImageClip(png, duration=duracao)
        if audio:
            clip = clip.with_audio(audio)

        clips.append(clip)
        dur_total += duracao

    if not clips:
        print("[video] Nenhum clip!")
        return

    print(f"[video] Concatenando {len(clips)} clips ({dur_total:.1f}s)...")
    video = concatenate_videoclips(clips, method="compose")

    print(f"[video] Renderizando {saida_mp4}...")
    video.write_videofile(
        saida_mp4,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="medium",
        ffmpeg_params=["-pix_fmt", "yuv420p", "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2"],
        logger=None,
    )
    video.close()
    print(f"[video] OK — {saida_mp4} ({dur_total:.1f}s, {os.path.getsize(saida_mp4)//1024} KB)")


# ------------------------------------------------------------
async def main_async():
    parser = argparse.ArgumentParser(description="Converte livro HTML em video")
    parser.add_argument("--html", default="http://localhost/agente/infoengine/output/aurora_futurista_quadrinho.html",
                        help="URL do HTML do livro")
    parser.add_argument("--book-json", default=r"C:\xampp\htdocs\agente\infoengine\tools\examples\book_aurora_futurista.json",
                        help="Caminho do book.json")
    parser.add_argument("--output", default=r"C:\xampp\htdocs\agente\infoengine\output\aurora_futurista_video.mp4",
                        help="Arquivo MP4 de saida")
    parser.add_argument("--temp", default=None,
                        help="Pasta temporaria para PNGs e audios")
    parser.add_argument("--voz", default="pt-BR-AntonioNeural",
                        help="Voz Edge-TTS (padrao: pt-BR-AntonioNeural)")
    parser.add_argument("--skip-capture", action="store_true",
                        help="Pular captura (reusar PNGs existentes)")
    parser.add_argument("--skip-audio", action="store_true",
                        help="Pular geracao de audio (reusar MP3s existentes)")
    args = parser.parse_args()

    # Pasta temporaria
    if args.temp:
        temp_dir = args.temp
    else:
        temp_dir = tempfile.mkdtemp(prefix="book_video_")
    print(f"[main] Temp dir: {temp_dir}")

    # 1. Capturar paginas
    if args.skip_capture:
        pngs = sorted(Path(temp_dir).glob("pagina_*.png"))
        arquivos_png = [str(p) for p in pngs]
        print(f"[main] Pulando captura, {len(arquivos_png)} PNGs existentes")
    else:
        arquivos_png = await capturar_paginas(args.html, temp_dir)

    # 2. Gerar audio
    if args.skip_audio:
        mp3s = sorted(Path(temp_dir).glob("audio_*.mp3"))
        arquivos_mp3 = [str(m) for m in mp3s]
        print(f"[main] Pulando audio, {len(arquivos_mp3)} MP3s existentes")
    else:
        arquivos_mp3 = await gerar_audio(args.book_json, temp_dir, args.voz)

    # Alinhar listas (mesmo tamanho)
    n = min(len(arquivos_png), len(arquivos_mp3))
    arquivos_png = arquivos_png[:n]
    arquivos_mp3 = arquivos_mp3[:n]

    # 3. Criar video
    criar_video(arquivos_png, arquivos_mp3, args.output)

    print(f"\n[main] Video pronto: {args.output}")
    print(f"[main] Tamanho: {os.path.getsize(args.output)//1024} KB")


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
