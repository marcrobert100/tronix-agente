#!/usr/bin/env python3
"""Gerador do pacote Amazon do ebook ERVAS — InfoEngine.

Produz, na pasta do Desktop 'ERVAS-Amazon':
- 00-CAPA-ERVAS.png          (capa frontal 6x9pol @ 300 DPI)
- ERVAS-Indicacoes-e-Usos.epub  (formato Amazon/KDP)
- ERVAS-Indicacoes-e-Usos.pdf   (print A4, via Playwright)
- ERVAS-Indicacoes-e-Usos.html  (ebook digital interativo)
- designer/                     (gerador de capas)
- LEIA-ME-AMAZON.txt             (passo a passo de publicação)

Uso: python tools/gerar_pacote_amazon.py
"""

from __future__ import annotations

import html
import os
import shutil
import textwrap
import zipfile
from pathlib import Path

from criar_ervas import (
    AUTOR, MARCA, LOCAL, YOUTUBE_NOME, YOUTUBE_URL, EMAIL,
    INTRO_PARAGRAFOS, FINAL_PARAGRAFOS,
    ERVAS_PARA, BANHOS, FUNCAO_ENERGETICA,
    USO_MEDICINAL, INDICACOES, SIGNOS,
)

RAIZ = Path(__file__).resolve().parent.parent
DESKTOP = Path(os.path.join(os.environ.get("USERPROFILE", str(Path.home())), "Desktop"))
DESTINO = DESKTOP / "ERVAS-Amazon"

W, H = 1800, 2700  # 6x9in @ 300 DPI

E = html.escape


FONT_DIRS = [
    Path(r"C:\Windows\Fonts"),
    Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "Fonts",
]
FONT_CANDIDATOS = {
    "serif": ["Georgia.ttf", "georgia.ttf", "timesbd.ttf", "DejaVuSerif-Bold.ttf"],
    "serif_i": ["Georgia Italic.ttf", "georgiai.ttf", "timesi.ttf", "DejaVuSerif-Italic.ttf"],
    "serif_bi": ["Georgia Bold Italic.ttf", "georgiaz.ttf", "timesbi.ttf", "DejaVuSerif-BoldItalic.ttf"],
    "sans": ["arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf"],
    "sans_i": ["ariali.ttf", "Arial Italic.ttf", "DejaVuSans-Oblique.ttf"],
}


def caminho_fonte(nome: str) -> Path:
    for c in FONT_CANDIDATOS[nome]:
        for d in FONT_DIRS:
            p = d / c
            if p.exists():
                return p
    raise FileNotFoundError(f"Fonte {nome} não encontrada")


def fontes():
    """Localiza fontes do Windows com fallback DejaVu."""
    from PIL import ImageFont
    return {nome: ImageFont.truetype(str(caminho_fonte(nome)), size=40) for nome in FONT_CANDIDATOS}


