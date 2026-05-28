"""
Tronix Simple Video - Gerador de Videos Simples
Cria videos animacao via Pillow + FFmpeg (sem API externa)
Autor: Marcos Roberto / Tronix
"""

import os
import subprocess
import sys
from pathlib import Path

# Tenta importar pillow, instala se necessario
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("[TRONIX] Instalando Pillow...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow", "-q"])
    from PIL import Image, ImageDraw, ImageFont


class TronixSimpleVideo:
    """Cria videos simples com animacoes em Python."""

    def __init__(self, pasta_saida="tronix_output"):
        self.pasta_saida = Path(pasta_saida)
        self.pasta_saida.mkdir(parents=True, exist_ok=True)
        self.frames = []

    def criar_frame(self, texto="TRONIX", cor_bg=(10, 10, 30),
                    cor_texto=(0, 255, 255), tamanho=(640, 360)):
        """Cria um frame com texto centralizado."""
        img = Image.new("RGB", tamanho, cor_bg)
        draw = ImageDraw.Draw(img)

        # Tenta fonte padrao se arial no existir
        try:
            fonte = ImageFont.truetype("arial.ttf", 60)
        except:
            fonte = ImageFont.load_default()

        # Centraliza texto
        bbox = draw.textbbox((0, 0), texto, font=fonte)
        largura_texto = bbox[2] - bbox[0]
        altura_texto = bbox[3] - bbox[1]
        x = (tamanho[0] - largura_texto) // 2
        y = (tamanho[1] - altura_texto) // 2

        draw.text((x, y), texto, fill=cor_texto, font=fonte)
        return img

    def animacao_texto(self, texto="TRONIX", duracao=3, fps=30,
                       cor_bg=(10, 10, 30), cor_texto=(0, 255, 255)):
        """Cria animacao de texto com efeito neon pulsante."""
        total_frames = duracao * fps
        print(f"[TRONIX] Gerando {total_frames} frames...")

        for i in range(total_frames):
            # Efeito pulsante
            intensidade = int(128 + 127 * ((i % fps) / fps))
            cor = (0, intensidade, intensidade)

            frame = self.criar_frame(
                texto=texto,
                cor_bg=cor_bg,
                cor_texto=cor,
                tamanho=(640, 360)
            )
            self.frames.append(frame)

            if (i + 1) % 30 == 0:
                print(f"  Progresso: {i + 1}/{total_frames}")

        return self

    def animacao_logo(self, nome="TRONIX", duracao=3):
        """Cria animacao do logo com degrade de cores."""
        total_frames = duracao * 30
        print(f"[TRONIX] Gerando logo animado...")

        for i in range(total_frames):
            # Ciclo de cores RGB
            r = int(128 + 127 * ((i % 90) / 90))
            g = int(128 + 127 * (((i + 30) % 90) / 90))
            b = int(128 + 127 * (((i + 60) % 90) / 90))
            cor = (r, g, b)

            # Fundo com gradiente
            frame = Image.new("RGB", (640, 360), (5, 5, 15))
            draw = ImageDraw.Draw(frame)

            # Linha decorativa
            y_linha = int(180 + 80 * ((i % 30) / 30))
            draw.rectangle([0, y_linha, 640, y_linha + 2], fill=cor)

            # Texto
            try:
                fonte = ImageFont.truetype("arial.ttf", 72)
            except:
                fonte = ImageFont.load_default()

            bbox = draw.textbbox((0, 0), nome, font=fonte)
            lw = bbox[2] - bbox[0]
            lh = bbox[3] - bbox[1]
            x = (640 - lw) // 2
            y = (360 - lh) // 2
            draw.text((x, y), nome, fill=cor, font=fonte)

            self.frames.append(frame)

            if (i + 1) % 30 == 0:
                print(f"  Progresso: {i + 1}/{total_frames}")

        return self

    def animacao_paisagem(self, duracao=5):
        """Cria paisagem futurista simples."""
        total_frames = duracao * 30
        print(f"[TRONIX] Gerando paisagem cyberpunk...")

        for i in range(total_frames):
            frame = Image.new("RGB", (640, 360), (5, 5, 20))
            draw = ImageDraw.Draw(frame)

            # Ceu com estrelas
            import random
            random.seed(i)
            for _ in range(50):
                sx = random.randint(0, 640)
                sy = random.randint(0, 200)
                br = random.randint(100, 255)
                draw.point((sx, sy), fill=(br, br, br))

            # Predios
            cores_predios = [
                (20, 20, 60),
                (30, 10, 50),
                (10, 30, 50)
            ]
            predios = [
                (50, 200, 100, 360),
                (120, 180, 180, 360),
                (200, 150, 250, 360),
                (280, 190, 340, 360),
                (380, 170, 440, 360),
                (470, 210, 530, 360),
                (540, 160, 600, 360),
            ]
            for j, p in enumerate(predios):
                cor = cores_predios[j % len(cores_predios)]
                draw.rectangle(p, fill=cor)

            # Janelas iluminadas
            random.seed(i + 100)
            for _ in range(30):
                px = random.randint(50, 600)
                py = random.randint(150, 350)
                wcor = random.choice([(255, 255, 0), (0, 255, 255), (255, 100, 0)])
                draw.rectangle([px, py, px + 4, py + 6], fill=wcor)

            # Linha de neon no chao
            y_neon = int(355 + 3 * ((i % 30) / 30))
            draw.rectangle([0, y_neon, 640, y_neon + 1], fill=(0, 255, 255))

            # Lua
            draw.ellipse([500, 20, 560, 80], fill=(200, 200, 150))

            self.frames.append(frame)

            if (i + 1) % 30 == 0:
                print(f"  Progresso: {i + 1}/{total_frames}")

        return self

    def salvar_gif(self, nome="tronix_video.gif", loop=0):
        """Salva como GIF animado."""
        caminho = self.pasta_saida / nome
        if not self.frames:
            print("[ERRO] Nenhum frame gerado")
            return None

        print(f"[TRONIX] Salvando GIF: {caminho}")
        self.frames[0].save(
            caminho,
            save_all=True,
            append_images=self.frames[1:],
            duration=int(1000 / 30),
            loop=loop
        )
        print(f"[OK] GIF salvo: {caminho}")
        return str(caminho)

    def salvar_mp4(self, nome="tronix_video.mp4", fps=30):
        """Salva como MP4 usando FFmpeg."""
        caminho_gif = self.pasta_saida / "temp_anim.gif"
        caminho_mp4 = self.pasta_saida / nome

        if not self.frames:
            print("[ERRO] Nenhum frame gerado")
            return None

        # Primeiro salva como GIF
        print("[TRONIX] Convertendo para MP4...")
        self.frames[0].save(
            caminho_gif,
            save_all=True,
            append_images=self.frames[1:],
            duration=int(1000 / 30),
            loop=0
        )

        # Converte com FFmpeg
        try:
            cmd = [
                "ffmpeg", "-y", "-framerate", str(fps),
                "-i", str(caminho_gif),
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-crf", "23", "-preset", "fast",
                str(caminho_mp4)
            ]
            resultado = subprocess.run(
                cmd, capture_output=True, text=True, timeout=120
            )

            # Limpa GIF temp
            caminho_gif.unlink(missing_ok=True)

            if resultado.returncode == 0:
                print(f"[OK] MP4 salvo: {caminho_mp4}")
                return str(caminho_mp4)
            else:
                print(f"[AVISO] FFmpeg nao encontrado. GIF salvo como alternativa.")
                return str(caminho_gif)

        except FileNotFoundError:
            print("[AVISO] FFmpeg nao instalado. Salvando como GIF.")
            return str(caminho_gif)
        except Exception as e:
            print(f"[ERRO] {e}")
            return str(caminho_gif)

    def limpar_frames(self):
        """Limpa frames da memoria."""
        self.frames = []


