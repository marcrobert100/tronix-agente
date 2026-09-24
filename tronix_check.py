import os, sys, json, importlib, shutil, subprocess
from pathlib import Path

ROOT = Path(__file__).parent
PASS = 0
WARN = 0
FAIL = 0
SKIP = 0

def ok(msg):
    global PASS; PASS += 1
    print(f"  [PASS] {msg}")

def warn(msg):
    global WARN; WARN += 1
    print(f"  [WARN] {msg}")

def fail(msg):
    global FAIL; FAIL += 1
    print(f"  [FAIL] {msg}")

def check_python():
    print("\n--- Python ---")
    v = sys.version_info
    if v.major >= 3 and v.minor >= 10:
        ok(f"Python {v.major}.{v.minor}.{v.micro}")
    else:
        fail(f"Python {v.major}.{v.minor} (minimo 3.10)")

def check_deps():
    print("\n--- Dependencias Python ---")
    required = [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("aiohttp", "aiohttp"),
        ("crewai", "crewai"),
        ("pydantic", "pydantic"),
    ]
    optional = [
        ("edge-tts", "edge_tts"),
        ("moviepy", "moviepy"),
        ("instagrapi", "instagrapi"),
    ]
    for name, mod in required:
        try:
            importlib.import_module(mod)
            ok(f"{name}")
        except ImportError:
            fail(f"{name} - NAO INSTALADO")
    for name, mod in optional:
        try:
            importlib.import_module(mod)
            ok(f"{name}")
        except ImportError:
            warn(f"{name} - NAO INSTALADO (opcional)")

def check_ffmpeg():
    print("\n--- FFmpeg ---")
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        try:
            result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=5)
            ver = result.stdout.split("\n")[0] if result.stdout else "?"
            ok(f"FFmpeg encontrado: {ver[:60]}")
        except Exception:
            ok("FFmpeg encontrado (versao desconhecida)")
    else:
        trae_ffmpeg = Path(r"C:\Users\CHCONTE RECPÇÃO\AppData\Local\Programs\TRAE SOLO\bin\ffmpeg.exe")
        if trae_ffmpeg.exists():
            warn("FFmpeg nao no PATH, mas disponivel em TRAE SOLO/bin/")
        else:
            fail("FFmpeg nao encontrado")

def check_db():
    print("\n--- Banco de Dados ---")
    db_path = ROOT / "tronix.db"
    if db_path.exists():
        size = db_path.stat().st_size
        ok(f"tronix.db existe ({size/1024:.1f} KB)")
    else:
        fail("tronix.db nao encontrado")
    try:
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        c = conn.cursor()
        tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        expected = {"conteudo", "pipeline_log", "agendamento"}
        found = set(tables)
        if expected.issubset(found):
            ok(f"Tabelas: {', '.join(tables)}")
        else:
            warn(f"Tabelas encontradas: {', '.join(tables)}, esperadas: {expected}")
        conn.close()
    except Exception as e:
        fail(f"Erro conectando: {e}")

def check_core():
    print("\n--- Core Config ---")
    core_path = ROOT / "tronix_core.json"
    if core_path.exists():
        try:
            core = json.load(open(core_path, encoding="utf-8"))
            ok(f"tronix_core.json v{core.get('versao', '?')}")
            agentes = core.get("multi_agente", {}).get("agentes", [])
            ok(f"{len(agentes)} agentes configurados")
        except Exception as e:
            fail(f"Erro lendo: {e}")
    else:
        fail("tronix_core.json nao encontrado")

def check_memoria():
    print("\n--- Memoria ---")
    mem_path = ROOT / "memoria_tronix.json"
    if mem_path.exists():
        try:
            mem = json.load(open(mem_path, encoding="utf-8"))
            actions = len(mem.get("last_actions", []))
            ok(f"{actions} acoes registradas na memoria")
        except Exception as e:
            fail(f"Erro lendo: {e}")
    else:
        warn("memoria_tronix.json nao encontrado")

def check_env():
    print("\n--- Variaveis de Ambiente ---")
    env_path = ROOT / ".env"
    if env_path.exists():
        ok(".env encontrado")
    else:
        warn(".env nao encontrado")
    keys = ["OPENROUTER_API_KEY", "ANTHROPIC_API_KEY", "CF_API_TOKEN", "CF_ACCOUNT_ID"]
    for k in keys:
        if os.environ.get(k):
            ok(f"{k} configurada")
        else:
            warn(f"{k} nao configurada")

def check_gateway():
    print("\n--- Gateway ---")
    gw_path = ROOT / "api_gateway.py"
    if gw_path.exists():
        ok("api_gateway.py encontrado")
    else:
        fail("api_gateway.py nao encontrado")
    mcp_path = ROOT / "tronix_mcp_server.py"
    if mcp_path.exists():
        ok("tronix_mcp_server.py encontrado (MCP)")
    else:
        warn("tronix_mcp_server.py nao encontrado")

def check_mcp():
    print("\n--- MCP Config ---")
    trae_mcp = ROOT / ".trae" / "mcp.json"
    if trae_mcp.exists():
        ok(".trae/mcp.json encontrado (TRAE SOLO)")
    else:
        warn(".trae/mcp.json nao encontrado")

def main():
    print("=" * 50)
    print("  TRONIX - VERIFICACAO DE SISTEMA")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    checks = [
        check_python, check_deps, check_ffmpeg, check_db,
        check_core, check_memoria, check_env, check_gateway, check_mcp
    ]
    for check in checks:
        try:
            check()
        except Exception as e:
            print(f"  [ERRO] {check.__name__}: {e}")

    print("\n" + "=" * 50)
    print(f"  RESULTADO: {PASS} pass, {WARN} warn, {FAIL} fail, {SKIP} skip")
    print("=" * 50)
    if FAIL > 0:
        print("  Corriga os erros antes de iniciar o sistema.")
    elif WARN > 0:
        print("  Sistema funcional com ressalvas.")
    else:
        print("  Tudo pronto!")
    return 1 if FAIL > 0 else 0

from datetime import datetime
if __name__ == "__main__":
    sys.exit(main())
