@echo off
chcp 65001 > nul
title SISTEMA DE LICENCIAMENTO TRONIX
color 0B

echo.
echo ========================================
echo    SISTEMA DE LICENCIAMENTO TRONIX
echo ========================================
echo.
echo 1) Abrir Gerador de Licenças
echo 2) Abrir Validador de Licenças
echo 3) Abrir Modo Console
echo 4) Sair
echo.
echo ========================================
echo.

set /p escolha=Digite sua opção: 

if "%escolha%"=="1" goto GERADOR
if "%escolha%"=="2" goto VALIDADOR
if "%escolha%"=="3" goto CONSOLE
if "%escolha%"=="4" exit
goto ERRO

:GERADOR
cd /d C:\xampp\htdocs\agente
start "" "C:\Users\CHCONTE RECPÇÃO\AppData\Local\Programs\Python\Python312\python.exe" gerador_licencas_gui.py
exit

:VALIDADOR
cd /d C:\xampp\htdocs\agente
start "" "C:\Users\CHCONTE RECPÇÃO\AppData\Local\Programs\Python\Python312\python.exe" validador_licencas.py
exit

:CONSOLE
cd /d C:\xampp\htdocs\agente
cls
"C:\Users\CHCONTE RECPÇÃO\AppData\Local\Programs\Python\Python312\python.exe" licenca_tronix.py
pause
exit

:ERRO
echo Opção inválida!
pause
cls
goto MENU

:MENU
call "%~f0"
