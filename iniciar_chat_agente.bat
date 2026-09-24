@echo off
rem Inicia servidor de ferramentas do agente (porta 8000) se nao estiver rodando
tasklist /FI "IMAGENAME eq python.exe" 2>nul | find /I "python.exe" >nul
if not errorlevel 1 (
  curl -s http://localhost:8000/tools/status >nul 2>&1
  if not errorlevel 1 (
    echo Servidor de ferramentas ja ativo na porta 8000.
  ) else (
    start "" python "%~dp0tronix_agent_server.py"
    echo Servidor de ferramentas iniciado (porta 8000).
  )
) else (
  start "" python "%~dp0tronix_agent_server.py"
  echo Servidor de ferramentas iniciado (porta 8000).
)
start "" http://localhost/agente/chat_local.html
