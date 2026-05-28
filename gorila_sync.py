#!/usr/bin/env python3
"""
GORILA SYNC - Animacao Avancada de Sincronizacao Labial
=================================================================
Pipeline de video com efeitos de fala realista para o Kong.

Efeitos implementados:
- Deteccao de regiao do rosto (boca) usando OpenCV
- Variacao de brilho na area da boca durante a fala
- Efeito de "head bounce" sincronizado com a voz
- Variacao de saturacao e leve distorcao durante fonemas
- Pulso de energia visual sincronizado com intensidade da voz

Uso: python gorila_sync.py
=================================================================
"""

import os
import sys
import json
import math
import subprocess
from pathlib import Path
import cv2
import numpy as np


# ==================== CONFIGURACAO ====================

OUTPUT_DIR = Path(__file__).parent / "uploads" / "gorila"
FONT_PATH = "C:/Windows/Fonts/arial.ttf"

# Parametros de video
LARGURA = 1280
ALTURA = 720
FPS = 30

# Parametros de sincronizacao labial
BRILHO_BOCA_BASE = 1.0        # Fator base de brilho na boca
BRILHO_BOCA_FALA = 1.15       # Fator de brilho durante a fala
SATURACAO_BOCA_FALA = 1.1     # Aumento de saturacao durante a fala
INTENSIDADE_BOUNCE = 0.008    # Intensidade do efeito de bounce na cabeca
VELOCIDADE_BOUNCE = 8.0       # Velocidade de oscilacao do bounce


# ==================== MAPEAMENTO FONETICO ====================

# Mapeamento de fonemas portuges para intensidade de abertura labial
# Baseado em fonemas do Portugues Brasileiro
FONEMAS_PB = {
    # Vogais abertas (maior abertura)
    'a': 0.8, 'e': 0.7, 'o': 0.7, 'A': 0.8, 'E': 0.7, 'O': 0.7,
    # Vogais fechadas (menor abertura)
    'i': 0.3, 'u': 0.3, 'I': 0.3, 'U': 0.3,
    # Consoantes que afetam a boca
    'b': 0.4, 'd': 0.5, 'f': 0.3, 'g': 0.4, 'j': 0.5,
    'l': 0.4, 'm': 0.2, 'n': 0.2, 'p': 0.4, 'r': 0.3,
    's': 0.4, 't': 0.5, 'v': 0.3, 'z': 0.4,
    'c': 0.4, 'h': 0.1, 'k': 0.4, 'n': 0.2, 'q': 0.3,
    'w': 0.3, 'x': 0.3, 'y': 0.3,
    # Acentos e caracteres especiais sao ignorados
}

# Silabas para analise de ritmo
SILABAS_FORTES = ['ca', 'co', 'que', 'qui', 'ga', 'go', 'ta', 'to', 'da', 'do',
                  'pa', 'po', 'ba', 'bo', 'fa', 'fe', 've', 'za', 'ze', 'zo',
                  'ma', 'me', 'mi', 'mo', 'mu', 'na', 'ne', 'ni', 'no', 'nu']


# ==================== ANALISADOR DE FALA ====================

def analisar_texto(texto):
    """
    Analisa o texto e retorna uma lista de fonemas com timing estimado.
    Cada fonema tem: texto, inicio (s), fim (s), intensidade
    """
    # Limpa o texto
    texto_limpo = ''.join(c for c in texto.lower() if c.isalpha() or c in 'aeiou ')

    fonemas = []
    tempo_atual = 0.0

    # Estimativa: 4 a 6 fonemas por segundo em portugues brasileiro falado
    taxa_fonemas = 5.0  # fonemas por segundo

    for char in texto_limpo:
        if char == ' ':
            # Pausa entre palavras
            tempo_atual += 0.15
            continue

        # Intensidade baseada no fonema
        intensidade = FONEMAS_PB.get(char, 0.4)

        # Duracao do fonema (varia um pouco)
        duracao = 1.0 / taxa_fonemas * (0.8 + np.random.random() * 0.4)

        fonemas.append({
            'char': char,
            'inicio': tempo_atual,
            'fim': tempo_atual + duracao,
            'intensidade': intensidade
        })

        tempo_atual += duracao

    return fonemas


