#!/usr/bin/env python3
"""
KONG AVANCADO - Talking Head com Sync Labial Realista + Gestos
Usa deformacao de imagem para simular movimento humano

Uso: python gorila_avancado.py
"""

import cv2
import numpy as np
import os
import sys
import json
from pathlib import Path
import subprocess
import requests
import asyncio
import edge_tts

# Credenciais
TOKEN = "cfut_nI8gZqUUHil8sG6xjjE1W26wbVHgDyU8PRQTdUV2e61edb64"
ACCOUNT_ID = "038280d984d9c936772700b7dbbc479e"

OUTPUT_DIR = Path("C:/xampp/htdocs/agente/uploads/gorila")

def load_roteiro():
    with open(OUTPUT_DIR / "roteiro_kong.json", encoding="utf-8") as f:
        return json.load(f)

def load_image():
    img = cv2.imread(str(OUTPUT_DIR / "kong_imagem.png"))
    if img is None:
        print("ERRO: Imagem nao encontrada!")
        sys.exit(1)
    return img

def detectar_rosto(img):
    """Detecta a regiao do rosto para animacao usando proporcoes da imagem."""
    h, w = img.shape[:2]

    # Detecta regiao mais escura/central como possivel rosto
    # Como e um gorila humanizado em cafe, assume que rosto esta no terco superior-central
    # Proporcoes baseadas em figura half-body portrait

    # Rosto principal (regiao central-superior)
    face_w = int(w * 0.45)
    face_h = int(h * 0.40)
    face_x = int(w * 0.28)
    face_y = int(h * 0.18)

    # Boca (regiao inferior do rosto)
    mouth_w = int(face_w * 0.55)
    mouth_h = int(face_h * 0.22)
    mouth_x = int(face_x + face_w * 0.22)
    mouth_y = int(face_y + face_h * 0.68)

    # Olhos (regiao superior-media do rosto)
    eye_w = int(face_w * 0.5)
    eye_h = int(face_h * 0.18)
    eye_x = int(face_x + face_w * 0.25)
    eye_y = int(face_y + face_h * 0.28)

    return {
        "face": (face_x, face_y, face_w, face_h),
        "mouth": (mouth_x, mouth_y, mouth_w, mouth_h),
        "eyes": (eye_x, eye_y, eye_w, eye_h),
    }


def aplicar_sync_labial(frame, regiao, intensidade):
    """Aplica efeito de sync labial na regiao da boca."""
    x, y, w, h = regiao

    # Garante que a regiao esta dentro do frame
    if y < 0 or x < 0 or y + h > frame.shape[0] or x + w > frame.shape[1]:
        return frame

    roi = frame[y:y+h, x:x+w].copy()

    # Efeito de brilho na boca durante speaking
    brilho = int(30 * intensidade)
    roi = np.clip(roi.astype(np.int16) + brilho, 0, 255).astype(np.uint8)

    # Leve vibracao horizontal para simular movimento labial
    if intensidade > 0.3:
        shift = int(2 * np.sin(intensidade * 10))
        if abs(shift) > 0:
            roi = np.roll(roi, shift, axis=1)

    frame[y:y+h, x:x+w] = roi
    return frame


def aplicar_head_bob(frame, regiao_face, t, fase):
    """Aplica movimento de cabeca (head bob)."""
    x, y, w, h = regiao_face

    # Amplitudes diferentes por fase
    if fase == "inicio":
        # Cabeca levantando
        offset_y = int(-5 * np.sin(t * 2))
        offset_x = int(3 * np.cos(t * 1.5))
    elif fase == "falando":
        # Bob rhythmico durante fala
        offset_y = int(3 * np.sin(t * 4))
        offset_x = int(2 * np.cos(t * 3))
    elif fase == "enfase":
        # Cabeca baixa para enfase
        offset_y = int(4 * np.sin(t * 5))
        offset_x = int(5 * np.cos(t * 4))
    else:  # fim
        # Cabeca voltando
        offset_y = int(2 * np.sin(t * 1.5))
        offset_x = int(1 * np.cos(t))

    # Aplica transformacao perspectiva sutil na regiao do rosto
    h_frame, w_frame = frame.shape[:2]
    margin = 50

    # Pontos de controle para warp
    src_pts = np.float32([
        [x - margin, y - margin],
        [x + w + margin, y - margin],
        [x - margin, y + h + margin],
        [x + w + margin, y + h + margin]
    ])

    dst_pts = np.float32([
        [x - margin + offset_x, y - margin + offset_y],
        [x + w + margin - offset_x, y - margin + offset_y],
        [x - margin - offset_x, y + h + margin - offset_y],
        [x + w + margin + offset_x, y + h + margin - offset_y]
    ])

    # Calcula matriz de transformacao
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)

    # Aplica apenas na regiao com mascara
    mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    cv2.rectangle(mask, (x-margin, y-margin), (x+w+margin, y+h+margin), 255, -1)
    mask = cv2.GaussianBlur(mask, (21, 21), 10)

    # Warp a imagem completa
    frame_warped = cv2.warpPerspective(frame, M, (w_frame, h_frame))

    # Mistura com original usando a mascara
    mask_3ch = cv2.merge([mask, mask, mask]) / 255.0
    frame = (frame * (1 - mask_3ch) + frame_warped * mask_3ch).astype(np.uint8)

    return frame


