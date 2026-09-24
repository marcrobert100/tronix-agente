@echo off
echo Iniciando Tronix Memory System...
set PATH=%PATH%;%USERPROFILE%\.local\bin

echo [1] Iniciando agentmemory...
start /B agentmemory serve

echo [2] Aguardando 15 segundos...
timeout /t 15 /nobreak > nul

echo [3] Verificando status...
agentmemory status

echo.
echo Tronix Memory System iniciado!
echo REST API: http://localhost:3111
echo Viewer: http://localhost:3113