def desenhar_capa(path: Path) -> None:
    """Capa frontal 1800x2700 em verde profundo + dourado, com a marca.

    Salva PNG (EPUB), TIFF 300dpi (print KDP) e JPG q95 (capa digital).
    """
    import math
    from PIL import Image, ImageDraw, ImageFont, ImageFilter

    img = Image.new("RGB", (W, H))
    dr = ImageDraw.Draw(img)

    # ---- fundo radial (verde profundo -> quase preto nas bordas) ----
    cx, cy = W // 2, H // 2
    max_r = int(math.hypot(W, H) / 2) + 1
    for r in range(max_r, 0, -4):
        t = r / max_r
        cor = (
            int(22 + (10 - 22) * t),
            int(60 + (32 - 60) * t),
            int(42 + (20 - 42) * t),
        )
        dr.ellipse([cx - r, cy - r, cx + r, cy + r], fill=cor)
    # vignette suave extra
    for i in range(12):
        t = i / 12
        dr.rectangle([0, 0, W, int(H * t / 10)], fill=(0, 0, 0))
    dr.rectangle([0, 0, W, H], outline=(0, 0, 0), width=4)

    ORO = (218, 184, 80)
    ORO_SUAVE = (166, 126, 42)
    CREME = (250, 241, 214)
    VERDE_CLARO = (126, 182, 150)
    VERDE_FOLHA = (88, 138, 104)

    # ---- textura de folhas sutis no fundo ----
    import random
    rnd = random.Random(42)
    folha = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fdr = ImageDraw.Draw(folha)
    for _ in range(260):
        x, y = rnd.randint(0, W), rnd.randint(0, H)
        a = rnd.randint(4, 12)
        c = rnd.choice([(30, 66, 48, a), (24, 54, 40, a), (38, 80, 56, a)])
        fdr.ellipse([x - 4, y - 2, x + 4, y + 2], fill=c)
    folha = folha.filter(ImageFilter.GaussianBlur(2))
    img = Image.alpha_composite(img.convert("RGBA"), folha).convert("RGB")
    dr = ImageDraw.Draw(img)

    # ---- moldura dourada dupla com cantoneiras ----
    m = 55
    dr.rectangle([m, m, W - m, H - m], outline=ORO_SUAVE, width=3)
    dr.rectangle([m + 16, m + 16, W - m - 16, H - m - 16], outline=ORO_SUAVE, width=1)
    # cantoneiras
    g = 9
    for (fx, fy, sdx, sdy) in [(m, m, 1, 1), (W - m, m, -1, 1), (m, H - m, 1, -1), (W - m, H - m, -1, -1)]:
        dr.line([fx - sdx * g, fy, fx + sdx * g * 4, fy], fill=ORO, width=3)
        dr.line([fx, fy - sdy * g, fx, fy + sdy * g * 4], fill=ORO, width=3)
        dr.ellipse([fx - 8, fy - 8, fx + 8, fy + 8], outline=ORO, width=2)

    # ---- guirlanda de folhas (canto inferior) ----
    def folha_ornamento(x, y, ang, tam=18, cor=VERDE_FOLHA):
        pts = []
        for k in range(5):
            kk = k / 4
            px = x - tam * (1 - kk)
            py = y - tam * 0.45 * math.sin(math.pi * kk)
            px, py = px * math.cos(ang) - py * math.sin(ang), px * math.sin(ang) + py * math.cos(ang)
            pts.append((x + px, y + py))
        dr.line(pts, fill=cor, width=2)

    def guirlanda(cx0, cy0, dir_x):
        for i in range(14):
            x = cx0 + dir_x * i * 34
            y = cy0 + 14 * math.sin(i * 0.9) + i * 3
            folha_ornamento(x, y, dir_x * math.radians(30 + i * 7), tam=20 + (i % 3) * 4)
            dr.ellipse([x - 3, y - 3, x + 3, y + 3], fill=ORO_SUAVE)

    guirlanda(W - 320, H - 330, 1)
    guirlanda(320, H - 330, -1)

    f = fontes()
    cx = W // 2

    def centro(txt, font, y, fill=CREME, spacing=0):
        if spacing:
            chars = list(txt)
            widths = [dr.textlength(c, font=font) for c in chars]
            total = sum(widths) + spacing * (len(chars) - 1)
            x = cx - total / 2
            for c, wch in zip(chars, widths):
                dr.text((x, y), c, font=font, fill=fill)
                x += wch + spacing
        else:
            tw = dr.textlength(txt, font=font)
            dr.text((cx - tw / 2, y), txt, font=font, fill=fill)

    # ---- selo superior ----
    badge = "GUIA ESOTÉRICO · NATURAL · COMPLETO"
    bw = dr.textlength(badge, font=f["sans"])
    bw = max(bw, 430)
    y0 = 185
    dr.rounded_rectangle([cx - bw / 2 - 28, y0 - 18, cx + bw / 2 + 28, y0 + 36], radius=26, outline=ORO, width=3)
    centro(badge, f["sans"], y0, fill=ORO)

    # ---- estrela de 8 pontas + brilho ----
    cy_est, r = 560, 50
    pts = []
    for i in range(8):
        ang = math.radians(-90 + i * 45)
        rr = r if i % 2 == 0 else r * 0.44
        pts.append((cx + rr * math.cos(ang), cy_est + rr * math.sin(ang)))
    dr.polygon(pts, fill=ORO)
    for a in range(360):
        ang = math.radians(a)
        x = cx + (r + 34) * math.cos(ang)
        y = cy_est + (r + 34) * math.sin(ang)
        if 0 <= x < W and 0 <= y < H:
            dr.point((x, y), fill=ORO_SUAVE)

    # ---- título ----
    f_tit = ImageFont.truetype(str(caminho_fonte("serif_bi")), size=340)
    centro("ERVAS", f_tit, 760, fill=CREME, spacing=18)

    # brilho no título (desenha levemente deslocado atrás)
    tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    tdr = ImageDraw.Draw(tmp)
    tw = 0
    chars = list("ERVAS")
    for c in chars:
        tw += tdr.textlength(c, font=f_tit)
    tw += 18 * (len(chars) - 1)
    x = cx - tw / 2
    for c in chars:
        tdr.text((x, 760), c, font=f_tit, fill=(0, 0, 0, 0))
        x += tdr.textlength(c, font=f_tit) + 18
    img = Image.alpha_composite(img.convert("RGBA"), tmp.filter(ImageFilter.GaussianBlur(10))).convert("RGB")
    dr = ImageDraw.Draw(img)
    centro("ERVAS", f_tit, 760, fill=CREME, spacing=18)

    # ---- subtítulo ----
    centro("Indicações e Usos", f["serif_i"], 1170, fill=ORO)
    dr.line([cx - 190, 1295, cx + 190, 1295], fill=ORO_SUAVE, width=3)

    # ---- descrição ----
    centro("As ervas e suas propriedades energéticas, místicas e", f["serif_i"], 1370, fill=VERDE_CLARO)
    centro("medicinais — do cultivo ao uso no dia a dia.", f["serif_i"], 1418, fill=VERDE_CLARO)

    # ---- autor + marca ----
    centro(MARCA.upper(), f["sans"], 1940, fill=ORO)
    centro("por MARCOS ROBERTO", f["sans"], 2025, fill=CREME)
    centro(LOCAL, f["sans"], 2090, fill=VERDE_CLARO)

    # ---- contato ----
    dr.line([cx - 260, 2260, cx + 260, 2260], fill=(70, 105, 85), width=2)
    centro("YouTube: " + YOUTUBE_NOME, f["sans"], 2310, fill=CREME)
    centro(EMAIL, f["sans"], 2370, fill=CREME)

    # ---- rodapé (selo da marca) ----
    dr.ellipse([cx - 22, 2475, cx + 22, 2519], outline=ORO_SUAVE, width=2)
    dr.polygon(
        [(cx, 2484), (cx + 5, 2498), (cx, 2511), (cx - 5, 2498)],
        fill=ORO,
    )

    base = path.with_name(path.stem)
    png = path
    img.save(str(png), "PNG")
    print(f"[capa] PNG  OK  {png}")
    tiff = base.with_suffix(".tiff")
    img.save(str(tiff), "TIFF", compression="tiff_lzw", dpi=(300, 300))
    print(f"[capa] TIFF OK  {tiff}")
    jpg = base.with_suffix(".jpg")
    img.save(str(jpg), "JPEG", quality=95, dpi=(300, 300))
    print(f"[capa] JPG  OK  {jpg}")


