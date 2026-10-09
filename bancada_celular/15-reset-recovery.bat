@echo off
REM Reset de fabrica via recovery - rota mais barata e de menor risco.
REM Antes de apagar, o script CONFIRMA que o cliente tem a senha do Google
REM na mao. Sem isso o reset vira problema de FRP e voce perde dinheiro.
chcp 65001 >nul
setlocal
cd /d "%~dp0"
if not exist "logs" mkdir logs
python "%~dp0reset_recovery.py"
pause
