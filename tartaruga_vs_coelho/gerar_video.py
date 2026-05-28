"""
Tartaruga vs Coelhso - A Grande Vingança
A tartaruga ganha do coelho na corrida e fala: VENCI OTÁRIO!
"""

import os
from PIL import Image, ImageDraw, ImageFont

# Configurações
LARGURA = 800
ALTURA = 400
FPS = 30
DURACAO = 6  # segundos
TOTAL_FRAMES = FPS * DURACAO
PASTA_FRAMES = "frames_output"

# Cores
COR_GRAMA = (76, 175, 80)
COR_CEU = (135, 206, 250)
COR_PISTA = (180, 140, 100)
COR_LINHA_CHEGADA = (255, 255, 255)
COR_TARTARUGA = (34, 139, 34)
COR_COELHO = (200, 150, 100)
COR_TEXTO = (255, 255, 0)
COR_BORDA = (0, 0, 0)

# Posições
LINHA_CHEGADA = LARGURA - 80
LINHA_PARTIDA = 100
FAIXA_TARTARUGA = ALTURA // 2 - 50
FAIXA_COELHO = ALTURA // 2 + 30


def criar_pasta():
    if not os.path.exists(PASTA_FRAMES):
        os.makedirs(PASTA_FRAMES)


def desenhar_tartaruga(draw, x, y, tamanho=60, flip=False):
    """Desenha uma tartaruga"""
    dx = -1 if flip else 1
    # Casco (elipse)
    draw.ellipse([x, y, x + tamanho * dx, y + int(tamanho * 0.6)], fill=COR_TARTARUGA, outline=COR_BORDA, width=2)
    # Cabeça
    draw.ellipse([x + tamanho * 0.8 * dx, y + int(tamanho * 0.1), x + tamanho * 1.1 * dx, y + int(tamanho * 0.35)], fill=COR_TARTARUGA, outline=COR_BORDA, width=2)
    # Olho
    draw.ellipse([x + tamanho * 0.9 * dx, y + int(tamanho * 0.15), x + tamanho * 0.95 * dx, y + int(tamanho * 0.25)], fill=(0, 0, 0))
    # Pernas
    draw.ellipse([x + tamanho * 0.1 * dx, y + int(tamanho * 0.5), x + tamanho * 0.3 * dx, y + int(tamanho * 0.65)], fill=COR_TARTARUGA, outline=COR_BORDA)
    draw.ellipse([x + tamanho * 0.6 * dx, y + int(tamanho * 0.5), x + tamanho * 0.8 * dx, y + int(tamanho * 0.65)], fill=COR_TARTARUGA, outline=COR_BORDA)
    # Cauda
    draw.ellipse([x - tamanho * 0.1 * dx, y + int(tamanho * 0.25), x + tamanho * 0.05 * dx, y + int(tamanho * 0.35)], fill=COR_TARTARUGA)


def desenhar_coelho(draw, x, y, tamanho=55, flip=False):
    """Desenha um coelho"""
    dx = -1 if flip else 1
    # Corpo
    draw.ellipse([x, y + int(tamanho * 0.3), x + tamanho * dx, y + int(tamanho * 0.8)], fill=COR_COELHO, outline=COR_BORDA, width=2)
    # Cabeça
    draw.ellipse([x + tamanho * 0.5 * dx, y, x + tamanho * 1.1 * dx, y + int(tamanho * 0.45)], fill=COR_COELHO, outline=COR_BORDA, width=2)
    # Orelha esquerda
    draw.ellipse([x + tamanho * 0.55 * dx, y - int(tamanho * 0.5), x + tamanho * 0.75 * dx, y + int(tamanho * 0.1)], fill=COR_COELHO, outline=COR_BORDA, width=2)
    # Orelha direita
    draw.ellipse([x + tamanho * 0.8 * dx, y - int(tamanho * 0.45), x + tamanho * 1.0 * dx, y + int(tamanho * 0.1)], fill=COR_COELHO, outline=COR_BORDA, width=2)
    # Olho
    draw.ellipse([x + tamanho * 0.75 * dx, y + int(tamanho * 0.12), x + tamanho * 0.85 * dx, y + int(tamanho * 0.22)], fill=(0, 0, 0))
    # Nariz
    draw.ellipse([x + tamanho * 0.95 * dx, y + int(tamanho * 0.22), x + tamanho * 1.0 * dx, y + int(tamanho * 0.28)], fill=(255, 100, 100))
    # Pernas
    draw.ellipse([x + tamanho * 0.1 * dx, y + int(tamanho * 0.7), x + tamanho * 0.35 * dx, y + int(tamanho * 0.9)], fill=COR_COELHO, outline=COR_BORDA)
    draw.ellipse([x + tamanho * 0.5 * dx, y + int(tamanho * 0.7), x + tamanho * 0.75 * dx, y + int(tamanho * 0.9)], fill=COR_COELHO, outline=COR_BORDA)


