#!/usr/bin/env python3
"""
GORILA GESTOS - Efeitos de Animacao para o Video do Kong
Adiciona movimentos corporais: cabeca, ombros, corpo, respiracao, piscadas

Uso: python gorila_gestos.py
"""

import os
import sys
import json
import cv2
import numpy as np
from pathlib import Path

# Pasta de trabalho
SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "uploads" / "gorila"

# Configuracoes de video
LARGURA = 1280
ALTURA = 720
FPS = 30

# Configuracoes de gesticulacao
INTENSIDADE_CABECA = 8        # Pixel de oscilacao da cabeca
INTENSIDADE_OMBROS = 12       # Pixel de elevacao dos ombros
INTENSIDADE_CORPO = 18        # Pixel de balanco lateral
INTENSIDADE_RESPIRACAO = 6    # Pixel de expansao/contração
INTENSIDADE_PISCADA = 3       # Frames de duracao da piscada

# Ritmo da voz (frequencia base em Hz)
RITMO_VOZ = 3.0


def carregar_roteiro():
    """Carrega o roteiro com as falas e gestos."""
    arquivo = OUTPUT_DIR / "roteiro_kong.json"
    if not arquivo.exists():
        print(f"ERRO: Roteiro nao encontrado: {arquivo}")
        sys.exit(1)

    with open(arquivo, "r", encoding="utf-8") as f:
        return json.load(f)


def calcular_duracao_falas(roteiro):
    """Calcula duracao aproximada de cada fala baseada no texto."""
    duracoes = []
    for fala in roteiro["falas"]:
        # Estimativa: ~3 palavras por segundo para leitura natural
        palavras = len(fala["texto"].split())
        duracao = max(2.0, palavras / 3.0)  # Minimo 2 segundos
        duracoes.append(duracao)
    return duracoes


