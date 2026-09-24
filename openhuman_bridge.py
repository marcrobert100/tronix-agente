"""
OpenHuman ↔ Tronix Bridge
Conecta OpenHuman MCP Server ao ecossistema Tronix
Pontes: Memória, Voice Command, Pipeline, Integrações
"""
import os, sys, json, sqlite3, asyncio, hashlib, io
from datetime import datetime
from pathlib import Path
from typing import Optional

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).parent
DB_PATH = ROOT / "tronix.db"
MEMORIA_PATH = ROOT / "memoria_tronix.json"
OPENHUMAN_USER = Path(os.environ.get(
    "OPENHUMAN_USER_DIR",
    os.path.expanduser("~/.openhuman/users/6a165346ced0a054d8f058ff")
))
OPENHUMAN_MEMORY = OPENHUMAN_USER / "workspace" / "memory"
GATEWAY_URL = os.environ.get("TRONIX_GATEWAY", "http://localhost:8081")

# ─── Memória Sync ──────────────────────────────────────────────
class MemoriaSync:
    """Sincroniza memoria_tronix.json ↔ OpenHuman Memory Tree"""

    def __init__(self):
        self.tronix_mem = MEMORIA_PATH
        self.oh_memory = OPENHUMAN_MEMORY
        self.oh_memory.mkdir(parents=True, exist_ok=True)

    def load_tronix(self) -> dict:
        try:
            return json.load(open(self.tronix_mem, encoding="utf-8"))
        except Exception:
            return {"last_actions": [], "identity": "Tronix", "version": "1.5.0"}

    def save_tronix(self, data: dict):
        with open(self.tronix_mem, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def sync_to_openhuman(self):
        """Tronix → OpenHuman: exporta últimas ações como Markdown"""
        mem = self.load_tronix()
        actions = mem.get("last_actions", [])[-30:]

        md_lines = [
            f"# Tronix Memory Sync",
            f"Última sincronização: {datetime.now().isoformat()}",
            f"Versão: {mem.get('version', '?')}",
            f"Status: {mem.get('status', '?')}",
            "",
            "## Últimas Ações",
            ""
        ]

        for a in actions:
            ts = a.get("timestamp", "?")
            agent = a.get("agente", "?")
            action = a.get("acao", "?")
            md_lines.append(f"- **[{ts}]** `{agent}`: {action}")

        md_content = "\n".join(md_lines)
        out_path = self.oh_memory / "tronix_sync.md"
        out_path.write_text(md_content, encoding="utf-8")
        print(f"[SYNC] Tronix → OpenHuman: {len(actions)} ações exportadas")
        return out_path

    def sync_from_openhuman(self):
        """OpenHuman → Tronix: importa notas do Memory Tree"""
        sync_file = self.oh_memory / "tronix_sync.md"
        if not sync_file.exists():
            return None

        mem = self.load_tronix()

        # Marca que sincronizou
        last_sync = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

        # Adiciona entry de sync na memória
        novo_id = max((a["id"] for a in mem["last_actions"]), default=0) + 1
        mem["last_actions"].append({
            "id": novo_id,
            "agente": "SYNC",
            "acao": f"OPENHUMAN_SYNC: Memory Tree sincronizado com Tronix",
            "timestamp": last_sync
        })

        # Mantém apenas últimas 100 entries
        mem["last_actions"] = mem["last_actions"][-100:]
        self.save_tronix(mem)
        print(f"[SYNC] OpenHuman → Tronix: memória atualizada (id={novo_id})")
        return last_sync


# ─── Voice Command Parser ──────────────────────────────────────
class VoiceCommandParser:
    """Converte comandos de voz em ações Tronix"""

    COMMANDS = {
        "gerar video": {"script": "gerar_mini_novela", "action": "pipeline"},
        "mini novela": {"script": "gerar_mini_novela", "action": "pipeline"},
        "gerar imagem": {"script": "gera_video", "action": "image"},
        "super editor": {"script": "tronix_super_editor", "action": "voice"},
        "adicionar voz": {"script": "tronix_super_editor", "action": "voice"},
        "status": {"action": "health"},
        "agentes": {"action": "agents"},
        "pendentes": {"action": "pending"},
        "logs": {"action": "logs"},
        "dashboard": {"action": "dashboard"},
        "instagram": {"action": "instagram"},
        "youtube": {"action": "youtube"},
    }

    def parse(self, text: str) -> dict:
        text_lower = text.lower().strip()

        for keyword, cmd in self.COMMANDS.items():
            if keyword in text_lower:
                # Extrai tema se houver
                tema = text_lower.replace(keyword, "").strip()
                return {
                    "recognized": True,
                    "command": cmd,
                    "tema": tema or None,
                    "original": text
                }

        return {
            "recognized": False,
            "command": None,
            "tema": None,
            "original": text,
            "suggestion": "Tente: 'gerar video de alienigena', 'status', 'agentes'"
        }


# ─── Pipeline Bridge ───────────────────────────────────────────
class PipelineBridge:
    """Executa pipeline Tronix via voice/API"""

    def __init__(self):
        self.parser = VoiceCommandParser()

    def execute_voice_command(self, voice_text: str) -> dict:
        parsed = self.parser.parse(voice_text)

        if not parsed["recognized"]:
            return {
                "status": "not_recognized",
                "message": f"Comando não reconhecido: {voice_text}",
                "suggestion": parsed.get("suggestion")
            }

        cmd = parsed["command"]

        if cmd["action"] == "health":
            return self._check_health()
        elif cmd["action"] == "agents":
            return self._list_agents()
        elif cmd["action"] == "pending":
            return self._list_pending()
        elif cmd["action"] == "logs":
            return self._get_logs()
        elif cmd["action"] == "dashboard":
            return self._get_dashboard()
        elif cmd["action"] == "pipeline":
            return self._run_pipeline(cmd["script"], parsed.get("tema"))
        elif cmd["action"] == "voice":
            return self._run_voice(cmd["script"], parsed.get("tema"))
        elif cmd["action"] == "image":
            return self._run_image(parsed.get("tema"))

        return {"status": "unknown", "message": f"Ação '{cmd['action']}' não implementada"}

    def _check_health(self) -> dict:
        health = {"gateway": "offline", "banco": "unknown", "n8n": "unknown"}
        try:
            conn = sqlite3.connect(str(DB_PATH))
            conn.execute("SELECT 1")
            conn.close()
            health["banco"] = "online"
        except Exception as e:
            health["banco"] = f"erro: {e}"

        try:
            import urllib.request
            req = urllib.request.Request(f"{GATEWAY_URL}/health")
            with urllib.request.urlopen(req, timeout=5) as resp:
                health["gateway"] = "online"
        except Exception:
            health["gateway"] = "offline"

        return {"status": "ok", "health": health}

    def _list_agents(self) -> dict:
        try:
            core = json.load(open(ROOT / "tronix_core.json", encoding="utf-8"))
            agentes = core.get("multi_agente", {}).get("agentes", [])
            return {"status": "ok", "agentes": agentes, "total": len(agentes)}
        except Exception as e:
            return {"status": "erro", "message": str(e)}

    def _list_pending(self) -> dict:
        try:
            conn = sqlite3.connect(str(DB_PATH))
            conn.row_factory = sqlite3.Row
            rows = [dict(r) for r in conn.execute(
                "SELECT * FROM conteudo WHERE status_post='pendente' ORDER BY data_criacao DESC LIMIT 10"
            )]
            conn.close()
            return {"status": "ok", "pendentes": rows, "total": len(rows)}
        except Exception as e:
            return {"status": "erro", "message": str(e)}

    def _get_logs(self) -> dict:
        try:
            conn = sqlite3.connect(str(DB_PATH))
            conn.row_factory = sqlite3.Row
            rows = [dict(r) for r in conn.execute(
                "SELECT * FROM pipeline_log ORDER BY data DESC LIMIT 10"
            )]
            conn.close()
            return {"status": "ok", "logs": rows}
        except Exception as e:
            return {"status": "erro", "message": str(e)}

    def _get_dashboard(self) -> dict:
        try:
            conn = sqlite3.connect(str(DB_PATH))
            c = conn.cursor()
            stats = {
                "total": c.execute("SELECT COUNT(*) FROM conteudo").fetchone()[0],
                "pendentes": c.execute("SELECT COUNT(*) FROM conteudo WHERE status_post='pendente'").fetchone()[0],
                "postados": c.execute("SELECT COUNT(*) FROM conteudo WHERE status_post='postado'").fetchone()[0],
                "logs": c.execute("SELECT COUNT(*) FROM pipeline_log").fetchone()[0],
            }
            conn.close()
            return {"status": "ok", "dashboard": stats}
        except Exception as e:
            return {"status": "erro", "message": str(e)}

    def _run_pipeline(self, script: str, tema: Optional[str]) -> dict:
        import subprocess
        script_path = ROOT / f"{script}.py"
        if not script_path.exists():
            return {"status": "erro", "message": f"Script {script}.py não encontrado"}

        args = f'--tema "{tema}"' if tema else ""
        cmd = f'python "{script_path}" {args}'

        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=str(ROOT), timeout=300)
            output = (result.stdout + result.stderr)[-3000:]
            return {
                "status": "sucesso" if result.returncode == 0 else "erro",
                "script": script,
                "tema": tema,
                "output": output,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "message": "Script excedeu 300s"}
        except Exception as e:
            return {"status": "erro", "message": str(e)}

    def _run_voice(self, script: str, texto: Optional[str]) -> dict:
        import subprocess
        script_path = ROOT / f"{script}.py"
        if not script_path.exists():
            return {"status": "erro", "message": f"Script {script}.py não encontrado"}

        args = f'--texto "{texto}"' if texto else ""
        cmd = f'python "{script_path}" {args}'

        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=str(ROOT), timeout=300)
            output = (result.stdout + result.stderr)[-3000:]
            return {
                "status": "sucesso" if result.returncode == 0 else "erro",
                "script": script,
                "output": output
            }
        except Exception as e:
            return {"status": "erro", "message": str(e)}

    def _run_image(self, tema: Optional[str]) -> dict:
        return {
            "status": "info",
            "message": f"Use o Cloudflare SDXL para gerar imagem: {tema}",
            "comando": f'curl -X POST {GATEWAY_URL}/executar -d "{{\\"script\\": \\"gera_video\\", \\"args\\": \\"--tema {tema}\\"}}"'
        }


