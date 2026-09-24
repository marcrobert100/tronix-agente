import json
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR.parent / ".env"

print("Instalando dependências do TRONIX AI (JARVIS-Mark structure)...")
subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)

print("Instalando navegadores do Playwright...")
subprocess.run([sys.executable, "-m", "playwright", "install"], check=True)

key = ""
env_file = BASE_DIR.parent / ".env" or ENV_FILE
if ENV_FILE.exists():
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("GEMINI_API_KEY="):
            key = line.split("=", 1)[1].strip().strip('"')
            break

if key:
    cfg_path = BASE_DIR / "config" / "api_keys.json"
    cfg = {}
    if cfg_path.exists():
        try:
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        except Exception:
            cfg = {}
    cfg.setdefault("gemini_api_key", key)
    cfg.setdefault("assistant_name", "TRONIX")
    cfg.setdefault("user_name", "Marcos")
    cfg.setdefault("voice", "Kore")
    cfg.setdefault("language", "pt-BR")
    cfg.setdefault("os_system", "windows")
    cfg.setdefault("live_model", "gemini-3.1-flash-live-preview")
    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    cfg_path.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")
else:
    print("⚠️  GEMINI_API_KEY não encontrada no ../.env — o HUD vai pedir a chave no primeiro uso.")

print("\n✅ Setup completo! Rode 'python main.py' para iniciar o TRONIX AI.")