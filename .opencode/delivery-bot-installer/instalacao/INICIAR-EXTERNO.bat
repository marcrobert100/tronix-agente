@echo off
chcp 65001 >nul
title Delivery Bot - Servidor Externo
color 0D

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║     🌐 DELIVERY BOT - ACESSO EXTERNO                      ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

:: Verificar se ngrok está instalado
where ngrok >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Ngrok não encontrado!
    echo.
    echo Para instalar o Ngrok:
    echo 1. Acesse: https://ngrok.com/
    echo 2. Crie uma conta gratuita
    echo 3. Baixe e extraia o ngrok.exe nesta pasta
    echo 4. Execute: ngrok config add-authtoken SEU_TOKEN
    echo.
    echo Após instalar, execute este script novamente.
    pause
    exit /b 1
)

:: Verificar se .env existe
if not exist ".env" (
    echo ❌ Arquivo .env não encontrado!
    echo    Execute INSTALAR.bat primeiro.
    pause
    exit /b 1
)

echo ✅ Ngrok encontrado
echo.

:: Iniciar ngrok em segundo plano
echo [1/2] Iniciando túnel Ngrok...
start /b ngrok http 3000
timeout /t 5 /nobreak >nul

:: Obter URL do ngrok
echo.
echo [2/2] Obtendo URL pública...
echo.
echo ════════════════════════════════════════════════════════════
echo.
echo 🌐 URL pública: Verifique http://127.0.0.1:4040
echo.
echo 📱 Acesse o painel de qualquer lugar usando a URL do Ngrok
echo.
echo ════════════════════════════════════════════════════════════
echo.

:: Iniciar o servidor
echo ✅ Iniciando servidor...
echo.
echo ⚠️  Para parar, pressione Ctrl+C
echo.

node server.js

echo.
echo ⚠️  Servidor parado.
pause
