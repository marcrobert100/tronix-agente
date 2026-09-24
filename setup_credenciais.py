#!/usr/bin/env python3
"""
TRONIX - SETUP WIZARD DE CREDENCIAIS
Coleta Instagram, Replicate, GitHub token e grava em .env.
Uso: python setup_credenciais.py
"""

import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = Path(__file__).parent
ENV_FILE = BASE / ".env"

ENV_TEMPLATE = """# TRONIX - CREDENCIAIS
# Gerado por setup_credenciais.py em {timestamp}
# NAO COMMITAR. Adicionar .env no .gitignore.

# === IMAGENS ===
CF_ACCOUNT_ID=038280d984d9c936772700b7dbbc479e
CF_API_TOKEN=

# === VOZ (Edge-TTS, sem key) ===
EDGE_TTS_VOICE=pt-BR-AntonioNeural

# === LLM (OpenRouter para CrewAI) ===
OPENROUTER_API_KEY=

# === INSTAGRAM (instagrapi) ===
IG_USERNAME=
IG_PASSWORD=
IG_SESSION_FILE=tronix_ig_session.json

# === YOUTUBE (Google OAuth) ===
YOUTUBE_CLIENT_SECRETS=client_secret.json
YOUTUBE_TOKEN_FILE=token_youtube.pickle

# === REPLICATE (Wan 2.2 I2V, video) ===
REPLICATE_API_TOKEN=

# === GITHUB (Pages + Push) ===
GITHUB_TOKEN=
GITHUB_REPO=marcrobert100/tronix-agente
"""


def cor(txt, code):
    return f"\033[{code}m{txt}\033[0m"


def verde(txt): return cor(txt, "32")
def amarelo(txt): return cor(txt, "33")
def azul(txt): return cor(txt, "36")
def vermelho(txt): return cor(txt, "31")


def prompt(label, atual="", hidden=False):
    """Prompt com valor atual."""
    sufixo = f" [{atual}]" if atual else ""
    prompt_str = f"{amarelo(label)}{sufixo}: "
    if hidden:
        import getpass
        valor = getpass.getpass(prompt_str)
    else:
        valor = input(prompt_str)
    return valor.strip() or atual


def main():
    print(azul("=" * 60))
    print(azul("TRONIX - SETUP DE CREDENCIAIS"))
    print(azul("=" * 60))
    print()
    print("Este wizard coleta credenciais e grava em .env")
    print("Deixe em branco para manter o valor atual (se existir).")
    print()

    atual = {}
    if ENV_FILE.exists():
        for linha in ENV_FILE.read_text(encoding="utf-8").splitlines():
            if "=" in linha and not linha.strip().startswith("#"):
                k, v = linha.split("=", 1)
                atual[k.strip()] = v.strip()

    print(verde("[1/5] IMAGENS - Cloudflare (opcional, Pollinations ja funciona)"))
    cf_token = prompt("Cloudflare API Token", atual.get("CF_API_TOKEN", ""))
    print()

    print(verde("[2/5] LLM - OpenRouter (para CrewAI)"))
    print("  Obtenha em: https://openrouter.ai/keys")
    or_key = prompt("OpenRouter API Key", atual.get("OPENROUTER_API_KEY", ""))
    print()

    print(verde("[3/5] INSTAGRAM (instagrapi)"))
    print("  AVISO: Instagram bloqueia logins novos. Use conta secundaria.")
    ig_user = prompt("Instagram Username", atual.get("IG_USERNAME", ""))
    ig_pass = prompt("Instagram Password", atual.get("IG_PASSWORD", ""), hidden=True)
    print()

    print(verde("[4/5] REPLICATE (Wan 2.2 I2V, ~$0.01/video)"))
    print("  Obtenha em: https://replicate.com/account/api-tokens")
    print("  Adicione credito em: https://replicate.com/account/billing")
    rep_key = prompt("Replicate API Token", atual.get("REPLICATE_API_TOKEN", ""))
    print()

    print(verde("[5/5] GITHUB (para Pages + Push)"))
    print("  Obtenha em: https://github.com/settings/tokens (scope: repo, workflow)")
    gh_token = prompt("GitHub Token", atual.get("GITHUB_TOKEN", ""))
    print()

    conteudo = ENV_TEMPLATE.format(
        timestamp=__import__('datetime').datetime.now().isoformat()
    )
    replacements = {
        "CF_API_TOKEN": cf_token,
        "OPENROUTER_API_KEY": or_key,
        "IG_USERNAME": ig_user,
        "IG_PASSWORD": ig_pass,
        "REPLICATE_API_TOKEN": rep_key,
        "GITHUB_TOKEN": gh_token,
    }
    for k, v in replacements.items():
        if v:
            for linha in conteudo.splitlines():
                if linha.startswith(f"{k}="):
                    conteudo = conteudo.replace(linha, f"{k}={v}")
                    break

    if not ENV_FILE.exists() or input(amarelo(f"Sobrescrever {ENV_FILE}? [s/N]: ")).lower() == "s":
        ENV_FILE.write_text(conteudo, encoding="utf-8")
        try:
            os.chmod(ENV_FILE, 0o600)
        except:
            pass
        print(verde(f"\n[OK] Credenciais salvas em {ENV_FILE}"))
        print(amarelo("Lembre: .env deve estar no .gitignore!"))
    else:
        print(vermelho("\nCancelado."))


if __name__ == "__main__":
    main()
