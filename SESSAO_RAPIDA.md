# 🔴 REFERÊNCIA RÁPIDA — NOVA SESSÃO

> **Execute antes de qualquer coisa:** Leia este arquivo primeiro.

---

## 👤 IDENTIDADE

| Campo | Valor |
|-------|-------|
| **Usuário** | Marcos Roberto |
| **WhatsApp** | 5582991856656 |
| **Localização** | Viçosa-AL, Brasil |
| **Empresa** | PCsoluções |

---

## 🤖 IDENTIDADE DO AGENTE

| Campo | Valor |
|-------|-------|
| **Nome** | TRONIX |
| **Versão** | 1.6.0 |
| **Operador** | opencode CLI |
| **Mensagem de ativação** | "Tronix ativo em Viçosa. Pronto para o comando, Marcos." |

---

## 📂 ARQUIVOS ESSENCIAIS (ler ao iniciar)

| # | Arquivo | O que contém |
|---|---------|--------------|
| 1 | `C:\xampp\htdocs\agente\SESSAO_RAPIDA.md` | Este resumo |
| 2 | `C:\xampp\htdocs\agente\memoria_tronix.json` | Histórico completo (89 ações) |
| 3 | `C:\xampp\htdocs\agente\AGENTS.md` | InfoEngine + regras |
| 4 | `C:\xampp\htdocs\agente\tronix_core.json` | Config completa do Tronix |
| 5 | `C:\xampp\htdocs\agente\opencode.json` | Agentes da equipe |
| 6 | `C:\xampp\htdocs\agente\tronix.db` | Banco SQLite local |

---

## 🏗️ SISTEMAS INSTALADOS

### Portas & URLs

| Sistema | Porta | URL | Status |
|---------|-------|-----|--------|
| **Tronix AI** | 7000 | http://localhost:7000 | ✅ Pronto |
| **TRONIX AI HUD** | Desktop | `agente/tronix_jarvis/start.bat` | ✅ JARVIS-Mark |
| **OpenClaw** | 18789 | http://localhost:18789/ | ✅ 9Router |
| **API Gateway** | 8081 | http://localhost:8081 | ✅ FastAPI |
| **n8n** | 5678 | http://localhost:5678 | ✅ Workflows |
| **Langflow** | 7860 | http://localhost:7860 | ✅ Visual agents |
| **Dify** | 3000 | http://localhost:3000 | 🐳 Docker |
| **RAGFlow** | 9380 | http://localhost:9380 | 🐳 Docker |
| **NCA-ToolKit** | 8080 | http://localhost:8080 | ✅ Flask |
| **Moto S3** | 9090 | http://localhost:9090 | ✅ S3 mock |
| **MinIO** | 9000/9001 | http://localhost:9001 | 🐳 Docker |
| **InfoEngine** | 80 | localhost/agente/infoengine/ | 🌐 XAMPP |
| **Dashboard PHP** | 80 | localhost/agente/infoengine/dashboard/ | 🌐 XAMPP |
| **Jellyfin** | 8096 | http://localhost:8096 | 🐳 Media |
| **Radarr** | 7878 | http://localhost:7878 | 🐳 Filmes |
| **Sonarr** | 8989 | http://localhost:8989 | 🐳 Séries |
| **Prowlarr** | 9696 | http://localhost:9696 | 🐳 Indexers |
| **qBittorrent** | 8080 | http://localhost:8080 | 🐳 Torrent |
| **FlareSolverr** | 8191 | http://localhost:8191 | 🐳 Proxy |
| **Bazarr** | 6767 | http://localhost:6767 | 🐳 Legendas |
| **Ombi** | 3579 | http://localhost:3579 | 🐳 Pedidos |

### Credenciais

| Sistema | Usuário | Senha |
|---------|---------|-------|
| **Tronix AI** | admin | Admin123! |
| **Betting System** | admin | admin123 |
| **Betting (Bar)** | bar_admin | bar123 |
| **Betting (Cliente)** | cliente | cliente123 |
| **qBittorrent** | admin | adminadmin |

