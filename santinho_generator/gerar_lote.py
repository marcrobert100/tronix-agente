"""
Tronix Santinho Generator - Lote Multi-Candidato
Gera santinhos para varios candidatos em uma unica execucao.
Equipe: Tronix-DEV + Tronix-MEDIA + Tronix-DB
"""
import json
import argparse
from pathlib import Path
from datetime import datetime

from santinho import gerar_pdf_lote, init_db, registrar_memoria

ROOT = Path(__file__).parent


def carregar_candidatos(arquivo_json: str) -> list[dict]:
    """Carrega lista de candidatos de um JSON."""
    with open(arquivo_json, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "candidatos" in data:
        return data["candidatos"]
    if isinstance(data, list):
        return data
    return [data]


def main():
    p = argparse.ArgumentParser(description="Gerar santinhos em lote para varios candidatos")
    p.add_argument("--input", required=True, help="JSON com lista de candidatos")
    p.add_argument("--quantidade", type=int, default=100, help="Quantidade por candidato")
    p.add_argument("--copias", type=int, default=9, help="Copias por pagina A4")
    p.add_argument("--sem-verso", action="store_true")
    p.add_argument("--saida-dir", default=str(ROOT / "outputs"))
    args = p.parse_args()

    init_db()
    candidatos = carregar_candidatos(args.input)
    print(f"[TRONIX] {len(candidatos)} candidato(s) carregado(s)")

    sucessos = []
    erros = []
    for i, cand in enumerate(candidatos, 1):
        nome = cand.get("nome", f"candidato_{i}")
        slug = nome.lower().replace(" ", "_")
        arquivo = f"{args.saida_dir}/lote_{slug}_x{args.quantidade}.pdf"
        try:
            print(f"\n[{i}/{len(candidatos)}] Gerando santinho de {nome}...")
            gerar_pdf_lote(cand, args.quantidade, args.copias, not args.sem_verso, arquivo)
            sucessos.append(nome)
        except Exception as e:
            print(f"[ERRO] {nome}: {e}")
            erros.append((nome, str(e)))

    print(f"\n=== RESUMO DO LOTE ===")
    print(f"Total: {len(candidatos)}")
    print(f"Sucessos: {len(sucessos)}")
    print(f"Erros: {len(erros)}")
    for n, e in erros:
        print(f"  - {n}: {e}")

    registrar_memoria(f"LOTE: {len(sucessos)}/{len(candidatos)} santinhos gerados a partir de {args.input}")


if __name__ == "__main__":
    main()
