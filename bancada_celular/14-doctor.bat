@echo off
REM Doctor - verifica o kit inteiro e valida o que o manual afirma contra
REM o que esta realmente instalado. Deriva o driver do codigo-fonte do mtkclient.
chcp 65001 >nul
setlocal
cd /d "%~dp0"
if not exist "logs" mkdir logs
python "%~dp0doctor.py"
echo.
pause
