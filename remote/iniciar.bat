@echo off
title Tronix Remote Server
color 0a
echo.
echo  ========================================
echo   TRONIX REMOTE - Controle Celular
echo  ========================================
echo.
echo  Iniciando servidor...
echo  Acesse: http://localhost:8765
echo.
echo  Para parar: Ctrl+C
echo  ========================================
echo.

cd /d "C:\xampp\htdocs\agente\remote"
python server.py
pause