# --------------------------------------------------------------------------
# EPUB
# --------------------------------------------------------------------------

CSS = """\
body{font-family:Georgia,'Times New Roman',serif;line-height:1.6;color:#2c2518;background:#fff;margin:0;padding:0}
h1{font-family:Georgia,serif;color:#1e4d33}
h2{color:#1e4d33;border-bottom:2px solid #b8860b;padding-bottom:6px;margin:1.2em 0 .4em}
h3{color:#3f7a56;margin:1em 0 .3em}
.capa{text-align:center;page-break-after:always;padding-top:14%}
.capa h1{font-size:4em;color:#0a2417;letter-spacing:.08em;margin:0}
.capa .sub{font-style:italic;font-size:1.8em;color:#b8860b;margin:.2em 0 1em}
.capa .marca{font-size:1.1em;color:#1e4d33}
.capa .local{font-size:.85em;color:#6b5f45}
.capa img{width:100%;max-width:420px;margin:1em 0}
.contra{margin-top:.5em;padding:0;text-align:center;font-size:.8em;color:#6b5f45}
p{margin:.5em 0;text-align:justify}
.portrait{font-style:italic;color:#1e4d33;margin:0}
.chips span{display:inline-block;background:#e7efdd;color:#1e4d33;border:1px solid #cfe0bd;border-radius:10px;padding:2px 8px;margin:2px;font-size:.85em}
table{border-collapse:collapse;width:100%;font-size:.9em}
td{border-bottom:1px solid #e0d3b0;padding:6px 8px;vertical-align:top}
td.nome{font-weight:bold;color:#1e4d33;white-space:nowrap}
.simbolo{float:left;font-size:1.6em;color:#b8860b;margin-right:10px}
.cap{border-bottom:2px solid #b8860b;padding-bottom:4px;font-variant:small-caps;letter-spacing:.12em}
a{color:#1e4d33}
.aviso{font-style:italic;font-size:.85em;color:#6b5f45;border-top:1px solid #b8860b;padding-top:8px;margin-top:1.5em}
"""


def xhtml_pagina(titulo: str, corpo: str) -> str:
    return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="pt-BR" xml:lang="pt-BR">
<head><title>{E(titulo)}</title><link rel="stylesheet" type="text/css" href="style.css"/></head>
<body>{corpo}</body>
</html>"""


def gerar_epub(destino_epub: Path, capa_png: Path) -> None:
    # cada página: (aid, titulo, html)
    paginas: list[tuple[str, str, str]] = []

    def add(aid: str, titulo: str, html_corpo: str) -> None:
        paginas.append((aid, titulo, html_corpo))

    add("cover", "Capa", xhtml_pagina("Capa", f"""