---

## 🆕 FERRAMENTAS NOVAS (v1.6.0)

| Ferramenta | Versão | Tipo | Uso |
|------------|--------|------|-----|
| **Crawl4AI** | 0.9.3 | pip | Web scraper LLM-friendly. `python tronix_crawl4ai.py <url>` |
| **llm-mem** | 0.1.1 | pip | Memória persistente cross-session. Worker HTTP porta 37777 |
| **GitNexus** | 1.6.11 | npm | Code graph intelligence. `gitnexus analyze` / `gitnexus mcp` |

### Comandos Rápidos

```powershell
# Crawl4AI - Scrapar URL
python tronix_crawl4ai.py https://github.com/trending --output output/trending.md

# Crawl4AI - Batch multi-URL
python tronix_crawl4ai.py --multi https://url1 https://url2 --batch-dir output/

# GitNexus - Indexar repo
gitnexus analyze C:\xampp\htdocs\agente

# GitNexus - Iniciar MCP server
gitnexus mcp

# llm-mem - Worker HTTP (porta 37777)
llm-mem worker
```

---

## 🚀 COMANDOS DE INICIALIZAÇÃO

```powershell
# Tudo de uma vez
C:\xampp\htdocs\agente\iniciar_tudo.bat

# Tronix AI Assistant
C:\xampp\htdocs\Tronix\start.bat

# TRONIX AI Control HUD (JARVIS-Mark, controle do PC por voz)
C:\xampp\htdocs\agente\tronix_jarvis\start.bat  # setup automático + HUD PyQt6

# API Gateway
cd C:\xampp\htdocs\agente && python api_gateway.py

# n8n
C:\xampp\htdocs\agente\iniciar_n8n.bat

# Infraestrutura (Docker + MinIO + NCA)
C:\xampp\htdocs\agente\iniciar_infra.ps1

# Dify + RAGFlow
C:\xampp\htdocs\agente\iniciar_dify_ragflow.bat

# Langflow
python -m langflow run --port 7860

# Homelab (Servidor de Midia)
C:\xampp\htdocs\agente\homelab\setup_completo.bat

# InfoEngine (requer XAMPP Apache ligado)
# Acesse: http://localhost/agente/infoengine/

# InfoEngine - Build de Livros
cd C:\xampp\htdocs\agente\infoengine
python tools/criar_historia.py                    # Gera book.json de exemplo
python tools/build_livro.py book.json output/livro.html  # Monta HTML
```

---

## 📁 ESTRUTURA DE PASTAS

```
C:\xampp\htdocs\
├── agente/                    # 🎯 CENTRO DE CONTROLE
│   ├── memoria_tronix.json    # Memória persistente
│   ├── tronix_core.json       # Config completa
│   ├── tronix.db              # Banco SQLite
│   ├── opencode.json          # Agentes
│   ├── AGENTS.md              # Regras
│   ├── api_gateway.py         # Gateway FastAPI
│   ├── tronix_crew.py         # CrewAI multi-agente
│   ├── tronix_mcp_server.py   # MCP server
│   ├── infoengine/            # Livros + infográficos
│   ├── dify/                  # Plataforma AI
│   ├── ragflow/               # Engine RAG
│   ├── nca-toolkit/           # Video tools
│   └── homelab/               # Servidor de Midia (Jellyfin/Radarr/Sonarr)
│
├── Tronix/                    # AI Assistant (FastAPI)
│   ├── app.py
│   ├── core/
│   └── static/
│
├── betting-system/            # Sistema de apostas
├── dashboard/                 # Dashboard geral
├── horti/                     # Horti Alecrim
└── sabor/                     # Sabor Nordestino

D:\Media\                      # Midia do Homelab
├── Filmes/                    # Radarr
├── Séries/                    # Sonarr
├── Downloads/                 # qBittorrent
├── Legendas/                  # Bazarr
└── Música/                    # Jellyfin
```

