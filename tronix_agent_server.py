"""
Tronix Agent Server — ferramentas locais pro chat com função (Ollama).
Porta 8000. Fornece: saldo Kie, listar scripts, memória, status, executar script.
"""
import json
import os
import subprocess
import time
from pathlib import Path
from urllib.request import urlopen, Request

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

BASE = Path(__file__).resolve().parent
API_BASE = "https://api.kie.ai"

app = FastAPI(title="Tronix Agent Server")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_kie_key():
    env = BASE / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.startswith("KIE_API_KEY="):
                return line.split("=", 1)[1].strip()
    return os.environ.get("KIE_API_KEY", "")

@app.get("/tools/kie_balance")
def kie_balance():
    key = get_kie_key()
    if not key:
        return {"ok": False, "erro": "KIE_API_KEY nao encontrada no .env"}
    try:
        req = urlopen(
            Request(
                f"{API_BASE}/api/v1/chat/credit",
                headers={"Authorization": f"Bearer {key}"},
            ),
            timeout=30,
        )
        j = json.loads(req.read())
        if j.get("code") == 200:
            return {"ok": True, "saldo": j["data"]}
        return {"ok": False, "erro": f"{j.get('code')} {j.get('msg')}"}
    except Exception as e:
        return {"ok": False, "erro": str(e)}

@app.get("/tools/scripts")
def listar_scripts():
    padroes = ("*.py", "*.bat", "*.ps1")
    scripts = []
    for p in sorted(BASE.glob("*.py")):
        scripts.append(p.name)
    for p in sorted(BASE.glob("*.bat")):
        scripts.append(p.name)
    return {"ok": True, "total": len(scripts), "scripts": scripts}

@app.get("/tools/memoria")
def memoria():
    m = BASE / "memoria_tronix.json"
    if not m.exists():
        raise HTTPException(404, "memoria nao encontrada")
    j = json.loads(m.read_text(encoding="utf-8"))
    acoes = j.get("last_actions", [])[-5:]
    return {
        "ok": True,
        "status": j.get("status"),
        "versao": j.get("version"),
        "ultimas_acoes": [f"{a.get('agente')}: {a.get('acao')}" for a in acoes],
    }

@app.get("/tools/status")
def status():
    def check(porta, nome):
        try:
            urlopen(f"http://localhost:{porta}/", timeout=2)
            return f"{nome}: ON"
        except Exception:
            return f"{nome}: OFF"
    return {"ok": True, "servicos": [check(8081, "Gateway"), check(11434, "Ollama"), check(80, "Apache")]}

SCRIPT_PERMITIDOS = {
    "tronix_kie.py": ["status"],
    "tronix_super_editor.py": [],
    "gerar_mini_novela.py": [],
    "mini_novela.py": [],
}

class Exec(BaseModel):
    script: str
    args: str = ""

class ChatMsg(BaseModel):
    role: str
    content: str = ""
    tool_calls: list = None
    tool_call_id: str = None

class ChatReq(BaseModel):
    messages: list
    tools: list = None
    model: str = "openai/gpt-oss-20b:free"

OPENROUTER_MODEL = "openai/gpt-oss-20b:free"

def get_openrouter_key():
    env = BASE / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.startswith("OPENROUTER_API_KEY="):
                return line.split("=", 1)[1].strip()
    return os.environ.get("OPENROUTER_API_KEY", "")

@app.post("/chat")
def chat(c: ChatReq):
    key = get_openrouter_key()
    if not key:
        return {"ok": False, "erro": "OPENROUTER_API_KEY nao encontrada no .env"}
    payload = {"model": c.model, "messages": [m if isinstance(m, dict) else m.dict(exclude_none=True) for m in c.messages]}
    if c.tools:
        payload["tools"] = c.tools
    req = Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urlopen(req, timeout=180) as resp:
            j = json.loads(resp.read())
        msg = j["choices"][0]["message"]
        return {"ok": True, "message": msg}
    except Exception as ex:
        return {"ok": False, "erro": str(ex)}

@app.post("/tools/executar")
def executar(e: Exec):
    if e.script not in SCRIPT_PERMITIDOS:
        raise HTTPException(403, f"Script nao permitido: {e.script}")
    args = [a for a in e.args.split() if a]
    for a in args:
        if a.startswith(("--key=", "-k=")):
            raise HTTPException(403, "Argumento bloqueado")
    try:
        r = subprocess.run(
            ["python", e.script, *args],
            capture_output=True, text=True, timeout=300, cwd=BASE,
        )
        out = (r.stdout or "")[-1500:]
        if r.returncode != 0:
            out += (r.stderr or "")[-500:]
        return {"ok": r.returncode == 0, "saida": out.strip()}
    except subprocess.TimeoutExpired:
        return {"ok": False, "saida": "TIMEOUT (300s)"}
    except Exception as ex:
        return {"ok": False, "saida": str(ex)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
