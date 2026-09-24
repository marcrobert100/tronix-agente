#!/usr/bin/env python3
"""Build um livro infantil HTML auto-contido a partir de book.json — InfoEngine.

Uso:
    python tools/build_livro.py book.json output/livro.html

O builder valida estrutura, SVGs, áudio e gera HTML com:
- Navegação por setas e dots
- Narração por página (Web Speech API ou áudio embutido)
- Auto-leitura
- Botão WhatsApp
- Exportação PDF (html2pdf.js)
"""

from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path
from typing import Any

TEMPLATE = Path(__file__).parent.parent / "templates" / "_livro_template.html"
AUDIO_DATA_URI = re.compile(
    r"^data:audio/[a-zA-Z0-9.+-]+(?:;[a-zA-Z0-9.+-]+=[^;,]+)*;base64,[A-Za-z0-9+/=]+$"
)
DANGEROUS_SVG_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "tag executável ou incorporada",
        re.compile(r"<\s*(?:script|foreignobject|iframe|object|embed|link|style|base)\b", re.IGNORECASE),
    ),
    ("handler de evento inline", re.compile(r"\son[a-z][\w:-]*\s*=", re.IGNORECASE)),
    (
        "link externo ou executável",
        re.compile(
            r"(?:href|xlink:href|src)\s*=\s*(['\"]?)\s*(?:https?:|//|javascript:|data:|file:)",
            re.IGNORECASE,
        ),
    ),
    (
        "URL CSS externa ou executável",
        re.compile(r"url\(\s*(['\"]?)\s*(?:https?:|//|javascript:|data:|file:)", re.IGNORECASE),
    ),
)

WHATSAPP_NUM = "5582991856656"


def falhar(mensagem: str) -> None:
    print(f"[build_livro] ERRO: {mensagem}", file=sys.stderr)
    raise SystemExit(1)


def eh_texto_nao_vazio(valor: Any) -> bool:
    return isinstance(valor, str) and bool(valor.strip())


def validar_svg(svg: str, label: str, problemas: list[str], ids_vistos: dict[str, str]) -> None:
    iniciado = svg.lstrip()
    if not iniciado.startswith("<svg"):
        problemas.append(f"{label} ilustração não é SVG ou não começa com <svg>")
        return
    if "viewBox" not in svg:
        problemas.append(f"{label} SVG sem viewBox (escalona errado)")

    for descricao, padrao in DANGEROUS_SVG_PATTERNS:
        if padrao.search(svg):
            problemas.append(f"{label} SVG contém {descricao} não permitido")

    for match in re.finditer(r'\bid\s*=\s*([\'"])(.*?)\1', svg, re.IGNORECASE | re.DOTALL):
        svg_id = match.group(2).strip()
        if not svg_id:
            problemas.append(f"{label} SVG tem id vazio")
        elif svg_id in ids_vistos:
            problemas.append(
                f"{label} SVG id=\"{svg_id}\" duplicado com {ids_vistos[svg_id]}; "
                "todos os IDs SVG devem ser únicos no livro"
            )
        else:
            ids_vistos[svg_id] = label


def validar_livro(livro: Any) -> list[str]:
    problemas: list[str] = []
    if not isinstance(livro, dict):
        return ["book.json deve ser um objeto JSON"]

    if not eh_texto_nao_vazio(livro.get("titulo")):
        problemas.append("Falta 'titulo' ou título vazio")

    for chave in ("subtitulo", "autor", "faixa_etaria", "lang", "texto_final"):
        if chave in livro and livro[chave] is not None and not isinstance(livro[chave], str):
            problemas.append(f"'{chave}' deve ser string")

    capa_svg = livro.get("capa_svg")
    ids_vistos: dict[str, str] = {}
    if not isinstance(capa_svg, str):
        problemas.append("Falta 'capa_svg' ou não é string")
    else:
        validar_svg(capa_svg, "Capa", problemas, ids_vistos)

    paginas = livro.get("paginas")
    if not isinstance(paginas, list):
        problemas.append("'paginas' deve ser array")
        return problemas
    if len(paginas) < 4:
        problemas.append(f"Só {len(paginas)} páginas; mínimo 4")

    for indice, pagina in enumerate(paginas, start=1):
        label = f"Página {indice}"
        if not isinstance(pagina, dict):
            problemas.append(f"{label} deve ser objeto")
            continue

        texto = pagina.get("texto")
        if not eh_texto_nao_vazio(texto):
            problemas.append(f"{label} sem texto ou texto vazio")

        svg = pagina.get("svg")
        if not isinstance(svg, str):
            problemas.append(f"{label} SVG ausente ou não é string")
        else:
            validar_svg(svg, label, problemas, ids_vistos)

        audio = pagina.get("audio", "")
        if not isinstance(audio, str):
            problemas.append(f"{label} 'audio' deve ser string")
        elif audio and not AUDIO_DATA_URI.fullmatch(audio):
            problemas.append(
                f"{label} 'audio' deve ser vazio ou data:audio/...;base64,..."
            )

    return problemas


def json_para_script(livro: dict[str, Any]) -> str:
    """Serializa JSON com segurança para inserir dentro de <script>."""
    return (
        json.dumps(livro, ensure_ascii=False, separators=(",", ":"))
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def main() -> None:
    if len(sys.argv) < 3:
        falhar("Uso: python tools/build_livro.py book.json output/livro.html [--template NOME]")

    caminho_entrada = Path(sys.argv[1])
    caminho_saida = Path(sys.argv[2])
    template_nome = "padrao"
    if len(sys.argv) >= 5 and sys.argv[3] == "--template":
        template_nome = sys.argv[4]

    if not caminho_entrada.is_file():
        falhar(f"Arquivo não encontrado: {caminho_entrada}")

    template_paths = {
        "padrao": TEMPLATE,
        "quadrinho": TEMPLATE.parent / "_livro_quadrinho_template.html",
    }
    template_path = template_paths.get(template_nome)
    if not template_path or not template_path.is_file():
        falhar(f"Template '{template_nome}' não encontrado em: {template_path}")

    try:
        livro = json.loads(caminho_entrada.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        falhar(f"Não foi possível ler UTF-8: {caminho_entrada}")
    except json.JSONDecodeError as erro:
        falhar(f"JSON inválido: linha {erro.lineno}, coluna {erro.colno}: {erro.msg}")

    problemas = validar_livro(livro)
    if problemas:
        for problema in problemas:
            print(f"[build_livro] ERRO: {problema}", file=sys.stderr)
        raise SystemExit(1)

    template = template_path.read_text(encoding="utf-8")
    if "__TITULO__" not in template or "__DADOS_LIVRO__" not in template:
        falhar("Template sem __TITULO__ ou __DADOS_LIVRO__")

    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    gerado = template.replace("__TITULO__", html.escape(livro["titulo"], quote=True))
    gerado = gerado.replace("__DADOS_LIVRO__", json_para_script(livro))
    caminho_saida.write_text(gerado, encoding="utf-8")

    paginas = livro["paginas"]
    audio_count = sum(1 for p in paginas if p.get("audio"))
    modo = (
        f"{audio_count}/{len(paginas)} páginas com áudio embutido"
        if audio_count
        else "narração pelo navegador (sem áudio embutido)"
    )
    tamanho_kb = caminho_saida.stat().st_size // 1024
    print(
        f"[build_livro] OK Gerado {caminho_saida} "
        f"({template_nome}, {len(paginas)} paginas + capa + final, {modo}, {tamanho_kb} KB)"
    )


if __name__ == "__main__":
    main()
