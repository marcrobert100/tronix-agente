# Tronix Knowledge Base - Estrutura de Dados

## Visao Geral
Este diretorio `agente/` contem o sistema Tronix, assistente IA de Marcos Roberto / PCsolucoes / InfoEngine / Vicosa-AL.

## Estrutura de Diretorios Principais

### Configuracao e Memoria
- `AGENTS.md` - Memoria persistente do projeto, preferencias, identidade do agente
- `memoria_tronix.json` - Estado completo do Tronix v1.2.0, 78 acoes registradas
- `opencode.json` - Definicoes de agentes (Gestor, Designer, DEV, Suporte, Secretaria)
- `tronix_core.json` - Core config do Tronix (agentes, manager LLM)
- `tronix_system.json` - System config
- `.env` - Variaveis de ambiente (NAO indexar conteudo sensivel)
- `.claude.json` - Config Claude

### Scripts Python (Pipeline de Midia)
- `gerar_novelinha.py` - Gerador de mini-novelas com Diretor cinematico
- `gerar_mini_novela.py` - Versao classica (tema alien)
- `gera_video.py` - Engine Ken Burns + texto animado
- `tronix_director.py` - Modulo Diretor: 8 planos + 10 movimentos de camera
- `tronix_super_editor.py` - Adiciona voz Edge-TTS AntonioNeural + legendas
- `tronix_crew.py` - CrewAI com 11 agentes
- `tronix_instagram.py` - Postagem Instagram
- `tronix_youtube.py` - Upload YouTube
- `tronix_logger.py` - Logger SQLite
- `tronix_sam3_demo.py` - Demo SAM3
- `tronix_mcp_server.py` - MCP server
- `roteirista.py` - Roteirista
- `gorila_*.py` - Animais talking head
- `mini_novela.py` - Concatena videos

### Diretorios de Saida
- `videos_saida/` - Videos finais
- `videos_animados/` - Videos com animacao
- `uploads/` - Imagens e arquivos enviados
- `tronix_output/` - Outputs Tronix

### Subprojetos
- `infoengine/` - InfoEngine (livros infantis + infograficos)
- `santinho_generator/` - Gerador de santinhos politicos (20 modelos)
- `curriculo_generator/` - Gerador de curriculos
- `horti/` - Horti
- `cms/` - CMS
- `dashboard/` - Dashboard
- `intranet/`, `intra/` - Intranet
- `Post/` - Sistema de posts
- `HIT/` - HIT
- `infoengine/` - InfoEngine
- `betting-system/` - Sistema de apostas
- `worker-imagens/` - Worker de imagens
- `flow-image-generator/` - Flow image gen
- `img/` - Imagens
- `apostas/` - Apostas
- `estoque/` - Estoque
- `estudo/` - Estudo
- `pcsolucoes/`, `pcsolucoes-memoria/` - PCsolucoes
- `prayer-diary-desktop/` - Prayer diary
- `virtual_office/` - Virtual office
- `tartaruga_vs_coelho/` - Jogo
- `HISTORINHA/` - Historias
- `webalizer/` - Web stats

### Infraestrutura
- `ComfyUI/` - ComfyUI clonado (sem GPU local)
- `nca-toolkit/` - NCA-ToolKit Flask server (porta 8080)
- `dify/` - Dify (langgenius) clonado
- `ragflow/` - RAGFlow (infiniflow) clonado
- `minio/` - MinIO
- `nca_temp/` - Temp NCA
- `open-webui/` - Open WebUI

### Assistentes IA Config
- `.claude/` - Claude config + skills
- `.opencode/` - OpenCode + skills (contem gpt-image-2, kb-retriever, web-design-engineer, web-video-presentation do Garden Skills)
- `.deepseek/` - DeepSeek config
- `.trae/` - Trae config
- `.github/` - GitHub config
- `.agent/` - Agent config (Antigravity Kit skills)

### Banco de Dados
- `tronix.db` - SQLite local (tabelas: conteudo, pipeline_log, agendamento)
- `santinho.db` - SQLite de santinhos
- MySQL `tronix_system` (XAMPP) - Tabelas: projetos(1), skills(46), logs_evolucao(24+), execucoes(0), projeto_skills(0)

### Novelinha Atual
- `novelinha_velho_estrela.json` - Roteiro "O Velho e a Estrela" (6 cenas)
- `novelinha_velho_estrela.mp4` - Video final (30s, 4.6MB, FullHD)
- `tronix_director_demo.md` - Demo do Director (gerado)

## Queries Comuns

### "Quem e o usuario?"
-> `AGENTS.md` secao "Preferencias do Usuario"

### "Qual o estado do pipeline?"
-> `memoria_tronix.json` campo `last_actions` (ultimas 78 acoes)

### "Quais skills estao instaladas?"
-> Listar `.opencode/skills/` + `Skills/` (Antigravity Kit)

### "Como gerar uma novelinha?"
-> `gerar_novelinha.py --input roteiro.json`

### "Quais APIs externas estao configuradas?"
-> `AGENTS.md` + `.env` (com cuidado) + logs de `logs_evolucao`

## Atualizacao
Esta estrutura deve ser atualizada quando:
- Novos diretorios sao criados
- Scripts importantes sao adicionados
- Configuracoes globais mudam
- Banco de dados e alterado
