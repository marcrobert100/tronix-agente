#!/usr/bin/env python3
"""
KONG TALKING HEAD - Animacao Avancada com Simetria Facial e Expressoes
Usa transformacoes geometricas avançadas para simular talking head realista

Uso: python gorila_talking.py
"""

import cv2
import numpy as np
import os
import json
from pathlib import Path
import subprocess

OUTPUT_DIR = Path("C:/xampp/htdocs/agente/uploads/gorila")


def load_assets():
    """Carrega roteiro, imagem e audio."""
    with open(OUTPUT_DIR / "roteiro_kong.json", encoding="utf-8") as f:
        roteiro = json.load(f)

    img = cv2.imread(str(OUTPUT_DIR / "kong_imagem.png"))
    if img is None:
        raise FileNotFoundError("Imagem nao encontrada!")

    audio_path = OUTPUT_DIR / "kong_audio_unificado.mp3"
    if not audio_path.exists():
        raise FileNotFoundError("Audio nao encontrado!")

    # Pega duracao
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)],
        capture_output=True, text=True
    )
    duracao = float(result.stdout.strip()) if result.stdout.strip() else 27.0

    return roteiro, img, duracao


def detectar_pontos_faciais(img):
    """
    Detecta pontos faciais aproximados usando anlise de imagem.
    Para um gorila humanizado half-body portrait.
    """
    h, w = img.shape[:2]

    # Para half-body portrait: rosto ocupa terco central-superior
    # Proporcoes tpicas de rosto humano/gorila

    # Pontos faciais normalizados (0-1)
    pontos = {
        # Rosto
        "face_left": (0.28, 0.20),
        "face_right": (0.72, 0.20),
        "face_top": (0.50, 0.12),
        "face_bottom": (0.50, 0.58),

        # Olhos
        "eye_left_inner": (0.40, 0.28),
        "eye_left_outer": (0.32, 0.29),
        "eye_right_inner": (0.60, 0.28),
        "eye_right_outer": (0.68, 0.29),

        # Sobancelhas
        "brow_left_inner": (0.40, 0.24),
        "brow_left_outer": (0.32, 0.23),
        "brow_right_inner": (0.60, 0.24),
        "brow_right_outer": (0.68, 0.23),

        # Nariz
        "nose_top": (0.50, 0.36),
        "nose_bottom": (0.50, 0.42),

        # Boca
        "mouth_left": (0.40, 0.48),
        "mouth_right": (0.60, 0.48),
        "mouth_top": (0.50, 0.46),
        "mouth_bottom": (0.50, 0.52),
        "mouth_center": (0.50, 0.49),

        # Mandibula
        "jaw_left": (0.30, 0.55),
        "jaw_right": (0.70, 0.55),
        "chin": (0.50, 0.58),
    }

    # Converte para pixels
    pontos_px = {}
    for k, (x_ratio, y_ratio) in pontos.items():
        pontos_px[k] = (
            int(w * x_ratio),
            int(h * y_ratio)
        )

    return pontos_px, w, h


def get_face_landmarks(pontos):
    """Retorna pontos do contorno do rosto."""
    return np.float32([
        pontos["face_left"],
        pontos["face_right"],
        pontos["face_top"],
        pontos["face_bottom"],
        pontos["jaw_left"],
        pontos["jaw_right"],
        pontos["chin"],
    ])


