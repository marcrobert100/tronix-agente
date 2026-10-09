"""Le o log ao vivo do kernel Kaggle em execucao e procura a URL do tunel.

    python live_log.py                      # stream uma vez
    python live_log.py --esperar            # fica ate achar TRONIX_URL=
    python live_log.py --esperar --min 30
"""
import os, re, sys, time, io

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
from kaggle.api.kaggle_api_extended import KaggleApi

REF = "pontinhodainformtica/tronix-ollama-gpu-32gb-tunel-cloudflare"
AQUI = os.path.dirname(os.path.abspath(__file__))
ARQ = os.path.join(AQUI, "tunnel_url.txt")
TMP = os.path.join(AQUI, "live_stream.txt")

esperar = "--esperar" in sys.argv
minutos = 30
if "--min" in sys.argv:
    minutos = int(sys.argv[sys.argv.index("--min") + 1])

api = KaggleApi()
api.authenticate()

acum = []
fim = time.time() + minutos * 60 if esperar else time.time() + 240
url = None

while time.time() < fim:
    try:
        for ev in api.kernels_logs_stream(REF):
            d = ev.get("data", "")
            acum.append(d)
            sys.stdout.write(d)
            sys.stdout.flush()
            m = re.search(r"https://[a-z0-9\-]+\.trycloudflare\.com", d)
            if m:
                url = m.group(0)
                break
    except Exception as e:
        print("\n[stream encerrado: %s %s]" % (type(e).__name__, str(e)[:160]), flush=True)

    io.open(TMP, "w", encoding="utf-8").write("".join(acum))
    if url:
        break
    if not esperar:
        break
    time.sleep(20)

if url:
    io.open(ARQ, "w", encoding="utf-8").write(url)
    print("\n" + "#" * 60)
    print("#  TUNEL ATIVO: %s" % url)
    print("#  salvo em %s" % ARQ)
    print("#" * 60)
    sys.exit(0)

print("\nsem URL ainda. Log completo em %s" % TMP)
sys.exit(2)
