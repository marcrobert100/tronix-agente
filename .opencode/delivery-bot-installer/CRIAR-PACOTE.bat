@echo off
chcp 65001 >nul
title Delivery Bot - Criar Pacote
color 0A

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║     📦 DELIVERY BOT - CRIAR PACOTE DE INSTALAÇÃO          ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

:: Verificar se a pasta instalacao existe
if not exist "instalacao" (
    echo ❌ Pasta 'instalacao' não encontrada!
    pause
    exit /b 1
)

:: Verificar se tem os arquivos necessários
echo [1/4] Verificando arquivos...
set ok=1
if not exist "instalacao\server.js" (
    echo ❌ server.js não encontrado na pasta instalacao
    set ok=0
)
if not exist "instalacao\package.json" (
    echo ❌ package.json não encontrado na pasta instalacao
    set ok=0
)
if not exist "instalacao\public" (
    echo ❌ Pasta public não encontrada na pasta instalacao
    set ok=0
)

if %ok% equ 0 (
    echo.
    echo ⚠️  Execute COPIAR-ARQUIVOS.bat primeiro para copiar os arquivos do bot.
    pause
    exit /b 1
)
echo ✅ Todos os arquivos encontrados

:: Criar pasta de distribuição
echo.
echo [2/4] Criando pasta de distribuição...
if not exist "dist" mkdir dist
set NOME_PACOTE=delivery-bot-v2.0.0
if exist "dist\%NOME_PACOTE%" rmdir /s /q "dist\%NOME_PACOTE%"
mkdir "dist\%NOME_PACOTE%"
echo ✅ Pasta criada: dist\%NOME_PACOTE%

:: Copiar arquivos para a pasta de distribuição
echo.
echo [3/4] Copiando arquivos...
xcopy /s /e /q "instalacao\*" "dist\%NOME_PACOTE%\" >nul
echo ✅ Arquivos copiados

:: Criar arquivo ZIP
echo.
echo [4/4] Criando arquivo ZIP...
powershell -Command "Compress-Archive -Path 'dist\%NOME_PACOTE%\*' -DestinationPath 'dist\%NOME_PACOTE%.zip' -Force" 2>nul
if %errorlevel% equ 0 (
    echo ✅ Pacote criado: dist\%NOME_PACOTE%.zip
) else (
    echo ❌ Erro ao criar arquivo ZIP
    pause
    exit /b 1
)

:: Mostrar tamanho do arquivo
for %%A in ("dist\%NOME_PACOTE%.zip") do set tamanho=%%~zA
set /a tamanhoMB=%tamanho% / 1048576

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║     ✅ PACOTE CRIADO COM SUCESSO!                         ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 📁 Pacote: dist\%NOME_PACOTE%.zip
echo 📊 Tamanho: %tamanhoMB% MB
echo.
echo 📋 Para instalar em outro computador:
echo    1. Extraia o arquivo ZIP
echo    2. Execute INSTALAR.bat
echo    3. Siga as instruções na tela
echo.
pause