def desenhar_nuvem(draw, x, y, tamanho=50):
    """Desenha uma nuvem"""
    draw.ellipse([x, y, x + tamanho, y + int(tamanho * 0.5)], fill=(255, 255, 255))
    draw.ellipse([x + int(tamanho * 0.2), y - int(tamanho * 0.15), x + int(tamanho * 0.7), y + int(tamanho * 0.4)], fill=(255, 255, 255))
    draw.ellipse([x + int(tamanho * 0.5), y, x + int(tamanho * 1.1), y + int(tamanho * 0.5)], fill=(255, 255, 255))


def desenhar_arvore(draw, x, y):
    """Desenha uma árvore"""
    # Tronco
    draw.rectangle([x + 15, y + 40, x + 30, y + 80], fill=(101, 67, 33))
    # Copa
    draw.ellipse([x - 10, y, x + 55, y + 50], fill=(34, 139, 34))


def desenhar_flor(draw, x, y):
    """Desenha uma flor"""
    draw.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(255, 200, 0))
    draw.ellipse([x - 8, y - 2, x - 2, y + 2], fill=(255, 100, 100))
    draw.ellipse([x + 2, y - 2, x + 8, y + 2], fill=(255, 100, 100))
    draw.ellipse([x - 2, y - 8, x + 2, y - 2], fill=(255, 100, 100))
    draw.ellipse([x - 2, y + 2, x + 2, y + 8], fill=(255, 100, 100))


def calcular_posicao(frame, personagem="tartaruga"):
    """Calcula a posição do personagem baseado no frame atual"""

    if personagem == "tartaruga":
        # A tartaruga começa devagar mas não para
        # Acelera progressivamente
        progresso = frame / TOTAL_FRAMES
        # Efeito de aceleração constante
        pos = LINHA_PARTIDA + (LINHA_CHEGADA - LINHA_PARTIDA) * (progresso ** 0.8)
        # Balanço
        balanco = abs(int(3 * (frame % 20) / 20 - 1.5))
    else:
        # O coelho começa rápido mas PARA no meio (a soneca!)
        if frame < TOTAL_FRAMES * 0.3:
            # Coelhso dispara na frente
            progresso = frame / (TOTAL_FRAMES * 0.3)
            pos = LINHA_PARTIDA + (LINHA_CHEGADA - LINHA_PARTIDA) * 0.65 * progresso
        elif frame < TOTAL_FRAMES * 0.7:
            # Coelhso para e dorme (soneca!)
            pos = LINHA_PARTIDA + (LINHA_CHEGADA - LINHA_PARTIDA) * 0.65
        elif frame < TOTAL_FRAMES * 0.85:
            # Coelhso acorda e volta a correr (mas é tarde!)
            progresso = (frame - TOTAL_FRAMES * 0.7) / (TOTAL_FRAMES * 0.15)
            pos = LINHA_PARTIDA + (LINHA_CHEGADA - LINHA_PARTIDA) * (0.65 + 0.25 * progresso)
        else:
            # O coelhso tenta alcançar mas não consegue!
            progresso = (frame - TOTAL_FRAMES * 0.85) / (TOTAL_FRAMES * 0.15)
            pos = LINHA_PARTIDA + (LINHA_CHEGADA - LINHA_PARTIDA) * (0.9 + 0.1 * progresso)
            if pos > LINHA_CHEGADA - 30:
                pos = LINHA_CHEGADA - 30

        balanco = abs(int(4 * (frame % 15) / 15 - 2))

    return int(pos), balanco


def desenhar_texto_buraco(draw, texto, x, y, tamanho_fonte=40):
    """Desenha texto com contorno preto"""
    try:
        fonte = ImageFont.truetype("arialbd.ttf", tamanho_fonte)
    except:
        fonte = ImageFont.load_default()

    # Contorno
    for dx in range(-3, 4):
        for dy in range(-3, 4):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), texto, fill=COR_BORDA, font=fonte)
    # Texto principal
    draw.text((x, y), texto, fill=COR_TEXTO, font=fonte)


