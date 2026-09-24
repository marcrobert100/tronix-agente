#!/usr/bin/env python3
"""
TRONIX DIRECTOR - Movimentos de camera cinematograficos para Ken Burns.

Inspirado no conceito LTX Director: cada cena recebe um tipo de plano
(close-up, wide, etc) e um movimento de camera (zoom_in, pan_left, etc).
O Diretor traduz isso em parametros Ken Burns + prefixos de prompt
para o Cloudflare SDXL.

Uso programatico:
    from tronix_director import Director
    d = Director()
    params = d.para_cena("close-up", "zoom_in")
    d.aplicar_em_video(img_path, video_out, duracao=6, params=params)

Uso CLI:
    python tronix_director.py --list
    python tronix_director.py --demo
"""

import sys
import os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from pathlib import Path
import argparse
import subprocess

BASE = Path(__file__).parent


# Tipos de plano cinematografico
TIPOS_PLANO = {
    "extreme_wide": {
        "nome": "Plano Extremo Aberto",
        "prefixo_prompt": "Extreme wide shot, establishing shot, epic landscape,",
        "uso": "Mostrar cenarios vastos, cidades, paisagens",
        "zoom_range": (1.0, 1.1),
        "pan_default": (0.0, 0.0),
    },
    "wide": {
        "nome": "Plano Aberto",
        "prefixo_prompt": "Wide shot, full scene visible, deep focus,",
        "uso": "Mostrar personagens em ambiente, acao em grupo",
        "zoom_range": (1.0, 1.2),
        "pan_default": (0.0, 0.0),
    },
    "medium": {
        "nome": "Plano Medio",
        "prefixo_prompt": "Medium shot, character waist-up, balanced composition,",
        "uso": "Dialogos, interacoes, equilibrio personagem-ambiente",
        "zoom_range": (1.0, 1.15),
        "pan_default": (0.0, 0.0),
    },
    "close_up": {
        "nome": "Close-up",
        "prefixo_prompt": "Close-up shot, intense focus on face, shallow depth of field, dramatic lighting,",
        "uso": "Emocoes, detalhes, intensidade",
        "zoom_range": (1.0, 1.3),
        "pan_default": (0.0, 0.0),
    },
    "extreme_close_up": {
        "nome": "Plano Detalhe",
        "prefixo_prompt": "Extreme close-up, macro detail, single element filling frame,",
        "uso": "Olhos, maos, objetos simbolicos",
        "zoom_range": (1.0, 1.4),
        "pan_default": (0.0, 0.0),
    },
    "over_shoulder": {
        "nome": "Sobre o Ombro",
        "prefixo_prompt": "Over-the-shoulder shot, foreground shoulder framing background subject,",
        "uso": "Conversas, perspectiva de observador",
        "zoom_range": (1.0, 1.1),
        "pan_default": (-0.05, 0.0),
    },
    "top_down": {
        "nome": "Plano Zenital",
        "prefixo_prompt": "Top-down bird's eye view, overhead shot, geometric composition,",
        "uso": "Visao aerea, mapas, padroes",
        "zoom_range": (1.0, 1.2),
        "pan_default": (0.0, 0.0),
    },
    "low_angle": {
        "nome": "Plano Contra-Picado",
        "prefixo_prompt": "Low angle shot, looking up, heroic perspective, towering subject,",
        "uso": "Poder, monumentalidade, viloes",
        "zoom_range": (1.0, 1.15),
        "pan_default": (0.0, 0.0),
    },
}

