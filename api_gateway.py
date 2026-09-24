import os, sys, json, subprocess, asyncio, uuid, time
from datetime import datetime
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import aiohttp
import sqlite3

ROOT = Path(__file__).parent
DB_PATH = ROOT / "tronix.db"
MEMORIA_PATH = ROOT / "memoria_tronix.json"
CORE_PATH = ROOT / "tronix_core.json"
SCRIPTS_DIR = ROOT
VERSION = "2.0.0"

sys.path.insert(0, str(ROOT))
from tronix_logger import inicializar as db_init, log_pipeline, registrar as db_registrar

background_tasks: dict[str, dict] = {}
websocket_clients: list[WebSocket] = []

async def broadcast(msg: dict):
    dead = []
    for ws in websocket_clients:
        try:
            await ws.send_json(msg)
        except Exception:
            dead.append(ws)
    for ws in dead:
        websocket_clients.remove(ws)

@asynccontextmanager
async def lifespan(app: FastAPI):
    db_init()
    log_pipeline("GATEWAY", "api_gateway.py", "sucesso", f"API Gateway v{VERSION} iniciado")
    yield
    log_pipeline("GATEWAY", "api_gateway.py", "sucesso", "API Gateway encerrado")

app = FastAPI(title="Tronix API Gateway", version=VERSION, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def carregar_memoria():
    with open(MEMORIA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_acao(agente, acao, suppress_broadcast=False):
    mem = carregar_memoria()
    novo_id = max(a["id"] for a in mem["last_actions"]) + 1 if mem["last_actions"] else 1
    entry = {
        "id": novo_id, "agente": agente, "acao": acao,
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    mem["last_actions"].append(entry)
    with open(MEMORIA_PATH, "w", encoding="utf-8") as f:
        json.dump(mem, f, indent=2, ensure_ascii=False)
    if not suppress_broadcast:
        asyncio.create_task(broadcast({"type": "memoria", "data": entry}))
    return novo_id

def descobrir_scripts():
    scripts = []
    for f in sorted(SCRIPTS_DIR.glob("*.py")):
        if f.name.startswith("_"):
            continue
        if f.name in ("api_gateway.py", "tronix_logger.py", "tronix_crew.py", "tronix_mcp_server.py"):
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

async def run_script_background(task_id: str, script: str, script_path: Path, args: str):
    try:
        start = time.time()
        cmd = f"python \"{script_path}\" {args}"
        proc = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=ROOT
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=600)
        elapsed = time.time() - start
        output = (stdout.decode(errors="replace") + stderr.decode(errors="replace"))[-3000:]
        status = "sucesso" if proc.returncode == 0 else "erro"
        background_tasks[task_id] = {
            "status": status, "returncode": proc.returncode, "output": output, "elapsed": round(elapsed, 2)
        }
        log_pipeline("EXECUTAR", script, status, output[:200])
        await broadcast({"type": "task_complete", "task_id": task_id, "status": status, "elapsed": round(elapsed, 2)})
    except asyncio.TimeoutError:
        background_tasks[task_id] = {"status": "timeout", "output": "Script excedeu timeout de 600s"}
        log_pipeline("EXECUTAR", script, "erro", "Timeout 600s")
        await broadcast({"type": "task_complete", "task_id": task_id, "status": "timeout"})
    except Exception as e:
        background_tasks[task_id] = {"status": "erro", "output": str(e)}
        log_pipeline("EXECUTAR", script, "erro", str(e))
        await broadcast({"type": "task_complete", "task_id": task_id, "status": "erro"})

@app.get("/")
async def root():
    return {
        "sistema": "Tronix API Gateway",
        "versao": VERSION,
        "status": "online",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    status = {"gateway": "online", "versao": VERSION, "timestamp": datetime.now().isoformat()}
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
    status["tasks_ativas"] = len([t for t in background_tasks.values() if t.get("status") in ("running",)])
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

    task_id = str(uuid.uuid4())[:8]
    background_tasks[task_id] = {"status": "running"}
    asyncio.create_task(run_script_background(task_id, req.script, script_path, req.args))

    return {
        "status": "disparado",
        "task_id": task_id,
        "script": req.script,
        "mensagem": f"Script {req.script}.py executando em background. Use GET /tasks/{task_id} para acompanhar."
    }

@app.get("/tasks/{task_id}")
async def task_status(task_id: str):
    task = background_tasks.get(task_id)
    if not task:
        raise HTTPException(404, "Task nao encontrada")
    return {"task_id": task_id, **task}

@app.get("/tasks")
async def list_tasks():
    return {
        "tasks": [{"task_id": tid, **t} for tid, t in list(background_tasks.items())[-50:]]
    }

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
        por_tipo = [dict(r) for r in c.execute("SELECT tipo, COUNT(*) as total, SUM(tamanho_kb) as kb FROM conteudo GROUP BY tipo").fetchall()]
        logs = [dict(r) for r in c.execute("SELECT * FROM pipeline_log ORDER BY data DESC LIMIT 20").fetchall()]
        conteudos = [dict(r) for r in c.execute("SELECT * FROM conteudo ORDER BY data_criacao DESC LIMIT 20").fetchall()]
        conn.close()
        return {
            "stats": {
                "total": total, "pendentes": pendentes, "postados": postados,
                "hoje": hoje, "kb_hoje": kb_hoje, "total_kb": total_kb,
                "por_tipo": por_tipo
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
        await broadcast({"type": "conteudo_novo", "id": id_, "titulo": req.titulo, "tipo": req.tipo})
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

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    websocket_clients.append(ws)
    try:
        await ws.send_json({"type": "connected", "versao": VERSION})
        while True:
            data = await ws.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await ws.send_json({"type": "pong"})
                elif msg.get("type") == "subscribe":
                    await ws.send_json({"type": "subscribed", "channel": msg.get("channel", "all")})
            except json.JSONDecodeError:
                await ws.send_json({"type": "error", "message": "JSON invalido"})
    except WebSocketDisconnect:
        pass
    finally:
        if ws in websocket_clients:
            websocket_clients.remove(ws)

@app.get("/ws-info")
async def ws_info():
    return {"clientes_conectados": len(websocket_clients)}

@app.get("/versao")
async def versao():
    core = json.load(open(CORE_PATH, encoding="utf-8"))
    return {
        "gateway": VERSION,
        "core": core.get("versao", "?"),
        "ultima_atualizacao": core.get("ultima_atualizacao", "?")
    }

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8081
    print(f"\n  [Gateway] Tronix API Gateway v{VERSION} rodando em http://localhost:{port}")
    print(f"  [Gateway] WebSocket: ws://localhost:{port}/ws")
    print(f"  [Gateway] Endpoints: /health /agentes /scripts /executar /tasks /memoria /dashboard/stats /n8n/disparar\n")
    uvicorn.run(app, host="0.0.0.0", port=port)