def aplicar_blink(frame, regiao_olhos, t, should_blink):
    """Simula piscada de olhos."""
    x, y, w, h = regiao_olhos

    if y < 0 or x < 0 or y + h > frame.shape[0] or x + w > frame.shape[1]:
        return frame

    roi = frame[y:y+h, x:x+w]

    if should_blink:
        # Escurece para simular olho fechado
        roi = (roi * 0.3).astype(np.uint8)
        frame[y:y+h, x:x+w] = roi

    return frame


def aplicar_gesto_ombros(frame, regiao_face, t, fase):
    """Aplica movimento de ombros."""
    x, y, w, h = regiao_face

    # Ombros estao abaixo do rosto
    ombro_y = y + h
    ombro_h = frame.shape[0] - ombro_y

    if ombro_y >= frame.shape[0] or ombro_h <= 0:
        return frame

    # Movimento lateral dos ombros
    if fase == "enfase":
        shift = int(10 * np.sin(t * 3))
    elif fase == "falando":
        shift = int(5 * np.sin(t * 2))
    else:
        shift = int(3 * np.sin(t * 1.5))

    # Aplica shear horizontal na regiao dos ombros
    M = np.float32([[1, 0.01 * np.sign(shift), shift], [0, 1, 0]])

    frame_copy = frame.copy()
    ombro_roi = frame_copy[ombro_y:frame.shape[0], :]
    ombro_warped = cv2.warpAffine(ombro_roi, M, (frame.shape[1], ombro_h))

    frame[ombro_y:frame.shape[0], :] = ombro_warped

    return frame


def criar_animacao_completa(caminho_img, duracao, fps=30):
    """Cria animacao completa com todos os efeitos."""

    img = load_image()
    rosto = detectar_rosto(img)

    h_img, w_img = img.shape[:2]

    # Dimensoes de saida
    out_w, out_h = 1280, 720

    # Escala para preencher
    scale = max(out_w / w_img, out_h / h_img)
    new_w, new_h = int(w_img * scale), int(h_img * scale)

    # Redimensiona imagem
    img_scaled = cv2.resize(img, (new_w, new_h))

    total_frames = int(duracao * fps)

    frames_dir = OUTPUT_DIR / "frames_animado"
    frames_dir.mkdir(parents=True, exist_ok=True)

    # Timing das falas (estimativa igual)
    num_falas = 4
    dur_fala = duracao / num_falas

    print(f"Criando {total_frames} frames com animacao completa...")

    last_blink = -1
    blink_interval = 3.0  # Piscada a cada 3 segundos

    for i in range(total_frames):
        t = i / fps
        progresso = t / duracao

        # Copia imagem base
        frame = img_scaled.copy()

        # Centraliza crop
        x_offset = (new_w - out_w) // 2
        y_offset = (new_h - out_h) // 2
        frame = frame[y_offset:y_offset+out_h, x_offset:x_offset+out_w]

        # Determina fase da animacao
        fala_atual = int(t / dur_fala)
        t_na_fala = t % dur_fala

        if fala_atual == 0:
            fase = "inicio"
        elif fala_atual == num_falas - 1:
            fase = "fim"
        elif t_na_fala < 0.3:
            fase = "inicio"
        elif t_na_fala > dur_fala - 0.5:
            fase = "enfase"
        else:
            fase = "falando"

        # Intensidade do sync labial (sempre ativo quando falando)
        intensidade_labial = 0.0
        if fase == "falando":
            # Padrão de speaking - pulsa com ritmo
            intensidade_labial = 0.3 + 0.4 * np.abs(np.sin(t * 8))
        elif fase == "enfase":
            intensidade_labial = 0.5 + 0.3 * np.sin(t * 6)

        # Ajusta regioes para a nova escala
        scale_factor = out_w / w_img
        rosto_scaled = {
            "face": tuple(int(v * scale_factor) for v in rosto["face"]),
            "mouth": tuple(int(v * scale_factor) for v in rosto["mouth"]),
            "eyes": tuple(int(v * scale_factor) for v in rosto["eyes"]),
        }

        # Aplica efeitos
        frame = aplicar_head_bob(frame, rosto_scaled["face"], t, fase)
        frame = aplicar_sync_labial(frame, rosto_scaled["mouth"], intensidade_labial)
        frame = aplicar_gesto_ombros(frame, rosto_scaled["face"], t, fase)

        # Piscadas
        if t - last_blink > blink_interval or (t < 0.5 and last_blink < 0):
            should_blink = (i % 5) < 2  # 2 frames de piscar
            frame = aplicar_blink(frame, rosto_scaled["eyes"], t, should_blink)
            if should_blink and last_blink < 0:
                last_blink = t
            elif should_blink and t - last_blink > 0.15:
                last_blink = t
                blink_interval = 2.5 + np.random.random() * 2

        # Vinheta cinematica
        vignette = criar_vinheta(out_w, out_h, intensidade=0.2)
        frame = cv2.addWeighted(frame, 1, vignette, 0.2, 0)

        # Barra dourada no topo
        frame[0:10, :] = [255, 215, 0]

        # Salva frame
        frame_path = str(frames_dir / f"frame_{i:05d}.png")
        cv2.imwrite(frame_path, frame)

        if i % 100 == 0:
            print(f"  Frame {i}/{total_frames} ({100*i//total_frames}%)")

    return frames_dir


