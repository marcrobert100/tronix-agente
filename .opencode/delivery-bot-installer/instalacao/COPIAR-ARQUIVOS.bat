@echo off
chcp 65001 >nul
title Delivery Bot - Copiar Arquivos
color 0B

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║     📋 DELIVERY BOT - COPIAR ARQUIVOS DO PROJETO          ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo Este script copia os arquivos principais do bot para esta pasta.
echo Use quando atualizar o bot principal.
echo.

:: Definir pasta de origem (altere se necessário)
set ORIGEM=..\..\..\casa

:: Verificar se a pasta de origem existe
if not exist "%ORIGEM%\server.js" (
    echo ❌ Pasta de origem não encontrada!
    echo    Procurando em: %ORIGEM%
    echo.
    echo    Por favor, edite este script e ajuste o caminho ORIGEM
    echo    para apontar para a pasta do bot principal.
    pause
    exit /b 1
)

echo [1/5] Copiando server.js...
copy /y "%ORIGEM%\server.js" "." >nul
if %errorlevel% equ 0 (
    echo ✅ server.js copiado
) else (
    echo ❌ Erro ao copiar server.js
)

echo.
echo [2/5] Copiando tts-service.js...
if exist "%ORIGEM%\tts-service.js" (
    copy /y "%ORIGEM%\tts-service.js" "." >nul
    echo ✅ tts-service.js copiado
) else (
    echo ⚠️  tts-service.js não encontrado
)

echo.
echo [3/5] Copiando arquivos públicos...
if exist "%ORIGEM%\public" (
    if not exist "public" mkdir public
    if not exist "public\css" mkdir public\css
    if not exist "public\js" mkdir public\js
    if not exist "public\img" mkdir public\img
    
    xcopy /s /e /q /y "%ORIGEM%\public\*" "public\" >nul
    echo ✅ Arquivos públicos copiados
) else (
    echo ❌ Pasta public não encontrada
)

echo.
echo [4/5] Copiando scripts...
if exist "%ORIGEM%\Scripts" (
    if not exist "Scripts" mkdir Scripts
    xcopy /s /e /q /y "%ORIGEM%\Scripts\*" "Scripts\" >nul
    echo ✅ Scripts copiados
) else (
    echo ⚠️  Pasta Scripts não encontrada
)

echo.
echo [5/5] Verificando arquivos...
set ok=1
if not exist "server.js" (
    echo ❌ server.js não encontrado
    set ok=0
)
if not exist "public\painel.html" (
    echo ❌ painel.html não encontrado
    set ok=0
)
if not exist "public\js\app.js" (
    echo ❌ app.js não encontrado
    set ok=0
)

if %ok% equ 1 (
    echo.
    echo ╔════════════════════════════════════════════════════════════╗
    echo ║                                                            ║
    echo ║     ✅ ARQUIVOS COPIADOS COM SUCESSO!                     ║
    echo ║                                                            ║
    echo ╚════════════════════════════════════════════════════════════╝
) else (
    echo.
    echo ⚠️  Alguns arquivos não foram encontrados.
    echo    Verifique se o caminho de origem está correto.
)

echo.
pause
