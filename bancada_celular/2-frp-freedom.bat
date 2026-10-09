@echo off
REM FRP universal Android 5 ate 15 - GUI tkinter. Com autorizacao do dono do aparelho.
setlocal
set BASE=%~dp0
cd /d "%BASE%frp\frp-freedom"
python main.py
if errorlevel 1 (
  echo.
  echo  ERRO ao iniciar. Verifique: python -m pip install -r requirements.txt
  pause
)
