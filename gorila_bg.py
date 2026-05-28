"""
╔══════════════════════════════════════════════════════════════════╗
║  GORILA BG - GERADOR DE BACKGROUNDS CINEMATOGRAFICOS              ║
║  Backgrounds dinamicos para video do Kong                        ║
║  Dependencias: opencv-python, numpy, moviepy                     ║
╚══════════════════════════════════════════════════════════════════╝
"""

import numpy as np
import cv2
try:
    from moviepy import VideoFileClip, AudioFileClip, CompositeVideoClip
except ImportError:
    from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip
import json
import os

# ═══════════════════════════════════════════════════════════════════
# CONFIGURACOES
# ═══════════════════════════════════════════════════════════════════

PASTA_ENTRADA = r"C:\xampp\htdocs\agente\uploads\gorila"
PASTA_SAIDA = r"C:\xampp\htdocs\agente\uploads\gorila\backgrounds"
ARQUIVO_ROTEIRO = os.path.join(PASTA_ENTRADA, "roteiro_kong.json")

# Resolucao padrao
LARGURA = 1280
ALTURA = 720
FPS = 30

# Paletas de cores por tema
PALETAS = {
    "cafe": {
        "nome": "Cafe Moderno",
        "cores": [(45, 35, 25), (80, 60, 40), (120, 85, 55), (160, 110, 70)],
        "cor_acao": (200, 150, 100)
    },
    "floresta": {
        "nome": "Floresta Amazonica",
        "cores": [(20, 60, 30), (35, 90, 45), (50, 120, 60), (70, 140, 40)],
        "cor_acao": (100, 200, 80)
    },
    "cidade": {
        "nome": "Cidade Noturna",
        "cores": [(15, 10, 30), (30, 20, 60), (50, 35, 80), (80, 60, 120)],
        "cor_acao": (255, 220, 100)
    },
    "estadio": {
        "nome": "Estadio de Luta",
        "cores": [(50, 10, 10), (100, 20, 20), (150, 40, 40), (180, 60, 30)],
        "cor_acao": (255, 200, 50)
    }
}


# ═══════════════════════════════════════════════════════════════════
# FUNCOES DE GERACAO DE BACKGROUNDS
# ═══════════════════════════════════════════════════════════════════

def criar_gradiente(cores, largura, altura, angulo=0):
    """Cria gradiente diagonal com multiplas cores."""
    gradiente = np.zeros((altura, largura, 3), dtype=np.uint8)

    for y in range(altura):
        for x in range(largura):
            # Normaliza posicao
            nx = x / largura
            ny = y / altura
            t = (nx + ny) / 2  # Gradiente diagonal

            # Interpola entre cores
            idx = t * (len(cores) - 1)
            i = int(idx)
            f = idx - i

            if i >= len(cores) - 1:
                cor = cores[-1]
            else:
                cor = tuple(
                    int(cores[i][j] * (1 - f) + cores[i + 1][j] * f)
                    for j in range(3)
                )
            gradiente[y, x] = cor

    return gradiente


