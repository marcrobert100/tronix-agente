@echo off
chcp 65001 >nul
title Sistema de Estudo - College Prep

echo.
echo ========================================
echo   SISTEMA DE ESTUDO - COLLEGE PREP
echo ========================================
echo.

cd /d "C:\xampp\htdocs\agente\estudo"

echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERRO: Python não encontrado!
    echo.
    echo Opções:
    echo 1. Use o XAMPP (Inicie o Apache e acesse http://localhost/agente/estudo/)
    echo 2. Instale o Python em https://www.python.org/downloads/
    echo.
    pause
    exit /b
)

echo.
echo Python detectado!
echo Iniciando servidor em http://localhost:8000
echo.
echo Para parar: Pressione Ctrl+C
echo ========================================
echo.

start "" "http://localhost:8000"
python -m http.server 8000