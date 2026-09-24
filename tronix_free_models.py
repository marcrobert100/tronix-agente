"""
Tronix Free Models Config
Configura Tronix + OpenHuman com modelos 100% gratuitos
"""
import json, os, sys, io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ─── Free API Keys (signup sem cartão) ─────────────────────────
FREE_PROVIDERS = {
    "openrouter": {
        "name": "OpenRouter",
        "url": "https://openrouter.ai",
        "signup": "https://openrouter.ai/auth/signup",
        "free_models": [
            "google/gemma-4-31b-it:free",
            "nvidia/nemotron-3-super-120b-a12b:free",
            "openai/gpt-oss-120b:free",
            "qwen/qwen3-coder:free",
            "meta-llama/llama-3.3-70b-instruct:free",
            "nvidia/nemotron-3-nano-30b-a3b:free",
            "nvidia/nemotron-nano-12b-v2-vl:free",
        ],
        "rate_limit": "20 req/min gratis",
        "api_format": "openai"
    },
    "google": {
        "name": "Google Gemini",
        "url": "https://aistudio.google.com",
        "signup": "https://aistudio.google.com/apikey",
        "free_models": [
            "gemini-2.0-flash",
            "gemini-2.5-flash",
            "gemini-1.5-flash",
        ],
        "rate_limit": "60 req/min gratis",
        "api_format": "gemini"
    },
    "groq": {
        "name": "Groq",
        "url": "https://console.groq.com",
        "signup": "https://console.groq.com/keys",
        "free_models": [
            "llama-3.3-70b-versatile",
            "gemma2-9b-it",
            "mixtral-8x7b-32768",
        ],
        "rate_limit": "14400 req/dia gratis",
        "api_format": "openai"
    },
    "nvidia_nim": {
        "name": "NVIDIA NIM",
        "url": "https://build.nvidia.com",
        "signup": "https://build.nvidia.com/nim/signup",
        "free_models": [
            "nvidia/nemotron-3-ultra-550b-a55b",
            "nvidia/llama-3.1-nemotron-70b-instruct",
            "meta/llama-3.1-8b-instruct",
        ],
        "rate_limit": "1000 req/dia gratis",
        "api_format": "openai"
    },
    "deepseek": {
        "name": "DeepSeek",
        "url": "https://platform.deepseek.com",
        "signup": "https://platform.deepseek.com/api_keys",
        "free_models": [
            "deepseek-chat",
            "deepseek-reasoner",
        ],
        "rate_limit": "Promocional: gratis agora",
        "api_format": "openai"
    },
    "huggingface": {
        "name": "HuggingFace",
        "url": "https://huggingface.co",
        "signup": "https://huggingface.co/settings/tokens",
        "free_models": [
            "meta-llama/Llama-3.3-70B-Instruct",
            "Qwen/Qwen3-Coder",
            "mistralai/Mistral-7B-Instruct-v0.3",
        ],
        "rate_limit": "Rate limited gratis",
        "api_format": "huggingface"
    }
}

# ─── Recommended Configs ───────────────────────────────────────
RECOMMENDED_CONFIGS = {
    "tronix_crewai": {
        "description": "Para CrewAI multi-agente (melhor reasoning)",
        "primary": "nvidia_nim",
        "model": "nvidia/nemotron-3-ultra-550b-a55b",
        "fallback": "openrouter",
        "fallback_model": "nvidia/nemotron-3-super-120b-a12b:free"
    },
    "tronix_fast": {
        "description": "Para respostas rápidas (pipeline, scripts)",
        "primary": "groq",
        "model": "llama-3.3-70b-versatile",
        "fallback": "google",
        "fallback_model": "gemini-2.0-flash"
    },
    "openhuman_chat": {
        "description": "Para chat no OpenHuman",
        "primary": "openrouter",
        "model": "google/gemma-4-31b-it:free",
        "fallback": "groq",
        "fallback_model": "llama-3.3-70b-versatile"
    },
    "openhuman_reasoning": {
        "description": "Para tarefas complexas no OpenHuman",
        "primary": "nvidia_nim",
        "model": "nvidia/nemotron-3-ultra-550b-a55b",
        "fallback": "deepseek",
        "fallback_model": "deepseek-reasoner"
    }
}


