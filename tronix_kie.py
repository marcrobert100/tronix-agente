import os
import sys
import json
import time
import argparse
import requests
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE = Path(__file__).parent
API_BASE = "https://api.kie.ai"
UPLOAD_BASE = "https://kieai.redpandaai.co"

try:
    import tronix_logger as db
    db.inicializar()
except ImportError:
    db = None


def get_key():
    key = os.getenv("KIE_API_KEY", "").strip()
    if key:
        return key
    core = BASE / "tronix_core.json"
    if core.exists():
        try:
            data = json.loads(core.read_text(encoding="utf-8"))
            key = (data.get("api_keys") or {}).get("KIE_API_KEY") or ""
        except Exception:
            key = ""
    if not key:
        print("ERRO: KIE_API_KEY nao definida.")
        print("1. Login em https://kie.ai (conta Google ou email)")
        print("2. Crie key em: https://kie.ai/api-key")
        print('3. Adicione no .env: "KIE_API_KEY": "sua-key-aqui"')
    return key


def headers():
    return {
        "Authorization": f"Bearer {get_key()}",
        "Content-Type": "application/json",
    }


def creditos():
    r = requests.get(f"{API_BASE}/api/v1/chat/credit", headers=headers(), timeout=30)
    j = r.json()
    if j.get("code") == 200:
        print(f"Creditos restantes: {j.get('data')}")
        return j.get("data")
    print(f"ERRO: {j.get('code')} {j.get('msg')}")
    return None


def upload_arquivo(caminho, upload_path="tronix"):
    if not os.path.exists(caminho):
        print(f"ERRO: arquivo nao encontrado: {caminho}")
        return None
    with open(caminho, "rb") as f:
        r = requests.post(
            f"{UPLOAD_BASE}/api/file-stream-upload",
            headers={"Authorization": f"Bearer {get_key()}"},
            files={"file": (os.path.basename(caminho), f)},
            data={"uploadPath": upload_path},
            timeout=120,
        )
    j = r.json()
    if j.get("success"):
        url = j["data"]["fileUrl"]
        print(f"  Upload OK: {url}")
        return url
    print(f"ERRO upload: {j}")
    return None


def criar_tarefa(modelo, inp, callback_url=None):
    payload = {"model": modelo, "input": inp}
    if callback_url:
        payload["callBackUrl"] = callback_url
    r = requests.post(f"{API_BASE}/api/v1/jobs/createTask", headers=headers(), json=payload, timeout=60)
    j = r.json()
    if j.get("code") == 200:
        tid = j["data"]["taskId"]
        print(f"  Tarefa criada: {tid}")
        return tid
    print(f"ERRO criar tarefa: {j.get('code')} {j.get('msg')}")
    return None


def consultar(tid):
    r = requests.get(f"{API_BASE}/api/v1/jobs/recordInfo", headers=headers(), params={"taskId": tid}, timeout=30)
    j = r.json()
    if j.get("code") != 200:
        print(f"ERRO consulta: {j.get('code')} {j.get('msg')}")
        return None
    return j.get("data") or {}


def aguardar(tid, timeout=300, intervalo=5):
    inicio = time.time()
    while time.time() - inicio < timeout:
        data = consultar(tid)
        if data:
            state = data.get("state") or data.get("status")
            if isinstance(state, dict):
                state = state.get("state") or state.get("status")
            print(f"  [{int(time.time()-inicio)}s] state: {state}")
            if state == "success":
                return data
            if state in ("fail", "failed"):
                print(f"  FALHA: {data.get('failMsg') or data}")
                return data
        time.sleep(intervalo)
    print("  TIMEOUT aguardando conclusao.")
    return None


def extrair_urls(data):
    urls = []
    rj = data.get("resultJson")
    if rj:
        if isinstance(rj, str):
            try:
                rj = json.loads(rj)
            except Exception:
                rj = None
        if isinstance(rj, dict):
            for lista in (rj.get("resultUrls"), rj.get("result_urls"), rj.get("urls")):
                if isinstance(lista, list):
                    urls.extend(str(u) for u in lista if str(u).startswith("http"))
            for v2 in rj.values():
                if isinstance(v2, str) and v2.startswith("http"):
                    urls.append(v2)
                elif isinstance(v2, list):
                    urls.extend(str(i) for i in v2 if str(i).startswith("http"))
    for campo in ("output", "result", "results", "file_url", "video", "image"):
        v = data.get(campo)
        if isinstance(v, dict):
            for v2 in v.values():
                if isinstance(v2, str) and v2.startswith("http"):
                    urls.append(v2)
                elif isinstance(v2, list):
                    urls.extend(str(i) for i in v2 if str(i).startswith("http"))
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, str) and item.startswith("http"):
                    urls.append(item)
                elif isinstance(item, dict):
                    for v2 in item.values():
                        if isinstance(v2, str) and v2.startswith("http"):
                            urls.append(v2)
        elif isinstance(v, str) and v.startswith("http"):
            urls.append(v)
    seen = []
    for u in urls:
        if u not in seen:
            seen.append(u)
    return seen


