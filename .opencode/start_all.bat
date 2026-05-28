@echo off
title Tronix System - Full Startup
color 0A

echo ===================================================
echo     TRONIX SYSTEM - FULL STARTUP
echo ===================================================
echo.

:: 1. Iniciar assistente sem restricoes
echo [1/4] Iniciando assistente sem restricoes...
start "Tronix Unrestricted" python "C:\xampp\htdocs\agente\.opencode\tronix_unrestricted.py"
timeout /t 2 /nobreak >nul

:: 2. Sincronizar skills
echo [2/4] Sincronizando skills...
python sync_tronix.py
if %errorlevel% neq 0 (
    echo [ERRO] Falha na sincronizacao!
)
echo.

:: 3. Iniciar IA portatil
echo [3/4] Iniciando IA Portatil...
start "Tronix AI" "E:\Windows\start-fast-chat.bat"
timeout /t 3 /nobreak >nul

:: 4. Verificar status
echo [4/4] Verificando status...
python check_status.py

echo.
echo ===================================================
echo  TRONIX SYSTEM ESTA PRONTO!
echo ===================================================
echo.
echo  Assistente SEM RESTRICOES: http://localhost:8081
echo  IA Portatil:               http://localhost:3333
echo  Banco de Dados:            MySQL (tronix_system)
echo.
echo  O assistente pode executar QUALQUER comando no PC.
echo  Use a IA para controlar o sistema atraves dos comandos.
echo.
echo  Pressione Ctrl+C para encerrar tudo.
echo ===================================================
echo.

pause
