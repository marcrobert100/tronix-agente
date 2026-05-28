@echo off
chcp 65001 >nul
title Delivery Bot - Restaurar Backup
color 0E

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║     🔄 DELIVERY BOT - RESTAURAR BACKUP                    ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

:: Verificar se existem backups
if not exist "backups" (
    echo ❌ Pasta de backups não encontrada!
    echo    Execute BACKUP.bat primeiro para criar um backup.
    pause
    exit /b 1
)

:: Listar backups disponíveis
echo Backups disponíveis:
echo.
dir /b /o-d "backups\*.zip" 2>nul
dir /b /o-d "backups" 2>nul | findstr /v ".zip"
echo.

:: Solicitar qual backup restaurar
set /p nome_backup="Digite o nome do backup para restaurar (ou 'sair'): "
if /i "%nome_backup%"=="sair" (
    echo ❌ Operação cancelada.
    pause
    exit /b 0
)

:: Verificar se o backup existe
if not exist "backups\%nome_backup%" (
    if not exist "backups\%nome_backup%.zip" (
        echo ❌ Backup não encontrado: %nome_backup%
        pause
        exit /b 1
    )
)

echo.
echo ⚠️  ATENÇÃO: Esta ação irá substituir os dados atuais!
echo.
set /p confirmar="Deseja continuar? (S/N): "
if /i not "%confirmar%"=="S" (
    echo ❌ Operação cancelada.
    pause
    exit /b 0
)

:: Parar servidor se estiver rodando
tasklist /FI "IMAGENAME eq node.exe" 2>NUL | find /I "node.exe" >NUL
if %errorlevel% equ 0 (
    echo.
    echo ⚠️  Parando servidor...
    taskkill /F /IM node.exe >nul 2>&1
    timeout /t 2 /nobreak >nul
)

:: Extrair backup se for zip
if exist "backups\%nome_backup%.zip" (
    echo.
    echo [1/3] Extraindo backup...
    powershell -Command "Expand-Archive -Path 'backups\%nome_backup%.zip' -DestinationPath 'backups\%nome_backup%' -Force" 2>nul
    echo ✅ Backup extraído
)

:: Restaurar arquivos
echo.
echo [2/3] Restaurando arquivos...

if exist "backups\%nome_backup%\logs" (
    if exist "logs" rmdir /s /q "logs"
    xcopy /s /e /q "backups\%nome_backup%\logs" "logs\" >nul
    echo ✅ Logs restaurados
)

if exist "backups\%nome_backup%\config.json" (
    copy /y "backups\%nome_backup%\config.json" "." >nul
    echo ✅ config.json restaurado
)

if exist "backups\%nome_backup%\.env" (
    copy /y "backups\%nome_backup%\.env" "." >nul
    echo ✅ .env restaurado
)

if exist "backups\%nome_backup%\.wwebjs_auth" (
    if exist ".wwebjs_auth" rmdir /s /q ".wwebjs_auth"
    xcopy /s /e /q "backups\%nome_backup%\.wwebjs_auth" ".wwebjs_auth\" >nul
    echo ✅ Dados do WhatsApp restaurados
)

echo.
echo [3/3] Verificando integridade...
if exist "config.json" (
    echo ✅ config.json OK
) else (
    echo ⚠️  config.json não encontrado
)
if exist ".env" (
    echo ✅ .env OK
) else (
    echo ⚠️  .env não encontrado
)

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║     ✅ RESTAURAÇÃO CONCLUÍDA!                             ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 📋 Execute INICIAR.bat para iniciar o servidor.
echo.
pause
