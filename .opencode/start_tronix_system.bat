@echo off
title Tronix System - Full Startup
color 0A

echo ===================================================
echo     TRONIX SYSTEM - Full Startup
echo ===================================================
echo.

:: 1. Sincronizar skills com banco de dados
echo [1/3] Sincronizando skills com banco de dados...
python sync_tronix.py
if %errorlevel% neq 0 (
    echo [ERRO] Falha na sincronizacao!
    pause
    exit
)
echo.

:: 2. Verificar conexao MySQL
echo [2/3] Verificando conexao MySQL...
cmd /c "C:\xampp\mysql\bin\mysql.exe" -u root -e "SELECT COUNT(*) FROM tronix_system.skills;" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] MySQL nao disponivel!
    echo Inicie o XAMPP Control Panel e ative o MySQL.
    pause
    exit
)
echo [OK] MySQL conectado!
echo.

:: 3. Iniciar IA Portatil
echo [3/3] Iniciando IA Portatil...
echo.
echo ===================================================
echo  TRONIX SYSTEM ESTA PRONTO!
echo ===================================================
echo.
echo  Acesse: http://localhost:3333
echo  Banco:  MySQL (tronix_system)
echo.
echo  Pressione Ctrl+C para encerrar.
echo ===================================================
echo.

:: Iniciar chat server com banco de dados
python "E:\Shared\chat_server_db.py"