def analisar_intensidade_audio(caminho_audio):
    """
    Usa OpenCV para analisar o audio e detectar regioes de fala.
    Retorna lista de timestamps com intensidade de energia.
    """
    try:
        import moviepy.editor
        audio = moviepy.editor.AudioFileClip(caminho_audio)
        duracao = audio.duration
        audio.close()
    except Exception as e:
        print(f"AVISO: Nao foi possivel analisar audio: {e}")
        return [], 10.0

    # Usa ffmpeg para extrair volume em intervalos
    arquivo_vol = OUTPUT_DIR / "volume_data.txt"

    try:
        cmd = [
            "ffmpeg", "-y", "-i", caminho_audio,
            "-af", "volumedetect",
            "-f", "null", "-"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        # Parseia output para detectar volume medio
        media_vol = -20.0  # fallback
        for line in result.stderr.split('\n'):
            if 'mean_volume' in line:
                try:
                    val = line.split('mean_volume:')[1].split('dB')[0].strip()
                    media_vol = float(val)
                except:
                    pass

    except Exception:
        media_vol = -20.0

    # Cria curva de intensidade baseada no texto (mais realista para PT-BR)
    # Retorna lista de (timestamp, intensidade_normalizada)
    intensidades = []

    return intensidades, duracao


# ==================== DETECCAO DE ROSTO ====================

def detectar_regiao_boca(img):
    """
    Detecta a regiao aproximada da boca no rosto.
    Se o rosto for detectado com Haar Cascade, usa-o.
    Caso contrario, usa heuristicas baseadas na imagem.
    Retorna: (x, y, w, h) da regiao da boca ou None
    """
    # Tenta usar Haar Cascade para detectar rosto
    try:
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        if len(faces) > 0:
            # Usa o maior rosto detectado
            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])

            # A boca fica na metade inferior do rosto
            boca_y = int(y + h * 0.65)
            boca_h = int(h * 0.25)
            boca_x = int(x + w * 0.2)
            boca_w = int(w * 0.6)

            return (boca_x, boca_y, boca_w, boca_h)
    except Exception as e:
        print(f"AVISO: Deteccao de rosto falhou: {e}")

    # Fallback: usa heuristicas baseadas no centro da imagem
    h, w = img.shape[:2]
    centro_x = w // 2
    centro_y = int(h * 0.55)  # Um pouco abaixo do centro

    # Regiao da boca como proporcao da imagem
    boca_w = int(w * 0.15)
    boca_h = int(h * 0.08)
    boca_x = int(centro_x - boca_w // 2)
    boca_y = int(centro_y - boca_h // 2)

    return (boca_x, boca_y, boca_w, boca_h)


def detectar_regiao_cabeca(img):
    """
    Detecta a regiao aproximada da cabeca para efeito de bounce.
    Retorna: (x, y, w, h) da cabeca
    """
    try:
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        if len(faces) > 0:
            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])

            # Expandir para incluir mais da cabeca
            cabeca_x = int(x - w * 0.1)
            cabeca_y = int(y - h * 0.3)
            cabeca_w = int(w * 1.2)
            cabeca_h = int(h * 1.3)

            return (cabeca_x, cabeca_y, cabeca_w, cabeca_h)
    except:
        pass

    # Fallback: tercio superior da imagem
    h, w = img.shape[:2]
    return (int(w * 0.2), 0, int(w * 0.6), int(h * 0.7))


# ==================== EFEITOS VISUAIS ====================

def aplicar_efeito_boca(frame, regiao_boca, intensidade_fala, fonema_intensidade):
    """
    Aplica efeito visual na regiao da boca baseado na intensidade da fala.

    Efeitos:
    - Variacao de brilho
    - Variacao de saturacao
    - Leve distorcao de cor
    """
    x, y, w, h = regiao_boca

    # Garante que a regiao esta dentro do frame
    x1 = max(0, x)
    y1 = max(0, y)
    x2 = min(frame.shape[1], x + w)
    y2 = min(frame.shape[0], y + h)

    if x2 <= x1 or y2 <= y1:
        return frame

    # Extrai regiao da boca
    boca_roi = frame[y1:y2, x1:x2].copy()

    # Converte para HSV para manipular saturacao
    hsv = cv2.cvtColor(boca_roi, cv2.COLOR_BGR2HSV).astype(np.float32)

    # Fator de brilho baseado na intensidade
    fator_brilho = BRILHO_BOCA_BASE + (BRILHO_BOCA_FALA - BRILHO_BOCA_BASE) * intensidade_fala * fonema_intensidade

    # Ajusta valor (brilho)
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] * fator_brilho, 0, 255)

    # Ajusta saturacao
    fator_sat = 1.0 + (SATURACAO_BOCA_FALA - 1.0) * intensidade_fala * fonema_intensidade
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * fator_sat, 0, 255)

    # Converte de volta para BGR
    boca_ajustada = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    # Mistura com original baseado na intensidade
    alpha = intensidade_fala * fonema_intensidade * 0.3
    boca_roi = cv2.addWeighted(boca_roi, 1 - alpha, boca_ajustada, alpha, 0)

    # Aplica blur leve para suavizar transicoes
    if intensidade_fala > 0.3:
        ksize = int(3 + fonema_intensidade * 3)
        if ksize % 2 == 0:
            ksize += 1
        boca_roi = cv2.GaussianBlur(boca_roi, (ksize, ksize), 0)

    # Copia de volta
    frame[y1:y2, x1:x2] = boca_roi

    return frame


