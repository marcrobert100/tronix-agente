import os, sys, json, sqlite3, subprocess, urllib.request, urllib.error
from datetime import datetime
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type

MEMORIA_PATH = os.path.join(os.path.dirname(__file__), "memoria_tronix.json")
CORE_PATH = os.path.join(os.path.dirname(__file__), "tronix_core.json")
DB_PATH = os.path.join(os.path.dirname(__file__), "tronix.db")
GATEWAY_URL = os.environ.get("TRONIX_GATEWAY", "http://localhost:8081")

env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    with open(env_path, encoding='utf-8') as f:
        env_data = json.load(f).get('env', {})
        for k, v in env_data.items():
            if v and k not in os.environ:
                os.environ[k] = str(v)

OR_KEY = (os.environ.get("OPENROUTER_API_KEY") or os.environ.get("NVIDIA_API_KEY") or os.environ.get("ANTHROPIC_API_KEY") or "")
if OR_KEY and not os.environ.get("OPENROUTER_API_KEY"):
    os.environ["OPENROUTER_API_KEY"] = OR_KEY

LLM_MODEL = os.environ.get("TRONIX_LLM", "openrouter/nvidia/llama-3.1-nemotron-ultra-253b-v1")

def carregar_memoria():
    with open(MEMORIA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_acao(agente, acao):
    mem = carregar_memoria()
    novo_id = max(a["id"] for a in mem["last_actions"]) + 1 if mem["last_actions"] else 1
    mem["last_actions"].append({
        "id": novo_id,
        "agente": agente,
        "acao": acao,
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    })
    with open(MEMORIA_PATH, "w", encoding="utf-8") as f:
        json.dump(mem, f, indent=2, ensure_ascii=False)
    return novo_id

class MemoriaTool(BaseTool):
    name: str = "MemoriaTronix"
    description: str = "Le e escreve na memoria persistente do Tronix (memoria_tronix.json)"
    agent_name: str = "Tronix"

    def _run(self, acao: str) -> str:
        salvar_acao(self.agent_name, acao)
        return f"Acao registrada: {acao}"

class ExecutarScriptTool(BaseTool):
    name: str = "ExecutarScript"
    description: str = "Executa um dos scripts Tronix (gera_video, tronix_super_editor, mini_novela, etc)"
    script: str = ""
    args: str = ""

    class InputSchema(BaseModel):
        script: str = Field(..., description="Nome do script (ex: gera_video, tronix_super_editor)")
        args: str = Field("", description="Argumentos para o script")

    InputSchema: Type[BaseModel] = InputSchema

    def _run(self, script: str, args: str = "") -> str:
        cmd = f"python {script}.py {args}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=os.path.dirname(__file__))
        return result.stdout[-1000:] if result.stdout else result.stderr[-1000:]

class GatewayTool(BaseTool):
    name: str = "GatewayTronix"
    description: str = "Chama o API Gateway central para executar scripts, ler/escrever memoria, disparar n8n, e obter status do sistema"
    endpoint: str = ""

    class InputSchema(BaseModel):
        endpoint: str = Field(..., description="Endpoint do gateway: /health, /agentes, /scripts, /memoria, /executar, /dashboard/stats, /n8n/disparar, /log, /conteudo")
        method: str = Field("GET", description="GET ou POST")
        body: str = Field("", description="JSON body para POST (ex: '{\"script\":\"gera_video\",\"args\":\"--tema natureza\"}')")

    InputSchema: Type[BaseModel] = InputSchema

    def _run(self, endpoint: str, method: str = "GET", body: str = "") -> str:
        url = f"{GATEWAY_URL}{endpoint}"
        data = body.encode("utf-8") if body else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8")[:2000]
        except urllib.error.URLError as e:
            return f"Erro conectando ao gateway ({GATEWAY_URL}): {e.reason}"

class N8nTool(BaseTool):
    name: str = "N8nTronix"
    description: str = "Dispara o pipeline n8n ou verifica status do n8n via API Gateway"

    class InputSchema(BaseModel):
        workflow_id: str = Field("tronix-pipeline", description="ID do workflow no n8n")
        payload: str = Field("{}", description="JSON com payload para disparar")

    InputSchema: Type[BaseModel] = InputSchema

    def _run(self, workflow_id: str = "tronix-pipeline", payload: str = "{}") -> str:
        url = f"{GATEWAY_URL}/n8n/disparar"
        data = json.dumps({"workflow_id": workflow_id, "payload": json.loads(payload)}).encode()
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read().decode("utf-8")[:2000]
        except urllib.error.URLError as e:
            return f"Erro n8n: {e.reason}"

def criar_agentes():
    with open(CORE_PATH, "r", encoding="utf-8") as f:
        core = json.load(f)

    localizacao = core["localizacao"]
    cidade = f"{localizacao['cidade']}-{localizacao['estado']}"

    TOOLS_COMUNS = [MemoriaTool(), GatewayTool()]
    TOOLS_EXEC = TOOLS_COMUNS + [ExecutarScriptTool()]

    return {
        "DEV": Agent(
            role="Tronix-DEV",
            goal="Criar e manter scripts, pipelines e ferramentas do ecossistema Tronix. Usa o Gateway para tudo.",
            backstory=f"Programador principal do Tronix em {cidade}. Domina Python, PHP, JS e FFmpeg.",
            allow_delegation=False,
            verbose=True,
            tools=TOOLS_EXEC + [N8nTool()],
            llm=LLM_MODEL
        ),
        "MEDIA": Agent(
            role="Tronix-MEDIA",
            goal="Gerar imagens, videos e animacoes. Usa Gateway para executar scripts de midia e disparar n8n.",
            backstory=f"Especialista em geracao de midia do Tronix em {cidade}. Pipeline: imagem -> video -> voz.",
            allow_delegation=True,
            verbose=True,
            tools=TOOLS_EXEC + [N8nTool()],
            llm=LLM_MODEL
        ),
        "SUPER": Agent(
            role="Tronix-SUPER",
            goal="Adicionar voz e texto em videos usando Edge-TTS e FFmpeg via Gateway",
            backstory=f"Editor de audio/voz do Tronix em {cidade}. Voz padrao: pt-BR-AntonioNeural.",
            allow_delegation=False,
            verbose=True,
            tools=TOOLS_EXEC,
            llm=LLM_MODEL
        ),
        "ROTEIRISTA": Agent(
            role="Tronix-ROTEIRISTA",
            goal="Criar roteiros criativos em portugues para mini-novelas, videos promocionais e conteudo de redes sociais. Cada roteiro deve conter: tema, 3-5 cenas com descricao visual, falas dos personagens e sugestao de hashtags.",
            backstory=f"Roteirista principal do Tronix em {cidade}. Especialista em storytelling curto para redes sociais. Cria scripts envolventes que combinam com o pipeline Cloudflare SDXL + Ken Burns + Edge-TTS.",
            allow_delegation=False,
            verbose=True,
            tools=TOOLS_COMUNS,
            llm=LLM_MODEL
        ),
        "DIRETOR": Agent(
            role="Tronix-DIRETOR",
            goal="Planejar e dirigir a execucao de cada cena: escolher os prompts de imagem (Cloudflare SDXL), definir transicoes, atribuir tom de voz (Edge-TTS AntonioNeural) e orquestrar a sequencia de producao. Usa Gateway para executar scripts.",
            backstory=f"Diretor de cena do Tronix em {cidade}. Transforma roteiros em producoes audiovisuais completas. Decide estilo visual, ritmo da narracao e coordenada a pipeline de geracao.",
            allow_delegation=True,
            verbose=True,
            tools=TOOLS_EXEC + [N8nTool()],
            llm=LLM_MODEL
        ),
        "IG": Agent(
            role="Tronix-IG",
            goal="Postar videos e Reels no Instagram automaticamente via Gateway",
            backstory=f"Gestor de midias sociais do Tronix em {cidade}. Usa instagrapi para postar.",
            allow_delegation=False,
            verbose=True,
            tools=TOOLS_COMUNS,
            llm=LLM_MODEL
        ),
        "YT": Agent(
            role="Tronix-YT",
            goal="Fazer upload de videos no YouTube via OAuth 2.0 usando Gateway",
            backstory=f"Publicador YouTube do Tronix em {cidade}.",
            allow_delegation=False,
            verbose=True,
            tools=TOOLS_COMUNS,
            llm=LLM_MODEL
        ),
        "DB": Agent(
            role="Tronix-DB",
            goal="Gerenciar banco SQLite, registrar logs e consultar dados. Usa Gateway para persistencia.",
            backstory=f"Engineer de dados do Tronix em {cidade}. Cuida do tronix.db e logging.",
            allow_delegation=False,
            verbose=True,
            tools=TOOLS_COMUNS,
            llm=LLM_MODEL
        ),
        "INFRA": Agent(
            role="Tronix-INFRA",
            goal="Manter infraestrutura: Gateway, Docker, MinIO, Moto S3, NCA-ToolKit. Monitorar via /health.",
            backstory=f"DevOps do Tronix em {cidade}. Infraestrutura local e em nuvem.",
            allow_delegation=False,
            verbose=True,
            tools=TOOLS_COMUNS,
            llm=LLM_MODEL
        ),
        "RESEARCH": Agent(
            role="Tronix-RESEARCH",
            goal="Pesquisar novas ferramentas, modelos e tendencias. Consultar /scripts e /ferramentas do Gateway.",
            backstory=f"Pesquisador do Tronix em {cidade}. Sempre buscando a proxima evolucao.",
            allow_delegation=False,
            verbose=True,
            tools=TOOLS_COMUNS,
            llm=LLM_MODEL
        ),
        "SYNC": Agent(
            role="Tronix-SYNC",
            goal="Sincronizar estado entre todos os agentes via Gateway. Garantir que memoria e core estejam consistentes.",
            backstory=f"Orquestrador de sincronizacao do Tronix em {cidade}.",
            allow_delegation=False,
            verbose=True,
            tools=TOOLS_COMUNS,
            llm=LLM_MODEL
        ),
    }

def criar_tarefas_padrao(agentes):
    return [
        Task(
            description="Registrar no log a ativacao do Tronix via Gateway (/memoria POST). Carregar estado atual do sistema via Gateway (/health, /agentes).",
            expected_output="Relatorio completo do estado do sistema",
            agent=agentes["SYNC"]
        ),
        Task(
            description="Criar um roteiro original para mini-novela ou video promocional em portugues. Definir tema, 3-5 cenas com descricao visual e falas.",
            expected_output="Roteiro completo com cenas e falas em portugues",
            agent=agentes["ROTEIRISTA"]
        ),
        Task(
            description="Com base no roteiro, planejar a producao: gerar prompts de imagem para Cloudflare SDXL, definir transicoes Ken Burns, configurar voz Edge-TTS e executar a pipeline via Gateway (/executar).",
            expected_output="Video produzido seguindo o roteiro",
            agent=agentes["DIRETOR"]
        ),
        Task(
            description="Verificar status do banco de dados via Gateway (/dashboard/stats). Reportar total de conteudos, pendentes e postados.",
            expected_output="Status do banco de dados com numeros",
            agent=agentes["DB"]
        ),
        Task(
            description="Verificar saude de toda infraestrutura via Gateway (/health e /scripts). Confirmar que scripts de midia estao disponiveis, n8n online, gateway responsivo.",
            expected_output="Relatorio de infraestrutura completo",
            agent=agentes["INFRA"]
        ),
    ]

def criar_crew():
    agentes = criar_agentes()
    tarefas = criar_tarefas_padrao(agentes)

    crew = Crew(
        agents=list(agentes.values()),
        tasks=tarefas,
        process=Process.hierarchical,
        manager_llm=LLM_MODEL,
        verbose=True,
        memory=True
    )
    return crew

if __name__ == "__main__":
    crew = criar_crew()
    salvar_acao("Tronix", f"CREWAI: Time multi-agente Tronix inicializado com {LLM_MODEL}")
    result = crew.kickoff()
    print("=== RESULTADO ===")
    print(result)
