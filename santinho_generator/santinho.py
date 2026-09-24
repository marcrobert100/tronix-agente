"""
Tronix Santinho Generator - Engine Python
Gera santinhos politicos em alta qualidade (300 DPI) com frente/verso
e grid A4 para grafica.

Equipe Tronix:
  - Tronix-MEDIA: design dos templates
  - Tronix-DEV: logica de renderizacao
  - Tronix-SUPER: pipeline de producao
  - Tronix-DB: persistencia SQLite
"""
from __future__ import annotations

import json
import os
import sys
import math
import sqlite3
import argparse
from pathlib import Path
from datetime import datetime

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm
    HAS_RL = True
except ImportError:
    HAS_RL = False

ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"
FOTOS = ASSETS / "fotos"
OUTPUTS = ROOT / "outputs"
DB_PATH = ROOT / "santinho.db"
MODELOS_PATH = ROOT / "models.json"
MEMORIA_PATH = ROOT.parent / "memoria_tronix.json"

# Cores dos modelos (RGB)
CORES_MODELOS = {
    "classico":            {"c1": (200, 16, 46),  "c2": (26, 26, 26),   "ct": (255, 255, 255)},
    "moderno_minimalista": {"c1": (15, 12, 46),   "c2": (0, 212, 255),  "ct": (255, 255, 255)},
    "premium_executivo":   {"c1": (255, 215, 0),  "c2": (26, 26, 26),   "ct": (255, 255, 255)},
    "colorido_partidario": {"c1": (255, 107, 0),  "c2": (255, 255, 255),"ct": (255, 255, 255)},
    "jovem_dinamico":      {"c1": (123, 44, 191), "c2": (255, 51, 102), "ct": (255, 255, 255)},
    "tradicao_brasileiro": {"c1": (0, 156, 59),   "c2": (0, 39, 118),   "ct": (0, 39, 118)},
    "agro_forte":          {"c1": (139, 69, 19),  "c2": (45, 80, 22),   "ct": (255, 255, 255)},
    "sindical_trabalhador":{"c1": (214, 40, 40),  "c2": (255, 255, 255),"ct": (214, 40, 40)},
    "empresarial_pro":     {"c1": (29, 53, 87),   "c2": (0, 212, 255),  "ct": (255, 255, 255)},
    "fotografico_impacto": {"c1": (255, 215, 0),  "c2": (17, 17, 17),   "ct": (255, 255, 255)},
    "minimalista_horizontal":{"c1": (17, 17, 17), "c2": (0, 0, 0),      "ct": (255, 255, 255)},
    "cristao_familia":     {"c1": (176, 137, 104),"c2": (254, 249, 243),"ct": (93, 64, 55)},
    "tecnologico_inovador":{"c1": (0, 180, 216),  "c2": (0, 29, 61),    "ct": (255, 255, 255)},
    "esporte_juventude":   {"c1": (251, 133, 0),  "c2": (255, 183, 3),  "ct": (255, 255, 255)},
    "diagonal_dinamico":   {"c1": (29, 78, 216),  "c2": (15, 23, 42),   "ct": (255, 255, 255)},
    "retro_vintage":       {"c1": (120, 53, 15),  "c2": (254, 243, 199),"ct": (120, 53, 15)},
    "gradient_suave":      {"c1": (102, 126, 234),"c2": (118, 75, 162), "ct": (255, 255, 255)},
    "black_gold_luxo":     {"c1": (212, 175, 55), "c2": (10, 10, 10),   "ct": (212, 175, 55)},
    "tropical_verao":      {"c1": (12, 74, 110),  "c2": (251, 191, 36), "ct": (12, 74, 110)},
    "civico_municipal":    {"c1": (30, 58, 138),  "c2": (248, 250, 252),"ct": (30, 58, 138)},
}

SIMBOLOS_DISPONIVEIS = ["nenhum", "cruz", "estrela", "coracao", "bandeira", "raio", "mao", "familia", "pomba"]
SIMBOLO_CHAR = {"cruz": "✝", "estrela": "★", "coracao": "♥", "bandeira": "⚑", "raio": "⚡", "mao": "✋", "familia": "♀♂", "pomba": "☮"}
MOLDURAS_DISPONIVEIS = ["quadrada", "redonda", "losango", "hexagonal", "escudo"]
BADGES_DISPONIVEIS = ["nenhum", "mulher", "jovem", "renovacao", "experiencia", "educacao", "saude", "seguranca", "agro", "religioso", "trabalhador", "novo"]
BADGES_TEXTO = {
    "mulher": "♀ MULHER", "jovem": "★ JOVEM", "renovacao": "↻ RENOVACAO",
    "experiencia": "✓ EXPERIENCIA", "educacao": "EDUCACAO", "saude": "+ SAUDE",
    "seguranca": "🛡 SEGURANCA", "agro": "🌱 AGRO", "religioso": "✝ CRISTAO",
    "trabalhador": "⚒ TRABALHADOR", "novo": "★ NOVO"
}
ESTILOS_FOTO = ["normal", "pb", "sepia", "duotone"]

