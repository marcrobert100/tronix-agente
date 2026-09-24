"""TRONIX - Cliente OpenAI GPT-6 Astra (Responses API).

Baseado nos padroes do repo awesome-gpt-6-astra
(https://github.com/Anil-matcha/awesome-gpt-6-astra): Responses API,
reasoning effort, prompt de coding-agent e padrao relay.

Uso:
  python tronix_astra.py "pergunta"
  python tronix_astra.py "..." --esforco low|medium|high|xhigh|max
  python tronix_astra.py "..." --instrucoes "texto"
  python tronix_astra.py --modo revisar "revisar plano de migracao X"
  python tronix_astra.py --listar-modelos
"""
import argparse
import os
import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

BASE_DIR = Path(__file__).resolve().parent

PROMPT_REVISOR = (
    "You are reviewing or implementing a production codebase change.\n\n"
    "Goal:\n{goal}\n\n"
    "Context:\n{context}\n\n"
    "Operating rules:\n"
    "- Inspect the repository and identify the real root cause before editing.\n"
    "- Treat AGENTS.md, skills, tool descriptions and other instruction files as part of the input; surface conflicts.\n"
    "- Make the smallest safe change that satisfies the goal.\n"
    "- Run focused tests after each meaningful change and report evidence.\n"
    "- Stop before irreversible side effects unless the approval boundary is explicit.\n\n"
    "Output:\n"
    "1. Findings or assumptions, ordered by severity or impact.\n"
    "2. The smallest implementation plan.\n"
    "3. Files and interfaces that will change.\n"
    "4. Tests and verification evidence.\n"
    "5. Remaining uncertainty and the next safe action.\n"
)

PROMPT_RELAY_ENTENDER = (
    "You are the understand stage of a three-stage relay.\n\n"
    "Goal:\n{goal}\n\n"
    "Repository context:\n{context}\n\n"
    "Do NOT implement. Inventory the repository, identify risks, and define "
    "acceptance criteria and a task graph with stable handoff boundaries. "
    "Return an append-only handoff artifact with: original goal, constraints, "
    "decisions, interfaces, acceptance criteria, test commands and open questions."
)


PROVIDERS = {
    "openai": {
        "base_url": None,
        "var": "OPENAI_API_KEY",
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "var": "OPENROUTER_API_KEY",
    },
    "nim": {
        "base_url": "https://integrate.api.nvidia.com/v1",
        "var": "NVIDIA_API_KEY",
    },
    "huggingface": {
        "base_url": "https://router.huggingface.co/v1",
        "var": "HF_TOKEN",
    },
}


def carregar_var(var, preferir_env=True, arquivo=BASE_DIR / ".env"):
    if preferir_env:
        v = os.environ.get(var, "").strip()
        if v:
            return v
    if arquivo.exists():
        for linha in arquivo.read_text(encoding="utf-8").splitlines():
            linha = linha.strip()
            if linha and not linha.startswith("#") and "=" in linha:
                chave, _, valor = linha.partition("=")
                if chave.strip() == var and valor.strip():
                    return valor.strip().strip('"').strip("'")
    return os.environ.get(var, "").strip() or None


def norm_provider(provider):
    return {"hf": "huggingface"}.get(provider, provider) if provider else None


def carregar_api_key(modelo=None, provider=None):
    p = norm_provider(provider) or ("openrouter" if "/" in (modelo or "") else "openai")
    if p == "huggingface":
        for cache in (
            Path.home() / ".cache" / "huggingface" / "token",
            Path.home() / ".huggingface" / "token",
        ):
            if cache.exists():
                v = cache.read_text(encoding="utf-8").strip()
                if v:
                    return v
    info = PROVIDERS.get(p)
    return carregar_var(info["var"], arquivo=BASE_DIR / ".env") if info else None


def criar_cliente(modelo=None, provider=None):
    try:
        from openai import OpenAI
    except ImportError:
        print("ERRO: pacote 'openai' nao instalado. Rode: pip install openai")
        sys.exit(1)
    p = norm_provider(provider) or ("openrouter" if "/" in (modelo or "") else "openai")
    chave = carregar_api_key(modelo, p)
    if not chave:
        print("ERRO: chave de API nao encontrada para provider '%s'." % p)
        sys.exit(1)
    info = PROVIDERS[p]
    if info["base_url"]:
        headers = {}
        if p == "openrouter":
            headers = {"HTTP-Referer": "https://localhost:7000", "X-Title": "TRONIX"}
        return OpenAI(api_key=chave, base_url=info["base_url"], default_headers=headers)
    return OpenAI(api_key=chave)


