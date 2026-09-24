#!/usr/bin/env python3
"""
TRONIX - SETUP REPLICATE (Wan 2.2 Image-to-Video)
Testa credenciais, valida billing, e roda um video de teste.
Uso: python setup_replicate.py
"""

import os
import sys
import json
import time
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

try:
    import requests
except ImportError:
    print("ERRO: pip install requests")
    sys.exit(1)

BASE = Path(__file__).parent if '__file__' in globals() else Path.cwd()


def ler_env():
    env = {}
    env_file = BASE / ".env"
    if env_file.exists():
        for linha in env_file.read_text(encoding="utf-8").splitlines():
            if "=" in linha and not linha.startswith("#"):
                k, v = linha.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def testar_conectividade(token):
    """Testa token e billing do Replicate."""
    headers = {"Authorization": f"Token {token}"}
    try:
        r = requests.get("https://api.replicate.com/v1/account", headers=headers, timeout=10)
        if r.status_code == 200:
            conta = r.json()
            return True, conta
        return False, f"Status {r.status_code}: {r.text[:200]}"
    except Exception as e:
        return False, str(e)


def listar_modelos_video(token):
    """Lista modelos de video populares."""
    headers = {"Authorization": f"Token {token}"}
    try:
        r = requests.get(
            "https://api.replicate.com/v1/models?collection_slug=image-to-video",
            headers=headers, timeout=15
        )
        if r.status_code == 200:
            return r.json().get("results", [])[:10]
    except:
        pass
    return []


def main():
    print("=" * 60)
    print("TRONIX - SETUP REPLICATE")
    print("=" * 60)

    env = ler_env()
    token = env.get("REPLICATE_API_TOKEN", "") or os.environ.get("REPLICATE_API_TOKEN", "")

    if not token:
        print("ERRO: REPLICATE_API_TOKEN nao encontrado no .env")
        print("Obtenha em: https://replicate.com/account/api-tokens")
        print("Adicione credito em: https://replicate.com/account/billing")
        sys.exit(1)

    print(f"\n[1/3] Testando token...")
    ok, info = testar_conectividade(token)
    if not ok:
        print(f"FALHOU: {info}")
        sys.exit(1)
    print(f"[OK] Conta: {info.get('username', 'N/A')}")
    print(f"     Tipo: {info.get('account_type', 'N/A')}")

    print(f"\n[2/3] Listando modelos de video...")
    modelos = listar_modelos_video(token)
    if modelos:
        for m in modelos[:5]:
            print(f"  - {m.get('name', 'N/A')} ({(m.get('description') or '')[:60]})")

    wan22 = next((m for m in modelos if "wan" in m.get("name", "").lower()), None)
    if not wan22:
        print("  Wan 2.2 nao encontrado, mas credenciais estao OK.")
    else:
        print(f"  Wan 2.2 disponivel: {wan22.get('url', 'N/A')}")

    print(f"\n[3/3] Setup completo!")
    print("Use tronix_animar_replicate.py para gerar videos com Wan 2.2.")
    print("Custo estimado: $0.01-0.05 por video de 5s.")


if __name__ == "__main__":
    from pathlib import Path
    main()
