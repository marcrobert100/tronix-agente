@echo off
title Tronix Assistente Completo
color 0A

echo ===================================================
echo     TRONIX ASSISTENTE COMPLETO
echo ===================================================
echo.
echo  Iniciando assistente sem restricoes...
echo.

:: Iniciar assistente em background
start "Tronix Assistente" python "C:\xampp\htdocs\agente\.opencode\tronix_assistente.py"

:: Aguardar inicialização
timeout /t 3 /nobreak >nul

:: Iniciar IA portátil
echo Iniciando IA Portatil...
start "Tronix AI" "E:\Windows\start-fast-chat.bat"

echo.
echo ===================================================
echo  ASSISTENTE INICIADO!
echo ===================================================
echo.
echo  Assistente API: http://localhost:8080
echo  IA Portatil:    http://localhost:3333
echo.
echo  O assistente pode executar qualquer comando no PC.
echo  Use a IA para controlar o sistema atraves dos comandos.
echo.
echo  Pressione Ctrl+C para encerrar tudo.
echo ===================================================
echo.

:: Manter script rodando
pause
