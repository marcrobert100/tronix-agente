#!/usr/bin/env python3
"""
Gerador de video com efeito Ken Burns e texto animado.
Uso: python gera_video.py [--pasta uploads] [--texto "Legenda"] [--hashtag "#tag"]

Efeitos de texto disponiveis:
  - fade: aparecimento suave
  - typewriter: efeito de maquina de escrever
  - slide: desliza da lateral
  - bounce: aparece com salto
"""

import os
import sys
import argparse
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from pathlib import Path
from moviepy import (
    ImageClip,
    TextClip,
    CompositeVideoClip,
    concatenate_videoclips,
    ColorClip,
)
from moviepy.video.fx import FadeIn, FadeOut
import os
os.environ["IMAGEIO_FFMPEG_EXE"] = "ffmpeg"


def criar_texto_animado(texto, duracao, dimensao, posicao="centro", animacao="fade",
                           cor="white", tamanho=60, fonte="C\\:/Windows/Fonts/arial.ttf"):
    """
    Cria um clip de texto com animacao.

    Args:
        texto: texto a exibir
        duracao: duracao em segundos
        dimensao: tupla (largura, altura)
        posicao: 'centro', 'topo', 'baixo', 'esquerda', 'direita'
        animacao: 'fade', 'typewriter', 'slide', 'bounce'
        cor: cor do texto (CSS ou RGB)
        tamanho: tamanho da fonte
        fonte: nome da fonte
    """
    if not texto:
        return None

    # Remove quebra de linhas e limita tamanho
    texto = texto.replace("\n", " ")[:100]

    # Calcula posicao
    posicoes = {
        "centro": ("center", "center"),
        "topo": ("center", 0.15),      # 15% do topo
        "baixo": ("center", 0.85),     # 85% (15% do fundo)
        "esquerda": (0.1, "center"),   # 10% da esquerda
        "direita": (0.9, "center"),    # 90% (10% da direita)
        "baixo-centro": ("center", 0.75),
    }

    pos = posicoes.get(posicao, ("center", "center"))

    # Tempo de animacao (proporcao do duracao)
    tempo_animacao = min(0.5, duracao * 0.3)  # 30% ou max 0.5s

    # Cria TextClip com sombra para legibilidade
    txt_clip = TextClip(
        text=texto,
        font_size=tamanho,
        font=fonte,
        color=cor,
        stroke_color="black",
        stroke_width=2,
        method="label",
    )

    # Centraliza se posicao e centro
    if pos == ("center", "center"):
        txt_clip = txt_clip.with_position(("center", "center"))
    else:
        txt_clip = txt_clip.with_position(pos, relative=True)

    # Aplica animacao de entrada
    if animacao in ("fade", "slide", "bounce", "typewriter"):
        txt_clip = txt_clip.with_duration(duracao).with_effects([
            FadeIn(tempo_animacao),
            FadeOut(tempo_animacao),
        ])

    txt_w, txt_h = txt_clip.size if hasattr(txt_clip, 'size') else (txt_clip.w, txt_clip.h)
    bg = ColorClip(size=(int(txt_w * 1.2), int(txt_h * 1.4)), color=(0, 0, 0))
    bg = bg.with_opacity(0.4).with_position("center")

    # Compoe fundo + texto
    composite = CompositeVideoClip([bg, txt_clip], size=dimensao)

    return composite.with_duration(duracao)


