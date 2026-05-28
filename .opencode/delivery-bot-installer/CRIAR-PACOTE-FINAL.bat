@echo off
chcp 65001 >nul
title Delivery Bot - Criar Pacote Final
color 0A

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║     📦 DELIVERY BOT - CRIAR PACOTE PRONTO                 ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo Criando pacote completo para instalar em outro PC...
echo.

:: Definir caminhos
set BOT_ORIGEM=C:\xampp\htdocs\agente\.opencode\casa
set PACOTE=C:\xampp\htdocs\agente\.opencode\delivery-bot-installer\instalacao
set DIST=C:\xampp\htdocs\agente\.opencode\delivery-bot-installer\dist

:: Limpar pasta dist
if exist "%DIST%" rmdir /s /q "%DIST%"
mkdir "%DIST%\delivery-bot"

echo [1/5] Copiando servidor...
copy /y "%BOT_ORIGEM%\server.js" "%PACOTE%\" >nul 2>&1
copy /y "%BOT_ORIGEM%\tts-service.js" "%PACOTE%\" >nul 2>&1
echo ✅ Servidor copiado

echo.
echo [2/5] Copiando painel...
if not exist "%PACOTE%\public" mkdir "%PACOTE%\public"
if not exist "%PACOTE%\public\css" mkdir "%PACOTE%\public\css"
if not exist "%PACOTE%\public\js" mkdir "%PACOTE%\public\js"
if not exist "%PACOTE%\public\img" mkdir "%PACOTE%\public\img"
xcopy /s /e /q /y "%BOT_ORIGEM%\public\*" "%PACOTE%\public\" >nul 2>&1
echo ✅ Painel copiado

echo.
echo [3/5] Criando estrutura...
if not exist "%PACOTE%\logs" mkdir "%PACOTE%\logs"
if not exist "%PACOTE%\logs\tts" mkdir "%PACOTE%\logs\tts"
echo ✅ Estrutura criada

echo.
echo [4/5] Gerando ZIP...
xcopy /s /e /q "%PACOTE%\*" "%DIST%\delivery-bot\" >nul 2>&1
powershell -Command "Compress-Archive -Path '%DIST%\delivery-bot\*' -DestinationPath '%DIST%\delivery-bot.zip' -Force" 2>nul
echo ✅ ZIP criado

echo.
echo [5/5] Limpando...
rmdir /s /q "%DIST%\delivery-bot" 2>nul
echo ✅ Pronto!

:: Abrir pasta
explorer "%DIST%"

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║     ✅ PACOTE PRONTO!                                     ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 📁 Arquivo: dist\delivery-bot.zip
echo.
echo 📋 Para o cliente instalar:
echo    1. Extrair o ZIP
echo    2. Abrir a pasta
echo    3. Clicar em INSTALAR.bat
echo    4. Abrir instalar.html para configurar
echo    5. Clicar em INICIAR.bat
echo.
pause
