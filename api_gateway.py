import os, sys, json, subprocess, importlib.util, inspect
from datetime import datetime
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import aiohttp
import sqlite3

ROOT = Path(__file__).parent
DB_PATH = ROOT / "tronix.db"
MEMORIA_PATH = ROOT / "memoria_tronix.json"
CORE_PATH = ROOT / "tronix_core.json"
SCRIPTS_DIR = ROOT

sys.path.insert(0, str(ROOT))
from tronix_logger import inicializar as db_init, log_pipeline, registrar as db_registrar

@asynccontextmanager
async def lifespan(app: FastAPI):
    db_init()
    log_pipeline("GATEWAY", "api_gateway.py", "sucesso", "API Gateway iniciado")
    yield
    log_pipeline("GATEWAY", "api_gateway.py", "sucesso", "API Gateway encerrado")

app = FastAPI(title="Tronix API Gateway", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def carregar_memoria():
    with open(MEMORIA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_acao(agente, acao):
    mem = carregar_memoria()
    novo_id = max(a["id"] for a in mem["last_actions"]) + 1 if mem["last_actions"] else 1
    mem["last_actions"].append({
        "id": novo_id, "agente": agente, "acao": acao,
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    })
    with open(MEMORIA_PATH, "w", encoding="utf-8") as f:
        json.dump(mem, f, indent=2, ensure_ascii=False)
    return novo_id

def descobrir_scripts():
    scripts = []
    for f in sorted(SCRIPTS_DIR.glob("*.py")):
        if f.name.startswith("_"):
            continue
        if f.name in ("api_gateway.py", "tronix_logger.py", "tronix_crew.py"):
            continue
        scripts.append({
            "nome": f.stem,
            "arquivo": f.name,
            "caminho": str(f),
            "modificado": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
        })
    return scripts

def descobrir_ferramentas_visuais():
    core = json.load(open(CORE_PATH, encoding="utf-8"))
    return core.get("ferramentas_visuais", {})

# --- Models ---

class ExecutarRequest(BaseModel):
    script: str
    args: str = ""
    agente: str = "Gateway"

class MemoriaRequest(BaseModel):
    agente: str
    acao: str

class LogRequest(BaseModel):
    acao: str
    script: Optional[str] = None
    status: str = "sucesso"
    mensagem: str = ""

class N8nDisparoRequest(BaseModel):
    workflow_id: Optional[str] = None
    payload: dict = {}

class ConteudoRequest(BaseModel):
    tipo: str
    titulo: str
    arquivo: str
    pasta: str = "uploads"
    legenda: str = ""
    hashtags: str = ""
    voz_usada: str = ""
    tamanho_kb: int = 0
    duracao_seg: int = 0

# --- Endpoints ---

@app.get("/")
async def root():
    return {
        "sistema": "Tronix API Gateway",
        "versao": "1.0.0",
        "status": "online",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    status = {"gateway": "online", "timestamp": datetime.now().isoformat()}

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("SELECT 1")
        conn.close()
        status["banco"] = "online"
    except Exception as e:
        status["banco"] = f"erro: {e}"

    n8n_ok = False
    try:
        async with aiohttp.ClientSession() as s:
            r = await s.get("http://localhost:5678/health", timeout=2)
            n8n_ok = r.status == 200
    except Exception:
        pass
    status["n8n"] = "online" if n8n_ok else "offline"

    status["scripts_disponiveis"] = len(descobrir_scripts())
    return status

@app.get("/agentes")
async def listar_agentes():
    core = json.load(open(CORE_PATH, encoding="utf-8"))
    agentes = core.get("multi_agente", {}).get("agentes", [])
    memoria = carregar_memoria()
    ultimas_acoes = {}
    for a in agentes:
        for acao in reversed(memoria["last_actions"]):
            if acao["agente"] == f"Tronix-{a}" or acao["agente"] == a:
                ultimas_acoes[a] = acao
                break
    return {
        "framework": core.get("multi_agente", {}).get("framework", "CrewAI"),
        "processo": core.get("multi_agente", {}).get("processo", "hierarchical"),
        "agentes": [{
            "nome": a,
            "ultima_acao": ultimas_acoes.get(a, {}).get("acao", "Nenhuma"),
            "ultimo_timestamp": ultimas_acoes.get(a, {}).get("timestamp", "")
        } for a in agentes]
    }

@app.get("/scripts")
async def listar_scripts():
    return {"scripts": descobrir_scripts(), "total": len(descobrir_scripts())}

@app.get("/ferramentas")
async def listar_ferramentas():
    return descobrir_ferramentas_visuais()

@app.post("/executar")
async def executar(req: ExecutarRequest):
    script_path = SCRIPTS_DIR / f"{req.script}.py"
    if not script_path.exists():
        raise HTTPException(400, f"Script '{req.script}.py' nao encontrado")

    log_pipeline("EXECUTAR", req.script, "sucesso", f"Agente: {req.agente}, args: {req.args}")
    salvar_acao(req.agente, f"EXECUTOU: {req.script}.py {req.args}")

    try:
        cmd = f"python \"{script_path}\" {req.args}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=ROOT, timeout=300)
        output = (result.stdout + result.stderr)[-3000:]
        status = "sucesso" if result.returncode == 0 else "erro"
        log_pipeline("EXECUTAR", req.script, status, output[:200])
        return {"status": status, "returncode": result.returncode, "output": output}
    except subprocess.TimeoutExpired:
        log_pipeline("EXECUTAR", req.script, "erro", "Timeout 300s")
        raise HTTPException(504, "Script excedeu timeout de 300s")
    except Exception as e:
        log_pipeline("EXECUTAR", req.script, "erro", str(e))
        raise HTTPException(500, str(e))

@app.post("/memoria")
async def escrever_memoria(req: MemoriaRequest):
    salvar_acao(req.agente, req.acao)
    return {"status": "ok", "agente": req.agente, "acao": req.acao}

@app.get("/memoria")
async def ler_memoria(limit: int = Query(20, ge=1, le=200)):
    mem = carregar_memoria()
    return {
        "identity": mem.get("identity"),
        "version": mem.get("version"),
        "status": mem.get("status"),
        "ultimas_acoes": mem["last_actions"][-limit:]
    }

@app.post("/log")
async def registrar_log(req: LogRequest):
    log_pipeline(req.acao, req.script, req.status, req.mensagem)
    return {"status": "ok"}

@app.get("/dashboard/stats")
async def dashboard_stats():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        total = c.execute("SELECT COUNT(*) FROM conteudo").fetchone()[0]
        pendentes = c.execute("SELECT COUNT(*) FROM conteudo WHERE status_post='pendente'").fetchone()[0]
        postados = c.execute("SELECT COUNT(*) FROM conteudo WHERE status_post='postado'").fetchone()[0]
        hoje = c.execute("SELECT COUNT(*) FROM conteudo WHERE DATE(data_criacao) = DATE('now')").fetchone()[0]
        kb_hoje = c.execute("SELECT SUM(tamanho_kb) FROM conteudo WHERE DATE(data_criacao) = DATE('now')").fetchone()[0] or 0
        total_kb = c.execute("SELECT SUM(tamanho_kb) FROM conteudo").fetchone()[0] or 0

        logs = [dict(r) for r in c.execute("SELECT * FROM pipeline_log ORDER BY data DESC LIMIT 10").fetchall()]
        conteudos = [dict(r) for r in c.execute("SELECT * FROM conteudo ORDER BY data_criacao DESC LIMIT 20").fetchall()]
        conn.close()

        return {
            "stats": {
                "total": total, "pendentes": pendentes, "postados": postados,
                "hoje": hoje, "kb_hoje": kb_hoje, "total_kb": total_kb
            },
            "logs": logs,
            "conteudos": conteudos
        }
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/conteudo")
async def criar_conteudo(req: ConteudoRequest):
    id_ = db_registrar(req.tipo, req.titulo, req.arquivo, req.pasta,
                       req.legenda, req.hashtags, req.voz_usada,
                       req.tamanho_kb, req.duracao_seg)
    if id_:
        return {"status": "ok", "id": id_}
    raise HTTPException(500, "Erro ao registrar conteudo")

@app.post("/n8n/disparar")
async def disparar_n8n(req: N8nDisparoRequest):
    webhook_id = req.workflow_id or "tronix-pipeline"
    try:
        async with aiohttp.ClientSession() as s:
            url = f"http://localhost:5678/webhook/{webhook_id}"
            r = await s.post(url, json=req.payload, timeout=30)
            body = await r.text()
            status = "sucesso" if r.status == 200 else "erro"
            log_pipeline("N8N_DISPARO", webhook_id, status, body[:200])
            return {"status": status, "http_status": r.status, "resposta": body[:1000]}
    except Exception as e:
        log_pipeline("N8N_DISPARO", webhook_id, "erro", str(e))
        raise HTTPException(502, f"Erro ao conectar n8n: {e}")

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8081
    print(f"\n  [Gateway] Tronix API Gateway rodando em http://localhost:{port}")
    print(f"  [Gateway] Endpoints: /health /agentes /scripts /executar /memoria /dashboard/stats /n8n/disparar\n")
    uvicorn.run(app, host="0.0.0.0", port=port)
