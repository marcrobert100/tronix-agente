@echo off
chcp 65001 >nul
title Delivery Bot - Servidor
color 0B

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║     🚀 DELIVERY BOT - INICIANDO...                        ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

:: Verificar se .env existe
if not exist ".env" (
    echo ❌ Arquivo .env não encontrado!
    echo    Execute INSTALAR.bat primeiro ou crie o arquivo .env
    pause
    exit /b 1
)

:: Verificar se node_modules existe
if not exist "node_modules" (
    echo ⚠️  node_modules não encontrado. Instalando dependências...
    call npm install --production
    echo.
)

:: Iniciar o servidor
echo ✅ Iniciando servidor...
echo.
echo 📱 Acesse o painel em: http://localhost:3000
echo 🔐 Login padrão: admin / admin123
echo.
echo ⚠️  Para parar o servidor, pressione Ctrl+C
echo.
echo ════════════════════════════════════════════════════════════
echo.

node server.js

:: Se o servidor parar
echo.
echo ⚠️  Servidor parado.
pause
