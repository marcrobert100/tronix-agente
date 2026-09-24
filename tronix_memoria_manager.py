import os, sys, json, sqlite3
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).parent
DB_PATH = ROOT / "tronix.db"
MEMORIA_PATH = ROOT / "memoria_tronix.json"
MAX_MEMORY_ENTRIES = 100

def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS memoria_archive (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            original_id INTEGER,
            agente      TEXT NOT NULL,
            acao        TEXT NOT NULL,
            timestamp   TEXT NOT NULL,
            data_arquivamento DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_memoria_archive_data ON memoria_archive(data_arquivamento);
    """)
    conn.commit()
    conn.close()

def archive_old_entries(keep: int = MAX_MEMORY_ENTRIES):
    if not MEMORIA_PATH.exists():
        return 0
    with open(MEMORIA_PATH, "r", encoding="utf-8") as f:
        mem = json.load(f)
    actions = mem.get("last_actions", [])
    if len(actions) <= keep:
        return 0
    to_archive = actions[:-keep]
    to_keep = actions[-keep:]
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    archived = 0
    for entry in to_archive:
        try:
            c.execute(
                "INSERT INTO memoria_archive (original_id, agente, acao, timestamp) VALUES (?, ?, ?, ?)",
                (entry.get("id"), entry.get("agente", "?"), entry.get("acao", "?"), entry.get("timestamp", ""))
            )
            archived += 1
        except Exception:
            pass
    conn.commit()
    mem["last_actions"] = to_keep
    mem["version"] = "1.2.0"
    mem["last_archival"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    mem["archived_count"] = mem.get("archived_count", 0) + archived
    with open(MEMORIA_PATH, "w", encoding="utf-8") as f:
        json.dump(mem, f, indent=2, ensure_ascii=False)
    conn.close()
    return archived

def get_archive_stats() -> dict:
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    total = c.execute("SELECT COUNT(*) FROM memoria_archive").fetchone()[0]
    por_agente = [dict(r) for r in c.execute(
        "SELECT agente, COUNT(*) as total FROM memoria_archive GROUP BY agente ORDER BY total DESC"
    ).fetchall()]
    ultimos = [dict(r) for r in c.execute(
        "SELECT * FROM memoria_archive ORDER BY data_arquivamento DESC LIMIT 10"
    ).fetchall()]
    conn.close()
    return {"total_arquivados": total, "por_agente": por_agente, "ultimos_arquivados": ultimos}

def search_archive(termo: str, limit: int = 50) -> list:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    rows = [dict(r) for r in c.execute(
        "SELECT * FROM memoria_archive WHERE acao LIKE ? OR agente LIKE ? ORDER BY data_arquivamento DESC LIMIT ?",
        (f"%{termo}%", f"%{termo}%", limit)
    ).fetchall()]
    conn.close()
    return rows

if __name__ == "__main__":
    init_db()
    archived = archive_old_entries()
    print(f"  [MEMORIA] Arquivados: {archived}")
    stats = get_archive_stats()
    print(f"  [MEMORIA] Total arquivados: {stats['total_arquivados']}")
    print(f"  [MEMORIA] Por agente: {stats['por_agente']}")