def criar_padroes_geometricos(largura, altura, tema, tempo=0):
    """Cria padroes geometricos sutis para depth."""
    img = np.zeros((altura, largura, 3), dtype=np.uint8)

    paleta = PALETAS[tema]
    cor_base = paleta["cores"][0]

    # Camadas de profundidade (parallax simulado)
    for camada in range(3):
        tamanho = 50 + camada * 80
        opacidade = 0.15 - camada * 0.04
        offset_x = int((tempo * 10 + camada * 100) % largura)
        offset_y = int((tempo * 5 + camada * 50) % altura)

        # Hexagonos sutis
        for i in range(-2, largura // tamanho + 3):
            for j in range(-2, altura // tamanho + 3):
                cx = i * tamanho + offset_x - largura // 2
                cy = j * tamanho + offset_y - altura // 2

                # Desenha hexagono
                pontos = []
                for k in range(6):
                    ang = np.radians(60 * k + tempo * 20)
                    px = int(cx + tamanho * 0.4 * np.cos(ang))
                    py = int(cy + tamanho * 0.4 * np.sin(ang))
                    pontos.append([px, py])

                pontos = np.array([pontos], dtype=np.int32)
                cor_hex = tuple(int(c * opacidade) for c in cor_base)
                cv2.polylines(img, pontos, True, cor_hex, 1)

    return img


def criar_particulas(largura, altura, tema, tempo, num_particulas=50):
    """Cria particulas flutuantes animadas."""
    img = np.zeros((altura, largura, 3), dtype=np.uint8)
    paleta = PALETAS[tema]

    np.random.seed(42)
    particulas = []

    # Gera particulas
    for i in range(num_particulas):
        x = np.random.randint(0, largura)
        y_base = np.random.randint(0, altura)
        tamanho = np.random.randint(1, 4)
        velocidade_y = np.random.uniform(0.2, 1.0)

        # Cor baseda no tema
        cor_idx = np.random.randint(0, len(paleta["cores"]))
        cor = tuple(max(0, min(255, int(c * 1.5))) for c in paleta["cores"][cor_idx])

        particulas.append({
            "x": x, "y": y_base, "tamanho": tamanho,
            "vel_y": velocidade_y, "cor": cor
        })

    # Desenha e anima particulas
    for p in particulas:
        y = int(p["y"] + tempo * p["vel_y"] * 20)
        y = y % altura  # Loop vertical

        # Halo suave
        raio = p["tamanho"] * 3
        cv2.circle(img, (p["x"], y), raio, p["cor"], -1)

    return img


def criar_luz_radial(largura, altura, posicao, cor, intensidade=0.5):
    """Cria efeito de luz radial."""
    img = np.zeros((altura, largura, 3), dtype=np.uint8)

    centro_x, centro_y = posicao
    raio_max = max(largura, altura)

    for r in range(raio_max, 0, -5):
        alpha = (1 - r / raio_max) * intensidade
        cor_atual = tuple(int(c * alpha) for c in cor)
        cv2.circle(img, (centro_x, centro_y), r, cor_atual, -1)

    return img


def criar_efeito_profundidade(largura, altura, tema, tempo):
    """Cria efeito de profundidade com linhas convergentes."""
    img = np.zeros((altura, largura, 3), dtype=np.uint8)
    paleta = PALETAS[tema]

    # Ponto de fuga central
    centro_x, centro_y = largura // 2, int(altura * 0.4 + tempo * 10 % 50)

    # Linhas convergentes
    for i in range(-5, 6):
        angulo = np.radians(30 + i * 8)
        x_fim = int(centro_x + np.cos(angulo) * largura)
        y_fim = altura

        cor = tuple(c // 4 for c in paleta["cores"][1])
        cv2.line(img, (centro_x, centro_y), (x_fim, y_fim), cor, 1)

    return img


def gerar_background(tema, largura, altura, tempo=0.0):
    """Gera um frame de background completo."""
    paleta = PALETAS[tema]

    # Camada 1: Gradiente base
    gradiente = criar_gradiente(paleta["cores"], largura, altura)

    # Camada 2: Padroes geometricos
    geometria = criar_padroes_geometricos(largura, altura, tema, tempo)

    # Camada 3: Efeito de profundidade
    profundidade = criar_efeito_profundidade(largura, altura, tema, tempo)

    # Camada 4: Particulas
    particulas = criar_particulas(largura, altura, tema, tempo)

    # Camada 5: Luz radial (acento)
    luz = criar_luz_radial(
        largura, altura,
        (largura // 2, altura // 3),
        paleta["cor_acao"],
        0.3
    )

    # Garante que todas as camadas tem 3 canais
    if len(gradiente.shape) == 2:
        gradiente = cv2.cvtColor(gradiente, cv2.COLOR_GRAY2BGR)
    if len(geometria.shape) == 2:
        geometria = cv2.cvtColor(geometria, cv2.COLOR_GRAY2BGR)
    if len(profundidade.shape) == 2:
        profundidade = cv2.cvtColor(profundidade, cv2.COLOR_GRAY2BGR)
    if len(particulas.shape) == 2:
        particulas = cv2.cvtColor(particulas, cv2.COLOR_GRAY2BGR)
    if len(luz.shape) == 2:
        luz = cv2.cvtColor(luz, cv2.COLOR_GRAY2BGR)

    # Composicao das camadas
    resultado = cv2.add(gradiente, geometria)
    resultado = cv2.add(resultado, profundidade)
    resultado = cv2.add(resultado, particulas)
    resultado = cv2.add(resultado, luz)

    # Vinheta sutil
    vinheta = criar_vinheta(largura, altura, intensidade=0.3)
    if len(vinheta.shape) == 2:
        vinheta = cv2.cvtColor(vinheta, cv2.COLOR_GRAY2BGR)
    resultado = cv2.multiply(resultado.astype(np.float64), vinheta.astype(np.float64) / 255)

    return resultado.astype(np.uint8)


def criar_vinheta(largura, altura, intensidade=0.5):
    """Cria efeito de vinheta nas bordas usando OpenCV otimizado."""
    # Usa getGaussianKernel para criar elipse de vinheta
    kernel_x = cv2.getGaussianKernel(largura, largura // 2)
    kernel_y = cv2.getGaussianKernel(altura, altura // 2)
    kernel = kernel_y * kernel_x.T
    kernel = kernel / kernel.max()
    # Inverte: centro=1, bordas = 1-intensidade
    vinheta = 1 - (1 - kernel) * intensidade
    vinheta = np.clip(vinheta, 0.2, 1.0)
    # Retorna em uint8
    return (vinheta * 255).astype(np.uint8)


# ═══════════════════════════════════════════════════════════════════
# GERENCIAMENTO DO ROTEIRO
# ═══════════════════════════════════════════════════════════════════

def carregar_roteiro():
    """Carrega o roteiro do arquivo JSON."""
    with open(ARQUIVO_ROTEIRO, "r", encoding="utf-8") as f:
        return json.load(f)


def detectar_tema(texto, gesto):
    """Detecta o tema baseado no conteudo da fala."""
    texto_lower = texto.lower()

    # Analise de palavras-chave
    if any(palavra in texto_lower for palavra in ["luta", "livre", "liberdade", "direito", "libertas"]):
        return "estadio"  # Energia forte
    elif any(palavra in texto_lower for palavra in ["drama", "ator", "julgamento", "julgar"]):
        return "cidade"  # Reflexao filosofica/urbana
    elif any(palavra in texto_lower for palavra in ["felicidade", "feliz", "relaxado", "curta", "aproveitar"]):
        return "floresta"  # Natureza/calma
    else:
        return "cafe"  # Padrao - ambiente contemporaneo


def mapear_falas_temas(roteiro):
    """Mapeia cada fala ao seu tema correspondente."""
    mapeamento = []

    for i, fala in enumerate(roteiro["falas"]):
        tema = detectar_tema(fala["texto"], fala["gesto"])
        mapeamento.append({
            "indice": i,
            "texto": fala["texto"],
            "gesto": fala["gesto"],
            "tema": tema,
            "nome_tema": PALETAS[tema]["nome"]
        })

    return mapeamento


# ═══════════════════════════════════════════════════════════════════
# GERACAO DE VIDEO
# ═══════════════════════════════════════════════════════════════════

def criar_frame_array(frames):
    """Converte lista de frames OpenCV para formato moviepy."""
    if len(frames) == 0:
        return None

    # Normaliza frames para float
    frames_np = np.array(frames, dtype=np.uint8)

    # Converte BGR para RGB
    frames_rgb = frames_np[..., ::-1]

    return frames_rgb


def gerar_video_backgrounds(duracao_por_fala=5.0):
    """
    Gera video com backgrounds dinamicos para cada fala.

    Args:
        duracao_por_fala: Duracao em segundos de cada background

    Returns:
        caminho do video gerado
    """
    roteiro = carregar_roteiro()
    mapeamento = mapear_falas_temas(roteiro)

    print("=" * 60)
    print("GERADOR DE BACKGROUNDS CINEMATOGRAFICOS")
    print("=" * 60)
    print(f"\nRoteiro carregado: {roteiro['nome']}")
    print(f"Total de falas: {len(roteiro['falas'])}")
    print(f"Duracao por fala: {duracao_por_fala}s")
    print()

    # Lista de frames
    todos_frames = []
    total_frames = int(duracao_por_fala * FPS)

    for item in mapeamento:
        tema = item["tema"]
        print(f"[{item['indice'] + 1}/{len(mapeamento)}] Gerando: {item['nome_tema']}")
        print(f"    Fala: {item['texto'][:50]}...")

        # Gera frames com animacao gradual
        for i in range(total_frames):
            tempo = i / FPS
            frame = gerar_background(tema, LARGURA, ALTURA, tempo)
            todos_frames.append(frame)

    print(f"\nTotal de frames gerados: {len(todos_frames)}")

    # Salva frames como imagens (para debug)
    os.makedirs(PASTA_SAIDA, exist_ok=True)

    for i, frame in enumerate(todos_frames):
        if i % 30 == 0:  # Salva 1 frame por segundo
            caminho_frame = os.path.join(PASTA_SAIDA, f"frame_{i:04d}.png")
            cv2.imwrite(caminho_frame, frame)

    print(f"\nFrames salvos em: {PASTA_SAIDA}")

    # Gera video com moviepy
    import moviepy as mpy

    # Metodo alternativo: gerar video diretamente com OpenCV
    caminho_video = os.path.join(PASTA_SAIDA, "backgrounds_kong.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(caminho_video, fourcc, FPS, (LARGURA, ALTURA))

    for frame in todos_frames:
        out.write(frame)

    out.release()

    print(f"Video gerado: {caminho_video}")
    print("\n" + "=" * 60)
    print("GERACAO CONCLUIDA!")
    print("=" * 60)

    return caminho_video


def mostrar_mapeamento():
    """Mostra o mapeamento de falas para temas."""
    roteiro = carregar_roteiro()
    mapeamento = mapear_falas_temas(roteiro)

    print("\n" + "=" * 60)
    print("MAPEAMENTO DE TEMAS")
    print("=" * 60)

    for item in mapeamento:
        print(f"\n[Fala {item['indice'] + 1}]")
        print(f"  Tema: {item['nome_tema']}")
        print(f"  Texto: {item['texto']}")
        print(f"  Gesto: {item['gesto']}")


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("GORILA BG - Background Cinematografico")
    print("Gerador de backgrounds para video do Kong")
    print("=" * 60)

    # Cria pasta de saida
    os.makedirs(PASTA_SAIDA, exist_ok=True)

    # Mostra mapeamento
    mostrar_mapeamento()

    # Gera videos
    print("\n[INICIANDO GERACAO DE BACKGROUNDS...]\n")

    caminho_video = gerar_video_backgrounds(duracao_por_fala=5.0)

    print(f"""
    ╔══════════════════════════════════════════════════════════════════╗
    ║  RESULTADO                                                       ║
    ╠══════════════════════════════════════════════════════════════════╣
    ║  Video: {caminho_video}
    ║  Pasta de frames: {PASTA_SAIDA}
    ║                                                                  ║
    ║  Use os backgrounds gerados atras do Kong no editor de video   ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)
