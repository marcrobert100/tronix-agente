"""
Gerador de PDF — InfoEngine
Converte templates HTML para PDF usando playwright.

Uso: python gerar_pdf.py <arquivo.html> [output.pdf]
"""

import sys
import os


def gerar_pdf(html_path, output_path=None):
    """Converte HTML para PDF usando playwright."""
    if not os.path.exists(html_path):
        print(f"Erro: arquivo não encontrado: {html_path}")
        return False

    if output_path is None:
        output_path = os.path.splitext(html_path)[0] + ".pdf"

    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(f"file://{os.path.abspath(html_path)}")
            page.pdf(
                path=output_path,
                format="A4",
                print_background=True,
                margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"},
            )
            browser.close()

        print(f"PDF gerado: {output_path}")
        return True

    except ImportError:
        print("Playwright não instalado. Instale com:")
        print("  pip install playwright")
        print("  playwright install chromium")
        print()
        print("Alternativa: abra o HTML no navegador e use 'Baixar PDF'.")
        return False


def listar_templates(diretorio="templates"):
    """Lista templates HTML disponíveis."""
    if not os.path.exists(diretorio):
        print(f"Diretório não encontrado: {diretorio}")
        return []

    templates = []
    for root, dirs, files in os.walk(diretorio):
        for f in files:
            if f.endswith(".html"):
                templates.append(os.path.join(root, f))

    return templates


if __name__ == "__main__":
    if len(sys.argv) > 1:
        gerar_pdf(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    else:
        print("=== InfoEngine — Gerador de PDF ===")
        print("Uso: python gerar_pdf.py <arquivo.html> [output.pdf]")
        print()
        templates = listar_templates()
        if templates:
            print("Templates disponíveis:")
            for t in templates:
                print(f"  - {t}")