def aplicar_efeito_bounce(frame, regiao_cabeca, fase_bounce):
    """
    Aplica efeito de movimento sutil na cabeca (bounce).
    Usa uma leve distorcao perspectiva para simular inclinacao.
    """
    x, y, w, h = regiao_cabeca

    # Garante que a regiao esta dentro do frame
    x1 = max(0, x)
    y1 = max(0, y)
    x2 = min(frame.shape[1], x + w)
    y2 = min(frame.shape[0], y + h)

    if x2 <= x1 or y2 <= y1:
        return frame

    # Calcula deslocamento baseado na fase
    dx = int(INTENSIDADE_BOUNCE * LARGURA * math.sin(fase_bounce))
    dy = int(INTENSIDADE_BOUNCE * ALTURA * math.cos(fase_bounce * 1.3))

    # Aplica translacao suave na regiao da cabeca
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    cabeca_roi = frame[y1:y2, x1:x2].copy()
    cabeca_deslocada = cv2.warpAffine(cabeca_roi, M, (x2 - x1, y2 - y1),
                                       borderMode=cv2.BORDER_REFLECT)

    # Mistura com original
    frame[y1:y2, x1:x2] = cv2.addWeighted(cabeca_roi, 0.7, cabeca_deslocada, 0.3, 0)

    return frame


def aplicar_efeito_pulso(frame, intensidade):
    """
    Aplica efeito de pulso geral na imagem baseado na intensidade da voz.
    Simula a energia vital do personagem falando.
    """
    if intensidade < 0.1:
        return frame

    # Variacao sutil de gamma
    gamma = 1.0 + (0.05 * intensidade)
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255
                      for i in np.arange(0, 256)]).astype(np.uint8)

    # Aplica LUT
    frame = cv2.LUT(frame, table)

    return frame


# ==================== PROCESSADOR PRINCIPAL ====================