def criar_vinheta(w, h, intensidade=0.2):
    """Cria efeito de vinheta."""
    kernel_x = cv2.getGaussianKernel(w, w // 2)
    kernel_y = cv2.getGaussianKernel(h, h // 2)
    kernel = kernel_y * kernel_x.T
    mask = kernel / kernel.max()
    mask = 1 - (1 - mask) * intensidade

    vinheta = np.zeros((h, w, 3), dtype=np.float32)
    for c in range(3):
        vinheta[:, :, c] = mask * 255

    return vinheta.astype(np.uint8)


def gerar_video(frames_dir, audio_path, output_path):
    """Gera video final com FFmpeg."""
    cmd = [
        "ffmpeg", "-y",
        "-framerate", "30",
        "-i", str(frames_dir / "frame_%05d.png").replace("\\", "/"),
        "-i", str(audio_path).replace("\\", "/"),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        str(output_path).replace("\\", "/")
    ]

    print("\nCodificando video com FFmpeg...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

    if result.returncode != 0:
        print(f"ERRO: {result.stderr[-500:]}")
        return False

    # Limpa frames
    import shutil
    try:
        shutil.rmtree(frames_dir)
    except:
        pass

    return True


def main():
    print("=" * 60)
    print("  KONG AVANCADO - Talking Head com Animacao Realista")
    print("=" * 60)

    # Carrega assets
    roteiro = load_roteiro()
    print(f"Roteiro carregado: {len(roteiro['falas'])} falas")

    # Audio ja existe
    audio_path = OUTPUT_DIR / "kong_audio_unificado.mp3"
    if not audio_path.exists():
        print("ERRO: Audio nao encontrado!")
        sys.exit(1)

    # Pega duracao do audio
    import subprocess
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)],
        capture_output=True, text=True
    )
    duracao = float(result.stdout.strip()) if result.stdout.strip() else 27.0
    print(f"Duracao: {duracao:.1f}s")

    # Cria animacao
    frames_dir = criar_animacao_completa(str(OUTPUT_DIR / "kong_imagem.png"), duracao)

    # Gera video
    output_path = OUTPUT_DIR / "kong_avancado.mp4"
    if gerar_video(frames_dir, audio_path, output_path):
        tamanho = output_path.stat().st_size / (1024 * 1024)
        print(f"\n" + "=" * 60)
        print(f"SUCESSO! VIDEO AVANCADO DO KONG PRONTO!")
        print(f"Arquivo: {output_path}")
        print(f"Tamanho: {tamanho:.2f} MB")
        print("=" * 60)
    else:
        print("FALHA ao gerar video!")


if __name__ == "__main__":
    main()
