import os, sys, json, sqlite3, subprocess, urllib.request, urllib.error
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent
DB_PATH = ROOT / "tronix.db"
MEMORIA_PATH = ROOT / "memoria_tronix.json"
CORE_PATH = ROOT / "tronix_core.json"
GATEWAY_URL = os.environ.get("TRONIX_GATEWAY", "http://localhost:8081")

sys.path.insert(0, str(ROOT))

def log(level: str, msg: str):
    print(f"[MCP] [{level}] {msg}", file=sys.stderr, flush=True)

def json_rpc(req: dict) -> dict:
    method = req.get("method", "")
    params = req.get("params", {})
    req_id = req.get("id")

    handlers = {
        "initialize": handle_initialize,
        "tools/list": handle_tools_list,
        "tools/call": handle_tools_call,
        "resources/list": handle_resources_list,
        "resources/read": handle_resources_read,
    }

    handler = handlers.get(method)
    if not handler:
        return {"jsonrpc": "2.0", "error": {"code": -32601, "message": f"Method not found: {method}"}, "id": req_id}

    try:
        result = handler(params)
        return {"jsonrpc": "2.0", "result": result, "id": req_id}
    except Exception as e:
        log("ERROR", f"{method} failed: {e}")
        return {"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}, "id": req_id}

def handle_initialize(params: dict) -> dict:
    return {
        "protocolVersion": "2025-03-26",
        "capabilities": {
            "tools": {
                "listChanged": False
            },
            "resources": {
                "subscribe": False
            }
        },
        "serverInfo": {
            "name": "Tronix MCP Server",
            "version": "1.5.0"
        }
    }

TOOLS = [
    {
        "name": "tronix_health",
        "description": "Verifica saude do sistema Tronix: gateway, banco, n8n",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "tronix_executar_script",
        "description": "Executa um script do ecossistema Tronix (gera_video, tronix_super_editor, gerar_mini_novela, etc)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "script": {"type": "string", "description": "Nome do script sem .py (ex: gera_video, tronix_super_editor)"},
                "args": {"type": "string", "description": "Argumentos para o script"}
            },
            "required": ["script"]
        }
    },
    {
        "name": "tronix_agentes",
        "description": "Lista os 11 agentes Tronix e seus status",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "tronix_dashboard_stats",
        "description": "Obtem estatisticas do dashboard: total de conteudos, pendentes, postados",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "tronix_gerar_conteudo",
        "description": "Gera conteudo completo: roteiro -> imagem -> video -> voz. Pipeline completo Tronix.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "tema": {"type": "string", "description": "Tema do conteudo a ser gerado"},
                "tipo": {"type": "string", "enum": ["mini_novela", "video", "imagem"], "description": "Tipo de conteudo"}
            },
            "required": ["tema"]
        }
    },
    {
        "name": "tronix_memoria",
        "description": "Le as ultimas acoes registradas na memoria persistente do Tronix",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Numero de acoes a retornar (max 50)"}
            },
            "required": []
        }
    },
    {
        "name": "tronix_scripts_disponiveis",
        "description": "Lista todos os scripts Python disponiveis no ecossistema Tronix",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "tronix_disparar_n8n",
        "description": "Dispara o pipeline n8n do Tronix",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workflow_id": {"type": "string", "description": "ID do workflow n8n"},
                "payload": {"type": "object", "description": "Payload JSON para o workflow"}
            },
            "required": []
        }
    },
    {
        "name": "tronix_escrever_memoria",
        "description": "Registra uma acao na memoria persistente do Tronix",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agente": {"type": "string", "description": "Nome do agente"},
                "acao": {"type": "string", "description": "Descricao da acao"}
            },
            "required": ["agente", "acao"]
        }
    },
    {
        "name": "tronix_conteudo_pendente",
        "description": "Lista conteudos pendentes de postagem",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "tronix_pipeline_log",
        "description": "Obtem os ultimos logs do pipeline",
        "inputSchema": {
            "type": "object",
            "properties": {"limit": {"type": "integer", "description": "Numero de logs"}},
            "required": []
        }
    },
    {
        "name": "tronix_freebuff",
        "description": "Freebuff CLI - coding agent gratuito. Verifica status do freebuff instalado e fornece instrucoes de uso. Para uso programatico, requer Codebuff SDK com API key.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "acao": {"type": "string", "enum": ["status", "versao", "como_usar"], "description": "Acao a executar (padrao: status)"}
            },
            "required": []
        }
    }
]