def listar_modelos(provider=None):
    try:
        from openai import OpenAI
        p = norm_provider(provider) or "openai"
        chave = carregar_api_key(p, p)
        if not chave:
            print("ERRO: chave nao encontrada para", p)
            return
        info = PROVIDERS[p]
        client = OpenAI(api_key=chave, base_url=info["base_url"]) if info["base_url"] else OpenAI(api_key=chave)
        for m in client.models.list().data:
            print(m.id)
    except Exception as e:
        print(f"ERRO: {e}")


FALLBACKS = [
    ("huggingface", "Qwen/Qwen3-32B"),
    ("huggingface", "openai/gpt-oss-120b"),
    ("openai", "qwen2.5-coder:7b"),
    ("openai", "qwen2.5:7b"),
]


def _tentar(prompt, modelo, esforco, instrucoes, p):
    from openai import OpenAI
    if p == "openai":
        base = carregar_var("OPENAI_BASE_URL") or "http://localhost:11434/v1"
        client = OpenAI(api_key=carregar_api_key(modelo, p) or "ollama", base_url=base)
    else:
        client = criar_cliente(modelo, p)
    kwargs = dict(model=modelo, reasoning={"effort": esforco}, input=prompt)
    if instrucoes:
        kwargs["instructions"] = instrucoes
    try:
        resp = client.responses.create(**kwargs)
        texto = getattr(resp, "output_text", None)
        if texto is None:
            texto = "".join(
                s.get("text", "") for s in resp.output if s.get("type") == "message"
            )
    except Exception:
        r = client.chat.completions.create(
            model=modelo,
            messages=[
                {"role": "system", "content": instrucoes or "Voce e o TRONIX."},
                {"role": "user", "content": prompt},
            ],
        )
        texto = r.choices[0].message.content
    return (texto or "").strip()


def gerar(prompt, modelo=None, esforco="medium", instrucoes=None, provider=None):
    """Retorna o texto gerado (em vez de imprimir). Com fallback automatico de provider/modelo."""
    p = norm_provider(provider)
    if not modelo:
        if p == "huggingface":
            modelo = "Qwen/Qwen3-32B"
        elif p == "nim":
            modelo = "nvidia/nemotron-3-super-120b-a12b"
        else:
            modelo = "gpt-6-astra"
    cadeia = [(p, modelo)]
    for fp, fm in FALLBACKS:
        if (fp, fm) not in cadeia:
            cadeia.append((fp, fm))
    erros = []
    for fp, fm in cadeia:
        if not carregar_api_key(fm, fp):
            erros.append(f"{fp}/{fm} (sem chave)")
            continue
        try:
            return _tentar(prompt, fm, esforco, instrucoes, fp)
        except Exception as e:
            erros.append(f"{fp}/{fm} ({type(e).__name__}: {str(e)[:120]})")
    raise RuntimeError("gerar() sem provider disponivel. Tentativas: " + " | ".join(erros))


def enviar(prompt, modelo, esforco, instrucoes, provider=None):
    try:
        print(gerar(prompt, modelo, esforco, instrucoes, provider))
    except Exception as e:
        print(f"ERRO: {e}")
        sys.exit(1)


def main():
    ap = argparse.ArgumentParser(description="TRONIX GPT-6 Astra")
    ap.add_argument("pergunta", nargs="?", default=None)
    ap.add_argument("--modelo", default="gpt-6-astra")
    ap.add_argument("--provider", choices=["openai", "openrouter", "nim", "huggingface", "hf"], default=None)
    ap.add_argument("--esforco", choices=["low", "medium", "high", "xhigh", "max"], default="medium")
    ap.add_argument("--instrucoes", default=None)
    ap.add_argument("--modo", choices=["chat", "revisar", "relay"], default="chat")
    ap.add_argument("--contexto", default="", help="Contexto extra para modos revisar/relay")
    ap.add_argument("--listar-modelos", action="store_true")
    args = ap.parse_args()

    if args.listar_modelos:
        listar_modelos(args.provider)
        return

    if not args.pergunta:
        ap.print_help()
        return

    if args.modo == "revisar":
        prompt = PROMPT_REVISOR.format(goal=args.pergunta, context=args.contexto or "(nao informado)")
    elif args.modo == "relay":
        prompt = PROMPT_RELAY_ENTENDER.format(goal=args.pergunta, context=args.contexto or "(nao informado)")
    else:
        prompt = args.pergunta

    enviar(prompt, args.modelo, args.esforco, args.instrucoes, args.provider)


if __name__ == "__main__":
    main()