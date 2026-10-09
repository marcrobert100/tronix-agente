@echo off
REM Monitor de modo BROM - fica olhando e avisa (com bipe) quando o MediaTek 0x0E8D engatar.
chcp 65001 >nul
setlocal
set BASE=%~dp0
cd /d "%BASE%"
python "%BASE%brom_watch.py"
echo.
pause