def generate_env_file():
    """Gera .env com placeholders para API keys gratuitas"""
    env_content = """# ═══════════════════════════════════════════════════════
# TRONIX + OPENHUMAN - FREE MODELS CONFIG
# ═══════════════════════════════════════════════════════
# API Keys GRÁTIS - cadastre-se sem cartão de crédito

# OpenRouter (26 modelos grátis, 20 req/min)
OPENROUTER_API_KEY=sk-or-v1-SUA_KEY_AQUI

# Google Gemini (3 modelos grátis, 60 req/min)
GOOGLE_AI_API_KEY=AIzaSySUA_KEY_AQUI

# Groq (ultra-rápido, 14400 req/dia)
GROQ_API_KEY=gsk_SUA_KEY_AQUI

# NVIDIA NIM (modelos grandes grátis, 1000 req/dia)
NVIDIA_API_KEY=nvapi-SUA_KEY_AQUI

# DeepSeek (promoção: grátis)
DEEPSEEK_API_KEY=sk-SUA_KEY_AQUI

# HuggingFace (milhares de modelos grátis)
HF_TOKEN=hf_SUA_KEY_AQUI

# ═══════════════════════════════════════════════════════
# MODELOS RECOMENDADOS POR TAREFA
# ═══════════════════════════════════════════════════════

# CrewAI multi-agente (reasoning forte)
CREWAI_LLM=nvidia/nemotron-3-ultra-550b-a55b

# Respostas rápidas (pipeline, scripts)
FAST_LLM=llama-3.3-70b-versatile

# Chat OpenHuman
CHAT_LLM=google/gemma-4-31b-it:free

# Embeddings (para memória)
EMBEDDING_MODEL=nvidia/nemotron-3-nano-30b-a3b:free
"""
    env_path = Path(__file__).parent / ".env.free_models"
    env_path.write_text(env_content, encoding="utf-8")
    print(f"[OK] Arquivo gerado: {env_path}")
    return env_path


def generate_tronix_config():
    """Gera config.json para Tronix usar modelos grátis"""
    config = {
        "free_models": {
            "provider": "openrouter",
            "api_base": "https://openrouter.ai/api/v1",
            "models": {
                "chat": "google/gemma-4-31b-it:free",
                "reasoning": "nvidia/nemotron-3-super-120b-a12b:free",
                "coding": "qwen/qwen3-coder:free",
                "fast": "nvidia/nemotron-3-nano-30b-a3b:free",
                "vision": "nvidia/nemotron-nano-12b-v2-vl:free"
            }
        },
        "providers": FREE_PROVIDERS,
        "routing": RECOMMENDED_CONFIGS
    }

    config_path = Path(__file__).parent / "free_models_config.json"
    config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[OK] Config gerada: {config_path}")
    return config_path


def generate_openhuman_config():
    """Gera config para OpenHuman usar modelos grátis"""
    oh_user = Path(os.path.expanduser("~/.openhuman/users/6a165346ced0a054d8f058ff"))
    config_path = oh_user / "config.toml"

    if not config_path.exists():
        print(f"[ERRO] Config não encontrado: {config_path}")
        return

    content = config_path.read_text(encoding="utf-8")

    # Adiciona seção de API keys gratuitas no final
    free_config = """
# ═══════════════════════════════════════════════════════
# FREE MODELS - Configurado por Tronix
# ═══════════════════════════════════════════════════════

[free_models]
enabled = true
provider = "openrouter"
api_base = "https://openrouter.ai/api/v1"

[free_models.models]
chat = "google/gemma-4-31b-it:free"
reasoning = "nvidia/nemotron-3-super-120b-a12b:free"
coding = "qwen/qwen3-coder:free"
fast = "nvidia/nemotron-3-nano-30b-a3b:free"
vision = "nvidia/nemotron-nano-12b-v2-vl:free"
"""

    # Adiciona apenas se não existe
    if "[free_models]" not in content:
        with open(config_path, "a", encoding="utf-8") as f:
            f.write(free_config)
        print(f"[OK] Free models adicionado ao OpenHuman config")
    else:
        print(f"[OK] Free models já configurado no OpenHuman")


def print_signup_guide():
    """Mostra guia de cadastro em cada plataforma"""
    print("\n" + "="*60)
    print("  GUIA DE CADASTRO - MODELOS GRÁTIS")
    print("="*60)

    for key, provider in FREE_PROVIDERS.items():
        print(f"\n{'─'*60}")
        print(f"  {provider['name']}")
        print(f"{'─'*60}")
        print(f"  URL: {provider['url']}")
        print(f"  Cadastro: {provider['signup']}")
        print(f"  Modelos grátis: {len(provider['free_models'])}")
        print(f"  Rate limit: {provider['rate_limit']}")
        print(f"  Formato API: {provider['api_format']}")
        print(f"\n  Modelos:")
        for m in provider['free_models']:
            print(f"    • {m}")

    print(f"\n{'='*60}")
    print("  PRIORIDADE DE CADASTRO:")
    print("  1. OpenRouter → 26 modelos grátis, mais versátil")
    print("  2. Groq → Ultra-rápido, 14400 req/dia")
    print("  3. Google Gemini → 60 req/min, modelos fortes")
    print("  4. NVIDIA NIM → Modelos grandes (550B params)")
    print("  5. DeepSeek → Reasoning forte, grátis em promoção")
    print("="*60)


if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"

    if cmd == "env":
        generate_env_file()
    elif cmd == "config":
        generate_tronix_config()
    elif cmd == "openhuman":
        generate_openhuman_config()
    elif cmd == "guide":
        print_signup_guide()
    elif cmd == "all":
        generate_env_file()
        generate_tronix_config()
        generate_openhuman_config()
        print_signup_guide()
    else:
        print("Uso: python tronix_free_models.py [env|config|openhuman|guide|all]")