def aplicar_ken_burns(caminho_imagem, duracao, dimensao, zoom_inicial=1.0, zoom_final=1.2, pan_start=(0, 0)):
    """Cria um clip com efeito Ken Burns."""
    clip = ImageClip(caminho_imagem)

    img_w, img_h = clip.size
    escala = max(dimensao[0] / img_w, dimensao[1] / img_h)
    clip = clip.resized((int(img_w * escala), int(img_h * escala)))

    def transformacao(get_frame, t):
        frame = get_frame(t)
        h_frame, w_frame = frame.shape[:2]
        progresso = min(t / duracao, 1.0)
        zoom = zoom_inicial + (zoom_final - zoom_inicial) * progresso
        pan_x = int(pan_start[0] * dimensao[0] * progresso)
        pan_y = int(pan_start[1] * dimensao[1] * progresso)
        centro_x = w_frame // 2 - pan_x
        centro_y = h_frame // 2 - pan_y
        crop_w = max(1, int(dimensao[0] / zoom))
        crop_h = max(1, int(dimensao[1] / zoom))
        x1 = int(max(0, min(centro_x - crop_w // 2, w_frame - crop_w)))
        y1 = int(max(0, min(centro_y - crop_h // 2, h_frame - crop_h)))

        import cv2
        crop = frame[y1:y1+crop_h, x1:x1+crop_w]
        saida = cv2.resize(crop, dimensao, interpolation=cv2.INTER_LANCZOS4)
        return saida

    clip = clip.with_memoize(False)
    return clip.transform(transformacao).with_duration(duracao)


def gerar_video(pasta_imagens, arquivo_saida, duracao=5, fps=30, dimensao=(1920, 1080),
                texto=None, hashtag=None, animacao_texto="fade", posicao_texto="baixo-centro"):
    """Gera video com Ken Burns e texto animado."""

    pasta = Path(pasta_imagens)
    if not pasta.exists():
        print(f"ERRO: Pasta nao encontrada: {pasta_imagens}")
        sys.exit(1)

    extensoes = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}
    imagens = sorted([
        f for f in pasta.iterdir()
        if f.suffix.lower() in extensoes and f.is_file()
    ])

    if not imagens:
        print(f"ERRO: Nenhuma imagem encontrada em: {pasta_imagens}")
        sys.exit(1)

    print(f"Encontradas {len(imagens)} imagens")
    print(f"Gerando video de {duracao}s com {len(imagens)} slides")

    clips = []
    duracao_por_slide = duracao / len(imagens)

    for i, img_path in enumerate(imagens):
        print(f"  Processando: {img_path.name} ({i+1}/{len(imagens)})")

        # Ken Burns alternado
        if i % 2 == 0:
            zoom_inicial, zoom_final = 1.0, 1.25
            pan_start = (-0.05, -0.03)
        else:
            zoom_inicial, zoom_final = 1.25, 1.0
            pan_start = (0.05, 0.03)

        clip_img = aplicar_ken_burns(
            str(img_path),
            duracao_por_slide,
            dimensao,
            zoom_inicial=zoom_inicial,
            zoom_final=zoom_final,
            pan_start=pan_start,
        )

        # Adiciona texto se fornecido
        if texto or hashtag:
            textos = []
            if texto:
                texto_clip = criar_texto_animado(
                    texto,
                    duracao_por_slide,
                    dimensao,
                    posicao=posicao_texto,
                    animacao=animacao_texto,
                    tamanho=50,
                    cor="white",
                )
                if texto_clip:
                    textos.append(texto_clip)

            if hashtag:
                hashtag_clip = criar_texto_animado(
                    hashtag,
                    duracao_por_slide,
                    dimensao,
                    posicao="baixo",
                    animacao="fade",
                    tamanho=36,
                    cor="#FFD700",  # Dourado
                )
                if hashtag_clip:
                    textos.append(hashtag_clip)

            if textos:
                clip_img = CompositeVideoClip([clip_img] + textos, size=dimensao)

        clips.append(clip_img)

    print("Juntando os clips...")
    video = concatenate_videoclips(clips, method="compose")

    Path(arquivo_saida).parent.mkdir(parents=True, exist_ok=True)

    print(f"Salvando video em: {arquivo_saida}")
    video.write_videofile(
        arquivo_saida,
        fps=fps,
        codec="libx264",
        audio=False,
        threads=4,
        logger=None,
    )

    print(f"SUCESSO! Video gerado: {arquivo_saida}")
    return arquivo_saida


def main():
    parser = argparse.ArgumentParser(description="Gerador de video Ken Burns com texto")
    parser.add_argument("--pasta", "-p", default="uploads", help="Pasta com imagens")
    parser.add_argument("--saida", "-s", default="video_kenburns.mp4", help="Video de saida")
    parser.add_argument("--duracao", "-d", type=float, default=5, help="Duracao em segundos")
    parser.add_argument("--largura", "-l", type=int, default=1920, help="Largura")
    parser.add_argument("--altura", "-a", type=int, default=1080, help="Altura")
    parser.add_argument("--fps", type=int, default=30, help="FPS")
    parser.add_argument("--texto", "-t", help="Legenda a exibir no video")
    parser.add_argument("--hashtag", help="Hashtag a exibir")
    parser.add_argument("--animacao", default="fade",
                        choices=["fade", "slide", "typewriter", "bounce"],
                        help="Tipo de animacao do texto")
    parser.add_argument("--posicao", default="baixo-centro",
                        choices=["centro", "topo", "baixo", "baixo-centro"],
                        help="Posicao do texto")

    args = parser.parse_args()

    pasta = args.pasta
    if not os.path.isabs(pasta):
        pasta = Path(__file__).parent / pasta

    gerar_video(
        pasta_imagens=str(pasta),
        arquivo_saida=args.saida,
        duracao=args.duracao,
        fps=args.fps,
        dimensao=(args.largura, args.altura),
        texto=args.texto,
        hashtag=args.hashtag,
        animacao_texto=args.animacao,
        posicao_texto=args.posicao,
    )


if __name__ == "__main__":
    main()