<div class="capa">
  <p style="font-size:.8em;letter-spacing:.3em;color:#b8860b">GUIA ESOTÉRICO · NATURAL · COMPLETO</p>
  <h1>ERVAS</h1>
  <p class="sub">Indicações e Usos</p>
  <img src="cover.png" alt="Capa do livro ERVAS"/>
  <p class="marca">{E(MARCA)}</p>
  <p class="local">{E(LOCAL)}</p>
  <p class="local">{E(YOUTUBE_NOME)} · {E(EMAIL)}</p>
</div>
"""))

    corpo = "".join(f"<p>{E(p)}</p>" for p in INTRO_PARAGRAFOS)
    add("intro", "O Poder das Ervas", f"<h2>O Poder das Ervas</h2>{corpo}")

    cards = "".join(
        f"<h3>{E(k)}</h3><p class='chips'>{''.join(f'<span>{E(c.strip())}</span>' for c in v.split(','))}</p>"
        for k, v in ERVAS_PARA
    )
    add("ervaspara", "Ervas Para…", f"<h2>Ervas Para…</h2>{cards}")

    banhos = "".join(f"<h3>{E(k)}</h3><p><em>Misture:</em> {E(v)}</p>" for k, v in BANHOS)
    add("banhos", "Banhos de Ervas", f"<h2>Banhos de Ervas Para…</h2>{banhos}")

    energia = "".join(f"<h3>{E(k)}</h3><p>{E(v)}</p>" for k, v in FUNCAO_ENERGETICA)
    add("energia", "Função Energética", f"<h2>Nome da Planta e Sua Função Energética</h2>{energia}")

    add("uso_ini", "O Uso das Ervas e Vegetais", f"<h2 class='cap'>O Uso das Ervas e Vegetais</h2>{corpo}")
    for i in range(0, len(USO_MEDICINAL), 4):
        chunk = USO_MEDICINAL[i : i + 4]
        corpo_chunk = "".join(
            f"<section><h2>{E(nome)}</h2><p class='portrait'>{E(latin)}</p><p>{E(texto)}</p></section>"
            for nome, latin, texto in chunk
        )
        add(f"uso{i}", USO_MEDICINAL[i][0], corpo_chunk)

    linhas = "".join(f"<tr><td class='nome'>{E(k)}</td><td>{E(v)}</td></tr>" for k, v in INDICACOES)
    add("indicacoes", "Indicações das Ervas", f"<h2>Indicações das Ervas</h2><table>{linhas}</table>")

    signos = "".join(
        f"<p><span class='simbolo'>{'♈♉♊♋♌♍♎♏♐♑♒♓'[i]}</span><strong>{E(k)}</strong> — {E(v)}</p>"
        for i, (k, v) in enumerate(SIGNOS)
    )
    add("signos", "Ervas dos Signos", f"<h2>Ervas dos Signos</h2>{signos}")

    add("sobre", "Sobre o Autor", f"""
<h2>Sobre o Autor</h2>
<p>Olá! Eu sou {E(AUTOR)}, o <strong>{E(MARCA)}</strong> de {E(LOCAL.split(' — ')[0])}. Apaixonado pela natureza e pelos saberes populares, percorro as matas do agreste alagoano coletando, estudando e preservando o conhecimento tradicional sobre plantas, ervas e seus usos.</p>
<p>Meu trabalho une ciência, cultura e espiritualidade — sempre com respeito à floresta e às pessoas que guardam esses segredos. Este guia é fruto dessa caminhada.</p>
<p style="margin-top:.6em">📺 <strong>YouTube:</strong> <a href="{YOUTUBE_URL}">{E(YOUTUBE_NOME)}</a></p>
<p>✉️ <strong>E-mail:</strong> <a href="mailto:{EMAIL}">{E(EMAIL)}</a></p>
<p style="text-align:center;font-style:italic;color:#b8860b">"Cada erva tem uma história. Cada mata, um segredo."</p>
""")

    final = "".join(f"<p>{E(p)}</p>" for p in FINAL_PARAGRAFOS)
    add("final", "Para Finalizar", f"""
