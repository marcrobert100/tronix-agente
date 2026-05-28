# Tronix AI - Sistema Completo

## 🎯 Resumo do que foi configurado

### IA Portátil Potente
✅ **Ollama** com 7 modelos de linguagem instalados  
✅ **Interface Web** em `http://localhost:3333`  
✅ **Banco de Dados MySQL** conectado ao XAMPP  
✅ **Sincronização Automática** de skills  

### Modelos Disponíveis
- **Gemma 2 2B** - Rápido e eficiente
- **Llama 3.1 8B** - Melhor para raciocínio complexo
- **Gemma 4 2B** - Equilíbrio velocidade/qualidade
- **Llama 3 8B** - Excelente para codificação
- E mais 3 modelos

## 🚀 Como Iniciar

### Opção 1: Script Completo
```bash
cd C:\xampp\htdocs\agente\.opencode
start_tronix_system.bat
```

### Opção 2: Manual
1. **Iniciar MySQL**: XAMPP Control Panel → Start MySQL
2. **Sincronizar skills**: `python sync_tronix.py`
3. **Iniciar IA**: Duplo-clique em `E:\Windows\start-fast-chat.bat`
4. **Abrir navegador**: `http://localhost:3333`

## 📊 Banco de Dados

### Conexão Estabelecida
- **Servidor**: localhost:3306
- **Banco**: tronix_system
- **Usuário**: root (sem senha)

### Tabelas
- `skills` - 46 skills sincronizadas
- `projetos` - Projetos ativos
- `logs_evolucao` - Logs de operações
- `execucoes` - Execuções de tarefas

## 🔧 Comandos Rápidos

### Verificar Status
```bash
# Verificar MySQL
cmd /c "C:\xampp\mysql\bin\mysql.exe" -u root -e "SHOW DATABASES;"

# Verificar skills no banco
cmd /c "C:\xampp\mysql\bin\mysql.exe" -u root -e "USE tronix_system; SELECT COUNT(*) FROM skills;"

# Sincronizar manualmente
python sync_tronix.py
```

### Gerenciar IA
```bash
# Iniciar IA com banco
python "E:\Shared\chat_server_db.py"

# Verificar modelos Ollama
curl http://127.0.0.1:11434/api/tags
```

## 📁 Arquivos Importantes

| Arquivo | Descrição |
|---------|-----------|
| `sync_tronix.py` | Sincroniza skills com MySQL |
| `tronix_db_sync.py` | Conector de banco de dados |
| `E:\Shared\chat_server_db.py` | Chat server com DB |
| `E:\Windows\start-fast-chat.bat` | Iniciar IA (atualizado) |
| `TRONIX_SETUP.md` | Documentação completa |

## ⚠️ Requisitos

1. **XAMPP** - MySQL deve estar rodando
2. **Python 3.12+** - Para scripts de sincronização
3. **Ollama** - Instalado no USB (E:\Shared\bin\)
4. **Conexão de rede** - Para baixar modelos (se necessário)

## 🎯 Funcionalidades

### IA Portátil
- Chat em tempo real com modelos locais
- Histórico salvo no banco de dados
- Interface web responsiva
- Suporte a múltiplos modelos

### Banco de Dados
- Sincronização automática de skills
- Logs de evolução
- Gerenciamento de projetos
- Histórico de conversas

## 🐛 Solução de Problemas

### MySQL não conecta
- Iniciar XAMPP Control Panel
- Clique em "Start" ao lado de MySQL
- Verificar porta 3306: `netstat -an | findstr :3306`

### Ollama não responde
- Verificar se está rodando: `curl http://127.0.0.1:11434/api/tags`
- Reiniciar: `taskkill /f /im ollama-windows.exe`

### Erro de Python
- Instalar pymysql: `pip install pymysql`
- Verificar versão: `python --version`

## 📈 Próximos Passos

1. ✅ IA portátil configurada
2. ✅ Banco de dados conectado
3. ✅ Skills sincronizadas
4. ⏳ Testar interface web
5. ⏳ Criar API de consultas
6. ⏳ Integrar com outros sistemas

## 🎉 Sistema Pronto!

O Tronix está totalmente configurado e pronto para uso!

**Acesse**: `http://localhost:3333`  
**Banco**: `tronix_system` (MySQL)  
**Skills**: 46 sincronizadas  

Para iniciar tudo de uma vez:
```bash
cd C:\xampp\htdocs\agente\.opencode
start_tronix_system.bat
```
