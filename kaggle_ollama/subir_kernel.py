"""Sobe o notebook GPU do Kaggle via API e captura a URL do tunel.

    python subir_kernel.py            # cria/p atualiza e fica politando ate a URL
    python subir_kernel.py --parar    # deleta o kernel (para de gastar cota)

Requer: kaggle auth login feito.
"""
import io, json, os, re, subprocess, sys, time

AQUI = os.path.dirname(os.path.abspath(__file__))
PUSH = os.path.join(AQUI, "_push")
ARQ_URL = os.path.join(AQUI, "tunnel_url.txt")
SLUG = "tronix-ollama-gpu-32gb-tunel-cloudflare"  # tem que bater com o slug do titulo
TITULO = "TRONIX Ollama GPU 32GB (tunel Cloudflare)"


def kaggle(*args, **kw):
    r = subprocess.run(["kaggle"] + list(args), capture_output=True, text=True,
                       encoding="utf-8", errors="replace", **kw)
    return r


def meu_usuario():
    """Dono do kernel: credentials.json (fonte real) > CLI > env."""
    cred = os.path.join(os.path.expanduser("~"), ".kaggle", "credentials.json")
    if os.path.exists(cred):
        try:
            u = json.load(io.open(cred, encoding="utf-8")).get("username")
            if u:
                return u
        except Exception:
            pass
    r = kaggle("kernels", "list", "--mine", "--page-size", "1")
    m = re.search(r"([A-Za-z0-9\-_]+)/[A-Za-z0-9\-_]+", r.stdout or "")
    if m:
        return m.group(1)
    r = kaggle("config", "view")
    m = re.search(r"username[\"']?\s*[:=]\s*[\"']?([A-Za-z0-9\-_]+)", r.stdout or "")
    if m:
        return m.group(1)
    return os.environ.get("KAG_USERNAME", "pontinhodainformatica")


def preparar(ref_owner):
    os.makedirs(PUSH, exist_ok=True)
    src = os.path.join(AQUI, "kaggle_ollama.ipynb")
    dst = os.path.join(PUSH, "code.ipynb")
    nb = json.load(io.open(src, encoding="utf-8"))
    # markdown no push via API quebra a execucao do pipeline: fora
    nb["cells"] = [c for c in nb["cells"] if c.get("cell_type") == "code"]

    # BUG que custou 6 pushes: rstrip() tirava tambem o "\n" de cada linha,
    # "".join(source) virava UMA linha so. Como o script comeca com "#",
    # a celula inteira virava comentario: rodava e nao imprimia nada.
    # Aqui so removemos "\r" e garantimos o newline final de cada linha.
    for c in nb.get("cells", []):
        src = c.get("source", [])
        if isinstance(src, str):
            src = src.splitlines()
        linhas = [l.rstrip("\r") for l in src]
        c["source"] = [l + "\n" for l in linhas[:-1]] + ([linhas[-1]] if linhas else [])
        if c.get("cell_type") == "code":
            c["outputs"] = []
            c["execution_count"] = None

    io.open(dst, "w", encoding="utf-8").write(json.dumps(nb, ensure_ascii=False))
    meta = {
        "id": "%s/%s" % (ref_owner, SLUG),
        "title": TITULO,
        "code_file": "code.ipynb",
        "language": "python",
        "kernel_type": "notebook",
        "enable_gpu": True,
        "enable_internet": True,
        "is_private": True,
    }
    io.open(os.path.join(PUSH, "kernel-metadata.json"), "w", encoding="utf-8").write(
        json.dumps(meta, ensure_ascii=False, indent=1))
    return meta["id"]


def achar_url(ref, minutos=25):
    """Faz o push e fica olhando a saida do kernel ate achar a URL do tunel."""
    limite = time.time() + minutos * 60
    tentativa = 0
    while time.time() < limite:
        tentativa += 1
        r = kaggle("kernels", "status", ref)
        status = (r.stdout or r.stderr or "").strip()
        print("[%s] status: %s" % (time.strftime("%H:%M:%S"), status[:80]), flush=True)

        r = kaggle("kernels", "output", ref, "--file-pattern", "code.ipynb")
        texto = r.stdout or ""
        m = re.search(r"https://[a-z0-9\-]+\.trycloudflare\.com", texto)
        if m:
            io.open(ARQ_URL, "w", encoding="utf-8").write(m.group(0))
            return m.group(0)

        if "complete" in status.lower() or "error" in status.lower():
            log_txt = kaggle("kernels", "logs", ref).stdout or ""
            achou_stdout = '"stream_name":"stdout"' in log_txt or "TRONIX" in log_txt
            if tentativa > 2 and not achou_stdout:
                print("\nKernel parou sem executar as celulas. Log:")
                print(log_txt[-3000:])
                return None
            if tentativa > 2:
                print(log_txt[-3000:])
                return None
        time.sleep(30)
    return None