def criar_mascara_rosto(h, w, centro_y_ratio=0.38):
    """Cria mascara eliptica para area do rosto (para piscadas)."""
    centro_y = int(h * centro_y_ratio)
    centro_x = w // 2

    # Cria elipse para os olhos
    olhos_mascara = np.zeros((h, w), dtype=np.uint8)
    cv2.ellipse(
        olhos_mascara,
        (centro_x, centro_y),
        (w // 3, h // 8),
        0, 0, 360, 255, -1
    )
    return olhos_mascara


def aplicar_head_bob(frame, tempo, freq_voz=RITMO_VOZ):
    """
    Efeito de movimento de cabeca: oscilacao suave para cima/baixo.
    Sincronizado com o ritmo da voz.
    """
    # Oscilacao baseada em seno composto
    oscilacao_principal = np.sin(tempo * freq_voz * 2 * np.pi)
    oscilacao_secundaria = np.sin(tempo * freq_voz * 4 * np.pi) * 0.3

    deslocamento_y = int((oscilacao_principal + oscilacao_secundaria) * INTENSIDADE_CABECA)

    if deslocamento_y != 0:
        # Move a imagem verticalmente
        if deslocamento_y > 0:
            frame = frame[:-deslocamento_y, :]
            frame = np.vstack([frame, np.zeros((deslocamento_y, LARGURA, 3), dtype=np.uint8)])
        else:
            frame = frame[-deslocamento_y:, :]
            frame = np.vstack([np.zeros((-deslocamento_y, LARGURA, 3), dtype=np.uint8), frame])

    return frame


def aplicar_shoulder_raise(frame, tempo, intensidade_gesto=1.0):
    """
    Efeito de elevacao de ombros: ombros se movem para cima
    quando Kong enfatiza algo.
    """
    # Elevacao periodica dos ombros
    freq_shoulder = 2.5
    fase = tempo * freq_shoulder * 2 * np.pi

    # Elevacao segue uma onda triangular modificada
    elevacao = abs(np.sin(fase)) * intensidade_gesto
    pixel_raise = int(elevacao * INTENSIDADE_OMBROS)

    if pixel_raise > 0:
        # Corta parte inferior e adiciona no topo
        frame_cortado = frame[:-pixel_raise, :] if pixel_raise < ALTURA else frame
        padding = np.zeros((pixel_raise, LARGURA, 3), dtype=np.uint8)
        frame = np.vstack([padding, frame_cortado])

    return frame


def aplicar_body_sway(frame, tempo, freq_voz=RITMO_VOZ):
    """
    Efeito de balanco corporal: movimento lateral do corpo
    como se Kong estivesse conversando.
    """
    # Balanco lateral suave
    balanco = np.sin(tempo * freq_voz * 1.5 * np.pi) * INTENSIDADE_CORPO
    balanco += np.sin(tempo * 0.8 * np.pi) * INTENSIDADE_CORPO * 0.5

    desloc_x = int(balanco)

    if desloc_x != 0:
        if desloc_x > 0:
            frame = frame[:, :-desloc_x]
            frame = np.hstack([frame, np.zeros((ALTURA, desloc_x, 3), dtype=np.uint8)])
        else:
            frame = frame[:, -desloc_x:]
            frame = np.hstack([np.zeros((ALTURA, -desloc_x, 3), dtype=np.uint8), frame])

    return frame


def aplicar_breathing_effect(frame, tempo):
    """
    Efeito de respiracao: leve expansao/contração do frame
    simulando a respiracao natural.
    """
    # Respiracao: ciclo de 4 segundos aproximadamente
    freq_resp = 0.25  # 4 segundos por ciclo
    fase_resp = tempo * freq_resp * 2 * np.pi

    # Expansao suave
    escala = 1.0 + np.sin(fase_resp) * (INTENSIDADE_RESPIRACAO / ALTURA)

    h, w = frame.shape[:2]
    novo_h = int(h * escala)
    novo_w = int(w * escala)

    if abs(novo_h - h) > 1 or abs(novo_w - w) > 1:
        # Redimensiona
        frame_expandido = cv2.resize(frame, (novo_w, novo_h), interpolation=cv2.INTER_LANCZOS4)

        # Centraliza no canvas
        frame_resultado = np.zeros((h, w, 3), dtype=np.uint8)
        y_offset = (h - novo_h) // 2
        x_offset = (w - novo_w) // 2

        # Copia a imagem expandida para o centro
        y1 = max(0, y_offset)
        y2 = min(h, y_offset + novo_h)
        x1 = max(0, x_offset)
        x2 = min(w, x_offset + novo_w)

        frame_resultado[y1:y2, x1:x2] = frame_expandido[
            max(0, -y_offset):novo_h - max(0, y_offset + novo_h - h),
            max(0, -x_offset):novo_w - max(0, x_offset + novo_w - w)
        ]

        return frame_resultado

    return frame


def aplicar_eye_blink(frame, tempo, mascara_olhos, ultimo_blink=0):
    """
    Efeito de piscada: piscadas automaticas em intervalos naturais.
    """
    # Intervalo entre piscadas: 2.5 a 4.5 segundos
    tempo_prox_blink = 3.5
    tempo_desde_blink = tempo - ultimo_blink

    if tempo_desde_blink >= tempo_prox_blink:
        # Hora de piscar!
        # Duracao da piscada em frames
        duracao_blink = INTENSIDADE_PISCADA
        fase_blink = (tempo_desde_blink % 0.15) / 0.15  # 150ms de duracao

        # Curva da piscada (fecha e abre)
        if fase_blink < 0.5:
            # Fechando
            fechamento = fase_blink * 2
        else:
            # Abrindo
            fechamento = (1 - fase_blink) * 2

        fechamento = min(1.0, max(0.0, fechamento))

        # Aplica escurecimento na area dos olhos
        if fechamento > 0.1:
            olho_region = frame.copy()
            olho_region[mascara_olhos > 0] = frame[mascara_olhos > 0] * (1 - fechamento * 0.7)
            frame = cv2.addWeighted(frame, 1, olho_region, fechamento, 0)

        return frame, tempo if fase_blink < 0.5 else ultimo_blink

    return frame, ultimo_blink


def aplicar_gesto_especial(frame, texto_fala, gesto, tempo, inicio_fala, duracao_fala):
    """
    Aplica efeitos especiais baseados no gesto descrito.
    """
    gesto_lower = gesto.lower()

    # Progresso na fala (0 a 1)
    progresso = (tempo - inicio_fala) / duracao_fala
    progresso = max(0, min(1, progresso))

    # Bater no peito
    if "bater" in gesto_lower or "peito" in gesto_lower:
        # Impacto periodico no meio da fala
        if 0.3 < progresso < 0.7:
            impacto = np.sin((progresso - 0.3) * np.pi / 0.4) * 10
            frame = aplicar_shoulder_raise(frame, tempo, intensidade_gesto=1.5 + impacto)

    # Acenar com cabeca
    if "acena" in gesto_lower:
        # Movimento afirmativo
        freq_aceno = 4
        aceno = np.sin(progresso * np.pi * freq_aceno) * 5
        h = frame.shape[0]
        if abs(aceno) > 0.5:
            shift = int(aceno)
            frame = frame[:, shift:] if shift > 0 else frame[:, :shift]
            frame = np.hstack([
                frame,
                np.zeros((h, abs(shift), 3), dtype=np.uint8) if shift > 0
                else np.zeros((h, abs(shift), 3), dtype=np.uint8)
            ])

    # Erguer punho
    if "punho" in gesto_lower or "grita" in gesto_lower:
        # Elevacao mais intensa dos ombros
        if progresso > 0.4:
            intensidade = (progresso - 0.4) * 1.5
            frame = aplicar_shoulder_raise(frame, tempo, intensidade_gesto=1.5 + intensidade)

    # Sorriso relaxado
    if "sorriso" in gesto_lower or "relaxad" in gesto_lower:
        # Respiracao mais profunda
        frame = aplicar_breathing_effect(frame, tempo)
        frame = aplicar_breathing_effect(frame, tempo + 0.5)

    # Apontar
    if "aponta" in gesto_lower:
        # Balanco lateral mais pronunciado
        balanco_extra = np.sin(progresso * np.pi * 3) * 10
        frame = aplicar_body_sway(frame, tempo)
        h = frame.shape[0]
        shift = int(balanco_extra)
        if abs(shift) > 0:
            if shift > 0:
                frame[:, shift:] = frame[:, :-shift]
                frame[:, :shift] = 0
            else:
                frame[:, :shift] = frame[:, -shift:]
                frame[:, shift:] = 0

    return frame


def criar_frame_com_gestos(img_original, tempo, duracao_falas, roteiro, mascara_olhos, ultimo_blink):
    """
    Cria um frame com todos os efeitos de gesto aplicados.
    """
    # Copia a imagem original
    frame = img_original.copy()

    # Calcula qual fala esta ativa
    fala_atual = None
    inicio_acumulado = 0
    for i, duracao in enumerate(duracao_falas):
        if inicio_acumulado <= tempo < inicio_acumulado + duracao:
            fala_atual = roteiro["falas"][i]
            progresso_fala = (tempo - inicio_acumulado) / duracao
            break
        inicio_acumulado += duracao

    # Aplica efeitos base (sempre ativos)
    frame = aplicar_head_bob(frame, tempo)
    frame = aplicar_shoulder_raise(frame, tempo, intensidade_gesto=0.8)
    frame = aplicar_body_sway(frame, tempo)
    frame = aplicar_breathing_effect(frame, tempo)

    # Aplica gesto especial da fala atual
    if fala_atual:
        inicio_fala = inicio_acumulado
        duracao_fala = duracao if 'duracao' in dir() else 3.0
        frame = aplicar_gesto_especial(
            frame,
            fala_atual["texto"],
            fala_atual["gesto"],
            tempo,
            inicio_fala,
            duracao_falas[roteiro["falas"].index(fala_atual)]
        )

    # Aplica piscadas
    frame, novo_blink = aplicar_eye_blink(frame, tempo, mascara_olhos, ultimo_blink)

    return frame, novo_blink


def processar_video_com_gestos(caminho_imagem, caminho_audio):
    """
    Processa o video inteiro com todos os efeitos de gesto.
    """
    print("=" * 60)
    print("[ANIMADOR] Processando video com gestos animados...")
    print("=" * 60)

    # Carrega roteiro
    roteiro = carregar_roteiro()
    duracao_falas = calcular_duracao_falas(roteiro)
    duracao_total = sum(duracao_falas) + 1.0  # +1 para seguranca

    print(f"Duracao total estimada: {duracao_total:.1f}s")
    print(f"Total de falas: {len(roteiro['falas'])}")

    # Carrega imagem base
    img = cv2.imread(str(caminho_imagem))
    if img is None:
        print(f"ERRO: Nao foi possivel carregar imagem: {caminho_imagem}")
        return None

    h_img, w_img = img.shape[:2]
    print(f"Imagem original: {w_img}x{h_img}")

    # Redimensiona para tamanho padrao
    img_base = cv2.resize(img, (LARGURA, ALTURA), interpolation=cv2.INTER_LANCZOS4)

    # Cria mascara para area dos olhos
    mascara_olhos = criar_mascara_rosto(ALTURA, LARGURA)

    # Pasta para frames
    frames_dir = OUTPUT_DIR / "frames_gestos"
    frames_dir.mkdir(exist_ok=True)

    # Limpa pasta de frames anteriores
    for arq in frames_dir.glob("*.png"):
        arq.unlink()

    # Processa cada frame
    total_frames = int(duracao_total * FPS)
    ultimo_blink = 0.0

    print(f"\nGerando {total_frames} frames com gestos...")
    print("Efeitos ativos: cabeca, ombros, corpo, respiracao, piscadas")

    for i in range(total_frames):
        tempo = i / FPS

        # Verifica se esta dentro de uma fala
        inicio_acumulado = 0
        duracao_fala_atual = 3.0
        for idx, duracao in enumerate(duracao_falas):
            if inicio_acumulado <= tempo < inicio_acumulado + duracao:
                duracao_fala_atual = duracao
                break
            inicio_acumulado += duracao

        # Aplica Ken Burns (do script original)
        progresso = tempo / duracao_total
        zoom = 1.0 + 0.04 * np.sin(progresso * np.pi * 2)

        # Pan suave
        pan_x = int(15 * np.sin(progresso * np.pi * 2.5))
        pan_y = int(10 * np.cos(progresso * np.pi * 2))

        # Calcula crop para zoom
        crop_w = int(w_img / zoom)
        crop_h = int(h_img / zoom)

        center_x = w_img // 2 + pan_x
        center_y = h_img // 2 + pan_y

        x1 = max(0, min(center_x - crop_w // 2, w_img - crop_w))
        y1 = max(0, min(center_y - crop_h // 2, h_img - crop_h))

        # Aplica crop e resize
        img_crop = img[y1:y1+crop_h, x1:x1+crop_w]
        img_frame = cv2.resize(img_crop, (LARGURA, ALTURA), interpolation=cv2.INTER_LANCZOS4)

        # Aplica efeitos de gesto
        img_frame, ultimo_blink = criar_frame_com_gestos(
            img_frame, tempo, duracao_falas, roteiro, mascara_olhos, ultimo_blink
        )

        # Adiciona vinheta sutil
        vignette = criar_vinheta(LARGURA, ALTURA, intensidade=0.2)
        img_frame = cv2.addWeighted(img_frame, 1, vignette, 0.2, 0)

        # Barra dourada no topo
        img_frame[0:6, :] = [255, 215, 0]

        # Salva frame
        cv2.imwrite(str(frames_dir / f"frame_{i:05d}.png"), img_frame)

        # Progresso
        if i % 50 == 0:
            progresso_pct = 100 * i // total_frames
            print(f"  Frame {i}/{total_frames} ({progresso_pct}%)")

    print(f"\nFrames com gestos salvos em: {frames_dir}")

    # Cria video com FFmpeg
    arquivo_video = OUTPUT_DIR / "kong_video_gestos.mp4"

    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", str(frames_dir / "frame_%05d.png"),
        "-i", str(caminho_audio).replace("\\", "/"),
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        str(arquivo_video).replace("\\", "/")
    ]

    print("\nCodificando video com gestos (FFmpeg)...")
    import subprocess
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

    if result.returncode != 0:
        print(f"ERRO FFmpeg: {result.stderr[-500:]}")
        return None

    # Limpa frames
    try:
        import shutil
        shutil.rmtree(frames_dir)
        print("Frames temporarios removidos.")
    except:
        pass

    tamanho = arquivo_video.stat().st_size / (1024 * 1024)
    print(f"\n" + "=" * 60)
    print(f"SUCESSO! VIDEO COM GESTOS CRIADO!")
    print(f"Arquivo: {arquivo_video}")
    print(f"Tamanho: {tamanho:.2f} MB")
    print(f"Duracao: {duracao_total:.1f}s")
    print("=" * 60)

    return str(arquivo_video)


def criar_vinheta(w, h, intensidade=0.2):
    """Cria efeito de vinheta para as bordas."""
    kernel_x = cv2.getGaussianKernel(w, w // 2)
    kernel_y = cv2.getGaussianKernel(h, h // 2)
    kernel = kernel_y * kernel_x.T
    mask = kernel / kernel.max()
    mask = 1 - (1 - mask) * intensidade

    vinheta = np.zeros((h, w, 3), dtype=np.float32)
    for c in range(3):
        vinheta[:, :, c] = mask * 255

    return vinheta.astype(np.uint8)


def main():
    print("=" * 60)
    print("  GORILA GESTOS - Animacao de Gestos do Kong")
    print("  Animador de Linguagem Corporal")
    print("=" * 60)

    # Verifica arquivos necessarios
    imagem = OUTPUT_DIR / "kong_imagem.png"
    audio = OUTPUT_DIR / "kong_audio_unificado.mp3"

    if not imagem.exists():
        print(f"ERRO: Imagem nao encontrada: {imagem}")
        print("Execute primeiro: python gorila_video.py")
        sys.exit(1)

    if not audio.exists():
        print(f"ERRO: Audio nao encontrado: {audio}")
        print("Execute primeiro: python gorila_video.py")
        sys.exit(1)

    print(f"Imagem: {imagem}")
    print(f"Audio: {audio}")

    # Carrega e exibe roteiro
    roteiro = carregar_roteiro()
    print(f"\nRoteiro carregado - {len(roteiro['falas'])} falas:")
    for i, fala in enumerate(roteiro["falas"]):
        print(f"  {i+1}. {fala['texto'][:50]}...")
        print(f"     Gesto: {fala['gesto']}")

    # Processa video com gestos
    caminho_video = processar_video_com_gestos(str(imagem), str(audio))

    if caminho_video:
        print("\n" + "=" * 60)
        print("ANIMACAO COMPLETA! Video do Kong com gestos!")
        print(f"Arquivo final: {caminho_video}")
        print("=" * 60)
    else:
        print("\nFALHA ao processar video com gestos.")
        sys.exit(1)


if __name__ == "__main__":
    main()
