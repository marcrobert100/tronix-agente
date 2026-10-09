"""Cliente Windows pro modelo que roda no Kaggle (via tunel Cloudflare).

Uso:
    python cliente.py "sua pergunta"
    python cliente.py --url https://xxxx.trycloudflare.com --listar
    python cliente.py --url https://xxxx.trycloudflare.com "crie um hello.py"

Le a URL do arquivo tunnel_url.txt (copiado do Kaggle) se --url nao for informado.
"""
import sys, os, json, urllib.request, argparse

AQUI = os.path.dirname(os.path.abspath(__file__))
ARQ_URL = os.path.join(AQUI, "tunnel_url.txt")


def carregar_url(arg=None):
    if arg:
        return arg.rstrip("/")
    if os.path.exists(ARQ_URL):
        with open(ARQ_URL, encoding="utf-8") as f:
            u = f.read().strip()
        if u:
            return u.rstrip("/")
    sys.exit("URL nao informada. Use --url https://xxxx.trycloudflare.com")


def get(url, timeout=30):
    req = urllib.request.Request(url, headers={"Authorization": "Bearer ollama"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def erro(exc):
    sys.exit("\nFALHOU: %s\nConfere: a celula do tunel no Kaggle ainda esta rodando? "
             "A URL trycloudflare morre quando a celula para." % exc)


def listar(url):
    dados = get(url + "/api/tags")
    for m in dados.get("models", []):
        print("  %-28s %6.1f GB" % (m["name"], m.get("size", 0) / 1e9))
    if not dados.get("models"):
        print("  (nenhum modelo instalado no Kaggle)")


def chat(url, prompt, modelo, stream=False):
    corpo = json.dumps({
        "model": modelo, "prompt": prompt, "stream": False,
        "options": {"temperature": 0.2, "num_ctx": 8192},
    }).encode("utf-8")
    req = urllib.request.Request(
        url + "/api/generate", data=corpo,
        headers={"Content-Type": "application/json", "Authorization": "Bearer ollama"})
    with urllib.request.urlopen(req, timeout=600) as r:
        resp = json.loads(r.read().decode("utf-8", "replace"))
    return resp.get("response", "").strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pergunta", nargs="*")
    ap.add_argument("--url", default=os.environ.get("KAGGLE_TUNNEL_URL"))
    ap.add_argument("--modelo", default=os.environ.get("KAGGLE_MODEL", "qwen3-coder:30b"))
    ap.add_argument("--listar", action="store_true")
    a = ap.parse_args()

    url = carregar_url(a.url)
    print(">> tunel:", url)

    try:
        if a.listar:
            listar(url)
            return

        if not a.pergunta:
            ap.print_help()
            return

        print(">> modelo:", a.modelo)
        print("-" * 60)
        print(chat(url, " ".join(a.pergunta), a.modelo))
        print("-" * 60)
    except Exception as exc:
        erro(exc)


if __name__ == "__main__":
    main()
