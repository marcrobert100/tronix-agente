@echo off
chcp 65001 > nul
title Gerador de Licenças TRONIX
color 0A

echo ========================================
echo   SISTEMA DE LICENCIAMENTO TRONIX
echo ========================================
echo.
echo [1] Gerador de Licenças (GUI)
echo [2] Validador de Licenças (GUI)
echo [3] Modo Console
echo [4] Sair
echo.
set /p opcao=Escolha uma opção: 

if "%opcao%"=="1" (
    cls
    echo Iniciando Gerador de Licenças...
    python gerador_licencas_gui.py
    goto fim
)

if "%opcao%"=="2" (
    cls
    echo Iniciando Validador de Licenças...
    python validador_licencas_gui.py
    goto fim
)

if "%opcao%"=="3" (
    cls
    echo Iniciando Modo Console...
    python licenca_tronix.py
    goto fim
)

if "%opcao%"=="4" (
    exit
)

echo Opção inválida!
pause
goto inicio

:fim
pause
