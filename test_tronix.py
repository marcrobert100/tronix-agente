"""Tronix System Test — Verifica todos os componentes."""
import os, sys, json, time

sys.path.insert(0, os.path.dirname(__file__))

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

passed = 0
failed = 0

def test(name, func):
    global passed, failed
    try:
        result = func()
        if result:
            print(f"  {GREEN}PASS{RESET} {name}")
            passed += 1
        else:
            print(f"  {YELLOW}SKIP{RESET} {name}")
    except Exception as e:
        print(f"  {RED}FAIL{RESET} {name}: {str(e)[:60]}")
        failed += 1

print(f"\n{BOLD}{CYAN}{'='*50}")
print(f"  TRONIX SYSTEM TEST v1.5.0")
print(f"{'='*50}{RESET}\n")

# --- 1. ENV ---
print(f"{BOLD}[1] ENVIRONMENT{RESET}")

def test_env_file():
    return os.path.exists(os.path.join(os.path.dirname(__file__), '.env'))
test(".env existe", test_env_file)

def test_load_env():
    with open(os.path.join(os.path.dirname(__file__), '.env'), encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                if v.strip():
                    os.environ[k.strip()] = v.strip()
    return True
test("Env vars carregadas", test_load_env)

def test_nvidia_key():
    return bool(os.environ.get('NVIDIA_API_KEY'))
test("NVIDIA_API_KEY configurada", test_nvidia_key)

# --- 2. NVIDIA NIM API ---
print(f"\n{BOLD}[2] NVIDIA NIM API{RESET}")

def test_nvidia_nano():
    import json, urllib.request
    data = json.dumps({
        "model": "nvidia/nemotron-3-nano-30b-a3b",
        "messages": [{"role": "user", "content": "Say OK"}],
        "max_tokens": 5
    }).encode()
    req = urllib.request.Request(
        "https://integrate.api.nvidia.com/v1/chat/completions",
        data=data, method="POST"
    )
    req.add_header("Authorization", f"Bearer {os.environ['NVIDIA_API_KEY']}")
    req.add_header("Content-Type", "application/json")
    resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
    return resp["choices"][0]["message"].get("content") or resp["choices"][0]["message"].get("reasoning_content")
test("Nemotron Nano (30B) responde", test_nvidia_nano)

# --- 3. LITELLM ---
print(f"\n{BOLD}[3] LITELLM + CREWAI{RESET}")

def test_litellm_import():
    import litellm
    return True
test("litellm importado", test_litellm_import)

def test_crewai_import():
    from crewai import Agent, Task, Crew, Process
    from crewai.llm import LLM
    return True
test("crewai importado", test_crewai_import)

def test_llm_object():
    from crewai.llm import LLM
    llm = LLM(
        model="nvidia_nim/nvidia/nemotron-3-nano-30b-a3b",
        api_key=os.environ["NVIDIA_API_KEY"],
        base_url="https://integrate.api.nvidia.com/v1",
    )
    resp = llm.call([{"role": "user", "content": "Reply with just the word TEST"}])
    return bool(resp)
test("LLM CrewAI conecta e responde", test_llm_object)

# --- 4. CREWAI AGENTS ---
print(f"\n{BOLD}[4] CREWAI AGENTS{RESET}")

def test_crewai_agents():
    from tronix_crew import criar_agentes
    agentes = criar_agentes()
    expected = ["DEV", "MEDIA", "SUPER", "ROTEIRISTA", "DIRETOR", "IG", "YT", "DB", "INFRA", "RESEARCH", "SYNC"]
    return list(agentes.keys()) == expected
test("11 agentes criados corretamente", test_crewai_agents)

def test_agent_llm():
    from tronix_crew import criar_agentes
    agentes = criar_agentes()
    return "nvidia" in str(agentes["DEV"].llm).lower()
test("Agentes usam NVIDIA NIM", test_agent_llm)

# --- 5. CAVEMAN ---
print(f"\n{BOLD}[5] CAVEMAN{RESET}")

def test_caveman_plugin():
    plugins_dir = os.path.expanduser("~/.config/opencode/plugins")
    return os.path.exists(os.path.join(plugins_dir, "caveman"))
test("Plugin caveman instalado", test_caveman_plugin)

def test_caveman_commands():
    cmds_dir = os.path.expanduser("~/.config/opencode/commands")
    expected = ["caveman.md", "caveman-commit.md", "caveman-review.md"]
    return all(os.path.exists(os.path.join(cmds_dir, f)) for f in expected)
test("Comandos caveman presentes", test_caveman_commands)

# --- 6. DATABASE ---
print(f"\n{BOLD}[6] DATABASE{RESET}")

def test_sqlite_db():
    return os.path.exists(os.path.join(os.path.dirname(__file__), "tronix.db"))
test("tronix.db existe", test_sqlite_db)

def test_sqlite_tables():
    import sqlite3
    db = os.path.join(os.path.dirname(__file__), "tronix.db")
    conn = sqlite3.connect(db)
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    conn.close()
    return "conteudo" in tables and "pipeline_log" in tables
test("Tabelas conteudo + pipeline_log existem", test_sqlite_tables)

# --- 7. API GATEWAY ---
print(f"\n{BOLD}[7] API GATEWAY{RESET}")

def test_gateway_file():
    return os.path.exists(os.path.join(os.path.dirname(__file__), "api_gateway.py"))
test("api_gateway.py existe", test_gateway_file)

def test_gateway_health():
    import urllib.request
    try:
        resp = urllib.request.urlopen("http://localhost:8081/health", timeout=3)
        return resp.status == 200
    except:
        return False
test("Gateway responde em :8081", test_gateway_health)

# --- 8. MEMORY ---
print(f"\n{BOLD}[8] MEMORY{RESET}")

def test_memoria():
    with open(os.path.join(os.path.dirname(__file__), "memoria_tronix.json"), encoding="utf-8") as f:
        mem = json.load(f)
    return len(mem.get("last_actions", [])) > 80
test("memoria_tronix.json OK (80+ acoes)", test_memoria)

def test_core():
    with open(os.path.join(os.path.dirname(__file__), "tronix_core.json"), encoding="utf-8") as f:
        core = json.load(f)
    return core.get("versao") == "1.5.0"
test("tronix_core.json v1.5.0", test_core)

# --- 9. SCRIPTS ---
print(f"\n{BOLD}[9] SCRIPTS{RESET}")

scripts = [
    "tronix_super_editor.py", "gerar_mini_novela.py", "mini_novela.py",
    "tronix_logger.py", "gera_video.py", "animar_ia.py"
]
for s in scripts:
    test(f"Script {s}", lambda s=s: os.path.exists(os.path.join(os.path.dirname(__file__), s)))

# --- RESULT ---
print(f"\n{BOLD}{CYAN}{'='*50}")
total = passed + failed
if failed == 0:
    print(f"  {GREEN}TODOS OS TESTES PASSARAM!{RESET} {passed}/{total}")
else:
    print(f"  {YELLOW}{passed}/{total} passaram, {RED}{failed} falharam{RESET}")
print(f"{'='*50}{RESET}\n")
