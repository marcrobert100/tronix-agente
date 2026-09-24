@echo off
title Tronix - Iniciar Servicos Core
echo ========================================
echo      TRONIX - INICIAR SERVICOS
echo ========================================
echo.
echo [1/3] Iniciando API Gateway (8081)...
start "Tronix API Gateway" /B python "%~dp0api_gateway.py"

echo [2/3] Abrindo n8n (5678)...
start "Tronix n8n" cmd /k "cd /d %~dp0 && npx n8n start"

echo [3/3] Verificando API Gateway...
timeout /t 4 /nobreak >nul
python -c "import requests; r=requests.get('http://localhost:8081/health', timeout=10); print('API Gateway:', r.status_code, r.json() if r.status_code==200 else '')" 2>nul

echo.
echo ========================================
echo      PRONTO!
echo ========================================
echo.
echo API Gateway: http://localhost:8081
echo n8n:         http://localhost:5678
echo Galeria:     http://localhost/agente/
echo ========================================
pause