@echo off
chcp 65001 > nul
title Delivery Bot WhatsApp — Marco Roberto
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║   🛵  DELIVERY BOT WHATSAPP                             ║
echo ║   Desenvolvido por Marco Roberto                        ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

:: Verificar Node.js
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Node.js nao encontrado!
    echo.
    echo Baixe e instale em: https://nodejs.org/
    echo Escolha a versao LTS.
    echo.
    pause
    exit /b 1
)

:: Instalar dependencias se express nao existir
if not exist "node_modules\express" (
    echo Instalando dependencias... Aguarde 1-2 minutos.
    echo.
    call npm install
    if %errorlevel% neq 0 (
        echo.
        echo [ERRO] Falha ao instalar dependencias.
        echo Verifique sua conexao com a internet e tente novamente.
        pause
        exit /b 1
    )
    echo.
    echo Dependencias instaladas com sucesso!
    echo.
)

echo Iniciando o servidor...
echo.
echo Acesse no navegador:  http://localhost:3000
echo.
echo O QR Code aparecera na tela - escaneie com o WhatsApp!
echo Para fechar o bot, feche esta janela ou pressione Ctrl+C
echo.
echo ================================================================
echo.

node server.js

pause
