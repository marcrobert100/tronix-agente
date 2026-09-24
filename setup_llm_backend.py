#!/usr/bin/env python3
"""
TRONIX - SETUP LLM BACKEND para Graphify
Detecta qual backend LLM esta disponivel e configura.

Uso: python setup_llm_backend.py
"""

import os
import sys
import subprocess
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

try:
    import requests
except ImportError:
    print("ERRO: pip install requests")
    sys.exit(1)

BASE = Path(__file__).parent if '__file__' in globals() else Path.cwd()


def testar_openai(key, base=None):
    url = (base or "https://api.openai.com/v1") + "/models"
    try:
        r = requests.get(url, headers={"Authorization": f"Bearer {key}"}, timeout=10)
        return r.status_code == 200
    except:
        return False


def testar_anthropic(key):
    try:
        r = requests.get("https://api.anthropic.com/v1/models",
                         headers={"x-api-key": key, "anthropic-version": "2023-06-01"}, timeout=10)
        return r.status_code == 200
    except:
        return False


def testar_openrouter(key):
    try:
        r = requests.get("https://openrouter.ai/api/v1/auth/key",
                         headers={"Authorization": f"Bearer {key}"}, timeout=10)
        return r.status_code == 200
    except:
        return False


def testar_gemini(key):
    try:
        r = requests.get(f"https://generativelanguage.googleapis.com/v1/models?key={key}", timeout=10)
        return r.status_code == 200
    except:
        return False


def testar_ollama():
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=5)
        if r.status_code == 200:
            modelos = r.json().get("models", [])
            return True, [m["name"] for m in modelos[:3]]
        return False, []
    except:
        return False, []


def testar_pollinations_text():
    try:
        r = requests.get("https://text.pollinations.ai/hi", timeout=15)
        return r.status_code == 200 and len(r.text) > 0
    except:
        return False


def main():
    print("=" * 60)
    print("TRONIX - SETUP LLM BACKEND PARA GRAPHIFY")
    print("=" * 60)
    print()

    env = {}
    env_file = BASE / ".env"
    if env_file.exists():
        for linha in env_file.read_text(encoding="utf-8").splitlines():
            if "=" in linha and not linha.startswith("#"):
                k, v = linha.split("=", 1)
                env[k.strip()] = v.strip()

    backends = []

    print("[1/6] OpenAI...")
    if testar_openai(env.get("OPENAI_API_KEY", "")):
        backends.append(("openai", "OpenAI (real)", {"OPENAI_API_KEY": env["OPENAI_API_KEY"]}))
        print("  [OK] OpenAI real key")
    else:
        print("  [skip] Sem key real")

    print("[2/6] Anthropic Claude...")
    if testar_anthropic(env.get("ANTHROPIC_API_KEY", "")):
        backends.append(("anthropic", "Anthropic Claude (real)", {"ANTHROPIC_API_KEY": env["ANTHROPIC_API_KEY"]}))
        print("  [OK] Anthropic real key")
    else:
        print("  [skip] Sem key real")

    print("[3/6] OpenRouter...")
    if testar_openrouter(env.get("OPENROUTER_API_KEY", "")):
        backends.append(("openai", "OpenRouter (compat OpenAI)",
                         {"OPENAI_API_KEY": env["OPENROUTER_API_KEY"], "OPENAI_BASE_URL": "https://openrouter.ai/api/v1"}))
        print("  [OK] OpenRouter real key")
    else:
        print("  [skip] Sem key real")

    print("[4/6] Google Gemini...")
    if testar_gemini(env.get("GEMINI_API_KEY", "") or env.get("GOOGLE_API_KEY", "")):
        backends.append(("gemini", "Google Gemini", {}))
        print("  [OK] Gemini real key")
    else:
        print("  [skip] Sem key real")

    print("[5/6] Ollama local...")
    ok, modelos = testar_ollama()
    if ok:
        backends.append(("ollama", f"Ollama local: {', '.join(modelos)}", {}))
        print(f"  [OK] Ollama rodando: {', '.join(modelos)}")
    else:
        print("  [skip] Ollama nao esta rodando (iniciar com 'ollama serve')")

    print("[6/6] Pollinations TEXT (free, sem key)...")
    if testar_pollinations_text():
        backends.append(("pollinations", "Pollinations TEXT (free, unstable)", {}))
        print("  [OK] Pollinations TEXT online (mas instavel para uso serio)")
    else:
        print("  [skip] Pollinations offline")

    print()
    print("=" * 60)
    if not backends:
        print("NENHUM backend LLM funcional detectado!")
        print()
        print("Recomendacoes:")
        print("  1. OpenAI: https://platform.openai.com/api-keys")
        print("  2. Anthropic: https://console.anthropic.com/settings/keys")
        print("  3. OpenRouter (recomendado, multi-provider): https://openrouter.ai/keys")
        print("  4. Ollama local: ollama pull llama3.2 && ollama serve")
        print("  5. Gemini free: https://aistudio.google.com/apikey")
        sys.exit(1)

    print(f"{len(backends)} backend(s) funcional(is):")
    for i, (backend, label, envvars) in enumerate(backends, 1):
        print(f"  {i}. {label} ({backend})")

    print()
    escolha = input(f"Escolha [1-{len(backends)}] ou Enter para melhor: ").strip()
    if not escolha:
        escolha = "1"
    idx = int(escolha) - 1
    if idx < 0 or idx >= len(backends):
        idx = 0

    backend_escolhido, label, envvars = backends[idx]
    print(f"\nSelecionado: {label}")

    for k, v in envvars.items():
        os.environ[k] = v

    print(f"\nRodando: graphify extract . --backend {backend_escolhido} --no-viz --force")
    print("(Isto pode demorar 5-15 min)")
    print()
    if input("Continuar? [S/n]: ").lower() not in ["", "s", "y"]:
        print("Cancelado.")
        return

    cmd = ["graphify", "extract", ".", "--backend", backend_escolhido, "--no-viz", "--force"]
    env_full = os.environ.copy()
    env_full.update(envvars)
    subprocess.run(cmd, cwd=str(BASE), env=env_full)


if __name__ == "__main__":
    from pathlib import Path
    main()