<h2>Para Finalizar</h2>
{final}
<p class="aviso">Aviso: este guia tem caráter informativo e cultural. As receitas e indicações não substituem orientação médica. Em caso de doença, procure um profissional de saúde.<br/>
© {E(AUTOR)} — {E(MARCA)}</p>
""")

    # sumário (após todos os títulos conhecidos)
    nav_lista = [(aid, titulo) for aid, titulo, _ in paginas]
    itens_sumario = "".join(
        f'<p><a href="{aid}.xhtml">{i}. {E(t)}</a></p>'
        for i, (aid, t) in enumerate(nav_lista, 1)
    )
    add("sumario", "Sumário", f"<h2>Sumário</h2>{itens_sumario}")

    # reordena: cover, sumario, resto
    paginas_ordenadas = [paginas[0]] + [paginas[-1]] + paginas[1:-1]

    manifest_itens = []
    for aid, _titulo, _html in paginas_ordenadas:
        manifest_itens.append(f'<item id="{aid}" href="{aid}.xhtml" media-type="application/xhtml+xml"/>')
    manifest_itens.append('<item id="style" href="style.css" media-type="text/css"/>')
    manifest_itens.append('<item id="cover-img" href="cover.png" media-type="image/png"/>')
    manifest = "\n".join(manifest_itens)

    spine_itens = "".join(f'<itemref idref="{aid}"/>' for aid, _t, _h in paginas_ordenadas)
    nav_xhtml = "".join(
        f'<li><a href="{aid}.xhtml">{E(t)}</a></li>' for aid, t, _h in paginas_ordenadas
    )

    opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="pt-BR">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
  <dc:identifier id="bookid">urn:uuid:ervas-2026</dc:identifier>
  <dc:title>ERVAS — Indicações e Usos</dc:title>
  <dc:creator>{AUTOR} ({MARCA})</dc:creator>
  <dc:language>pt-BR</dc:language>
  <dc:description>Guia esotérico, energético e medicinal das ervas.</dc:description>
  <meta property="dcterms:modified">2026-08-15T00:00:00Z</meta>
  <meta name="cover" content="cover-img"/>
</metadata>
<manifest>{manifest}</manifest>
<spine>{spine_itens}</spine>
</package>"""

    ncx = f"""<?xml version="1.0" encoding="utf-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
<head><meta name="dtb:uid" content="urn:uuid:ervas"/><meta name="dtb:depth" content="1"/></head>
<docTitle><text>ERVAS — Indicações e Usos</text></docTitle>
<navMap>
{''.join(f'<navPoint id="{aid}" playOrder="{i}"><navLabel><text>{E(t)}</text></navLabel><content src="{aid}.xhtml"/></navPoint>' for i, (aid, t, _h) in enumerate(paginas_ordenadas, 1))}
</navMap>
</ncx>"""

    nav_doc = f"""<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="pt-BR" xml:lang="pt-BR">
<head><title>Sumário</title><link rel="stylesheet" type="text/css" href="style.css"/></head>
<body><nav epub:type="toc" id="toc"><h2>Sumário</h2><ol>{nav_xhtml}</ol></nav></body></html>"""

    container = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>"""

    with zipfile.ZipFile(str(destino_epub), "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", container)
        z.writestr("OEBPS/content.opf", opf)
        z.writestr("OEBPS/toc.ncx", ncx)
        z.writestr("OEBPS/nav.xhtml", nav_doc)
        z.writestr("OEBPS/style.css", CSS)
        z.write(str(capa_png), "OEBPS/cover.png")
        for aid, _t, html_corpo in paginas_ordenadas:
            z.writestr(f"OEBPS/{aid}.xhtml", html_corpo)
    print(f"[epub] OK  {destino_epub}")


# --------------------------------------------------------------------------
# PRÉVIA / AMOSTRA
# --------------------------------------------------------------------------

def gerar_preview(destino_html: Path, capa_png: Path) -> None:
    """Amostra gratuita em HTML: capa + sumário + intro + 5 ervas + final."""
    capa_b64 = "data:image/png;base64," + __import__("base64").b64encode(capa_png.read_bytes()).decode()

    ervas_amostra = USO_MEDICINAL[:5]
    cards = "".join(
        f"<section class='erva'><h2>{E(nome)}</h2><p class='latin'>{E(latin)}</p><p>{E(texto)}</p></section>"
        for nome, latin, texto in ervas_amostra
    )

    banhos = "".join(f"<h3>{E(k)}</h3><p><em>Misture:</em> {E(v)}</p>" for k, v in BANHOS)

    intro = "".join(f"<p>{E(p)}</p>" for p in INTRO_PARAGRAFOS)
    final = "".join(f"<p>{E(p)}</p>" for p in FINAL_PARAGRAFOS)

    total_paginas = len(USO_MEDICINAL) + 8
    html_doc = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>ERVAS — Amostra Gratuita</title>
<style>
:root{{--verde:#1e4d33;--verde-c:#3f7a56;--ouro:#b8860b;--creme:#faf1d6}}
*{{box-sizing:border-box}}
body{{font-family:Georgia,'Times New Roman',serif;color:#2c2518;background:#f4efe2;margin:0;line-height:1.7}}
main{{max-width:760px;margin:0 auto;background:#fff;padding:0 34px 60px;box-shadow:0 0 24px rgba(0,0,0,.12)}}
.banner{{background:linear-gradient(160deg,var(--verde),#0a2417);color:var(--creme);text-align:center;padding:26px 0;margin-bottom:8px;border-bottom:4px solid var(--ouro)}}
.banner h1{{margin:0;letter-spacing:.25em;font-size:1.7em}}
.banner p{{margin:4px 0 0;font-style:italic;color:#d8c98a}}
.capa{{text-align:center;padding:26px 0}}
.capa img{{max-width:340px;border:6px solid var(--ouro);border-radius:4px;box-shadow:0 8px 24px rgba(0,0,0,.35)}}
.tag{{display:inline-block;background:var(--ouro);color:#fff;font-size:.75em;letter-spacing:.14em;padding:5px 14px;border-radius:20px;margin:18px 0 4px}}
h2{{color:var(--verde);border-bottom:2px solid var(--ouro);padding-bottom:6px}}
h3{{color:var(--verde-c)}}
.erva{{margin:22px 0}}
.latin{{font-style:italic;color:var(--verde-c);margin:-6px 0 8px}}
.sumario ol{{columns:2;column-gap:34px}}
.sumario a{{color:var(--verde);text-decoration:none}}
.fim{{margin-top:34px;padding:16px 20px;background:#f7f2e4;border-left:4px solid var(--ouro);font-style:italic;color:#6b5f45}}
.cta{{text-align:center;margin-top:30px}}
.cta a{{display:inline-block;background:var(--verde);color:#fff;text-decoration:none;padding:12px 26px;border-radius:30px;font-weight:bold}}
.cta small{{display:block;color:#6b5f45;margin-top:8px;font-size:.8em}}
.rodape{{text-align:center;color:#6b5f45;font-size:.85em;margin-top:30px;border-top:1px solid #ddd;padding-top:14px}}
</style>
</head>
<body>
<div class="banner"><h1>ERVAS</h1><p>Indicações e Usos · Amostra Gratuita</p></div>
<main>
  <div class="capa"><img src="{capa_b64}" alt="Capa do livro ERVAS"/></div>

  <span class="tag">GUIA ESOTÉRICO · NATURAL · COMPLETO</span>
  <h2>O que você vai encontrar</h2>
  <ul>
    <li>{len(USO_MEDICINAL)} ervas medicinais, uma por página, com nome científico e receita</li>
    <li>{len(INDICACOES)} indicações em tabela: qual erva usar para cada caso</li>
    <li>{len(ERVAS_PARA)} finalidades: sorte, amor, sucesso, finanças, proteção…</li>
    <li>Banhos de ervas, função energética e ervas dos 12 signos</li>
  </ul>

  <h2>Sumário</h2>
  <div class="sumario"><ol>
    <li>O Poder das Ervas</li><li>Ervas Para…</li><li>Banhos de Ervas</li>
    <li>Função Energética</li><li>O Uso das Ervas e Vegetais</li>
    <li>Indicações das Ervas</li><li>Ervas dos Signos</li>
    <li>Sobre o Autor</li><li>Para Finalizar</li>
  </ol></div>

  <h2>Introdução</h2>
  {intro}

  <h2>Amostra das ervas</h2>
  {cards}

  <h2>Banhos</h2>
  {banhos}

  <div class="fim">{final}</div>

  <div class="cta">
    <a href="ERVAS-Indicacoes-e-Usos.html">Ler o livro completo</a>
    <small>O livro completo tem {total_paginas} páginas · {E(MARCA)}</small>
  </div>

  <div class="rodape">
    {E(MARCA)} · {E(LOCAL)}<br/>
    YouTube: {E(YOUTUBE_NOME)} · E-mail: {E(EMAIL)}<br/>
    © {E(AUTOR)}
  </div>
</main>
</body>
</html>"""
    destino_html.write_text(html_doc, encoding="utf-8")
    print(f"[preview] OK  {destino_html}")


