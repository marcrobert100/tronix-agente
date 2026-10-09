@echo off
REM ==========================================================================
REM  Opencode (CLI) usando o modelo do Kaggle
REM  A config do provider "kaggle" esta no opencode.json desta pasta.
REM  Uso:  usar_opencode.bat    (interativo)
REM ==========================================================================
setlocal
cd /d "%~dp0"

if not "%~1"=="" echo %~1> tunnel_url.txt
if not exist tunnel_url.txt (
    echo Sem tunnel_url.txt. Rode primeiro: conectar.bat https://xxxx.trycloudflare.com
    pause
    exit /b 1
)

for /f "usebackq delims=" %%U in ("tunnel_url.txt") do set "TUNNEL=%%U"
set "TUNNEL=%TUNNEL:/ =%"
set "KAGGLE_TUNNEL_URL=%TUNNEL%"

echo.
echo Opencode com provider kaggle -> %TUNNEL%/v1
echo Modelos: /models   (escolha kaggle/qwen3-coder:30b)
echo.
call opencode %*
