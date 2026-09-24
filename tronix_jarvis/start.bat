@echo off
title TRONIX AI - Control HUD
cd /d "%~dp0"
echo [TRONIX] Iniciando JARVIS-Mark structure...
python -c "import PyQt6" 2>nul
if errorlevel 1 (
    echo [TRONIX] Dependencias faltando. Rodando setup (pip install + Playwright)...
    python setup.py
    if errorlevel 1 exit /b 1
)
python main.py