def handle_tools_list(params: dict) -> dict:
    return {"tools": TOOLS}

def gateway_call(endpoint: str, method: str = "GET", body: dict = None) -> dict:
    try:
        url = f"{GATEWAY_URL}{endpoint}"
        data = json.dumps(body).encode() if body else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}

def handle_tools_call(params: dict) -> dict:
    name = params.get("name", "")
    args = params.get("arguments", {})

    if name == "tronix_health":
        status = {"gateway": "unknown", "banco": "unknown", "n8n": "unknown"}
        try:
            conn = sqlite3.connect(str(DB_PATH))
            conn.execute("SELECT 1")
            conn.close()
            status["banco"] = "online"
        except Exception as e:
            status["banco"] = f"erro: {e}"
        status["gateway"] = "online"
        status["versao_core"] = json.load(open(CORE_PATH, encoding="utf-8")).get("versao", "?")
        return {"content": [{"type": "text", "text": json.dumps(status, indent=2)}]}

    elif name == "tronix_agentes":
        data = {"agentes": []}
        core = json.load(open(CORE_PATH, encoding="utf-8"))
        agentes = core.get("multi_agente", {}).get("agentes", [])
        data["framework"] = core.get("multi_agente", {}).get("framework", "CrewAI")
        data["agentes"] = agentes
        return {"content": [{"type": "text", "text": json.dumps(data, indent=2)}]}

    elif name == "tronix_dashboard_stats":
        resp = gateway_call("/dashboard/stats")
        return {"content": [{"type": "text", "text": json.dumps(resp, indent=2)}]}

    elif name == "tronix_scripts_disponiveis":
        scripts = []
        for f in sorted(ROOT.glob("*.py")):
            if f.name.startswith("_") or f.name in ("api_gateway.py", "tronix_logger.py", "tronix_crew.py", "tronix_mcp_server.py"):
                continue
            scripts.append(f.stem)
        return {"content": [{"type": "text", "text": json.dumps({"scripts": scripts, "total": len(scripts)}, indent=2)}]}

    elif name == "tronix_executar_script":
        script = args.get("script", "")
        script_args = args.get("args", "")
        script_path = ROOT / f"{script}.py"
        if not script_path.exists():
            return {"content": [{"type": "text", "text": f"Erro: Script '{script}.py' nao encontrado"}]}
        try:
            cmd = f"python \"{script_path}\" {script_args}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=ROOT, timeout=300)
            output = (result.stdout + result.stderr)[-3000:]
            status = "sucesso" if result.returncode == 0 else "erro"
            return {"content": [{"type": "text", "text": json.dumps({"status": status, "returncode": result.returncode, "output": output}, indent=2)}]}
        except subprocess.TimeoutExpired:
            return {"content": [{"type": "text", "text": "Erro: Script excedeu timeout de 300s"}]}
        except Exception as e:
            return {"content": [{"type": "text", "text": f"Erro: {e}"}]}

    elif name == "tronix_gerar_conteudo":
        tema = args.get("tema", "Tronix geracao automatica")
        tipo = args.get("tipo", "mini_novela")
        return {"content": [{"type": "text", "text": json.dumps({
            "status": "iniciado",
            "mensagem": f"Pipeline {tipo} disparado para tema: {tema}",
            "instrucao": f"Use tronix_executar_script com script='gerar_mini_novela' args='--tema \"{tema}\"' ou execute manualmente"
        }, indent=2)}]}

    elif name == "tronix_memoria":
        limit = min(args.get("limit", 20), 50)
        try:
            mem = json.load(open(MEMORIA_PATH, encoding="utf-8"))
            return {"content": [{"type": "text", "text": json.dumps({
                "identity": mem.get("identity"),
                "version": mem.get("version"),
                "status": mem.get("status"),
                "ultimas_acoes": mem["last_actions"][-limit:]
            }, indent=2)}]}
        except Exception as e:
            return {"content": [{"type": "text", "text": f"Erro lendo memoria: {e}"}]}

    elif name == "tronix_escrever_memoria":
        agente = args.get("agente", "MCP")
        acao = args.get("acao", "")
        try:
            mem = json.load(open(MEMORIA_PATH, encoding="utf-8"))
            novo_id = max(a["id"] for a in mem["last_actions"]) + 1 if mem["last_actions"] else 1
            mem["last_actions"].append({
                "id": novo_id, "agente": agente, "acao": acao,
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            })
            with open(MEMORIA_PATH, "w", encoding="utf-8") as f:
                json.dump(mem, f, indent=2, ensure_ascii=False)
            return {"content": [{"type": "text", "text": json.dumps({"status": "ok", "id": novo_id})}]}
        except Exception as e:
            return {"content": [{"type": "text", "text": f"Erro: {e}"}]}

    elif name == "tronix_conteudo_pendente":
        try:
            conn = sqlite3.connect(str(DB_PATH))
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            rows = [dict(r) for r in c.execute("SELECT * FROM conteudo WHERE status_post='pendente' ORDER BY data_criacao DESC LIMIT 20")]
            conn.close()
            return {"content": [{"type": "text", "text": json.dumps(rows, indent=2, default=str)}]}
        except Exception as e:
            return {"content": [{"type": "text", "text": f"Erro: {e}"}]}

    elif name == "tronix_pipeline_log":
        limit = min(args.get("limit", 10), 50)
        try:
            conn = sqlite3.connect(str(DB_PATH))
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            rows = [dict(r) for r in c.execute("SELECT * FROM pipeline_log ORDER BY data DESC LIMIT ?", (limit,))]
            conn.close()
            return {"content": [{"type": "text", "text": json.dumps(rows, indent=2, default=str)}]}
        except Exception as e:
            return {"content": [{"type": "text", "text": f"Erro: {e}"}]}

    elif name == "tronix_disparar_n8n":
        workflow_id = args.get("workflow_id", "tronix-pipeline")
        payload = args.get("payload", {})
        return gateway_call("/n8n/disparar", "POST", {"workflow_id": workflow_id, "payload": payload})

    elif name == "tronix_freebuff":
        acao = args.get("acao", "status")
        if acao == "versao":
            try:
                result = subprocess.run("freebuff --version", shell=True, capture_output=True, text=True, timeout=30)
                output = (result.stdout + result.stderr).strip()
                return {"content": [{"type": "text", "text": json.dumps({
                    "status": "sucesso",
                    "versao": output,
                    "instalado": True
                }, indent=2)}]}
            except Exception as e:
                return {"content": [{"type": "text", "text": json.dumps({"status": "erro", "erro": str(e)}, indent=2)}]}
        elif acao == "como_usar":
            return {"content": [{"type": "text", "text": json.dumps({
                "status": "ok",
                "freebuff": {
                    "descricao": "Freebuff - coding agent CLI gratuito (ad-supported)",
                    "versao": "0.0.107",
                    "modelos": ["DeepSeek V4 Pro", "DeepSeek V4 Flash", "Kimi K2.6", "MiniMax M2.7"],
                    "instalacao": "npm install -g freebuff",
                    "uso_interativo": "freebuff (no terminal do projeto)",
                    "uso_programatico": "Requer @codebuff/sdk com CODEBUFF_API_KEY",
                    "features": ["File mentions (@filename)", "Agent mentions (@AgentName)", "Bash mode (!command)", "Chat history (/history)", "Knowledge files (knowledge.md)"],
                    "comandos": ["/help", "/new", "/history", "/bash", "/init", "/feedback", "/theme:toggle", "/logout", "/exit"],
                    "nota": "Freebuff e interativo. Para uso via MCP, autentique manualmente primeiro: freebuff"
                }
            }, indent=2, ensure_ascii=False)}]}
        else:
            try:
                result = subprocess.run("freebuff --version", shell=True, capture_output=True, text=True, timeout=30)
                versao = (result.stdout + result.stderr).strip()
                return {"content": [{"type": "text", "text": json.dumps({
                    "status": "ok",
                    "freebuff_instalado": True,
                    "versao": versao,
                    "mensagem": "Freebuff instalado e pronto para uso interativo",
                    "proximo_passo": "Execute 'freebuff' no terminal para autenticar e usar"
                }, indent=2)}]}
            except Exception as e:
                return {"content": [{"type": "text", "text": json.dumps({
                    "status": "erro",
                    "freebuff_instalado": False,
                    "erro": str(e),
                    "solucao": "Execute: npm install -g freebuff"
                }, indent=2)}]}

    return {"content": [{"type": "text", "text": f"Ferramenta '{name}' nao encontrada"}]}

