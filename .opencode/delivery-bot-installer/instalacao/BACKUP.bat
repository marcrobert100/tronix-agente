@echo off
chcp 65001 >nul
title Delivery Bot - Backup
color 0E

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║     💾 DELIVERY BOT - BACKUP DE DADOS                     ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

:: Criar pasta de backups se não existir
if not exist "backups" mkdir backups

:: Nome do backup com data e hora
for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set data=%%c-%%b-%%a
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set hora=%%a%%b
set nome_backup=backup_%data%_%hora%

echo [1/4] Criando backup: %nome_backup%
echo.

:: Criar pasta do backup
mkdir "backups\%nome_backup%"

:: Copiar logs
echo [2/4] Copiando logs...
if exist "logs" (
    xcopy /s /e /q "logs" "backups\%nome_backup%\logs\" >nul
    echo ✅ Logs copiados
) else (
    echo ⚠️  Pasta logs não encontrada
)

:: Copiar configurações
echo [3/4] Copiando configurações...
if exist "config.json" (
    copy /y "config.json" "backups\%nome_backup%\" >nul
    echo ✅ config.json copiado
)
if exist ".env" (
    copy /y ".env" "backups\%nome_backup%\" >nul
    echo ✅ .env copiado
)

:: Copiar dados do WhatsApp
echo [4/4] Copiando dados do WhatsApp...
if exist ".wwebjs_auth" (
    xcopy /s /e /q ".wwebjs_auth" "backups\%nome_backup%\.wwebjs_auth\" >nul
    echo ✅ Dados do WhatsApp copiados
) else (
    echo ⚠️  Dados do WhatsApp não encontrados
)

:: Criar arquivo compactado
echo.
echo Compactando backup...
powershell -Command "Compress-Archive -Path 'backups\%nome_backup%\*' -DestinationPath 'backups\%nome_backup%.zip' -Force" 2>nul
if %errorlevel% equ 0 (
    rmdir /s /q "backups\%nome_backup%"
    echo ✅ Backup compactado: backups\%nome_backup%.zip
) else (
    echo ✅ Backup salvo em: backups\%nome_backup%\
)

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║     ✅ BACKUP CONCLUÍDO!                                  ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 📁 Backup salvo em: backups\
echo.
pause
