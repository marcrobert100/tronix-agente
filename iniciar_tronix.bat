@echo off
title Tronix v1.4 - Unified System
cd /d "%~dp0"

echo.
echo  ========================================
echo    TRONIX v1.4 - SISTEMA UNIFICADO
echo    PCsoluções, Viçosa-AL
echo  ========================================
echo.

:: 1. Verificacao rapida
echo  [CHECK] Verificando sistema...
python tronix_check.py 2>nul
echo.

:: 2. Inicializa banco SQLite
echo  [1/5] Inicializando banco de dados...
python tronix_logger.py
if %errorlevel% neq 0 echo  [WARN] Erro no banco, mas continuando...

:: 3. Arquivar memoria antiga
echo  [2/5] Arquivando memoria...
python tronix_memoria_manager.py 2>nul

:: 4. Sobe API Gateway v2 (porta 8081)
echo  [3/5] Subindo API Gateway v2 (porta 8081, WebSocket ativo)...
start "Tronix-Gateway" cmd /c "python api_gateway.py 8081"

timeout /t 3 /nobreak >nul

:: 5. Verifica gateway
echo  [4/5] Verificando gateway...
python -c "import urllib.request;print('  [OK] Gateway:',urllib.request.urlopen('http://localhost:8081/health',timeout=5).read().decode()[:100])" 2>nul || echo  [WARN] Gateway ainda iniciando...

:: 6. Abre interfaces
echo  [5/5] Abrindo interfaces:
start http://localhost/agente/dashboard.php
start http://localhost:8081/
start http://localhost:8081/health
start http://localhost/agente/dashboard_v2.html

echo.
echo  ========================================
echo    SISTEMA PRONTO - TRONIX v1.4
echo.
echo    Gateway:     http://localhost:8081
echo    WebSocket:   ws://localhost:8081/ws
echo    Health:      http://localhost:8081/health
echo    Dashboard:   http://localhost/agente/dashboard.php
echo    DashboardV2: http://localhost/agente/dashboard_v2.html
echo    n8n:         http://localhost:5678
echo.
echo    MCP Server (para TRAE SOLO):
echo      python tronix_mcp_server.py
echo      Config: .trae/mcp.json
echo.
echo    Time Multi-Agente:
echo      python tronix_crew.py
echo.
echo    Verificacao:
echo      python tronix_check.py
echo.
echo    Memoria:
echo      python tronix_memoria_manager.py
echo.
echo    Interfaces visuais:
echo      Dify:     http://localhost:3000
echo      RAGFlow:  http://localhost:9380
echo      Langflow: http://localhost:7860
echo  ========================================
echo.

pause
