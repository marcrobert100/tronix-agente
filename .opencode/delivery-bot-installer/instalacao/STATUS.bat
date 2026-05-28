@echo off
chcp 65001 >nul
title Delivery Bot - Status
color 0F

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║     📊 DELIVERY BOT - STATUS DO SISTEMA                   ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

:: Verificar Node.js
echo [1/6] Verificando Node.js...
node --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('node --version') do echo ✅ Node.js: %%i
) else (
    echo ❌ Node.js não encontrado
)

:: Verificar npm
echo.
echo [2/6] Verificando npm...
npm --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('npm --version') do echo ✅ npm: %%i
) else (
    echo ❌ npm não encontrado
)

:: Verificar dependências
echo.
echo [3/6] Verificando dependências...
if exist "node_modules" (
    echo ✅ node_modules encontrado
) else (
    echo ❌ node_modules não encontrado (execute INSTALAR.bat)
)

:: Verificar configurações
echo.
echo [4/6] Verificando configurações...
if exist ".env" (
    echo ✅ .env encontrado
) else (
    echo ❌ .env não encontrado
)
if exist "config.json" (
    echo ✅ config.json encontrado
) else (
    echo ⚠️  config.json não encontrado (será criado no primeiro acesso)
)

:: Verificar servidor
echo.
echo [5/6] Verificando servidor...
tasklist /FI "IMAGENAME eq node.exe" 2>NUL | find /I "node.exe" >NUL
if %errorlevel% equ 0 (
    echo ✅ Servidor rodando
    :: Verificar se a porta está respondendo
    curl -s -o nul -w "%%{http_code}" http://localhost:3000 >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Painel acessível em http://localhost:3000
    ) else (
        echo ⚠️  Servidor rodando mas painel não responde
    )
) else (
    echo ❌ Servidor não está rodando
)

:: Verificar logs
echo.
echo [6/6] Verificando logs...
if exist "logs" (
    for /f %%i in ('dir /b "logs\*.jsonl" 2^>nul ^| find /c /v ""') do set count=%%i
    echo ✅ Arquivos de log: %count%
) else (
    echo ⚠️  Pasta logs não encontrada
)

:: Verificar espaço em disco
echo.
echo ════════════════════════════════════════════════════════════
echo.
echo 💾 Espaço em disco:
for /f "tokens=3" %%a in ('dir /-c 2^>nul ^| findstr /c:"bytes free"') do echo    Livre: %%a bytes
echo.

:: Verificar backups
if exist "backups" (
    for /f %%i in ('dir /b "backups\*.zip" 2^>nul ^| find /c /v ""') do set bcount=%%i
    echo 📁 Backups disponíveis: %bcount%
) else (
    echo 📁 Nenhum backup encontrado
)

echo.
echo ════════════════════════════════════════════════════════════
echo.
pause