def sincronizar_opencode(caminho, url):
    """Reescreve provider.kaggle.options.baseURL num opencode.json, sem perder
    o resto do arquivo. Atomico: grava .tmp e substitui, pra nunca deixar
    config pela metade se der ctrl+c no meio."""
    if not os.path.exists(caminho):
        return None
    cfg = json.load(io.open(caminho, encoding="utf-8"))
    prov = cfg.get("provider", {}).get("kaggle")
    if not prov:
        return None
    novo = url + "/v1"
    if prov.get("options", {}).get("baseURL") == novo:
        return None
    prov.setdefault("options", {})["baseURL"] = novo
    tmp = caminho + ".tmp"
    json.dump(cfg, io.open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    io.open(tmp, "a", encoding="utf-8").write("\n")
    os.replace(tmp, caminho)
    return caminho


def propagar_url(url):
    """A URL do tunel muda a cada subida. Espalha para todo lugar que o opencode le:
    - config global (~/.config/opencode) -> funciona em qualquer pasta
    - opencode.json deste pacote e da copia do Desktop -> segue funcionando offline do env
    - variavel de ambiente do usuario, usada pelos .bat
    Sem isso o global fica apontando para um tunel morto e da UnknownError, ou o
    local fica com '{env:KAGGLE_TUNNEL_URL}' vazio e da 'cannot be parsed as a URL'."""
    avisos = []
    home = os.path.expanduser("~")

    alvos = [
        os.path.join(home, ".config", "opencode", "opencode.json"),
        os.path.join(AQUI, "opencode.json"),
        os.path.join(home, "Desktop", "Agente Kaggle GPU", "opencode.json"),
    ]
    for caminho in alvos:
        try:
            mudou = sincronizar_opencode(caminho, url)
            if mudou:
                avisos.append("%s -> %s/v1" % (mudou, url))
        except Exception as e:
            avisos.append("ERRO em %s (%s)" % (caminho, str(e)[:60]))

    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_SET_VALUE) as k:
            winreg.SetValueEx(k, "KAGGLE_TUNNEL_URL", 0, winreg.REG_SZ, url)
        avisos.append("variavel KAGGLE_TUNNEL_URL -> %s" % url)
    except Exception as e:
        avisos.append("variavel de ambiente NAO atualizada (%s)" % str(e)[:60])

    return avisos


def main():
    if "--ref" in sys.argv:
        i = sys.argv.index("--ref")
        ref = sys.argv[i + 1]
        print("ref:", ref)
        url = achar_url(ref)
        if url:
            print("TUNEL ATIVO: %s" % url)
            for a in propagar_url(url):
                print("  propagado:", a)
        else:
            sys.exit(2)
        return

    if "--parar" in sys.argv:
        dono = meu_usuario()
        ref = "%s/%s" % (dono, SLUG)
        r = kaggle("kernels", "delete", ref, "--yes")
        print("deletado:", ref)
        print((r.stdout or "") + (r.stderr or ""))
        return

    dono = meu_usuario()
    ref = preparar(dono)
    print("owner:", dono, "| kernel:", ref)
    r = kaggle("kernels", "push", "-p", PUSH)
    saida = (r.stdout or "") + (r.stderr or "")
    print(saida)
    if r.returncode != 0:
        print("PUSH FALHOU. Se pedir confirmacao de celular, faca no navegador:")
        print("  https://www.kaggle.com/settings")
        sys.exit(1)

    # o Kaggle deriva o slug do TITULO, entao usa a URL real devolvida no push
    m = re.search(r"kaggle\.com/code/([A-Za-z0-9\-_]+)/([A-Za-z0-9\-_]+)", saida)
    if m:
        ref = "%s/%s" % (m.group(1), m.group(2))
        print("ref real:", ref)

    print("\nRodando. Procurando a URL do tunel (pode levar 5-15 min no 1o download)...")
    url = achar_url(ref)
    if not url:
        sys.exit("Nao achei a URL. Olhe os logs do kernel no site.")

    print("\n" + "#" * 60)
    print("#  TUNEL ATIVO: %s" % url)
    print("#  salvo em %s" % ARQ_URL)
    print("#  VS Code/Cline  -> Base URL: %s/v1 | API Key: ollama" % url)
    print("#  opencode       -> /models  e escolha kaggle/qwen3-coder:30b")
    print("#  Ao terminar:  python subir_kernel.py --parar   (nao gasta cota)")
    print("#" * 60)
    for a in propagar_url(url):
        print("#  propagado: %s" % a)


if __name__ == "__main__":
    main()
