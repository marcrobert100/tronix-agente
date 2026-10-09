@echo off
REM Samsung FRP via ADB - interface grafica. Requer USB debugging ja ativado no aparelho.
setlocal
set BASE=%~dp0
cd /d "%BASE%frp\samsung-frp-gui"
python -c "import frp_gui" 2>nul
python main.py
if errorlevel 1 (
  echo.
  echo  ERRO. Instale deps: cd "%BASE%frp\samsung-frp-gui" ^&^& python -m pip install -r requirements.txt
  pause
)
