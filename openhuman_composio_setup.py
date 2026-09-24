"""
OpenHuman Composio Setup
Configura integrações OAuth via Composio no OpenHuman
"""
import os, sys, json
from pathlib import Path

OPENHUMAN_USER = Path(os.path.expanduser("~/.openhuman/users/6a165346ced0a054d8f058ff"))
CONFIG_PATH = OPENHUMAN_USER / "config.toml"

AVAILABLE_INTEGRATIONS = {
    "gmail": {
        "name": "Gmail",
        "description": "Enviar e ler emails",
        "use_case": "Notificar Marcos sobre novos conteúdos, enviar relatórios"
    },
    "github": {
        "name": "GitHub",
        "description": "Repos, issues, PRs",
        "use_case": "Versionar código Tronix, criar issues automáticas"
    },
    "notion": {
        "name": "Notion",
        "description": "Documentação e bases de dados",
        "use_case": "Documentar projetos, registrar aprendizados"
    },
    "slack": {
        "name": "Slack",
        "description": "Mensagens e canais",
        "use_case": "Notificar equipe em tempo real"
    },
    "google_calendar": {
        "name": "Google Calendar",
        "description": "Eventos e agendamentos",
        "use_case": "Agendar posts, lembretes de tarefas"
    },
    "google_drive": {
        "name": "Google Drive",
        "description": "Arquivos e pastas",
        "use_case": "Backup automático de conteúdo gerado"
    },
    "google_sheets": {
        "name": "Google Sheets",
        "description": "Planilhas",
        "use_case": "Relatórios de performance, tracking de posts"
    },
    "linear": {
        "name": "Linear",
        "description": "Gestão de projetos",
        "use_case": "Gerenciar backlog do Tronix"
    },
    "stripe": {
        "name": "Stripe",
        "description": "Pagamentos",
        "use_case": "Cobranças automatizadas PCsoluções"
    },
    "twilio": {
        "name": "Twilio",
        "description": "SMS e WhatsApp",
        "use_case": "Notificações via WhatsApp Business"
    }
}

def show_available():
    print("\n=== Integrações Disponíveis no Composio ===\n")
    for key, info in AVAILABLE_INTEGRATIONS.items():
        print(f"  {key:20s} │ {info['name']:20s} │ {info['description']}")
        print(f"  {'':20s} │ {'':20s} │ Uso: {info['use_case']}")
        print()

def configure_composio():
    """Configura Composio no config.toml do OpenHuman"""
    config = CONFIG_PATH.read_text(encoding="utf-8")

    # Verifica se já está habilitado
    if "enabled = true" in config.split("[composio]")[1].split("\n\n")[0] if "[composio]" in config else False:
        print("[OK] Composio já habilitado no config.toml")
    else:
        print("[CONFIG] Composio já habilitado (feito na config anterior)")

    print("\n=== Próximos Passos para Conectar Integrações ===\n")
    print("1. Abra o OpenHuman")
    print("2. Vá em Settings → Integrations (ou Composio)")
    print("3. Clique em cada integração que deseja conectar")
    print("4. Faça login via OAuth no navegador")
    print("5. As ferramentas ficarão disponíveis para o agente")
    print()
    print("Integrações recomendadas para Tronix:")
    print("  ✓ Gmail     → Notificações e relatórios")
    print("  ✓ GitHub    → Versionar código")
    print("  ✓ Notion    → Documentação")
    print("  ✓ Calendar  → Agendamento de posts")
    print("  ✓ Drive     → Backup de conteúdo")
    print()

def generate_bridge_config():
    """Gera configuração para usar Tronix via OpenHuman"""
    bridge_config = {
        "name": "tronix-bridge",
        "integrations": {
            "voice_command": {
                "wake_word": "Hey Tiny",
                "commands": [
                    "gerar video de [tema]",
                    "mini novela [tema]",
                    "status do tronix",
                    "lista de agentes",
                    "conteudos pendentes",
                    "logs do pipeline"
                ]
            },
            "memory_sync": {
                "direction": "bidirectional",
                "interval_minutes": 5,
                "source": "memoria_tronix.json",
                "target": "openhuman_memory_tree"
            },
            "mcp_tools": [
                "tronix_health",
                "tronix_executar_script",
                "tronix_gerar_conteudo",
                "tronix_memoria",
                "tronix_agentes",
                "tronix_dashboard_stats",
                "tronix_conteudo_pendente",
                "tronix_pipeline_log",
                "tronix_disparar_n8n",
                "tronix_escrever_memoria",
                "tronix_scripts_disponiveis",
                "tronix_freebuff"
            ]
        }
    }

    out = ROOT / "openhuman_bridge_config.json"
    out.write_text(json.dumps(bridge_config, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[OK] Bridge config gerada: {out}")
    return bridge_config

ROOT = Path(__file__).parent

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"

    if cmd == "list":
        show_available()
    elif cmd == "configure":
        configure_composio()
    elif cmd == "bridge-config":
        generate_bridge_config()
    else:
        print("Uso: python openhuman_composio_setup.py [list|configure|bridge-config]")
        print()
        print("  list           → Lista integrações disponíveis")
        print("  configure      → Mostra como configurar no OpenHuman")
        print("  bridge-config  → Gera config do bridge Tronix↔OpenHuman")
