@echo off
title Tronix - Unified System
cd /d "%~dp0"

echo.
echo  ========================================
echo    TRONIX - SISTEMA UNIFICADO
echo    PCsoluoes, Viosa-AL
echo  ========================================
echo.
echo  Pressione CTRL+C para parar tudo
echo.

:: 1. Inicializa banco SQLite
echo  [1/4] Inicializando banco de dados...
python tronix_logger.py
if %errorlevel% neq 0 echo  [WARN] Erro no banco, mas continuando...

:: 2. Sobe API Gateway (porta 8081)
echo  [2/4] Subindo API Gateway (porta 8081)...
start "Tronix-Gateway" cmd /c "python api_gateway.py 8081"

:: Aguarda gateway ficar online
timeout /t 3 /nobreak >nul

:: 3. Verifica gateway
echo  [3/4] Verificando gateway...
python -c "import urllib.request; print('  [OK] Gateway:', urllib.request.urlopen('http://localhost:8081/health', timeout=5).read().decode()[:100])" 2>nul || echo  [WARN] Gateway ainda iniciando...

:: 4. Abre dashboard
echo  [4/4] Abrindo interfaces:
start http://localhost/agente/dashboard.php
start http://localhost:8081/
start http://localhost:8081/health

echo.
echo  ========================================
echo    SISTEMA PRONTO
echo    Gateway:  http://localhost:8081
echo    Health:   http://localhost:8081/health
echo    Dashboard: http://localhost/agente/dashboard.php
echo    n8n:      http://localhost:5678
echo.
echo    Para iniciar o time CrewAI:
echo      python tronix_crew.py
echo.
echo    Para testar o gateway:
echo      curl http://localhost:8081/agentes
echo      curl -X POST http://localhost:8081/executar -H "Content-Type: application/json" -d "{\"script\":\"gera_video\",\"args\":\"--teste\"}"
echo.
echo    Interfaces visuais (se instaladas):
echo      Dify:     http://localhost:3000
echo      RAGFlow:  http://localhost:9380
echo      Langflow: http://localhost:7860
echo  ========================================
echo.

:: Mantm janela aberta
pause