# ─── Auto-Sync Daemon ─────────────────────────────────────────
class AutoSyncDaemon:
    """Sincroniza memória automaticamente a cada N minutos"""

    def __init__(self, interval_minutes: int = 5):
        self.syncer = MemoriaSync()
        self.interval = interval_minutes * 60
        self.running = False

    def start(self):
        self.running = True
        print(f"[DAEMON] Auto-sync iniciado (intervalo: {self.interval//60}min)")

        while self.running:
            try:
                self.syncer.sync_to_openhuman()
                self.syncer.sync_from_openhuman()
            except Exception as e:
                print(f"[DAEMON] Erro: {e}")

            asyncio.get_event_loop().run_until_complete(
                asyncio.sleep(self.interval)
            )

    def stop(self):
        self.running = False
        print("[DAEMON] Auto-sync parado")


# ─── Main ──────────────────────────────────────────────────────
def main():
    import argparse
    parser = argparse.ArgumentParser(description="OpenHuman ↔ Tronix Bridge")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("sync", help="Sincronizar memória Tronix ↔ OpenHuman")
    sub.add_parser("sync-once", help="Sync uma vez e sai")

    voice_cmd = sub.add_parser("voice", help="Processar comando de voz")
    voice_cmd.add_argument("text", help="Texto do comando de voz")

    status_cmd = sub.add_parser("status", help="Status da integração")

    args = parser.parse_args()

    if args.command == "sync":
        daemon = AutoSyncDaemon()
        daemon.start()
    elif args.command == "sync-once":
        syncer = MemoriaSync()
        syncer.sync_to_openhuman()
        syncer.sync_from_openhuman()
    elif args.command == "voice":
        bridge = PipelineBridge()
        result = bridge.execute_voice_command(args.text)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.command == "status":
        print(json.dumps({
            "bridge": "OpenHuman ↔ Tronix",
            "version": "1.0.0",
            "gateway": GATEWAY_URL,
            "tronix_db": str(DB_PATH),
            "tronix_memoria": str(MEMORIA_PATH),
            "openhuman_user": str(OPENHUMAN_USER),
            "openhuman_memory": str(OPENHUMAN_MEMORY),
            "memoria_sync": "disponivel",
            "voice_parser": "disponivel",
            "pipeline_bridge": "disponivel"
        }, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
