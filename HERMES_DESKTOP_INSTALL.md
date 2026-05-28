# Hermes Agent Desktop - Instalação Completa

## Visão Geral

O Hermes Agent Desktop é uma aplicação de desktop para instalar, configurar e conversar com o Hermes Agent - um assistente de IA autônomo com uso de ferramentas, multi-plataforma e aprendizado contínuo.

## Requisitos do Sistema

- **Sistema Operacional**: Windows 10/11 (64-bit)
- **Memória RAM**: 4GB mínimo (8GB recomendado)
- **Espaço em disco**: 500MB livre
- **Conexão com internet**: Para download e uso dos serviços de IA

## Dependências Automáticas

O script de instalação instala automaticamente:

1. **Node.js v20.11.0** - Runtime para a aplicação Electron
2. **Python 3.11.7** - Para scripts e integrações
3. **Git** - Para controle de versão e atualizações
4. **Hermes Agent Desktop v0.3.5** - Aplicação principal
5. **Hermes Agent CLI** - Interface de linha de comando

## Métodos de Instalação

### Método 1: Script Automático (Recomendado)

1. Baixe e execute o script PowerShell:
   ```powershell
   # Execute como Administrador
   powershell -ExecutionPolicy Bypass -File "C:\xampp\htdocs\agente\install-hermes-desktop.ps1"
   ```

2. Ou execute o arquivo batch:
   ```cmd
   # Execute como Administrador
   C:\xampp\htdocs\agente\install-hermes-desktop.bat
   ```

### Método 2: Instalação Manual

1. **Baixe o instalador**:
   - URL: https://github.com/fathah/hermes-desktop/releases/download/v0.3.5/hermes-desktop-0.3.5-setup.exe

2. **Execute o instalador**:
   - Clique duas vezes no arquivo `.exe`
   - Siga as instruções do assistente

3. **Configure as dependências**:
   - Node.js: https://nodejs.org/
   - Python: https://www.python.org/
   - Git: https://git-scm.com/

## Configuração Inicial

### Primeira Execução

1. **Abra o Hermes Agent Desktop**:
   - Clique no atalho no Desktop ou Menu Iniciar

2. **Siga o assistente de configuração**:
   - Escolha entre modo local ou remoto
   - Configure o provedor de IA (OpenRouter, Anthropic, OpenAI, etc.)
   - Insira as chaves de API necessárias

3. **Senha padrão**: `123`

### Configuração Avançada

Arquivos de configuração localizados em `%USERPROFILE%\.hermes\`:

- `config.yaml` - Configuração principal
- `.env` - Variáveis de ambiente

## Uso Básico

### Interface Gráfica

1. **Chat**: Conversas com o agente
2. **Sessões**: Histórico de conversas
3. **Agentes**: Perfis e configurações
4. **Ferramentas**: Gerenciamento de ferramentas
5. **Agendamentos**: Tarefas programadas
6. **Gateways**: Integrações com plataformas

### Comandos Úteis

- `/new` - Nova conversa
- `/clear` - Limpar conversa atual
- `/help` - Ajuda
- `/usage` - Uso de tokens
- `/tools` - Listar ferramentas
- `/model` - Mudar modelo

## Provedores de IA Suportados

### Provedores Remotos
- **OpenRouter** - 200+ modelos via API única
- **Anthropic** - Claude direto
- **OpenAI** - GPT direto
- **Google (Gemini)** - Google AI Studio
- **xAI (Grok)** - Modelos Grok
- **Nous Portal** - Tier gratuito disponível
- **Qwen** - Modelos QwenAI
- **MiniMax** - Global e China
- **Hugging Face** - 20+ modelos open source
- **Groq** - Inferência rápida

### Provedores Locais
- **Ollama** - `http://localhost:11434`
- **LM Studio** - `http://localhost:1234`
- **vLLM** - Endpoint OpenAI compatível
- **llama.cpp** - Endpoint OpenAI compatível

## Solução de Problemas

### Erro de Permissão
Se encontrar erros de permissão:
1. Execute o instalador como Administrador
2. Verifique se o antivirus não está bloqueando

### Erro de Cache
Se encontrar erros de cache:
```powershell
# Limpar cache do Electron
Remove-Item -Path "$env:APPDATA\Hermes Agent" -Recurse -Force
```

### Atualização
Para atualizar para a versão mais recente:
1. Baixe o novo instalador
2. Execute sobre a instalação existente
3. As configurações serão preservadas

## Comandos Úteis

### Iniciar Hermes Agent
```powershell
Start-Process "$env:LOCALAPPDATA\Programs\hermes-desktop\hermes-agent.exe"
```

### Verificar Instalação
```powershell
# Verificar Node.js
node --version

# Verificar Python
python --version

# Verificar Git
git --version

# Verificar Hermes Desktop
Test-Path "$env:LOCALAPPDATA\Programs\hermes-desktop\hermes-agent.exe"
```

### Desinstalar
1. Use "Adicionar ou Remover Programas" do Windows
2. Ou execute: `%LOCALAPPDATA%\Programs\hermes-desktop\Uninstall hermes-agent.exe`

## Segurança

- **Senha padrão**: `123` (altere após a primeira execução)
- **Chaves de API**: Armazenadas localmente no seu computador
- **Dados**: Todos os dados ficam no seu computador local

## Atualizações

O Hermes Agent Desktop inclui atualização automática:
- Verifica atualizações ao iniciar
- Baixa e instala automaticamente
- Mantém suas configurações e dados

## Suporte

- **Documentação**: https://hermes-agent.nousresearch.com/docs/
- **Discord**: https://discord.gg/NousResearch
- **GitHub Issues**: https://github.com/fathah/hermes-desktop/issues

## Licença

MIT License - Veja LICENSE para detalhes

---

**Versão**: 0.3.5  
**Data**: 06/05/2026  
**Senha padrão**: 123