def criar_frame(frame_num):
    """Cria um frame individual"""
    img = Image.new('RGB', (LARGURA, ALTURA))
    draw = ImageDraw.Draw(img)

    # Céu
    draw.rectangle([0, 0, LARGURA, ALTURA // 2], fill=COR_CEU)
    # Grama
    draw.rectangle([0, ALTURA // 2, LARGURA, ALTURA], fill=COR_GRAMA)
    # Pista
    draw.rectangle([0, ALTURA // 2 - 10, LARGURA, ALTURA // 2 + 80], fill=COR_PISTA)
    # Linhas da pista
    for i in range(0, LARGURA, 40):
        draw.line([(i, ALTURA // 2 + 30), (i + 20, ALTURA // 2 + 30)], fill=(160, 120, 80), width=3)

    # Nuvens
    desenhar_nuvem(draw, 50, 30, 60)
    desenhar_nuvem(draw, 250, 60, 50)
    desenhar_nuvem(draw, 450, 20, 70)
    desenhar_nuvem(draw, 620, 50, 55)

    # Árvores e flores
    desenhar_arvore(draw, 30, ALTURA // 2 - 50)
    desenhar_arvore(draw, 700, ALTURA // 2 - 50)
    desenhar_arvore(draw, 350, ALTURA // 2 - 50)

    for i in range(5, LARGURA, 80):
        desenhar_flor(draw, i, ALTURA // 2 + 75)

    # Linha de chegada
    for i in range(0, ALTURA, 15):
        cor = COR_LINHA_CHEGADA if (i // 15) % 2 == 0 else COR_BORDA
        draw.rectangle([LINHA_CHEGADA, i, LINHA_CHEGADA + 10, i + 15], fill=cor)

    # Banner "CHEGADA"
    draw.rectangle([LINHA_CHEGADA - 5, 50, LINHA_CHEGADA + 15, 90], fill=(255, 255, 255), outline=COR_BORDA, width=2)
    try:
        fonte_small = ImageFont.truetype("arialbd.ttf", 12)
    except:
        fonte_small = ImageFont.load_default()
    draw.text((LINHA_CHEGADA - 2, 55), "F", fill=(0, 0, 0), font=fonte_small)
    draw.text((LINHA_CHEGADA - 2, 65), "I", fill=(0, 0, 0), font=fonte_small)
    draw.text((LINHA_CHEGADA - 2, 75), "N", fill=(0, 0, 0), font=fonte_small)

    # Posições dos personagens
    pos_tartaruga, _ = calcular_posicao(frame_num, "tartaruga")
    pos_coelho, _ = calcular_posicao(frame_num, "coelho")

    # Desenhar personagens (ordem baseada na posição Y para profundidade)
    if FAIXA_TARTARUGA < FAIXA_COELHO:
        desenhar_tartaruga(draw, pos_tartaruga, FAIXA_TARTARUGA)
        if abs(pos_coelho - pos_tartaruga) < 80:
            # Se estão perto, desenhar coelho atrás da tartaruga (perspectiva)
            if pos_coelho > pos_tartaruga:
                desenhar_coelho(draw, pos_coelho, FAIXA_COELHO)
            else:
                desenhar_coelho(draw, pos_coelho, FAIXA_COELHO)
                desenhar_tartaruga(draw, pos_tartaruga, FAIXA_TARTARUGA)
        else:
            desenhar_coelho(draw, pos_coelho, FAIXA_COELHO)
    else:
        desenhar_coelho(draw, pos_coelho, FAIXA_COELHO)
        desenhar_tartaruga(draw, pos_tartaruga, FAIXA_TARTARUGA)

    # ===== TEXTO NA TELA =====
    progresso = frame_num / TOTAL_FRAMES

    # Título no início
    if frame_num < FPS * 1.5:
        alpha = min(255, (FPS * 1.5 - frame_num) * 3) if frame_num > FPS * 0.5 else 255
        alpha = max(0, min(255, alpha))
        texto_titulo = "A GRANDE CORRIDA"
        try:
            fonte_grande = ImageFont.truetype("arialbd.ttf", 50)
        except:
            fonte_grande = ImageFont.load_default()
        # Fundo do título
        draw.rectangle([LARGURA // 2 - 220, 100, LARGURA // 2 + 220, 170], fill=(0, 0, 0))
        draw.rectangle([LARGURA // 2 - 215, 105, LARGURA // 2 + 215, 165], fill=(50, 50, 150))
        # Contorno
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if dx != 0 or dy != 0:
                    draw.text((LARGURA // 2 - 160 + dx, 118 + dy), texto_titulo, fill=COR_BORDA, font=fonte_grande)
        draw.text((LARGURA // 2 - 160, 120), texto_titulo, fill=(255, 255, 255), font=fonte_grande)

    # Narrador no meio da corrida
    if frame_num > FPS * 1 and frame_num < FPS * 3:
        if frame_num < FPS * 1.8:
            narr = "Tartaruga: 'Devagar e constante vence a corrida!'"
        else:
            narr = "Coelhso: 'Essa é fácil! Vou dormir um pouco...'"
        try:
            fonte_narr = ImageFont.truetype("arial.ttf", 20)
        except:
            fonte_narr = ImageFont.load_default()
        draw.rectangle([10, ALTURA - 60, 500, ALTURA - 25], fill=(0, 0, 0))
        draw.text((15, ALTURA - 58), narr, fill=(255, 255, 255), font=fonte_narr)

    # A tartaruga cruza a linha primeiro!
    if frame_num >= FPS * (DURACAO - 2):
        frame_vitoria = frame_num - FPS * (DURACAO - 2)
        # Texto "VENCI OTÁRIO!"
        escala = 1.0 + 0.3 * min(1.0, frame_vitoria / (FPS * 0.3))
        tamanho_fonte = int(50 * escala)
        texto_venci = "VENCI OTÁRIO!"
        try:
            fonte_venci = ImageFont.truetype("arialbd.ttf", tamanho_fonte)
        except:
            fonte_venci = ImageFont.load_default()

        # Efeito de glow
        for glow in range(5, 0, -1):
            cor_glow = (255, 255 - glow * 30, 0)
            x_pos = LARGURA // 2 - len(texto_venci) * tamanho_fonte * 0.3
            draw.text((x_pos, 120), texto_venci, fill=cor_glow, font=fonte_venci)

        draw.text((x_pos, 120), texto_venci, fill=COR_TEXTO, font=fonte_venci)

        # Sub-título
        if frame_vitoria > FPS * 0.5:
            sub_texto = "A TARTARUGA GANHOU!"
            try:
                fonte_sub = ImageFont.truetype("arialbd.ttf", 30)
            except:
                fonte_sub = ImageFont.load_default()
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    draw.text((LARGURA // 2 - 130 + dx, 180 + dy), sub_texto, fill=COR_BORDA, font=fonte_sub)
            draw.text((LARGURA // 2 - 130, 180), sub_texto, fill=(0, 255, 0), font=fonte_sub)

    # Contador de tempo
    tempo = frame_num / FPS
    try:
        fonte_tempo = ImageFont.truetype("arial.ttf", 18)
    except:
        fonte_tempo = ImageFont.load_default()
    draw.rectangle([10, 10, 100, 40], fill=(0, 0, 0))
    draw.text((15, 15), f"T: {tempo:.1f}s", fill=(255, 255, 255), font=fonte_tempo)

    return img


def main():
    print("==> Gerando video: Tartaruga vs Coelho")
    print(f"   {TOTAL_FRAMES} frames | {FPS} FPS | {DURACAO}s")
    print()

    criar_pasta()

    # Gerar frames
    for i in range(TOTAL_FRAMES):
        if i % 30 == 0:
            progresso = (i / TOTAL_FRAMES) * 100
            print(f"   Gerando frame {i}/{TOTAL_FRAMES} ({progresso:.1f}%)")

        img = criar_frame(i)
        img.save(os.path.join(PASTA_FRAMES, f"frame_{i:04d}.png"))

    print()
    print("==> Frames gerados!")

    # Verificar se FFmpeg está disponível
    import subprocess
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        print("==> FFmpeg encontrado! Gerando video...")
    except:
        print("==> AVISO: FFmpeg nao encontrado. Instale o FFmpeg para gerar o video.")
        print("   Baixe em: https://ffmpeg.org/download.html")
        print("   Ou via winget: winget install ffmpeg")
        return

    # Gerar vídeo com FFmpeg
    output_video = "tartaruga_vs_coelho.mp4"
    comando = [
        'ffmpeg', '-y',
        '-framerate', str(FPS),
        '-i', os.path.join(PASTA_FRAMES, 'frame_%04d.png'),
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-crf', '18',
        '-preset', 'medium',
        output_video
    ]

    print(f"   Executando: {' '.join(comando)}")
    resultado = subprocess.run(comando, capture_output=True, text=True)

    if resultado.returncode == 0:
        tamanho = os.path.getsize(output_video)
        print()
        print(f"==> Video gerado com sucesso!")
        print(f"   Arquivo: {os.path.abspath(output_video)}")
        print(f"   Tamanho: {tamanho / (1024*1024):.2f} MB")
        print()
        print(f"   Reproduza com: start {output_video}")
    else:
        print(f"==> Erro ao gerar video:")
        print(resultado.stderr[-500:])


if __name__ == "__main__":
    main()
