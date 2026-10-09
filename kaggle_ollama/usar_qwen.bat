@echo off
REM ==========================================================================
REM  Qwen Code (CLI) apontado para o modelo do Kaggle
REM  Le a URL de tunnel_url.txt. Shift+clique = passa a URL como argumento.
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

set "OPENAI_BASE_URL=%TUNNEL%/v1"
set "OPENAI_API_BASE=%TUNNEL%/v1"
set "OPENAI_API_KEY=ollama"
set "OPENAI_MODEL=qwen3-coder:30b"
set "KAGGLE_TUNNEL_URL=%TUNNEL%"

echo.
echo Qwen Code usando %TUNNEL%/v1  modelo %OPENAI_MODEL%
echo.
call qwen %*