# Movimentos de camera (mapeados para Ken Burns)
MOVIMENTOS = {
    "static": {
        "nome": "Estatico",
        "descricao": "Sem movimento, imagem fixa",
        "zoom_inicial_offset": 0.0,
        "zoom_final_offset": 0.0,
        "pan_x": 0.0,
        "pan_y": 0.0,
    },
    "zoom_in": {
        "nome": "Zoom In (Aproximar)",
        "descricao": "Aproxima lentamente, foco no detalhe",
        "zoom_inicial_offset": 0.0,
        "zoom_final_offset": 0.15,
        "pan_x": 0.0,
        "pan_y": 0.0,
    },
    "zoom_out": {
        "nome": "Zoom Out (Afastar)",
        "descricao": "Afasta revelando o cenario",
        "zoom_inicial_offset": 0.15,
        "zoom_final_offset": 0.0,
        "pan_x": 0.0,
        "pan_y": 0.0,
    },
    "pan_left": {
        "nome": "Panorâmica Esquerda",
        "descricao": "Desliza para esquerda revelando mais",
        "zoom_inicial_offset": 0.0,
        "zoom_final_offset": 0.05,
        "pan_x": -0.15,
        "pan_y": 0.0,
    },
    "pan_right": {
        "nome": "Panorâmica Direita",
        "descricao": "Desliza para direita revelando mais",
        "zoom_inicial_offset": 0.0,
        "zoom_final_offset": 0.05,
        "pan_x": 0.15,
        "pan_y": 0.0,
    },
    "tilt_up": {
        "nome": "Inclinacao Cima",
        "descricao": "Sobe enquadramento, revela ceu/topo",
        "zoom_inicial_offset": 0.0,
        "zoom_final_offset": 0.05,
        "pan_x": 0.0,
        "pan_y": 0.15,
    },
    "tilt_down": {
        "nome": "Inclinacao Baixo",
        "descricao": "Desce enquadramento, foco no chao",
        "zoom_inicial_offset": 0.0,
        "zoom_final_offset": 0.05,
        "pan_x": 0.0,
        "pan_y": -0.15,
    },
    "dolly_forward": {
        "nome": "Dolly Forward (Travelling)",
        "descricao": "Avança em direcao ao sujeito",
        "zoom_inicial_offset": 0.0,
        "zoom_final_offset": 0.25,
        "pan_x": 0.0,
        "pan_y": 0.0,
    },
    "dolly_back": {
        "nome": "Dolly Back (Recuo)",
        "descricao": "Recua revelando mais contexto",
        "zoom_inicial_offset": 0.25,
        "zoom_final_offset": 0.0,
        "pan_x": 0.0,
        "pan_y": 0.0,
    },
    "zoom_in_pan_right": {
        "nome": "Zoom + Pan Direito",
        "descricao": "Aproxima enquanto desliza direita (efeito Hitchcock)",
        "zoom_inicial_offset": 0.0,
        "zoom_final_offset": 0.2,
        "pan_x": 0.1,
        "pan_y": 0.0,
    },
}