---

## 🤖 AGENTES (CrewAI)

| Agente | Função |
|--------|--------|
| **DEV** | Programador PHP/Python |
| **MEDIA** | Geração de conteúdo |
| **SUPER** | Voz + legenda (Edge-TTS) |
| **ROTEIRISTA** | Criação de roteiros |
| **DIRETOR** | Direção de projetos |
| **IG** | Instagram (instagrapi) |
| **YT** | YouTube (OAuth) |
| **DB** | Banco de dados |
| **INFRA** | Docker, servidores |
| **RESEARCH** | Pesquisa GitHub |
| **SYNC** | Sincronização |
| **OPENHUMAN** | Bridge OpenHuman |

---

## 🎨 PROJETOS ATIVOS

### 1. InfoEngine (Livros + Infográficos)
- **Local**: `C:\xampp\htdocs\agente\infoengine\`
- **Templates**: 6 (2 infantis, 2 infográficos, 2 utilitários)
- **PWA**: ✅ Stitch Contos Mágicos
- **WhatsApp**: Botão em todos os templates
- **Build System**: `criar_historia.py` → `book.json` → `build_livro.py` → `livro.html`
- **Guia SVG**: `references/svg_guide.md`

### 2. Santinho Generator
- **Local**: `C:\xampp\htdocs\agente\santinho_generator\`
- **Modelos**: 20 templates políticos
- **Banco**: santinho.db

### 3. Tronix AI Assistant
- **Local**: `C:\xampp\htdocs\Tronix\`
- **Stack**: FastAPI + SQLite + JWT
- **Features**: Chat, memória, tarefas, notas, skills

### 4. Pipeline de Mídia
- **Cloudflare SDXL** → **Ken Burns** → **Edge-TTS** → **FFmpeg**
- **Post**: Instagram (instagrapi), YouTube (OAuth)

---

## 📋 PRÓXIMOS PENDENTES

- [ ] Ativar GitHub Pages
- [ ] Configurar Replicate API (Wan 2.2)
- [ ] Credenciais Instagram corretas
- [ ] Dashboard com MySQL
- [ ] APK para Play Store

---

## 🔧 APIs & TOKENS

| Serviço | Variável | Onde |
|---------|----------|------|
| **OpenRouter** | OPENROUTER_API_KEY | .env |
| **Cloudflare** | CLOUDFLARE_API_TOKEN | .env |
| **Replicate** | REPLICATE_API_TOKEN | .env |
| **NVIDIA NIM** | NVIDIA_API_KEY | .env |

---

## 💡 COMO USAR EM NOVA SESSÃO

1. **Abra este arquivo** (`SESSAO_RAPIDA.md`)
2. **Leia os 6 arquivos essenciais** (tabela acima)
3. **Verifique portas** com `netstat -an | findstr "LISTEN"`
4. **Pronto!** Você tem todo o contexto

---

## 📊 BANCO DE DADOS (tronix.db)

### Tabelas

| Tabela | Registros | Descrição |
|--------|-----------|-----------|
| **conteudo** | 20 | Vídeos e imagens gerados |
| **pipeline_log** | 11 | Log de execuções |
| **tarefas** | - | Tarefas dos agentes |
| **agendamento** | - | Agendamentos |

### Últimos Conteúdos

| ID | Tipo | Título | Status |
|----|------|--------|--------|
| 1 | video | Mini Novela Alienígena | pendente |
| 2 | imagem | Teste pipeline 094513 | pendente |
| 3 | video | cena01_raw_voz.mp4 | pendente |

### Últimos Logs

| Ação | Script | Status |
|------|--------|--------|
| gerar_mini_novela | gerar_mini_novela.py | sucesso |
| super_editor | tronix_super_editor.py | sucesso |
| GATEWAY | api_gateway.py | sucesso |

---

*Última atualização: 16/06/2026*
*Versão: 1.5.0*
