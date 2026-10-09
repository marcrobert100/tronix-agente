# ==========================================================================
#  KAGGLE -> OLLAMA -> TUNEL CLOUDFLARE -> VS CODE (Windows)
#  Script de 1 celula. Cole num Kaggle Notebook (Python) e rode.
#
#  No painel Settings do notebook:
#    Internet: ON
#    Accelerator: GPU T4 x2  (a API do Kaggle ja entrega 2x T4 = 30 GB)
#
# fim: o script NAO termina. Ele fica de guarda com o tunel no ar.
#  Para encerrar:  python subir_kernel.py --parar
# ==========================================================================
import subprocess, os, re, time, json, shutil

CADEIA = [("qwen3-coder:30b", 22.0),   # ~19 GB  (sobe o 30B)
          ("qwen3:14b", 11.0),         # ~9 GB
          ("qwen3:8b", 6.0)]          # ~5 GB  (sempre cabe)
RAIZ = "/kaggle/working/ollama"       # /kaggle/working PERSISTE entre sessoes
ALVO = "http://localhost:11434"
CF = "/kaggle/working/cloudflared"


def sh(cmd, show=3000):
    print("\n$ %s" % cmd, flush=True)
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.stdout.strip():
        print(r.stdout[-show:], flush=True)
    if r.returncode != 0:
        print("[rc=%s] %s" % (r.returncode, (r.stderr or "")[-show:]), flush=True)
    return r


def onde_esta_ollama():
    for c in (shutil.which("ollama"), "/usr/local/bin/ollama",
              os.path.expanduser("~/.ollama/bin/ollama"),
              "/root/.ollama/bin/ollama"):
        if c and os.path.exists(c):
            return c
    return None


# ------------------------------------------------------------------ 1) GPU
print("=" * 60)
print("1) VERIFICANDO GPU")
print("=" * 60)
sh("nvidia-smi --query-gpu=name,memory.total --format=csv,noheader")

try:
    txt = subprocess.run("nvidia-smi --query-gpu=memory.total --format=csv,noheader",
                         shell=True, capture_output=True, text=True).stdout
    mibs = [int(x) for x in re.findall(r"(\d+)\s*MiB", txt)]
except Exception as e:
    print("erro lendo VRAM:", e)
    mibs = []
total_gb = sum(mibs) / 1024.0
print("\nVRAM total: %.1f GB em %d GPU(s)" % (total_gb, len(mibs)))

MODELO = CADEIA[-1][0]
for nome, precisa in CADEIA:
    if total_gb >= precisa:
        MODELO = nome
        break
if not mibs:
    print("!!! NENHUM GPU DETECTADO - o Accelerator nao esta ligado.")
    print("!!! Indo assim mesmo com %s, mas provavelmente vai falhar." % MODELO)
print("Modelo escolhido: %s" % MODELO)

# ------------------------------------------------------- 2) zstd (exigido!)
print("\n" + "=" * 60)
print("2) INSTALANDO zstd (o install.sh do ollama EXIGE esse binario)")
print("=" * 60)
sh("apt-get update -qq 2>&1 | tail -2")
r = sh("DEBIAN_FRONTEND=noninteractive apt-get install -y -qq zstd 2>&1 | tail -5")
if sh("zstd --version", show=200).returncode != 0:
    print("!!! zstd continua faltando - o install do ollama vai falhar.")
sh("pip install -q zstandard 2>&1 | tail -2")

# ------------------------------------------------------------------ 3) ollama
print("\n" + "=" * 60)
print("3) INSTALANDO OLLAMA")
print("=" * 60)
sh("curl -fsSL https://ollama.com/install.sh | sh 2>&1 | tail -12")

OLLAMA = onde_esta_ollama()
if not OLLAMA:
    print("\n!!! ollama NAO instalado. Baixando o binario direto como plano B.")
    sh("mkdir -p /usr/local/bin && curl -fsSL -o /usr/local/bin/ollama "
       "https://ollama.com/download/ollama-linux-amd64.tgz 2>/dev/null || true")
    OLLAMA = onde_esta_ollama()
if not OLLAMA:
    raise SystemExit("FALHOU: nao achei o binario do ollama.Veja o log acima.")
print("ollama em: %s" % OLLAMA)
sh("%s --version" % OLLAMA, show=200)

# -------------------------------------------------------------- 4) servidor
print("\n" + "=" * 60)
print("4) SUBINDO O SERVIDOR OLLAMA em 0.0.0.0:11434")
print("=" * 60)
os.makedirs(RAIZ, exist_ok=True)
env = os.environ.copy()
env["OLLAMA_HOST"] = "0.0.0.0:11434"
env["OLLAMA_MODELS"] = RAIZ + "/models"
env["OLLAMA_KEEP_ALIVE"] = "-1"
env["PATH"] = os.path.dirname(OLLAMA) + ":" + env.get("PATH", "")

log_srv = open(os.path.join(RAIZ, "ollama.log"), "w")
subprocess.Popen([OLLAMA, "serve"], env=env, stdout=log_srv,
                 stderr=subprocess.STDOUT, start_new_session=True)