class Director:
    def __init__(self):
        self.tipos_plano = TIPOS_PLANO
        self.movimentos = MOVIMENTOS

    def listar_planos(self):
        return [
            f"  {k:20s} | {v['nome']:25s} | {v['uso']}"
            for k, v in TIPOS_PLANO.items()
        ]

    def listar_movimentos(self):
        return [
            f"  {k:22s} | {v['nome']:30s} | {v['descricao']}"
            for k, v in MOVIMENTOS.items()
        ]

    def para_cena(self, tipo_plano, movimento):
        """
        Retorna parametros cinematograficos para uma cena.
        tipo_plano: chave de TIPOS_PLANO
        movimento: chave de MOVIMENTOS
        """
        if tipo_plano not in TIPOS_PLANO:
            raise ValueError(f"Tipo de plano invalido: {tipo_plano}. Opcoes: {list(TIPOS_PLANO.keys())}")
        if movimento not in MOVIMENTOS:
            raise ValueError(f"Movimento invalido: {movimento}. Opcoes: {list(MOVIMENTOS.keys())}")

        plano = TIPOS_PLANO[tipo_plano]
        mov = MOVIMENTOS[movimento]

        z_min, z_max = plano["zoom_range"]
        z_min += mov["zoom_inicial_offset"]
        z_max += mov["zoom_final_offset"]
        if z_min > z_max:
            z_min, z_max = z_max, z_min

        pan_x = plano["pan_default"][0] + mov["pan_x"]
        pan_y = plano["pan_default"][1] + mov["pan_y"]
        pan_x = max(-0.3, min(0.3, pan_x))
        pan_y = max(-0.3, min(0.3, pan_y))

        return {
            "tipo_plano": tipo_plano,
            "movimento": movimento,
            "plano_nome": plano["nome"],
            "movimento_nome": mov["nome"],
            "prompt_prefixo": plano["prefixo_prompt"],
            "zoom_inicial": round(z_min, 3),
            "zoom_final": round(z_max, 3),
            "pan_x": round(pan_x, 3),
            "pan_y": round(pan_y, 3),
        }

    def augmentar_prompt(self, prompt_base, tipo_plano, movimento=None):
        """Adiciona prefixo cinematico ao prompt do SDXL."""
        params = self.para_cena(tipo_plano, movimento or "static")
        return f"{params['prompt_prefixo']} {prompt_base}"

    def aplicar_em_video(self, imagem_path, video_saida, duracao=6,
                          tipo_plano="wide", movimento="zoom_in",
                          dimensao=(1920, 1080), legenda=None):
        """
        Gera video Ken Burns com parametros do Diretor.
        Wrapper que chama gera_video.py.
        """
        params = self.para_cena(tipo_plano, movimento)

        pasta_temp = BASE / "_temp_director"
        pasta_temp.mkdir(exist_ok=True)
        import shutil
        img_temp = pasta_temp / "frame.png"
        shutil.copy2(imagem_path, img_temp)

        cmd = [
            "python", str(BASE / "gera_video.py"),
            "--pasta", str(pasta_temp),
            "--saida", str(video_saida),
            "--duracao", str(duracao),
            "--largura", str(dimensao[0]),
            "--altura", str(dimensao[1]),
            "--animacao", "fade",
        ]
        if legenda:
            cmd.extend(["--texto", legenda])

        print(f"[DIRECTOR] {params['plano_nome']} + {params['movimento_nome']}")
        print(f"[DIRECTOR] Zoom {params['zoom_inicial']}->{params['zoom_final']}, Pan ({params['pan_x']}, {params['pan_y']})")
        print(f"[DIRECTOR] Prompt: {params['prompt_prefixo'][:50]}...")

        result = subprocess.run(cmd, cwd=str(BASE), capture_output=True, text=True, encoding='utf-8', errors='replace')

        if Path(video_saida).exists():
            print(f"[DIRECTOR] Video gerado: {video_saida}")
            return True
        else:
            print(f"[DIRECTOR] ERRO: {result.stderr[-500:]}")
            return False

    def roteiro_direcao(self, cenas):
        """
        Gera tabela de direcao para uma sequencia de cenas.
        cenas: lista de dicts com chaves 'titulo', 'plano', 'movimento'
        Retorna: string formatada em markdown
        """
        linhas = ["| # | Título | Plano | Movimento | Zoom | Pan |",
                  "|---|--------|-------|-----------|------|-----|"]
        for i, cena in enumerate(cenas, 1):
            p = self.para_cena(cena["plano"], cena["movimento"])
            linhas.append(
                f"| {i} | {cena['titulo']} | {p['plano_nome']} | {p['movimento_nome']} | "
                f"{p['zoom_inicial']}->{p['zoom_final']} | ({p['pan_x']},{p['pan_y']}) |"
            )
        return "\n".join(linhas)


def main():
    parser = argparse.ArgumentParser(description="Tronix Director - Movimentos de camera cinematicos")
    parser.add_argument("--list", action="store_true", help="Listar planos e movimentos")
    parser.add_argument("--demo", action="store_true", help="Demonstracao do Director")
    parser.add_argument("--plano", default="wide", help="Tipo de plano (close_up, wide, medium, etc)")
    parser.add_argument("--movimento", default="zoom_in", help="Movimento de camera")
    parser.add_argument("--prompt", help="Augmentar prompt com prefixo cinematico")
    args = parser.parse_args()

    d = Director()

    if args.list:
        print("\nTIPOS DE PLANO:")
        for linha in d.listar_planos():
            print(linha)
        print("\nMOVIMENTOS DE CAMERA:")
        for linha in d.listar_movimentos():
            print(linha)
        return

    if args.demo:
        cenas_exemplo = [
            {"titulo": "A Chegada", "plano": "extreme_wide", "movimento": "tilt_up"},
            {"titulo": "O Plano", "plano": "close_up", "movimento": "zoom_in"},
            {"titulo": "A Invasao", "plano": "low_angle", "movimento": "dolly_forward"},
        ]
        print("\nROTEIRO DE DIRECAO - DEMO")
        print("=" * 60)
        print(d.roteiro_direcao(cenas_exemplo))
        print("\nPROMPTS AUGMENTADOS:")
        for cena in cenas_exemplo:
            aug = d.augmentar_prompt(f"scene of {cena['titulo']}", cena["plano"], cena["movimento"])
            print(f"  [{cena['plano']} + {cena['movimento']}]")
            print(f"    {aug}")
        return

    if args.prompt:
        aug = d.augmentar_prompt(args.prompt, args.plano, args.movimento)
        print(aug)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