# Dimensoes 300 DPI
DPI = 300
MM_TO_PX = DPI / 25.4
SANTINHO_W_MM = 70
SANTINHO_H_MM = 100
SANTINHO_W_PX = int(SANTINHO_W_MM * MM_TO_PX)
SANTINHO_H_PX = int(SANTINHO_H_MM * MM_TO_PX)


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS candidatos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cargo TEXT,
            partido TEXT,
            numero TEXT,
            cidade TEXT,
            slogan1 TEXT,
            slogan2 TEXT,
            whatsapp TEXT,
            instagram TEXT,
            site TEXT,
            coligacao TEXT,
            propostas TEXT,
            foto_path TEXT,
            modelo TEXT,
            cor_primaria TEXT,
            cor_secundaria TEXT,
            created_at TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS geracoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidato_id INTEGER,
            quantidade INTEGER,
            copias_por_pagina INTEGER,
            com_verso INTEGER,
            arquivo_saida TEXT,
            created_at TEXT,
            FOREIGN KEY (candidato_id) REFERENCES candidatos(id)
        )
    """)
    con.commit()
    con.close()


def get_font(size: int, bold: bool = False):
    """Tenta carregar uma fonte do sistema, fallback para default."""
    candidates = []
    if bold:
        candidates += [
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/calibrib.ttf",
            "C:/Windows/Fonts/segoeuib.ttf",
        ]
    else:
        candidates += [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/calibri.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
        ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def truncate_text(text: str, font, max_width: int, draw: ImageDraw.ImageDraw) -> str:
    """Trunca texto com reticencias se passar da largura."""
    if not text:
        return ""
    if draw.textlength(text, font=font) <= max_width:
        return text
    while text and draw.textlength(text + "...", font=font) > max_width:
        text = text[:-1]
    return text + "..."


def wrap_text(text: str, font, max_width: int, draw: ImageDraw.ImageDraw) -> list[str]:
    """Quebra texto em varias linhas."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        if draw.textlength(test, font=font) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def carregar_foto(path: str | None, target_w: int, target_h: int, estilo: str = "normal") -> Image.Image:
    """Carrega e ajusta foto para o tamanho alvo, com filtros opcionais."""
    if not path or not os.path.exists(path):
        img = Image.new("RGB", (target_w, target_h), (230, 230, 230))
        d = ImageDraw.Draw(img)
        d.text((target_w // 2 - 30, target_h // 2 - 10), "FOTO", fill=(180, 180, 180))
        return aplicar_estilo_foto(img, estilo)
    try:
        foto = Image.open(path).convert("RGB")
        ratio = max(target_w / foto.width, target_h / foto.height)
        nw, nh = int(foto.width * ratio), int(foto.height * ratio)
        foto = foto.resize((nw, nh), Image.LANCZOS)
        x = (nw - target_w) // 2
        y = (nh - target_h) // 2
        foto = foto.crop((x, y, x + target_w, y + target_h))
        return aplicar_estilo_foto(foto, estilo)
    except Exception as e:
        print(f"[WARN] Erro ao carregar foto: {e}")
        img = Image.new("RGB", (target_w, target_h), (230, 230, 230))
        return aplicar_estilo_foto(img, estilo)


def aplicar_estilo_foto(foto: Image.Image, estilo: str) -> Image.Image:
    """Aplica filtro de estilo a foto."""
    if estilo == "pb":
        return ImageOps.grayscale(foto).convert("RGB")
    elif estilo == "sepia":
        gray = ImageOps.grayscale(foto)
        sepia = Image.new("RGB", gray.size, (112, 66, 20))
        sepia.paste(gray, mask=gray)
        return sepia
    elif estilo == "duotone":
        gray = ImageOps.grayscale(foto)
        duotone = Image.new("RGB", gray.size, (60, 120, 200))
        duotone.paste(gray, mask=gray)
        return duotone
    return foto


def aplicar_moldura_foto(foto: Image.Image, moldura: str, borda_cor: tuple = (200, 16, 46), borda_px: int = 12) -> Image.Image:
    """Aplica moldura a foto (redonda, losango, hexagonal, escudo)."""
    if moldura == "quadrada" or moldura == "nenhum" or not moldura:
        # Apenas borda
        w, h = foto.size
        nova = Image.new("RGB", (w + 2 * borda_px, h + 2 * borda_px), borda_cor)
        nova.paste(foto, (borda_px, borda_px))
        return nova
    elif moldura == "redonda":
        w, h = foto.size
        size = min(w, h)
        # Centralizar
        if w != h:
            square = Image.new("RGB", (size, size), (0, 0, 0))
            square.paste(foto, ((size - w) // 2, (size - h) // 2))
            foto = square
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
        # Borda circular
        borda = Image.new("RGB", (size + 2 * borda_px, size + 2 * borda_px), borda_cor)
        mask_borda = Image.new("L", borda.size, 0)
        ImageDraw.Draw(mask_borda).ellipse((0, 0, borda.size[0], borda.size[1]), fill=255)
        result = Image.new("RGBA", borda.size, (0, 0, 0, 0))
        result.paste(borda, mask=mask_borda)
        # Colar foto circular dentro
        foto_circ = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        foto_circ.paste(foto, (0, 0), mask)
        result.paste(foto_circ, (borda_px, borda_px), foto_circ)
        return result.convert("RGB")
    elif moldura == "losango":
        w, h = foto.size
        mask = Image.new("L", (w, h), 0)
        ImageDraw.Draw(mask).polygon([(w//2, 0), (w, h//2), (w//2, h), (0, h//2)], fill=255)
        result = Image.new("RGB", (w + 2 * borda_px, h + 2 * borda_px), borda_cor)
        mask_b = Image.new("L", result.size, 0)
        ImageDraw.Draw(mask_b).polygon([(result.size[0]//2, 0), (result.size[0], result.size[1]//2), (result.size[0]//2, result.size[1]), (0, result.size[1]//2)], fill=255)
        result.putalpha(mask_b)
        foto_d = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        foto_d.paste(foto, (0, 0), mask)
        result.paste(foto_d, (borda_px, borda_px), foto_d)
        return result.convert("RGB")
    elif moldura == "hexagonal":
        w, h = foto.size
        mask = Image.new("L", (w, h), 0)
        ImageDraw.Draw(mask).polygon([
            (int(w*0.25), 0), (int(w*0.75), 0),
            (w, h//2), (int(w*0.75), h), (int(w*0.25), h), (0, h//2)
        ], fill=255)
        result = Image.new("RGB", (w + 2 * borda_px, h + 2 * borda_px), borda_cor)
        mask_b = Image.new("L", result.size, 0)
        bw, bh = result.size
        ImageDraw.Draw(mask_b).polygon([
            (int(bw*0.25), 0), (int(bw*0.75), 0),
            (bw, bh//2), (int(bw*0.75), bh), (int(bw*0.25), bh), (0, bh//2)
        ], fill=255)
        result.putalpha(mask_b)
        foto_d = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        foto_d.paste(foto, (0, 0), mask)
        result.paste(foto_d, (borda_px, borda_px), foto_d)
        return result.convert("RGB")
    else:  # escudo ou outros = quadrada com borda
        w, h = foto.size
        nova = Image.new("RGB", (w + 2 * borda_px, h + 2 * borda_px), borda_cor)
        nova.paste(foto, (borda_px, borda_px))
        return nova


def render_acessorios(draw: ImageDraw.ImageDraw, img: Image.Image, dados: dict, cores: dict) -> None:
    """Renderiza acessorios sobre o santinho (modifica a imagem in-place)."""
    acc = dados.get("acessorios") or {}
    c1 = cores.get("c1", (200, 16, 46))
    W, H = img.size

    f_selo = get_font(20, bold=True)
    f_badge = get_font(22, bold=True)
    f_simbolo = get_font(360, bold=True)
    f_proposta = get_font(28, bold=True)
    f_vice = get_font(20, bold=True)
    f_zona = get_font(20, bold=True)

    # Selo Justica Eleitoral
    if acc.get("selo_je"):
        selo_text = "JE"
        bbox = draw.textbbox((0, 0), selo_text, font=f_selo)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.rectangle([W - tw - 24, 12, W - 12, 12 + th + 10], fill=(0, 0, 0))
        draw.text((W - tw - 18, 17), selo_text, fill=(255, 255, 255), font=f_selo)

    # Badge
    badge = acc.get("badge", "nenhum")
    if badge and badge != "nenhum" and badge in BADGES_TEXTO:
        texto = BADGES_TEXTO[badge]
        bbox = draw.textbbox((0, 0), texto, font=f_badge)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        # Pill no topo esquerdo
        draw.rounded_rectangle([10, 12, 10 + tw + 20, 12 + th + 10], radius=15, fill=c1)
        draw.text((20, 17), texto, fill=(255, 255, 255), font=f_badge)

    # Simbolo de fundo
    simbolo = acc.get("simbolo", "nenhum")
    if simbolo and simbolo != "nenhum" and simbolo in SIMBOLO_CHAR:
        char = SIMBOLO_CHAR[simbolo]
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.text((W // 2 - 180, H // 2 - 200), char, fill=(*c1, 30), font=f_simbolo)
        img.paste(Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"))

    # Proposta destaque
    proposta = acc.get("proposta_destaque", "")
    if proposta:
        bbox = draw.textbbox((0, 0), proposta.upper(), font=f_proposta)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        y_box = H - 700
        draw.rectangle([20, y_box, W - 20, y_box + th + 14], fill=c1)
        txt_w = draw.textlength(proposta.upper(), font=f_proposta)
        draw.text((20 + ((W - 40 - txt_w) // 2), y_box + 7), proposta.upper(), fill=(255, 255, 255), font=f_proposta)

    # Vice
    vice = acc.get("vice", "")
    if vice:
        texto = f"VICE: {vice.upper()}"
        bbox = draw.textbbox((0, 0), texto, font=f_vice)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        y_box = H - 56
        draw.rectangle([10, y_box, 10 + tw + 16, y_box + th + 8], fill=(0, 0, 0))
        draw.text((18, y_box + 4), texto, fill=(255, 255, 255), font=f_vice)

    # Zona/ secao
    zona = acc.get("zona_secao", "")
    if zona:
        texto = f"ZONA {zona}"
        bbox = draw.textbbox((0, 0), texto, font=f_zona)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        y_box = H - 56
        draw.rectangle([W - tw - 26, y_box, W - 10, y_box + th + 8], fill=(255, 255, 255), outline=(180, 180, 180))
        draw.text((W - tw - 18, y_box + 4), texto, fill=(40, 40, 40), font=f_zona)

    # Faixa de cor inferior
    if acc.get("faixa_cor", True):
        draw.rectangle([0, H - 24, W, H], fill=c1)


def render_frente(dados: dict, cores: dict | None = None) -> Image.Image:
    """Renderiza a frente do santinho."""
    modelo = dados.get("modelo", "classico")
    cores = cores or CORES_MODELOS.get(modelo, CORES_MODELOS["classico"])
    c1 = cores.get("c1", (200, 16, 46))
    c2 = cores.get("c2", (26, 26, 26))
    ct = cores.get("ct", (255, 255, 255))

    img = Image.new("RGB", (SANTINHO_W_PX, SANTINHO_H_PX), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    nome = dados.get("nome", "NOME DO CANDIDATO").upper()
    cargo = dados.get("cargo", "Vereador(a)").upper()
    partido = dados.get("partido", "PARTIDO")
    numero = dados.get("numero", "00000")
    cidade = dados.get("cidade", "")
    foto_path = dados.get("foto_path")

    f_h1 = get_font(60, bold=True)
    f_nome = get_font(48, bold=True)
    f_cargo = get_font(28, bold=True)
    f_num = get_font(180, bold=True)
    f_part = get_font(36, bold=True)
    f_cid = get_font(26)
    f_peq = get_font(22)

    if modelo == "classico":
        # Faixa vermelha no topo
        draw.rectangle([0, 0, SANTINHO_W_PX, 60], fill=c1)
        cargo_text = truncate_text(cargo, f_cargo, SANTINHO_W_PX - 30, draw)
        bbox = draw.textbbox((0, 0), cargo_text, font=f_cargo)
        tw = bbox[2] - bbox[0]
        draw.text(((SANTINHO_W_PX - tw) // 2, 15), cargo_text, fill=ct, font=f_cargo)
        # Foto
        foto = carregar_foto(foto_path, int(120 * MM_TO_PX), int(150 * MM_TO_PX))
        fx, fy = (SANTINHO_W_PX - foto.width) // 2, 90
        draw.rectangle([fx - 6, fy - 6, fx + foto.width + 6, fy + foto.height + 6], fill=c1)
        img.paste(foto, (fx, fy))
        # Texto
        draw.text((SANTINHO_W_PX // 2, fy + foto.height + 30), "CANDIDATO A", fill=(80, 80, 80), font=f_cargo, anchor="mm")
        nome_text = truncate_text(nome, f_nome, SANTINHO_W_PX - 40, draw)
        for i, linha in enumerate(wrap_text(nome_text, f_nome, SANTINHO_W_PX - 40, draw)[:2]):
            draw.text((SANTINHO_W_PX // 2, fy + foto.height + 90 + i * 50), linha, fill=(20, 20, 20), font=f_nome, anchor="mm")
        # Numero gigante
        bbox = draw.textbbox((0, 0), numero, font=f_num)
        tw = bbox[2] - bbox[0]
        draw.text(((SANTINHO_W_PX - tw) // 2, SANTINHO_H_PX - 280), numero, fill=c1, font=f_num)
        # Partido
        draw.text((SANTINHO_W_PX // 2, SANTINHO_H_PX - 70), partido, fill=(40, 40, 40), font=f_part, anchor="mm")
        # Cidade
        draw.text((SANTINHO_W_PX // 2, SANTINHO_H_PX - 30), cidade, fill=(120, 120, 120), font=f_cid, anchor="mm")

    elif modelo == "moderno_minimalista":
        draw.rectangle([0, 0, SANTINHO_W_PX, SANTINHO_H_PX], fill=c1)
        # Linha de destaque
        draw.rectangle([20, 80, 100, 90], fill=c2)
        # Numero tag
        draw.rectangle([20, 110, 200, 175], fill=c2)
        bbox = draw.textbbox((0, 0), numero, font=f_h1)
        tw = bbox[2] - bbox[0]
        draw.text((20 + (180 - tw) // 2, 120), numero, fill=c1, font=f_h1)
        # Nome
        nome_text = truncate_text(nome, f_nome, SANTINHO_W_PX - 60, draw)
        for i, linha in enumerate(wrap_text(nome_text, f_nome, SANTINHO_W_PX - 60, draw)[:3]):
            draw.text((30, 220 + i * 55), linha, fill=ct, font=f_nome)
        # Cargo
        draw.text((30, 220 + 3 * 55 + 20), cargo, fill=ct, font=f_cargo)
        # Foto
        foto = carregar_foto(foto_path, int(50 * MM_TO_PX), int(50 * MM_TO_PX))
        img.paste(foto, (20, 480))
        # Partido
        draw.text((30, SANTINHO_H_PX - 90), partido, fill=ct, font=f_part)
        draw.text((30, SANTINHO_H_PX - 50), cidade, fill=ct, font=f_cid)

    elif modelo == "premium_executivo":
        for y in range(SANTINHO_H_PX):
            ratio = y / SANTINHO_H_PX
            r = int(26 + (10 - 26) * ratio)
            g = int(26 + (10 - 26) * ratio)
            b = int(26 + (10 - 26) * ratio)
            draw.line([(0, y), (SANTINHO_W_PX, y)], fill=(r, g, b))
        # Linhas douradas
        for y in [80, SANTINHO_H_PX - 100]:
            for x in range(80, SANTINHO_W_PX - 80):
                alpha = 1 - abs(x - SANTINHO_W_PX // 2) / (SANTINHO_W_PX // 2)
                r = int(c1[0] * alpha)
                g = int(c1[1] * alpha)
                b = int(c1[2] * alpha)
                draw.point((x, y), fill=(r, g, b))
        # Nome
        nome_text = truncate_text(nome, f_nome, SANTINHO_W_PX - 60, draw)
        draw.text((SANTINHO_W_PX // 2, 100), nome_text, fill=c1, font=f_nome, anchor="mm")
        # Cargo
        draw.text((SANTINHO_W_PX // 2, 160), cargo, fill=(200, 200, 200), font=f_peq, anchor="mm")
        # Foto com moldura
        foto = carregar_foto(foto_path, int(110 * MM_TO_PX), int(140 * MM_TO_PX))
        fx, fy = (SANTINHO_W_PX - foto.width) // 2, 200
        draw.rectangle([fx - 8, fy - 8, fx + foto.width + 8, fy + foto.height + 8], outline=c1, width=6)
        img.paste(foto, (fx, fy))
        # Numero box
        nb_w, nb_h = 300, 100
        nb_x, nb_y = (SANTINHO_W_PX - nb_w) // 2, SANTINHO_H_PX - 280
        draw.rectangle([nb_x, nb_y, nb_x + nb_w, nb_y + nb_h], fill=c1)
        bbox = draw.textbbox((0, 0), numero, font=f_h1)
        tw = bbox[2] - bbox[0]
        draw.text((nb_x + (nb_w - tw) // 2, nb_y + 10), numero, fill=c1, font=f_h1)
        # Partido
        draw.text((SANTINHO_W_PX // 2, SANTINHO_H_PX - 130), partido, fill=ct, font=f_part, anchor="mm")

    elif modelo == "colorido_partidario":
        draw.rectangle([0, 0, SANTINHO_W_PX, SANTINHO_H_PX], fill=c1)
        # Header branco
        draw.rectangle([0, 0, SANTINHO_W_PX, 60], fill=(255, 255, 255))
        cargo_text = truncate_text(cargo, f_cargo, SANTINHO_W_PX - 30, draw)
        bbox = draw.textbbox((0, 0), cargo_text, font=f_cargo)
        tw = bbox[2] - bbox[0]
        draw.text(((SANTINHO_W_PX - tw) // 2, 18), cargo_text, fill=c1, font=f_cargo)
        # Nome
        nome_text = truncate_text(nome, f_nome, SANTINHO_W_PX - 40, draw)
        for i, linha in enumerate(wrap_text(nome_text, f_nome, SANTINHO_W_PX - 40, draw)[:2]):
            draw.text((SANTINHO_W_PX // 2, 100 + i * 55), linha, fill=ct, font=f_nome, anchor="mm")
        # Foto
        foto = carregar_foto(foto_path, int(100 * MM_TO_PX), int(125 * MM_TO_PX))
        fx, fy = (SANTINHO_W_PX - foto.width) // 2, 250
        draw.rectangle([fx - 6, fy - 6, fx + foto.width + 6, fy + foto.height + 6], fill=(255, 255, 255))
        img.paste(foto, (fx, fy))
        # Numero gigante com sombra
        bbox = draw.textbbox((0, 0), numero, font=f_num)
        tw = bbox[2] - bbox[0]
        nx, ny = (SANTINHO_W_PX - tw) // 2, 700
        # sombra
        draw.text((nx + 8, ny + 8), numero, fill=(0, 0, 0), font=f_num)
        draw.text((nx, ny), numero, fill=ct, font=f_num)
        # Partido
        draw.text((SANTINHO_W_PX // 2, SANTINHO_H_PX - 60), partido, fill=ct, font=f_part, anchor="mm")

    elif modelo == "fotografico_impacto":
        # Foto full bleed
        foto = carregar_foto(foto_path, SANTINHO_W_PX, SANTINHO_H_PX)
        img.paste(foto, (0, 0))
        # Overlay gradient
        overlay = Image.new("RGBA", (SANTINHO_W_PX, SANTINHO_H_PX), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        for y in range(SANTINHO_H_PX):
            if y > SANTINHO_H_PX * 0.5:
                alpha = int(255 * (y - SANTINHO_H_PX * 0.5) / (SANTINHO_H_PX * 0.5))
                od.line([(0, y), (SANTINHO_W_PX, y)], fill=(0, 0, 0, alpha))
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)
        # Texto
        bbox = draw.textbbox((0, 0), numero, font=f_num)
        tw = bbox[2] - bbox[0]
        draw.text(((SANTINHO_W_PX - tw) // 2, SANTINHO_H_PX - 350), numero, fill=c1, font=f_num)
        nome_text = truncate_text(nome, f_nome, SANTINHO_W_PX - 60, draw)
        for i, linha in enumerate(wrap_text(nome_text, f_nome, SANTINHO_W_PX - 60, draw)[:2]):
            draw.text((40, SANTINHO_H_PX - 230 + i * 55), linha, fill=(255, 255, 255), font=f_nome)
        draw.text((40, SANTINHO_H_PX - 100), cargo, fill=(255, 255, 255), font=f_cargo)

    else:
        # Generico para modelos nao implementados
        draw.rectangle([0, 0, SANTINHO_W_PX, SANTINHO_H_PX], fill=c1)
        draw.rectangle([0, 0, SANTINHO_W_PX, 80], fill=c2)
        cargo_text = truncate_text(cargo, f_cargo, SANTINHO_W_PX - 30, draw)
        bbox = draw.textbbox((0, 0), cargo_text, font=f_cargo)
        tw = bbox[2] - bbox[0]
        draw.text(((SANTINHO_W_PX - tw) // 2, 25), cargo_text, fill=ct, font=f_cargo)
        nome_text = truncate_text(nome, f_nome, SANTINHO_W_PX - 40, draw)
        for i, linha in enumerate(wrap_text(nome_text, f_nome, SANTINHO_W_PX - 40, draw)[:2]):
            draw.text((SANTINHO_W_PX // 2, 130 + i * 55), linha, fill=ct, font=f_nome, anchor="mm")
        foto = carregar_foto(foto_path, int(110 * MM_TO_PX), int(140 * MM_TO_PX), dados.get("estilo_foto", "normal"))
        fx, fy = (SANTINHO_W_PX - foto.width) // 2, 280
        img.paste(foto, (fx, fy))
        bbox = draw.textbbox((0, 0), numero, font=f_num)
        tw = bbox[2] - bbox[0]
        draw.text(((SANTINHO_W_PX - tw) // 2, SANTINHO_H_PX - 250), numero, fill=(255, 255, 255), font=f_num)
        draw.text((SANTINHO_W_PX // 2, SANTINHO_H_PX - 50), partido, fill=ct, font=f_part, anchor="mm")

    # Aplicar acessorios (sobrescreve em cima)
    render_acessorios(draw, img, dados, cores)
    return img


def render_verso(dados: dict, cores: dict | None = None) -> Image.Image:
    """Renderiza o verso do santinho."""
    modelo = dados.get("modelo", "classico")
    cores = cores or CORES_MODELOS.get(modelo, CORES_MODELOS["classico"])
    c1 = cores.get("c1", (200, 16, 46))

    img = Image.new("RGB", (SANTINHO_W_PX, SANTINHO_H_PX), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    f_header = get_font(36, bold=True)
    f_nome = get_font(38, bold=True)
    f_cargo = get_font(26)
    f_section = get_font(28, bold=True)
    f_prop = get_font(26)
    f_contato = get_font(22)
    f_peq = get_font(20)

    # Header
    draw.rectangle([0, 0, SANTINHO_W_PX, 50], fill=c1)
    cargo = dados.get("cargo", "Vereador(a)").upper()
    cidade = dados.get("cidade", "")
    header_text = truncate_text(f"{cargo} - {cidade}", f_header, SANTINHO_W_PX - 40, draw)
    bbox = draw.textbbox((0, 0), header_text, font=f_header)
    tw = bbox[2] - bbox[0]
    draw.text(((SANTINHO_W_PX - tw) // 2, 8), header_text, fill=(255, 255, 255), font=f_header)

    y = 80
    # Nome
    nome = dados.get("nome", "").upper()
    draw.text((SANTINHO_W_PX // 2, y), nome, fill=(20, 20, 20), font=f_nome, anchor="mm")
    y += 40
    # Numero / partido
    numero = dados.get("numero", "00000")
    partido = dados.get("partido", "")
    draw.text((SANTINHO_W_PX // 2, y), f"Numero {numero} - {partido}", fill=(80, 80, 80), font=f_cargo, anchor="mm")
    y += 50

    # Secao propostas
    draw.text((20, y), "MINHAS PROPOSTAS", fill=c1, font=f_section)
    y += 40
    draw.line([(20, y), (SANTINHO_W_PX - 20, y)], fill=(220, 220, 220), width=2)
    y += 15

    propostas = dados.get("propostas", "").split("\n")
    propostas = [p.strip() for p in propostas if p.strip()][:6]
    for prop in propostas:
        # Check
        draw.text((25, y), "✓", fill=c1, font=f_section)
        # Texto com wrap
        lines = wrap_text(prop, f_prop, SANTINHO_W_PX - 80, draw)
        for li, line in enumerate(lines):
            draw.text((55, y + li * 30), line, fill=(30, 30, 30), font=f_prop)
        y += max(35, len(lines) * 30)
        if y > SANTINHO_H_PX - 200:
            break

    # Contato
    y = SANTINHO_H_PX - 130
    draw.line([(20, y), (SANTINHO_W_PX - 20, y)], fill=(220, 220, 220), width=2)
    y += 15
    contato_parts = []
    if dados.get("whatsapp"): contato_parts.append(f"WhatsApp: {dados['whatsapp']}")
    if dados.get("instagram"): contato_parts.append(dados["instagram"])
    if dados.get("site"): contato_parts.append(dados["site"])
    contato = " · ".join(contato_parts)
    contato_lines = wrap_text(contato, f_contato, SANTINHO_W_PX - 40, draw)[:2]
    for line in contato_lines:
        draw.text((SANTINHO_W_PX // 2, y), line, fill=(80, 80, 80), font=f_contato, anchor="mm")
        y += 28

    # Coligacao
    if dados.get("coligacao"):
        draw.text((SANTINHO_W_PX // 2, SANTINHO_H_PX - 20), dados["coligacao"], fill=(150, 150, 150), font=f_peq, anchor="mm")

    return img


def gerar_pdf_lote(dados: dict, quantidade: int, copias_pagina: int = 9,
                   com_verso: bool = True, arquivo_saida: str | None = None) -> str:
    """Gera PDF com grade A4 de santinhos."""
    if not HAS_PIL or not HAS_RL:
        print("[ERRO] Dependencias faltando. Instale: pip install pillow reportlab")
        sys.exit(1)

    OUTPUTS.mkdir(parents=True, exist_ok=True)
    if not arquivo_saida:
        slug = (dados.get("nome") or "santinho").lower().replace(" ", "_")
        arquivo_saida = str(OUTPUTS / f"santinho_{slug}_x{quantidade}.pdf")

    cores = CORES_MODELOS.get(dados.get("modelo", "classico"))

    # Renderizar frente uma vez
    print(f"[1/3] Renderizando frente do modelo '{dados.get('modelo')}'...")
    frente = render_frente(dados, cores)
    print(f"[2/3] Renderizando verso...")
    verso = render_verso(dados, cores) if com_verso else None

    # Calcular grid
    if copias_pagina == 9: cols, rows = 3, 3
    elif copias_pagina == 6: cols, rows = 3, 2
    elif copias_pagina == 8: cols, rows = 4, 2
    elif copias_pagina == 10: cols, rows = 5, 2
    else: cols, rows = 3, 3

    total_paginas = math.ceil(quantidade / copias_pagina)

    c = canvas.Canvas(arquivo_saida, pagesize=A4)
    page_w, page_h = A4
    margin = 5 * mm
    gap = 2 * mm
    cell_w = (page_w - 2 * margin - (cols - 1) * gap) / cols
    cell_h = (page_h - 2 * margin - (rows - 1) * gap) / rows
    aspect = cell_h / cell_w

    # Salvar imagens temporarias
    tmp_frente = OUTPUTS / "_tmp_frente.png"
    tmp_verso = OUTPUTS / "_tmp_verso.png"
    frente.save(tmp_frente, "PNG", dpi=(DPI, DPI))
    if verso:
        verso.save(tmp_verso, "PNG", dpi=(DPI, DPI))

    print(f"[3/3] Compondo {total_paginas} paginas A4 ({quantidade} santinhos)...")

    restante = quantidade
    for pagina in range(total_paginas):
        n_na_pagina = min(copias_pagina, restante)
        for idx in range(n_na_pagina):
            col = idx % cols
            row = idx // cols
            x = margin + col * (cell_w + gap)
            y = page_h - margin - (row + 1) * cell_h - row * gap
            c.drawImage(str(tmp_frente), x, y, cell_w, cell_h, preserveAspectRatio=True)
        c.showPage()
        restante -= n_na_pagina

    # Verso
    if com_verso and verso:
        restante = quantidade
        for pagina in range(total_paginas):
            n_na_pagina = min(copias_pagina, restante)
            for idx in range(n_na_pagina):
                col = idx % cols
                row = idx // cols
                x = margin + col * (cell_w + gap)
                y = page_h - margin - (row + 1) * cell_h - row * gap
                c.drawImage(str(tmp_verso), x, y, cell_w, cell_h, preserveAspectRatio=True)
            c.showPage()
            restante -= n_na_pagina

    c.save()
    tmp_frente.unlink(missing_ok=True)
    tmp_verso.unlink(missing_ok=True)

    # Salvar no DB
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        INSERT INTO candidatos (nome, cargo, partido, numero, cidade, slogan1, slogan2, whatsapp, instagram, site, coligacao, propostas, foto_path, modelo, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (dados.get("nome"), dados.get("cargo"), dados.get("partido"), dados.get("numero"),
          dados.get("cidade"), dados.get("slogan1"), dados.get("slogan2"), dados.get("whatsapp"),
          dados.get("instagram"), dados.get("site"), dados.get("coligacao"), dados.get("propostas"),
          dados.get("foto_path"), dados.get("modelo"), datetime.now().isoformat()))
    cid = cur.lastrowid
    cur.execute("""
        INSERT INTO geracoes (candidato_id, quantidade, copias_por_pagina, com_verso, arquivo_saida, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (cid, quantidade, copias_pagina, int(com_verso), arquivo_saida, datetime.now().isoformat()))
    con.commit()
    con.close()

    print(f"\n[OK] PDF gerado: {arquivo_saida}")
    print(f"[OK] {quantidade} santinhos em {total_paginas} pagina(s) A4")
    return arquivo_saida


def registrar_memoria(acao: str):
    """Registra acao na memoria do Tronix."""
    if not MEMORIA_PATH.exists():
        return
    try:
        data = json.loads(MEMORIA_PATH.read_text(encoding="utf-8"))
        last_id = max((a.get("id", 0) for a in data.get("last_actions", [])), default=0)
        data.setdefault("last_actions", []).append({
            "id": last_id + 1,
            "agente": "Tronix-SANTINHO",
            "acao": acao,
            "timestamp": datetime.now().strftime("%Y-%m-%d")
        })
        MEMORIA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"[WARN] Falha ao registrar na memoria: {e}")


def main():
    parser = argparse.ArgumentParser(description="Tronix Santinho Generator - Lote")
    parser.add_argument("--modelo", default="classico", help="ID do modelo (classico, moderno_minimalista, etc)")
    parser.add_argument("--nome", help="Nome do candidato")
    parser.add_argument("--cargo", default="Vereador(a)", help="Cargo pretendido")
    parser.add_argument("--partido", default="PARTIDO", help="Partido")
    parser.add_argument("--numero", help="Numero na urna")
    parser.add_argument("--cidade", default="", help="Cidade - UF")
    parser.add_argument("--slogan1", default="", help="Slogan linha 1")
    parser.add_argument("--slogan2", default="", help="Slogan linha 2")
    parser.add_argument("--whatsapp", default="", help="WhatsApp")
    parser.add_argument("--instagram", default="", help="Instagram")
    parser.add_argument("--site", default="", help="Site")
    parser.add_argument("--coligacao", default="", help="Nome da coligacao")
    parser.add_argument("--propostas", default="", help="Propostas (uma por linha)")
    parser.add_argument("--foto", default=None, help="Caminho da foto")
    parser.add_argument("--quantidade", type=int, default=100, help="Quantidade de santinhos")
    parser.add_argument("--copias", type=int, default=9, help="Copias por pagina A4 (6, 8, 9 ou 10)")
    parser.add_argument("--verso", action="store_true", default=True, help="Incluir verso")
    parser.add_argument("--sem-verso", action="store_false", dest="verso", help="Sem verso")
    parser.add_argument("--saida", default=None, help="Arquivo de saida")
    parser.add_argument("--init-db", action="store_true", help="Apenas inicializar banco")
    parser.add_argument("--listar", action="store_true", help="Listar modelos disponiveis")
    args = parser.parse_args()

    init_db()

    if args.init_db:
        print("[OK] Banco inicializado em", DB_PATH)
        return

    if args.listar:
        with open(MODELOS_PATH, encoding="utf-8") as f:
            modelos = json.load(f)["modelos"]
        print("\nModelos disponiveis:")
        for m in modelos:
            print(f"  {m['id']:25s} {m['nome']:30s} [{m['categoria']}]")
        return

    if not args.nome or not args.numero:
        parser.print_help()
        sys.exit(1)

    dados = {
        "modelo": args.modelo,
        "nome": args.nome,
        "cargo": args.cargo,
        "partido": args.partido,
        "numero": args.numero,
        "cidade": args.cidade,
        "slogan1": args.slogan1,
        "slogan2": args.slogan2,
        "whatsapp": args.whatsapp,
        "instagram": args.instagram,
        "site": args.site,
        "coligacao": args.coligacao,
        "propostas": args.propostas,
        "foto_path": args.foto,
    }

    arquivo = gerar_pdf_lote(dados, args.quantidade, args.copias, args.verso, args.saida)
    registrar_memoria(f"GERADO: santinho {args.nome} (modelo {args.modelo}, {args.quantidade} copias) -> {Path(arquivo).name}")


if __name__ == "__main__":
    main()