def baixar(url, destino):
    r = requests.get(url, timeout=300)
    if r.status_code != 200:
        print(f"ERRO download {url}: {r.status_code}")
        return None
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with open(destino, "wb") as f:
        f.write(r.content)
    print(f"SUCESSO|{destino}")
    return str(destino)


def cmd_imagem(args):
    inp = {"prompt": args.prompt, "aspect_ratio": args.ar}
    tid = criar_tarefa("grok-imagine/text-to-image", inp)
    if not tid:
        return 1
    data = aguardar(tid, args.timeout)
    if not data:
        return 1
    urls = extrair_urls(data)
    if not urls:
        print(f"Sem URL no resultado. Dados: {json.dumps(data, ensure_ascii=False)[:500]}")
        return 1
    ts = int(time.time())
    destino = args.saida or (BASE / "uploads" / f"kie_img_{ts}.png")
    salvo = baixar(urls[0], destino)
    if salvo and db:
        db.registrar("imagem", f"Kie Grok Imagine - {args.prompt[:50]}", os.path.basename(salvo), "uploads",
                     legenda=args.prompt, hashtags="#kie #grokImagine #tronix")
    return 0


def cmd_video(args):
    inp = {"prompt": args.prompt, "duration": args.duracao, "resolution": args.res, "aspect_ratio": args.ar}
    modelo = "grok-imagine/text-to-video"
    if args.imagem:
        url_img = upload_arquivo(args.imagem)
        if not url_img:
            return 1
        inp["image_urls"] = [url_img]
        modelo = "grok-imagine/image-to-video"
    tid = criar_tarefa(modelo, inp)
    if not tid:
        return 1
    data = aguardar(tid, args.timeout)
    if not data:
        return 1
    urls = extrair_urls(data)
    if not urls:
        print(f"Sem URL no resultado. Dados: {json.dumps(data, ensure_ascii=False)[:500]}")
        return 1
    ts = int(time.time())
    destino = args.saida or (BASE / "videos_saida" / f"kie_video_{ts}.mp4")
    salvo = baixar(urls[0], destino)
    if salvo and db:
        db.registrar("video", f"Kie Grok Imagine - {args.prompt[:50]}", os.path.basename(salvo), "videos_saida",
                     legenda=args.prompt, hashtags="#kie #grokImagine #tronix",
                     duracao_seg=args.duracao)
    return 0


def main():
    p = argparse.ArgumentParser(description="Tronix - Kie.ai Grok Imagine")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_img = sub.add_parser("imagem", help="Texto -> Imagem (Grok Imagine)")
    p_img.add_argument("--prompt", required=True)
    p_img.add_argument("--ar", default="16:9", choices=["2:3", "3:2", "1:1", "16:9", "9:16"])
    p_img.add_argument("--saida", default=None)
    p_img.add_argument("--timeout", type=int, default=300)
    p_img.set_defaults(fn=cmd_imagem)

    p_vid = sub.add_parser("video", help="Texto/Imagem -> Video (Grok Imagine)")
    p_vid.add_argument("--prompt", required=True)
    p_vid.add_argument("--imagem", default=None, help="Imagem local p/ image-to-video")
    p_vid.add_argument("--ar", default="16:9", choices=["2:3", "3:2", "1:1", "16:9", "9:16"])
    p_vid.add_argument("--duracao", type=int, default=8)
    p_vid.add_argument("--res", default="720p", choices=["480p", "720p"])
    p_vid.add_argument("--saida", default=None)
    p_vid.add_argument("--timeout", type=int, default=600)
    p_vid.set_defaults(fn=cmd_video)

    p_s = sub.add_parser("status", help="Consultar saldo de creditos")
    p_s.add_argument("--task", default=None, help="TaskId p/ consultar status")
    p_s.set_defaults(fn=lambda a: consultar(a.task) if a.task else creditos())

    p_b = sub.add_parser("baixar", help="Baixar resultado de task ja concluida")
    p_b.add_argument("--task", required=True)
    p_b.add_argument("--saida", default=None)
    p_b.set_defaults(fn=lambda a: _baixar_task(a))

    args = p.parse_args()
    sys.exit(args.fn(args))


def _baixar_task(args):
    data = consultar(args.task)
    if not data:
        return 1
    urls = extrair_urls(data)
    if not urls:
        print(json.dumps(data, ensure_ascii=False)[:800])
        return 1
    ts = int(time.time())
    destino = args.saida or (BASE / "downloads" / f"kie_{ts}.bin")
    baixar(urls[0], destino)
    return 0


if __name__ == "__main__":
    main()