# --------------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------------

def main() -> None:
    DESTINO.mkdir(parents=True, exist_ok=True)
    (DESTINO / "designer").mkdir(parents=True, exist_ok=True)

    # capa (PNG para EPUB + TIFF/JPG 300dpi para KDP)
    capa_png = DESTINO / "00-CAPA-ERVAS.png"
    desenhar_capa(capa_png)

    # EPUB
    epub = DESTINO / "ERVAS-Indicacoes-e-Usos.epub"
    gerar_epub(epub, capa_png)

    # prévia/amostra
    preview = DESTINO / "ERVAS-AMOSTRA.html"
    gerar_preview(preview, capa_png)

    # PDF via Playwright (print do HTML com estilos próprios)
    from playwright.sync_api import sync_playwright
    pdf = DESTINO / "ERVAS-Indicacoes-e-Usos.pdf"
    html_livro = RAIZ / "output" / "ervas.html"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(html_livro.as_uri())
        page.pdf(path=str(pdf), format="A4", print_background=True,
                 margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"})
        browser.close()
    print(f"[pdf]  OK  {pdf}")

    # HTML interativo
    shutil.copy2(html_livro, DESTINO / "ERVAS-Indicacoes-e-Usos.html")

    # designer de capas
    designer = RAIZ.parent.parent / "agente" / "ebook_covers" / "index.html"
    if designer.exists():
        shutil.copy2(designer, DESTINO / "designer" / "designer-de-capas.html")

    # resumo
    resumo = DESTINO / "RESUMO-ERVAS.txt"
    resumo.write_text(textwrap.dedent(f"""\
        ===== RESUMO DO EBOOK =====
        ERVAS — Indicações e Usos
        {AUTOR} · {MARCA}
        {LOCAL}
        YouTube: {YOUTUBE_NOME} · E-mail: {EMAIL}

        SOBRE O LIVRO
        Guia esotérico, energético e medicinal que reúne o saber popular
        das matas do agreste alagoano. Apresenta, em linguagem simples e
        direta, as ervas e suas propriedades — do cultivo ao uso no dia a dia.

        O QUE VOCÊ ENCONTRA
        - 52 ervas medicinais, uma por página, com nome popular, nome
          científico e receita de uso.
        - 88 indicações em tabela: qual erva usar para cada caso.
        - 10 finalidades "Ervas Para…": sorte, amor, sucesso, finanças,
          proteção, amizades e mais.
        - 3 banhos de ervas: felicidade, proteção e amor.
        - Função energética de 19 plantas: de limpar a aura a dar coragem.
        - Ervas dos 12 signos do zodíaco.
        - Dicas de alimentação e equilíbrio energético do corpo.

        PARA QUEM É
        Público espiritual e esotérico, praticantes de magia natural,
        aromaterapia e quem busca uma vida mais saudável e equilibrada.

        AVISO
        Guia de caráter informativo e cultural. Não substitui orientação
        médica. Em caso de doença, procure um profissional de saúde.

        © {AUTOR} — {MARCA}
        """), encoding="utf-8")
    print(f"[resumo] OK  {resumo}")

    # palavras-chave
    keywords = DESTINO / "KEYWORDS-AMAZON.txt"
    keywords.write_text(textwrap.dedent(f"""\
        ===== PALAVRAS-CHAVE PARA A AMAZON (KDP) =====
        Livro: ERVAS — Indicações e Usos

        Frases curtas (máx. 50 caracteres) usadas pelos clientes na busca.
        Vá em KDP > 'Precificação' > 'Palavras-chave' e cole as 7 abaixo,
        uma por campo. A 7ª pode ser: PremioKindle

        1. ervas medicinais e esotéricas
        2. banhos de ervas espirituais
        3. guia de ervas e plantas
        4. remédios naturais caseiros
        5. ervas dos signos do zodíaco
        6. simpatias e magia natural
        7. livro de curas naturais

        DICA: as 3 primeiras são as mais importantes. Use termos que o
        público espiritual procura: "banhos", "simpatias", "magia natural".

        Extra (opcional, se concorrer ao Prêmio Kindle de Literatura):
        PremioKindle  (escreva exatamente assim, sem espaços)
        """), encoding="utf-8")
    print(f"[keywords] OK  {keywords}")

    # divulgação
    divulgacao = DESTINO / "DIVULGACAO.txt"
    divulgacao.write_text(textwrap.dedent(f"""\
        ===== DIVULGAÇÃO DO EBOOK =====
        ERVAS — Indicações e Usos
        {AUTOR} · {MARCA}
        Preço sugerido: R$ 9,90

        Depois que o livro aparecer na Amazon, troque os [LINK] pelo
        endereço real da página do livro (amazon.com.br/dp/ASIN).

        -------------------------------------------------------------------
        1) WHATSAPP (status + grupos)
        -------------------------------------------------------------------
        🌿 NOVIDADE! Meu guia de ervas chegou!

        "ERVAS — Indicações e Usos" é um guia esotérico, energético e
        medicinal com:
        ✔ 52 ervas com nome científico e receita
        ✔ 88 indicações: qual erva usar para cada caso
        ✔ Banhos, simpatias e ervas dos 12 signos

        Aproveita que tá saindo baratinho: R$ 9,90!
        Link: [LINK]

        #ervas #guia #esoterico #medicinal #livro #amazon

        -------------------------------------------------------------------
        2) STATUS CURTO (uma frase)
        -------------------------------------------------------------------
        "O segredo das ervas agora em livro. R$ 9,90 na Amazon! [LINK]"

        -------------------------------------------------------------------
        3) YOUTUBE (legenda do vídeo)
        -------------------------------------------------------------------
        🌿 MEU PRIMEIRO LIVRO ESTÁ NO AR!

        "ERVAS — Indicações e Usos" — guia esotérico, energético e
        medicinal. Reuni neste livro o conhecimento das matas do agreste
        alagoano: 52 ervas com receita, 88 indicações, banhos, signos e
        simpatias.

        Onde encontrar: [LINK]
        Preço: R$ 9,90

        Deixa seu comentário se já usa alguma dessas ervas! 👇

        #ervas #esoterico #livro #mato #alagoas

        -------------------------------------------------------------------
        4) INSTAGRAM (legenda + dica de post)
        -------------------------------------------------------------------
        Legenda:
        🌿 O conhecimento das matas agora virou livro!
        "ERVAS — Indicações e Usos" já está na Amazon por R$ 9,90.
        Sorte, amor, proteção, saúde... tá tudo aqui.
        Link na bio: [LINK]

        Ideias de post (com a capa 00-CAPA-ERVAS.jpg):
        - Post 1: a capa + "Você sabia que arruda protege contra mau olhado?"
        - Post 2: "3 banhos de ervas para começar a semana" (com cards)
        - Post 3: "Qual erva do seu signo?" (carrossel)

        -------------------------------------------------------------------
        5) DIVULGAR PARA GRUPOS DO NICHO
        -------------------------------------------------------------------
        Grupos que aceitam divulgação de livros: esoterismo, bruxaria
        natural, ervas medicinais, chás, umbanda/candomblé (respeitando
        as regras de cada grupo).

        -------------------------------------------------------------------
        DICAS
        -------------------------------------------------------------------
        - Pede para 5 pessoas lerem e deixarem review (avaliação) —
          reviews sobem o livro na busca.
        - No lançamento, o preço baixo (R$ 9,90) ajuda a gerar vendas
          e reviews. Depois de ~15 reviews, pode subir para R$ 12,90.

        © {AUTOR} — {MARCA}
        """), encoding="utf-8")
    print(f"[divulgacao] OK  {divulgacao}")
    leiame = DESTINO / "LEIA-ME-AMAZON.txt"
    leiame.write_text(
        f"""===== ERVAS — Indicações e Usos =====
            {AUTOR} · {MARCA}
            {LOCAL}
            YouTube: {YOUTUBE_NOME}
            E-mail: {EMAIL}

ARQUIVOS NESTA PASTA
  00-CAPA-ERVAS.png               Capa PNG (capa digital Kindle)
  00-CAPA-ERVAS.tiff              Capa TIFF 300dpi (impressão KDP)
  00-CAPA-ERVAS.jpg               Capa JPG q95 300dpi
  ERVAS-Indicacoes-e-Usos.epub    Livro em formato Amazon (KDP)
  ERVAS-Indicacoes-e-Usos.pdf     Versão em PDF (impressão)
  ERVAS-Indicacoes-e-Usos.html    Ebook digital interativo
  RESUMO-ERVAS.txt                Resumo/sinopse do livro
  KEYWORDS-AMAZON.txt             Palavras-chave para busca
  DIVULGACAO.txt                  Textos prontos de divulgação
  ERVAS-AMOSTRA.html              Amostra gratuita do livro
  designer/                       Gerador de capas (abrir no navegador)

COMO PUBLICAR NA AMAZON (KDP)
  1) Acesse kdp.amazon.com e entre com sua conta Amazon.
  2) "Criar" -> "Ebook" (Kindle).
  3) Idiomas: Português. Título: ERVAS — Indicações e Usos.
     Autor: {AUTOR}. Marca: {MARCA}.
  4) Upload do arquivo: ERVAS-Indicacoes-e-Usos.epub
  5) Upload da capa: 00-CAPA-ERVAS.png (ou .jpg se preferir)
  6) Descrição: Guia esotérico, energético e medicinal das ervas —
     propriedades, indicações, banhos, signos e receitas naturais.
  7) Preencha os 7 campos de metadados, defina preço e publique.
  8) Palavras-chave: copie as 7 de KEYWORDS-AMAZON.txt em
     Precificação > Palavras-chave.

VERSÃO IMPRESSA (brochura)
  1) "Criar" -> "Capa mole" (Paperback).
  2) Escolha 6x9 pol (15,24 x 22,86 cm) e preço do papel.
  3) Upload do miolo: ERVAS-Indicacoes-e-Usos.pdf
  4) Upload da capa: 00-CAPA-ERVAS.tiff (300dpi, sem margem de sangue
     — a moldura dourada fica dentro da área segura).

DICA DE PREÇO: livros de nicho espiritual vão bem entre R$ 19,90 e R$ 39,90.

CONVERSÃO PDF -> MOBI (KPF) se necessário: use "Kindle Create" (grátis).

© {AUTOR} — {MARCA}
""".replace("            ", "").replace("  ", ""),
        encoding="utf-8",
    )
    print(f"[leia-me] OK  {leiame}")
    print(f"\nPACOTE COMPLETO em: {DESTINO}")


if __name__ == "__main__":
    main()
