# Tronix AI - Setup Completo

## ✅ O que foi configurado

### 1. IA Portátil com Ollama
- **Local**: `E:\Windows\start-fast-chat.bat`
- **Interface**: `http://localhost:3333`
- **Modelos instalados**:
  - Gemma 2 2B (padrão)
  - Llama 3.1 8B
  - Gemma 4 2B
  - Llama 3 8B
  - E outros 3 modelos

### 2. Banco de Dados MySQL
- **Servidor**: XAMPP MySQL (localhost:3306)
- **Banco**: `tronix_system`
- **Tabelas**:
  - `skills` - Skills do Tronix
  - `projetos` - Projetos ativos
  - `logs_evolucao` - Logs de operações
  - `execucoes` - Execuções de tarefas
  - `projeto_skills` - Relação projeto-skill

### 3. Sincronização Automática
- **Script**: `sync_tronix.py`
- **Função**: Sincroniza skills do `tronix_core.json` com o banco
- **Status**: ✅ 46 skills sincronizadas

### 4. Chat Server com Banco de Dados
- **Arquivo**: `E:\Shared\chat_server_db.py`
- **Funcionalidade**: Salva conversas no MySQL
- **Endpoint**: `/api/db/save` e `/api/db/chats`

## 🚀 Como Usar

### Iniciar a IA Portátil
1. Duplo-clique em: `E:\Windows\start-fast-chat.bat`
2. Aguarde o Ollama iniciar
3. Abra o navegador em: `http://localhost:3333`

### Sincronizar Manualmente
```bash
cd C:\xampp\htdocs\agente\.opencode
python sync_tronix.py
```

### Verificar Conexão com Banco
```bash
cmd /c "C:\xampp\mysql\bin\mysql.exe" -u root -e "USE tronix_system; SHOW TABLES;"
```

## 📊 Skills Sincronizadas

As seguintes skills estão no banco de dados:
- 2d-games, 3d-games, api-patterns, app-builder
- architecture, bash-linux, behavioral-modes
- brainstorming, clean-code, code-review-checklist
- database-design, deployment-procedures
- ... e mais 34 skills

## 🔧 Comandos Úteis

### Verificar status do MySQL
```bash
netstat -an | findstr :3306
```

### Verificar tabelas do banco
```bash
cmd /c "C:\xampp\mysql\bin\mysql.exe" -u root -e "USE tronix_system; DESCRIBE skills;"
```

### Executar script de sincronização
```bash
python sync_tronix.py
```

## 📁 Estrutura de Arquivos

```
C:\xampp\htdocs\agente\.opencode\
├── tronix_core.json          # Configuração do Tronix
├── tronix_system.json        # Dados do sistema
├── sync_tronix.py           # Sincronizador automático
├── tronix_db_sync.py        # Conector de banco de dados
└── TRONIX_SETUP.md          # Este arquivo

E:\Shared\
├── chat_server_db.py        # Chat server com banco
├── chat_server.py           # Chat server original
├── chat_data\               # Dados de chat local
└── models\                  # Modelos Ollama

E:\Windows\
├── start-fast-chat.bat      # Iniciar IA (atualizado)
└── install.bat              # Instalador original
```

## ⚠️ Notas Importantes

1. **MySQL precisa estar rodando** - Iniciar pelo XAMPP Control Panel
2. **Ollama precisa estar acessível** - Porta 11434
3. **Python 3.12+ requerido** - Para scripts de sincronização
4. **Permissões de banco** - Usuário root sem senha (XAMPP padrão)

## 🎯 Próximos Passos

1. Testar a interface da IA em `http://localhost:3333`
2. Verificar se as conversas são salvas no banco
3. Criar API para consultar histórico de conversas
4. Integrar com outros sistemas via API

## 🐛 Solução de Problemas

### Erro de conexão MySQL
- Verificar se o XAMPP MySQL está rodando
- Testar conexão: `cmd /c "C:\xampp\mysql\bin\mysql.exe" -u root -e "SHOW DATABASES;"`

### Erro no Ollama
- Verificar se a porta 11434 está livre
- Reiniciar o Ollama: `taskkill /f /im ollama-windows.exe`

### Erro de Python
- Instalar pymysql: `pip install pymysql`
- Verificar versão: `python --version`