# ==================== MENU INTERATIVO ====================

def menu():
    print("\n" + "=" * 50)
    print("  TRONIX SIMPLE VIDEO - Gerador de Videos")
    print("=" * 50)
    print("  1 - Animacao de Texto Neon")
    print("  2 - Animacao de Logo")
    print("  3 - Paisagem Cyberpunk")
    print("  4 - Todos os efeitos (GIF)")
    print("  0 - Sair")
    print("=" * 50)


def main():
    while True:
        menu()
        escolha = input("Escolha uma opcao: ").strip()

        video = TronixSimpleVideo()

        if escolha == "1":
            texto = input("Texto (padrao: TRONIX): ").strip() or "TRONIX"
            duracao = int(input("Duracao em segundos (padrao: 3): ").strip() or "3")
            video.animacao_texto(texto, duracao=duracao)
            video.salvar_gif(f"tronix_texto_{int(os.times().elapsed * 100) % 10000}.gif")

        elif escolha == "2":
            nome = input("Nome (padrao: TRONIX): ").strip() or "TRONIX"
            duracao = int(input("Duracao (padrao: 3): ").strip() or "3")
            video.animacao_logo(nome, duracao=duracao)
            video.salvar_gif(f"tronix_logo_{int(os.times().elapsed * 100) % 10000}.gif")

        elif escolha == "3":
            duracao = int(input("Duracao (padrao: 5): ").strip() or "5")
            video.animacao_paisagem(duracao=duracao)
            video.salvar_gif(f"tronix_paisagem_{int(os.times().elapsed * 100) % 10000}.gif")

        elif escolha == "4":
            print("\nGerando todos os efeitos...")
            # Texto
            video.animacao_texto("TRONIX", duracao=2)
            # Logo
            video.animacao_logo("TRONIX", duracao=2)
            # Paisagem
            video.animacao_paisagem(duracao=3)
            video.salvar_gif(f"tronix_completo.gif")
            video.limpar_frames()

        elif escolha == "0":
            print("Adeus!")
            break

        else:
            print("Opcao invalida!")

        input("\nPressione ENTER para continuar...")


if __name__ == "__main__":
    # Se passar argumento, executa diretamente
    if len(sys.argv) > 1:
        opcao = sys.argv[1]
        video = TronixSimpleVideo()

        if opcao == "texto":
            texto = sys.argv[2] if len(sys.argv) > 2 else "TRONIX"
            video.animacao_texto(texto, duracao=3)
            video.salvar_gif()
        elif opcao == "logo":
            video.animacao_logo("TRONIX", duracao=3)
            video.salvar_gif("tronix_logo.gif")
        elif opcao == "paisagem":
            video.animacao_paisagem(duracao=5)
            video.salvar_gif("tronix_paisagem.gif")
        elif opcao == "demo":
            print("Gerando demo completo...")
            video.animacao_texto("TRONIX", duracao=2)
            video.animacao_logo("TRONIX", duracao=2)
            video.animacao_paisagem(duracao=3)
            video.salvar_gif("tronix_demo.gif")
        else:
            print("Uso: python tronix_simple_video.py [texto|logo|paisagem|demo]")
    else:
        main()
