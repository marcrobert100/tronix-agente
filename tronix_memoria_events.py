import os, sys, json, sqlite3, uuid
from datetime import datetime
from pathlib import Path
import shutil

ROOT = Path(__file__).parent
DB_PATH = ROOT / "tronix.db"
MEMORIA_PATH = ROOT / "memoria_tronix.json"
MAX_LAST_ACTIONS = 150

def _load():
    if not MEMORIA_PATH.exists():
        return {}
    try:
        with open(MEMORIA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _atomic_write(d: dict):
    tmp = str(MEMORIA_PATH) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    os.replace(tmp, str(MEMORIA_PATH))

def get_last_event_id():
    m = _load()
    return m.get("last_event_id")

def append_event(agente: str, acao: str, timestamp: str | None = None, orig_id=None) -> dict:
    ts = timestamp or datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
    m = _load()
    m.setdefault("events", [])
    m.setdefault("sequence", 0)
    seq = m["sequence"] + 1
    eid = str(uuid.uuid4())
    ev = {
        "id": eid,
        "seq": seq,
        "agente": agente,
        "acao": acao,
        "timestamp": ts,
    }
    if orig_id is not None:
        ev["orig_id"] = orig_id
    # dedup guard
    last = m.get("last_event_id")
    if last and ev.get("acao") == m["events"][-1]["acao"] if m["events"] else False:
        pass
    m["events"].append(ev)
    m["sequence"] = seq
    m["last_event_id"] = eid
    m["mode"] = "events_appendonly"
    m["version"] = m.get("version", "1.6.3")
    # keep last_actions for compat
    m.setdefault("last_actions", [])
    m["last_actions"].append({
        "id": ev.get("orig_id") or seq,
        "agente": agente,
        "acao": acao,
        "timestamp": ts,
    })
    if len(m["last_actions"]) > MAX_LAST_ACTIONS:
        m["last_actions"] = m["last_actions"][-MAX_LAST_ACTIONS:]
    m["ultimo_id"] = max(m.get("ultimo_id", 0), seq)
    _atomic_write(m)
    return ev

def replay_events(since_seq: int = 0) -> list:
    m = _load()
    return [e for e in m.get("events", []) if e.get("seq", 0) > since_seq]

def check_integrity() -> dict:
    m = _load()
    evs = m.get("events", [])
    gaps = 0
    for i,e in enumerate(evs):
        if e.get("seq") != i+1:
            gaps += 1
    return {"count": len(evs), "gaps": gaps, "sequence_ok": gaps==0, "last_event_id": m.get("last_event_id")}

if __name__ == "__main__":
    print(json.dumps(check_integrity(), indent=2, ensure_ascii=False))