def warp_face_region(frame, pontos, t, fase, intensidade_fala):
    """
    Aplica warp na regiao do rosto para simular expressoes faciais.
    """
    h, w = frame.shape[:2]
    face_left = pontos["face_left"]
    face_right = pontos["face_right"]
    face_top = pontos["face_top"]
    face_bottom = pontos["face_bottom"]
    mouth_center = pontos["mouth_center"]
    mouth_top = pontos["mouth_top"]
    mouth_bottom = pontos["mouth_bottom"]
    chin = pontos["chin"]

    # Calcula centro e tamanho do rosto
    face_cx = (face_left[0] + face_right[0]) // 2
    face_cy = (face_top[1] + face_bottom[1]) // 2
    face_w = face_right[0] - face_left[0]
    face_h = face_bottom[1] - face_top[1]

    # Margem ao redor do rosto
    margin = int(face_w * 0.15)

    x1 = max(0, face_left[0] - margin)
    y1 = max(0, face_top[1] - margin)
    x2 = min(w, face_right[0] + margin)
    y2 = min(h, face_bottom[1] + margin)

    # Extrai regiao do rosto
    face_roi = frame[y1:y2, x1:x2].copy()
    roi_h, roi_w = face_roi.shape[:2]

    if roi_h < 10 or roi_w < 10:
        return frame

    # Aplica transformacoes baseado na fase
    if fase == "inicio":
        # Cabeca levemente inclinada
        angle = 2 * np.sin(t * 2)
        scale = 1.0 + 0.01 * np.sin(t * 3)
    elif fase == "falando":
        # Movimento de speaking
        angle = 3 * np.sin(t * 4)
        scale = 1.0 + 0.02 * np.abs(np.sin(t * 6))
    elif fase == "enfase":
        # Cabeca baixa para enfase
        angle = -5 * np.sin(t * 3)
        scale = 1.0 + 0.01 * np.cos(t * 4)
    else:  # fim
        angle = 1 * np.sin(t * 2)
        scale = 1.0 + 0.005 * np.sin(t * 2)

    # Rotacao
    M_rot = cv2.getRotationMatrix2D((roi_w // 2, roi_h // 2), angle, scale)

    # Translacao sutil
    tx = int(3 * np.sin(t * 3))
    ty = int(2 * np.cos(t * 2.5))
    M_rot[0, 2] += tx
    M_rot[1, 2] += ty

    face_warped = cv2.warpAffine(face_roi, M_rot, (roi_w, roi_h),
                                   flags=cv2.INTER_LANCZOS4,
                                   borderMode=cv2.BORDER_REFLECT)

    # Coloca de volta
    frame[y1:y2, x1:x2] = face_warped

    return frame


def animate_mouth(frame, pontos, t, fase, intensidade):
    """
    Anima a regiao da boca para simular speaking.
    Usa brilho e vibracao na regiao labial.
    """
    if intensidade < 0.1:
        return frame

    h, w = frame.shape[:2]

    # Regiao da boca
    mouth_left = pontos["mouth_left"]
    mouth_right = pontos["mouth_right"]
    mouth_top = pontos["mouth_top"]
    mouth_bottom = pontos["mouth_bottom"]

    # Expande regiao da boca
    bx1 = max(0, mouth_left[0] - int((mouth_right[0] - mouth_left[0]) * 0.3))
    by1 = max(0, int(mouth_top[1] - (mouth_bottom[1] - mouth_top[1]) * 0.8))
    bx2 = min(w, mouth_right[0] + int((mouth_right[0] - mouth_left[0]) * 0.3))
    by2 = min(h, int(mouth_bottom[1] + (mouth_bottom[1] - mouth_top[1]) * 0.8))

    if by2 <= by1 or bx2 <= bx1:
        return frame

    mouth_roi = frame[by1:by2, bx1:bx2].copy()

    # Efeito de speaking: brilho pulsante
    pulso = np.abs(np.sin(t * 12))  # Frequencia alta para ritmo de fala
    brilho = int(40 * intensidade * pulso)

    # Converte para float, aplica brilho, volta
    mouth_float = mouth_roi.astype(np.float32)
    mouth_float = np.clip(mouth_float + brilho, 0, 255)
    mouth_roi = mouth_float.astype(np.uint8)

    # Vibracao horizontal sutil
    if intensidade > 0.3:
        vib = int(2 * np.sin(t * 15))
        if abs(vib) > 0:
            mouth_roi = np.roll(mouth_roi, vib, axis=1)

    frame[by1:by2, bx1:bx2] = mouth_roi

    # Adiciona sombra sutil ao redor da boca para profundidade
    shadow_intensity = int(20 * intensidade * pulso)
    shadow_roi = frame[by1:by2, bx1:bx2].copy()
    shadow_roi = cv2.GaussianBlur(shadow_roi, (5, 5), 1)
    shadow_roi = np.clip(shadow_roi - shadow_intensity, 0, 255).astype(np.uint8)
    frame[by1:by2, bx1:bx2] = cv2.addWeighted(
        frame[by1:by2, bx1:bx2], 0.7,
        shadow_roi, 0.3, 0
    )

    return frame


def animate_eyes(frame, pontos, t, last_blink, blink_interval):
    """
    Anima piscadas de olhos.
    """
    h, w = frame.shape[:2]

    eye_left = pontos["eye_left_inner"]
    eye_right = pontos["eye_right_inner"]

    # Tamanho aproximado dos olhos
    eye_size = int((pontos["eye_right_inner"][0] - pontos["eye_left_inner"][0]) * 0.5)

    # Verifica se deve piscar
    should_blink = False
    blink_duration = 0.12  # segundos

    if t - last_blink >= blink_interval:
        # Inicia piscada
        should_blink = True
        last_blink = t
        blink_interval = 2.5 + np.random.random() * 2

    # Ajusta intervalo baseado no tempo desde ultima piscada
    time_since_blink = t - last_blink
    if time_since_blink < blink_duration:
        should_blink = True
        # Intensidade da piscada (max no meio)
        blink_intensity = 1.0 - abs(time_since_blink / blink_duration - 0.5) * 2
        blink_intensity = max(0, min(1, blink_intensity))

        if blink_intensity > 0.3:
            # Escurece regiao dos olhos
            for eye_pt in [eye_left, eye_right]:
                ex1 = max(0, eye_pt[0] - eye_size)
                ey1 = max(0, eye_pt[1] - int(eye_size * 0.3))
                ex2 = min(w, eye_pt[0] + eye_size)
                ey2 = min(h, eye_pt[1] + int(eye_size * 0.7))

                if ey2 > ey1 and ex2 > ex1:
                    eye_roi = frame[ey1:ey2, ex1:ex2].copy()
                    dark_eye = np.clip(eye_roi * (1 - blink_intensity * 0.7), 0, 255).astype(np.uint8)
                    frame[ey1:ey2, ex1:ex2] = dark_eye

    return frame, last_blink, blink_interval


def animate_body_movement(frame, pontos, t, fase):
    """
    Anima movimento do corpo/ombros para gestos naturais.
    """
    h, w = frame.shape[:2]

    # Ombros estao abaixo do rosto
    face_bottom = pontos["face_bottom"]
    shoulder_y = face_bottom[1]
    shoulder_h = h - shoulder_y

    if shoulder_h < 50:
        return frame

    # Movimento baseado na fase
    if fase == "enfase":
        # Ombros sobem para enfatizar
        shift_x = int(15 * np.sin(t * 4))
        shift_y = int(-5 * np.abs(np.sin(t * 4)))
    elif fase == "falando":
        # Movimento rtmico durante fala
        shift_x = int(8 * np.sin(t * 3))
        shift_y = int(-3 * np.abs(np.sin(t * 3)))
    else:
        # Movimento suave
        shift_x = int(3 * np.sin(t * 1.5))
        shift_y = int(-1 * np.sin(t * 2))

    # Aplica shear nos ombros
    M = np.float32([
        [1, 0.05 * np.sign(shift_x), shift_x],
        [0, 1, shift_y]
    ])

    shoulder_roi = frame[shoulder_y:h, :].copy()
    shoulder_warped = cv2.warpAffine(shoulder_roi, M, (w, shoulder_h),
                                      borderMode=cv2.BORDER_REFLECT)

    frame[shoulder_y:h, :] = shoulder_warped

    return frame


def add_breathing_effect(frame, t):
    """
    Adiciona leve efeito de respiracao (expansao/contração sutil).
    """
    h, w = frame.shape[:2]

    # Expansao maxima de 1-2%
    scale = 1.0 + 0.008 * np.sin(t * 1.5)  # Frequencia de respiracao

    M = cv2.getRotationMatrix2D((w // 2, h // 2), 0, scale)
    frame = cv2.warpAffine(frame, M, (w, h), borderMode=cv2.BORDER_REFLECT)

    return frame


def create_talking_head_video():
    """
    Cria video completo do talking head com todos os efeitos.
    """
    print("=" * 60)
    print("  KONG TALKING HEAD - Animacao Avancada")
    print("=" * 60)

    # Carrega assets
    roteiro, img, duracao = load_assets()
    print(f"Roteiro: {len(roteiro['falas'])} falas")
    print(f"Duracao: {duracao:.1f}s")

    h_img, w_img = img.shape[:2]
    print(f"Imagem: {w_img}x{h_img}")

    # Dimensoes de saida
    out_w, out_h = 1280, 720

    # Escala para preencher
    scale = max(out_w / w_img, out_h / h_img)
    new_w = int(w_img * scale)
    new_h = int(h_img * scale)

    img_scaled = cv2.resize(img, (new_w, new_h))

    # Detecta pontos faciais
    pontos, _, _ = detectar_pontos_faciais(img)

    # Ajusta pontos para nova escala
    pontos_scaled = {}
    for k, (x, y) in pontos.items():
        pontos_scaled[k] = (
            int((x / w_img) * new_w - (new_w - out_w) // 2),
            int((y / h_img) * new_h - (new_h - out_h) // 2)
        )

    # Recalcula bounding box do rosto
    face_left = pontos_scaled["face_left"]
    face_right = pontos_scaled["face_right"]
    face_top = pontos_scaled["face_top"]
    face_bottom = pontos_scaled["face_bottom"]

    fps = 30
    total_frames = int(duracao * fps)

    # Numero de falas
    num_falas = len(roteiro['falas'])
    dur_fala = duracao / num_falas

    frames_dir = OUTPUT_DIR / "frames_talking"
    frames_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nCriando {total_frames} frames animados...")

    last_blink = -1.0
    blink_interval = 3.0

    for i in range(total_frames):
        t = i / fps
        progresso = t / duracao

        # Copia imagem base
        frame = img_scaled.copy()

        # Crop central
        x_offset = (new_w - out_w) // 2
        y_offset = (new_h - out_h) // 2
        frame = frame[y_offset:y_offset+out_h, x_offset:x_offset+out_w]

        # Recalcula pontos para o frame
        for k in pontos_scaled:
            orig = pontos[k]
            pontos_scaled[k] = (
                int((orig[0] / new_w) * out_w),
                int((orig[1] / new_h) * out_h)
            )

        # Atualiza pontos faciais para a escala do frame
        pontos_frame = {}
        for k, (x, y) in pontos.items():
            pontos_frame[k] = (
                int(x * out_w / w_img),
                int(y * out_h / h_img)
            )

        # Determina fase da animacao
        fala_atual = int(t / dur_fala)
        t_na_fala = t % dur_fala

        if fala_atual == 0 and t_na_fala < dur_fala * 0.3:
            fase = "inicio"
        elif fala_atual == num_falas - 1 and t_na_fala > dur_fala * 0.7:
            fase = "fim"
        elif t_na_fala > dur_fala - 0.5:
            fase = "enfase"
        elif t_na_fala > dur_fala * 0.2:
            fase = "falando"
        else:
            fase = "inicio"

        # Intensidade do speaking
        intensidade_fala = 0.0
        if fase == "falando":
            intensidade_fala = 0.4 + 0.5 * np.abs(np.sin(t * 10))
        elif fase == "enfase":
            intensidade_fala = 0.6 + 0.3 * np.sin(t * 7)
        elif fase == "inicio":
            intensidade_fala = 0.2 + 0.3 * np.sin(t * 5)

        # Aplica animacoes em ordem
        frame = add_breathing_effect(frame, t)
        frame = animate_body_movement(frame, pontos_frame, t, fase)
        frame = warp_face_region(frame, pontos_frame, t, fase, intensidade_fala)
        frame = animate_mouth(frame, pontos_frame, t, fase, intensidade_fala)
        frame, last_blink, blink_interval = animate_eyes(
            frame, pontos_frame, t, last_blink, blink_interval
        )

        # Vinheta cinematica
        vignette = criar_vinheta(out_w, out_h, intensidade=0.25)
        frame = cv2.addWeighted(frame, 1, vignette, 0.25, 0)

        # Barra dourada no topo
        frame[0:12, :] = [255, 215, 0]

        # Texto "KONG DIZ:" sutil
        cv2.putText(frame, "KONG DIZ:", (out_w//2 - 60, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 215, 0), 2,
                    cv2.LINE_AA)

        # Salva frame
        frame_path = str(frames_dir / f"frame_{i:05d}.png")
        cv2.imwrite(frame_path, frame)

        if i % 100 == 0:
            print(f"  Frame {i}/{total_frames} ({100*i//total_frames}%)")

    print(f"\nFrames salvos em: {frames_dir}")

    # Gera video
    audio_path = OUTPUT_DIR / "kong_audio_unificado.mp4"
    output_path = OUTPUT_DIR / "kong_talking_head.mp4"

    # Copia audio para mp4 se necessario
    import shutil
    shutil.copy(OUTPUT_DIR / "kong_audio_unificado.mp3", audio_path)

    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", str(frames_dir / "frame_%05d.png").replace("\\", "/"),
        "-i", str(audio_path).replace("\\", "/"),
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        str(output_path).replace("\\", "/")
    ]

    print("\nCodificando video final...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

    # Limpa frames
    try:
        shutil.rmtree(frames_dir)
    except:
        pass

    if result.returncode != 0:
        print(f"ERRO: {result.stderr[-500:]}")
        return False

    tamanho = output_path.stat().st_size / (1024 * 1024)
    print(f"\n" + "=" * 60)
    print(f"SUCESSO! KONG TALKING HEAD PRONTO!")
    print(f"Arquivo: {output_path}")
    print(f"Tamanho: {tamanho:.2f} MB")
    print(f"Duracao: {duracao:.1f}s")
    print("=" * 60)

    return True


def criar_vinheta(w, h, intensidade=0.25):
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


if __name__ == "__main__":
    create_talking_head_video()