def processar_video(caminho_imagem, caminho_audio, roteiro_path):
    """
    Processa o video com todos os efeitos de sincronizacao labial.
    """
    print("=" * 60)
    print("[GORILA SYNC] Processando video com sincronizacao labial...")
    print("=" * 60)

    # Carrega roteiro
    with open(roteiro_path, 'r', encoding='utf-8') as f:
        roteiro = json.load(f)

    falas = roteiro['falas']

    # Carrega audio para duracao
    try:
        import moviepy.editor
        audio = moviepy.editor.AudioFileClip(caminho_audio)
        duracao_total = audio.duration
        audio.close()
    except Exception as e:
        print(f"ERRO: Nao foi possivel carregar audio: {e}")
        duracao_total = 15.0

    print(f"Duracao total: {duracao_total:.1f}s")

    # Carrega imagem
    img = cv2.imread(caminho_imagem)
    if img is None:
        print(f"ERRO: Nao foi possivel carregar imagem: {caminho_imagem}")
        return None

    h_img, w_img = img.shape[:2]
    print(f"Imagem: {w_img}x{h_img}")

    # Detecta regioes
    regiao_boca = detectar_regiao_boca(img)
    if regiao_boca:
        print(f"Regiao boca detectada: {regiao_boca}")

    regiao_cabeca = detectar_regiao_cabeca(img)
    if regiao_cabeca:
        print(f"Regiao cabeca detectada: {regiao_cabeca}")

    # Analisa texto de cada fala para timing
    timings_falas = []
    tempo_atual = 0.0

    # Estima duracao por fala (divide o audio igualmente)
    duracao_por_fala = duracao_total / len(falas)

    for i, fala in enumerate(falas):
        inicio = tempo_atual
        fim = tempo_atual + duracao_por_fala
        texto = fala['texto']
        gesto = fala.get('gesto', '')

        # Analisa fonemas
        fonemas = analisar_texto(texto)

        timings_falas.append({
            'inicio': inicio,
            'fim': fim,
            'texto': texto,
            'gesto': gesto,
            'fonemas': fonemas
        })

        tempo_atual = fim

        print(f"  Fala {i+1}: {texto[:50]}...")
        print(f"    Timing: {inicio:.1f}s - {fim:.1f}s")

    # Cria frames
    print("\nGerando frames com efeitos de sincronizacao labial...")

    frames_dir = OUTPUT_DIR / "frames_sync"
    frames_dir.mkdir(exist_ok=True)

    total_frames = int(duracao_total * FPS)

    for i in range(total_frames):
        t = i / FPS
        progresso = t / duracao_total

        # Copia imagem base
        frame = img.copy()

        # Calcula intensidade de fala atual
        intensidade_fala = 0.0
        fase_bounce = 0.0
        fonema_intensidade = 0.0

        for info_fala in timings_falas:
            if info_fala['inicio'] <= t < info_fala['fim']:
                # Esta dentro de uma fala
                duracao_fala = info_fala['fim'] - info_fala['inicio']
                progresso_fala = (t - info_fala['inicio']) / duracao_fala

                # Intensidade envelope (sobe e desce suavemente)
                if progresso_fala < 0.1:
                    # Ataque
                    intensidade_fala = progresso_fala / 0.1
                elif progresso_fala > 0.85:
                    # Decaio
                    intensidade_fala = (1.0 - progresso_fala) / 0.15
                else:
                    # Sustain
                    intensidade_fala = 1.0 - (abs(progresso_fala - 0.5) * 0.3)

                intensidade_fala = max(0, min(1, intensidade_fala))

                # Bounce da cabeca
                fase_bounce = VELOCIDADE_BOUNCE * t

                # Intensidade do fonema atual
                tempo_local = t - info_fala['inicio']
                for fonema in info_fala['fonemas']:
                    if fonema['inicio'] <= tempo_local < fonema['fim']:
                        fonema_intensidade = fonema['intensidade']
                        break
                else:
                    fonema_intensidade = 0.5

                break

        # Aplica Ken Burns base
        zoom = 1.0 + 0.06 * np.sin(progresso * np.pi * 2.5)
        pan_x = int(25 * np.sin(progresso * np.pi * 3))
        pan_y = int(15 * np.cos(progresso * np.pi * 2))

        # Aplica bounce na cabeca
        if intensidade_fala > 0.2 and regiao_cabeca:
            frame = aplicar_efeito_bounce(frame, regiao_cabeca, fase_bounce * intensidade_fala)

        # Calcula crop
        crop_w = int(w_img / zoom)
        crop_h = int(h_img / zoom)

        center_x = w_img // 2 + pan_x
        center_y = h_img // 2 + pan_y

        x1 = max(0, min(center_x - crop_w // 2, w_img - crop_w))
        y1 = max(0, min(center_y - crop_h // 2, h_img - crop_h))

        crop = frame[y1:y1+crop_h, x1:x1+crop_w]

        # Resize
        frame = cv2.resize(crop, (LARGURA, ALTURA), interpolation=cv2.INTER_LANCZOS4)

        # Aplica efeito na boca
        if intensidade_fala > 0.1 and regiao_boca:
            # Ajusta coordenadas da boca para o novo tamanho
            escala_x = LARGURA / (w_img / zoom)
            escala_y = ALTURA / (h_img / zoom)

            boca_escalada = (
                int((regiao_boca[0] - x1) * escala_x),
                int((regiao_boca[1] - y1) * escala_y),
                int(regiao_boca[2] * escala_x),
                int(regiao_boca[3] * escala_y)
            )

            frame = aplicar_efeito_boca(frame, boca_escalada, intensidade_fala, fonema_intensidade)

        # Aplica pulso geral
        frame = aplicar_efeito_pulso(frame, intensidade_fala)

        # Efeito de gesticulacao baseado no gesto do roteiro
        for info_fala in timings_falas:
            if info_fala['inicio'] <= t < info_fala['fim']:
                gesto = info_fala.get('gesto', '')
                # Aplica efeitos especiais baseados no gesto
                if 'bater' in gesto.lower() or 'peito' in gesto.lower():
                    # Efeito de vibracao para bater no peito
                    if progresso_fala > 0.3 and progresso_fala < 0.6:
                        vib = int(2 * np.sin(t * 30))
                        frame = np.roll(frame, vib, axis=1)

                elif 'ergue' in gesto.lower() or 'punho' in gesto.lower():
                    # Leve inclinacao para erguer punho
                    if progresso_fala > 0.4:
                        incl = int(3 * np.sin(t * 5))
                        frame = np.roll(frame, incl, axis=0)

                elif 'acena' in gesto.lower() or 'sorri' in gesto.lower():
                    # Sorriso: aumenta brilho geral
                    if progresso_fala > 0.3:
                        frame = cv2.addWeighted(frame, 1, frame, 0.05, 5)

                break

        # Adiciona vinheta
        vignette = criar_vinheta(LARGURA, ALTURA, intensidade=0.25)
        frame = cv2.addWeighted(frame, 1, vignette, 0.25, 0)

        # Barra dourada no topo
        frame[0:8, :] = [255, 215, 0]

        # Salva frame
        cv2.imwrite(str(frames_dir / f"frame_{i:05d}.png"), frame)

        if i % 100 == 0 or i == total_frames - 1:
            print(f"  Processando: {i+1}/{total_frames} ({100*(i+1)//total_frames}%)")

    print(f"\nFrames processados: {frames_dir}")

    # Cria video com FFmpeg
    arquivo_video = OUTPUT_DIR / "kong_video_sync.mp4"

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

    print("\nCodificando video final...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

    if result.returncode != 0:
        print(f"ERRO FFmpeg: {result.stderr[-300:]}")
        return None

    # Limpa frames
    import shutil
    try:
        shutil.rmtree(frames_dir)
        print("Frames temporarios removidos.")
    except:
        pass

    tamanho = arquivo_video.stat().st_size / (1024 * 1024)
    print(f"\n" + "=" * 60)
    print(f"SUCESSO! VIDEO COM SYNC LABIAL CRIADO!")
    print(f"Arquivo: {arquivo_video}")
    print(f"Tamanho: {tamanho:.2f} MB")
    print(f"Duracao: {duracao_total:.1f}s")
    print("=" * 60)

    return str(arquivo_video)


def criar_vinheta(w, h, intensidade=0.25):
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


# ==================== VERIFICADOR DE DEPENDENCIAS ====================

def verificar_dependencias():
    """Verifica se todas as dependencias estao disponiveis."""
    deps = {}

    # OpenCV
    try:
        cv2.__version__
        deps['opencv'] = True
    except:
        deps['opencv'] = False

    # NumPy
    try:
        np.__version__
        deps['numpy'] = True
    except:
        deps['numpy'] = False

    # MoviePy
    try:
        import moviepy
        deps['moviepy'] = True
    except:
        deps['moviepy'] = False

    # FFmpeg
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
        deps['ffmpeg'] = result.returncode == 0
    except:
        deps['ffmpeg'] = False

    return deps


# ==================== MAIN ====================

def main():
    print("=" * 60)
    print("  GORILA SYNC - Sincronizacao Labial Avancada")
    print("=" * 60)

    # Verifica dependencias
    print("\nVerificando dependencias...")
    deps = verificar_dependencias()

    if not deps['opencv']:
        print("ERRO: OpenCV nao instalado. Execute: pip install opencv-python")
        sys.exit(1)
    if not deps['numpy']:
        print("ERRO: NumPy nao instalado. Execute: pip install numpy")
        sys.exit(1)
    if not deps['moviepy']:
        print("ERRO: MoviePy nao instalado. Execute: pip install moviepy")
        sys.exit(1)
    if not deps['ffmpeg']:
        print("AVISO: FFmpeg nao encontrado. Instale para melhor qualidade.")

    print("Dependencias OK.")

    # Verifica arquivos
    imagem = OUTPUT_DIR / "kong_imagem.png"
    audio = OUTPUT_DIR / "kong_audio_unificado.mp3"
    roteiro = OUTPUT_DIR / "roteiro_kong.json"

    if not imagem.exists():
        print(f"ERRO: Imagem nao encontrada: {imagem}")
        print("Execute primeiro: python gorila_video.py")
        sys.exit(1)

    if not audio.exists():
        print(f"ERRO: Audio nao encontrado: {audio}")
        print("Execute primeiro: python gorila_video.py")
        sys.exit(1)

    if not roteiro.exists():
        print(f"ERRO: Roteiro nao encontrado: {roteiro}")
        print("Execute primeiro: python gorila_video.py")
        sys.exit(1)

    print(f"\nArquivos encontrados:")
    print(f"  Imagem: {imagem}")
    print(f"  Audio: {audio}")
    print(f"  Roteiro: {roteiro}")

    # Processa video
    caminho_video = processar_video(str(imagem), str(audio), str(roteiro))

    if caminho_video:
        print(f"\nVideo final: {caminho_video}")
    else:
        print("\nFALHA no processamento.")
        sys.exit(1)


if __name__ == "__main__":
    main()