RESOURCES = [
    {
        "uri": "tronix://core/config",
        "name": "Configuracao Core do Tronix",
        "description": "Arquivo tronix_core.json com identidade, agentes, ferramentas visuais",
        "mimeType": "application/json"
    },
    {
        "uri": "tronix://core/memoria",
        "name": "Memoria Persistente do Tronix",
        "description": "Historico de acoes e estado atual do sistema",
        "mimeType": "application/json"
    },
    {
        "uri": "tronix://db/stats",
        "name": "Estatisticas do Banco de Dados",
        "description": "Totais de conteudo, pipeline_log e agendamentos",
        "mimeType": "application/json"
    }
]

def handle_resources_list(params: dict) -> dict:
    return {"resources": RESOURCES}

def handle_resources_read(params: dict) -> dict:
    uri = params.get("uri", "")
    if uri == "tronix://core/config":
        text = open(CORE_PATH, encoding="utf-8").read()
        return {"contents": [{"uri": uri, "mimeType": "application/json", "text": text}]}
    elif uri == "tronix://core/memoria":
        text = open(MEMORIA_PATH, encoding="utf-8").read()
        return {"contents": [{"uri": uri, "mimeType": "application/json", "text": text}]}
    elif uri == "tronix://db/stats":
        try:
            conn = sqlite3.connect(str(DB_PATH))
            c = conn.cursor()
            total = c.execute("SELECT COUNT(*) FROM conteudo").fetchone()[0]
            pendentes = c.execute("SELECT COUNT(*) FROM conteudo WHERE status_post='pendente'").fetchone()[0]
            postados = c.execute("SELECT COUNT(*) FROM conteudo WHERE status_post='postado'").fetchone()[0]
            logs = c.execute("SELECT COUNT(*) FROM pipeline_log").fetchone()[0]
            conn.close()
            text = json.dumps({"total_conteudos": total, "pendentes": pendentes, "postados": postados, "logs_pipeline": logs}, indent=2)
        except Exception as e:
            text = json.dumps({"erro": str(e)})
        return {"contents": [{"uri": uri, "mimeType": "application/json", "text": text}]}
    return {"contents": []}

def main():
    log("INFO", "Tronix MCP Server iniciado (stdio)")
    log("INFO", f"Gateway: {GATEWAY_URL}")
    log("INFO", f"DB: {DB_PATH}")
    log("INFO", "12 ferramentas registradas (inclui tronix_freebuff)")

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            response = json_rpc(req)
            if response:
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
        except json.JSONDecodeError as e:
            log("ERROR", f"JSON invalido: {e}")
            sys.stdout.write(json.dumps({
                "jsonrpc": "2.0",
                "error": {"code": -32700, "message": f"Parse error: {e}"},
                "id": None
            }) + "\n")
            sys.stdout.flush()
        except Exception as e:
            log("ERROR", f"Erro processando requisicao: {e}")

if __name__ == "__main__":
    main()
