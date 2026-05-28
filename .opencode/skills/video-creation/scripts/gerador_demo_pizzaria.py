"""
Gerador de Vídeos de Demonstração para Pizzarias
===============================================
Script Python para criar vídeos automáticos de demo de sistemas de pizzaria.
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class Cena:
    nome: str
    duracao: int
    imagem: str
    transicao: str = "fade"


@dataclass
class ConfigVideo:
    titulo: str
    fps: int = 30
    resolucao: tuple[int, int] = (1920, 1080)
    output: str = "demo_pizzaria.mp4"
    audio: Optional[str] = None


class GeradorVideoPizzaria:
    def __init__(self, pasta_imagens: str = "./screenshots"):
        self.pasta_imagens = Path(pasta_imagens)
        self.pasta_imagens.mkdir(exist_ok=True)
        self.cenas: list[Cena] = []
        self.config = None

    def adicionar_cena(
        self,
        nome: str,
        imagem: str,
        duracao: int = 3,
        transicao: str = "fade"
    ):
        """Adiciona uma cena ao vídeo."""
        self.cenas.append(Cena(nome, duracao, imagem, transicao))

    def gerar_demo_basico(self):
        """Gera sequência básica de demo para pizzaria."""
        self.cenas = [
            Cena("Login", "01_login.png", 3, "fade"),
            Cena("Cardápio", "02_cardapio.png", 4, "fade"),
            Cena("Detalhes Pizza", "03_pizza.png", 3, "fade"),
            Cena("Carrinho", "04_carrinho.png", 3, "fade"),
            Cena("Checkout", "05_checkout.png", 4, "fade"),
            Cena("Pedido Confirmado", "06_sucesso.png", 5, "fade"),
        ]

    def criar_frames(self, config: ConfigVideo):
        """Cria frames com transições entre as cenas."""
        output_dir = self.pasta_imagens / "frames"
        output_dir.mkdir(exist_ok=True)

        frame_idx = 0

        for i, cena in enumerate(self.cenas):
            if not Path(cena.imagem).exists():
                print(f"⚠️ Imagem não encontrada: {cena.imagem}")
                continue

            frames_por_cena = cena.duracao * config.fps

            for f in range(frames_por_cena):
                progress = f / frames_por_cena
                frame_name = f"frame_{frame_idx:04d}.png"
                subprocess.run([
                    "ffmpeg", "-y",
                    "-loop", "1",
                    "-i", cena.imagem,
                    "-vf", f"fade=t=out:st={progress-0.1}:d=0.1" if progress > 0.9 else "null",
                    "-t", str(1/config.fps),
                    "-r", str(config.fps),
                    str(output_dir / frame_name)
                ], capture_output=True)
                frame_idx += 1

        return output_dir

    def compilar_video(self, config: ConfigVideo):
        """Compila todas as imagens em vídeo usando FFmpeg."""
        output_dir = self.pasta_imagens / "frames"

        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(config.fps),
            "-i", str(output_dir / "frame_%04d.png"),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-r", str(config.fps),
            "-s", f"{config.resolucao[0]}x{config.resolucao[1]}",
        ]

        if config.audio:
            cmd.extend(["-i", config.audio, "-shortest"])

        cmd.append(config.output)

        subprocess.run(cmd, check=True)
        print(f"✅ Vídeo gerado: {config.output}")

    def executar(self, config: Optional[ConfigVideo] = None):
        """Executa todo o processo de geração do vídeo."""
        if config is None:
            config = ConfigVideo(titulo="Demo Pizzaria")

        if not self.cenas:
            self.gerar_demo_basico()

        print("🎬 Gerando frames...")
        self.criar_frames(config)

        print("🎥 Compilando vídeo...")
        self.compilar_video(config)

        print("✅ Demo de pizzaria concluído!")


def gerar_video_demo(
    titulo: str,
    imagens: list[str],
    output: str = "demo.mp4",
    fps: int = 30
):
    """Função principal para gerar vídeo de demo."""
    gerador = GeradorVideoPizzaria()

    for i, img in enumerate(imagens):
        gerador.adicionar_cena(
            nome=f"Cena {i+1}",
            imagem=img,
            duracao=3
        )

    config = ConfigVideo(titulo=titulo, fps=fps, output=output)
    gerador.executar(config)


if __name__ == "__main__":
    print("🎬 Gerador de Vídeos para Pizzaria")
    print("=" * 40)

    gerar_video_demo(
        titulo="Sistema de Delivery",
        imagens=[
            "screenshots/login.png",
            "screenshots/cardapio.png",
            "screenshots/pedido.png",
        ],
        output="demo_pizzaria.mp4"
    )