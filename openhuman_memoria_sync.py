"""
OpenHuman Memory Sync Service
Roda como daemon, sincroniza memoria_tronix.json ↔ OpenHuman Memory Tree
"""
import os, sys, json, time, sqlite3, hashlib, io
from datetime import datetime
from pathlib import Path

# Fix Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

ROOT = Path(__file__).parent
MEMORIA_PATH = ROOT / "memoria_tronix.json"
DB_PATH = ROOT / "tronix.db"
OPENHUMAN_USER = Path(os.path.expanduser("~/.openhuman/users/6a165346ced0a054d8f058ff"))
OPENHUMAN_MEMORY = OPENHUMAN_USER / "workspace" / "memory"

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def load_tronix():
    try:
        return json.load(open(MEMORIA_PATH, encoding="utf-8"))
    except:
        return {"last_actions": [], "identity": "Tronix"}

def save_tronix(data):
    with open(MEMORIA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def sync_to_openhuman():
    """Exporta memória Tronix para OpenHuman Memory Tree"""
    OPENHUMAN_MEMORY.mkdir(parents=True, exist_ok=True)
    mem = load_tronix()
    actions = mem.get("last_actions", [])[-50:]

    md = f"""# Tronix System Memory
Exportado: {datetime.now().isoformat()}
Versão: {mem.get('version', '?')}
Status: {mem.get('status', 'active')}

## Últimas {len(actions)} Ações

"""
    for a in actions:
        ts = a.get("timestamp", "?")
        agent = a.get("agente", "?")
        action = a.get("acao", "?")
        md += f"- `[{ts}]` **{agent}**: {action}\n"

    out = OPENHUMAN_MEMORY / "tronix_memory.md"
    out.write_text(md, encoding="utf-8")
    log(f"Tronix -> OpenHuman: {len(actions)} acoes")
    return out

def sync_db_stats():
    """Exporta stats do banco para OpenHuman"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()
        stats = {
            "timestamp": datetime.now().isoformat(),
            "total_conteudos": c.execute("SELECT COUNT(*) FROM conteudo").fetchone()[0],
            "pendentes": c.execute("SELECT COUNT(*) FROM conteudo WHERE status_post='pendente'").fetchone()[0],
            "postados": c.execute("SELECT COUNT(*) FROM conteudo WHERE status_post='postado'").fetchone()[0],
            "logs_pipeline": c.execute("SELECT COUNT(*) FROM pipeline_log").fetchone()[0],
            "tarefas": c.execute("SELECT COUNT(*) FROM tarefas").fetchone()[0] if self_table_exists(c, "tarefas") else 0,
        }
        conn.close()

        out = OPENHUMAN_MEMORY / "tronix_stats.md"
        md = f"""# Tronix Dashboard Stats
Atualizado: {datetime.now().isoformat()}

| Métrica | Valor |
|---------|-------|
| Total Conteúdos | {stats['total_conteudos']} |
| Pendentes | {stats['pendentes']} |
| Postados | {stats['postados']} |
| Logs Pipeline | {stats['logs_pipeline']} |
| Tarefas | {stats['tarefas']} |
"""
        out.write_text(md, encoding="utf-8")
        log(f"Stats exportadas: {stats['total_conteudos']} conteudos")
        return stats
    except Exception as e:
        log(f"Erro stats: {e}")
        return {}

def self_table_exists(cursor, table):
    try:
        cursor.execute(f"SELECT 1 FROM {table} LIMIT 1")
        return True
    except:
        return False

def run_daemon(interval_sec=300):
    log(f"Memory Sync Daemon iniciado (intervalo: {interval_sec//60}min)")
    while True:
        try:
            sync_to_openhuman()
            sync_db_stats()
        except Exception as e:
            log(f"Erro: {e}")
        time.sleep(interval_sec)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        sync_to_openhuman()
        sync_db_stats()
        log("Sync único concluído")
    else:
        interval = int(sys.argv[1]) if len(sys.argv) > 1 else 300
        run_daemon(interval)