for i in range(40):
    time.sleep(2)
    if subprocess.run("curl -sf %s/api/version" % ALVO, shell=True,
                      capture_output=True).returncode == 0:
        break
    print("  aguardando ollama... %ds" % ((i + 1) * 2), flush=True)
else:
    print(open(os.path.join(RAIZ, "ollama.log")).read()[-1500:])
    raise SystemExit("FALHOU: o servidor do ollama nao subiu.")
sh("curl -s %s/api/version" % ALVO)
print("Ollama started.")

# ----------------------------------------------------------------- 5) modelo
print("\n" + "=" * 60)
print("5) BAIXANDO O MODELO %s (pode levar 5-15 min)" % MODELO)
print("=" * 60)
NOMES = [n for n, _ in CADEIA]
r = sh("%s pull %s" % (OLLAMA, MODELO), show=1200)
if r.returncode != 0:
    for nome in NOMES[NOMES.index(MODELO) + 1:]:
        print("\n>>> pull falhou, tentando %s" % nome, flush=True)
        MODELO = nome
        r = sh("%s pull %s" % (OLLAMA, MODELO), show=1200)
        if r.returncode == 0:
            break
else:
    print("\n>>> pulando os fallbacks, %s ja caberia na VRAM" % MODELO)
sh("%s list" % OLLAMA)

# ------------------------------------------------------------ 6) teste local
print("\n" + "=" * 60)
print("6) TESTE LOCAL (tem que dar HTTP 200)")
print("=" * 60)
sh("curl -s -o /dev/null -w 'HTTP status: %%{http_code}\\n' %s/api/tags" % ALVO)
sh("""curl -s %s/api/generate -d '{"model":"%s","prompt":"Responda so: OK","stream":false,"options":{"num_predict":8}}'""" % (ALVO, MODELO), show=400)

# ------------------------------------------------------------- 7) cloudflared
print("\n" + "=" * 60)
print("7) CLOUDFLARED + TUNEL PUBLICO")
print("=" * 60)
sh("curl -L --output %s https://github.com/cloudflare/cloudflared/releases/latest/"
   "download/cloudflared-linux-amd64" % CF, show=300)
sh("chmod +x %s && %s --version" % (CF, CF), show=300)

log_tun = open(os.path.join(RAIZ, "tunnel.log"), "w")
proc = subprocess.Popen([CF, "tunnel", "--no-autoupdate", "--url", ALVO],
                        stdout=log_tun, stderr=subprocess.STDOUT, start_new_session=True)

URL = None
for i in range(60):
    time.sleep(2)
    txt = open(os.path.join(RAIZ, "tunnel.log")).read()
    m = re.search(r"https://[a-z0-9\-]+\.trycloudflare\.com", txt)
    if m:
        URL = m.group(0)
        break
    print("  esperando URL... %ds" % ((i + 1) * 2), flush=True)

if not URL:
    print(open(os.path.join(RAIZ, "tunnel.log")).read()[-1500:])
    raise SystemExit("FALHOU: o tunel nao gerou URL.")

# ---------------------------------------------------------- 8) teste público
print("\n" + "=" * 60)
print("8) TESTE DA URL PUBLICA")
print("=" * 60)
sh("curl -s -o /dev/null -w 'HTTP status: %%{http_code}\\n' %s/api/tags" % URL)
sh("curl -s %s/api/tags | head -c 300" % URL)
io_url = os.path.join(RAIZ, "tunnel_url.txt")
open(io_url, "w").write(URL)

print("\n" + "#" * 62)
print("#  TRONIX_URL=%s" % URL)
print("#  modelo=%s  |  vram=%.1f GB" % (MODELO, total_gb))
print("#")
print("#  VS Code / Cline (OpenAI Compatible):")
print("#     Base URL : %s/v1" % URL)
print("#     API Key  : ollama")
print("#     Model    : %s" % MODELO)
print("#")
print("#  Qwen Code / aider / opencode:")
print("#     OLLAMA_HOST=%s" % URL)
print("#     OLLAMA_MODEL=%s" % MODELO)
print("#" * 62)
print("TRONIX_TUNEL_PRONTO", flush=True)

# ------------------------------------------------------- 9) fica de guarda
# Se a celula terminar, o Kaggle derruba a sessao e o tunel morre.
print("\n[guarda] tunel no ar. Ctrl+C ou 'kaggle kernels delete' para derrubar.", flush=True)
while True:
    time.sleep(120)
    if proc.poll() is not None:
        print("\n[guarda] o cloudflared MORREU, reiniciando...", flush=True)
        log_tun = open(os.path.join(RAIZ, "tunnel2.log"), "w")
        proc = subprocess.Popen([CF, "tunnel", "--no-autoupdate", "--url", ALVO],
                                stdout=log_tun, stderr=subprocess.STDOUT, start_new_session=True)
    print("[guarda] vivo %s | %s" % (time.strftime("%H:%M:%S"), URL), flush=True)
