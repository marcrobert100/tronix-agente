@echo off
REM ==========================================================================
REM  Aider (CLI) apontado para o modelo do Kaggle
REM  Uso:  usar_aider.bat            (abre no diretorio atual)
REM        usar_aider.bat C:\projeto
REM ==========================================================================
setlocal
cd /d "%~dp0"

if not exist tunnel_url.txt (
    echo Sem tunnel_url.txt. Rode primeiro: conectar.bat https://xxxx.trycloudflare.com
    pause
    exit /b 1
)

for /f "usebackq delims=" %%U in ("tunnel_url.txt") do set "TUNNEL=%%U"
set "TUNNEL=%TUNNEL:/ =%"

set "OPENAI_API_BASE=%TUNNEL%/v1"
set "OPENAI_API_KEY=ollama"

if "%~1"=="" (cd /d "%CD%") else (cd /d "%~1")

echo.
echo Aider usando %TUNNEL%/v1  modelo openai/qwen3-coder:30b
echo Pasta: %CD%
echo.
aider --model openai/qwen3-coder:30b
