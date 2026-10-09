@echo off
REM ==========================================================================
REM  CONECTAR NO MODELO DO KAGGLE (tunel Cloudflare)
REM  Uso:  conectar.bat  https://xxxx.trycloudflare.com
REM  Sem argumento: pergunta a URL e testa a que estiver salva.
REM ==========================================================================
setlocal
cd /d "%~dp0"
chcp 65001 >nul
title TRONIX - Conectar no modelo do Kaggle

if not "%~1"=="" (
    echo %~1> tunnel_url.txt
)

if not exist tunnel_url.txt (
    set "URL="
    set /p "URL=URL do tunel (https://xxxx.trycloudflare.com): "
    if "%URL%"=="" (
        echo.
        echo URL obrigatoria. Copie a linha "TUNEL ATIVO: https://..." da saida do Kaggle.
        pause
        exit /b 1
    )
    echo %URL%> tunnel_url.txt
)

for /f "usebackq delims=" %%U in ("tunnel_url.txt") do set "TUNNEL=%%U"
set "TUNNEL=%TUNNEL:/ =%"

echo.
echo === TESTANDO O TUNEL ===
python cliente.py --listar
if errorlevel 1 (
    echo.
    echo FALHOU. conferir: a celula do tunel ainda esta rodando no Kaggle?
    echo A URL trycloudflare morre quando a celula para.
    pause
    exit /b 1
)

echo.
echo === CONFIGURANDO O CLINE (VS Code) ===
echo   API Provider : OpenAI Compatible
echo   Base URL     : %TUNNEL%/v1
echo   API Key      : ollama
echo   Model        : qwen3-coder:30b   (ou o que o --listar mostrar)
echo.
echo   Copie esses 4 campos na engrenagem do Cline.
echo.

set "KAGGLE_TUNNEL_URL=%TUNNEL%"
set "OPENAI_BASE_URL=%TUNNEL%/v1"
set "OPENAI_API_BASE=%TUNNEL%/v1"
set "OPENAI_API_KEY=ollama"
set "KAGGLE_MODEL=qwen3-coder:30b"

echo === ABRINDO O VS CODE ===
if exist "%LOCALAPPDATA%\Programs\Microsoft VS Code\bin\code.cmd" (
    "%LOCALAPPDATA%\Programs\Microsoft VS Code\bin\code.cmd" "%~dp0"
) else (
    echo VS Code nao encontrado em %%LOCALAPPDATA%%\Programs\Microsoft VS Code
    start "" "https://code.visualstudio.com/download"
)

echo.
echo === TESTE DE RESPOSTA ===
set /p "P=Pergunta de teste (Enter para pular): "
if not "%P%"=="" python cliente.py "%P%"

echo.
echo Dica: ambiente pronto so nesta janela. Para usar o Qwen Code/aider
echo com o mesmo modelo, rode:  usar_qwen.bat
echo.
echo Lembre-se: ao terminar, pare a celula do tunel + Stop Session no Kaggle.
pause
