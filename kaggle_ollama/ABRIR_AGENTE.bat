@echo off
chcp 65001 >nul
title Agente - VS Code + Cline na GPU do Kaggle
cd /d "%~dp0"

echo.
echo ==========================================================
echo   AGENTE - GPU do Kaggle (qwen3-coder:30b) + Cline
echo ==========================================================
echo.

where kaggle >nul 2>nul || (echo ERRO: CLI do Kaggle nao esta no PATH. Rode: pip install kaggle & kaggle auth login)
where code   >nul 2>nul || (echo ERRO: VS Code nao esta no PATH.)

set "CODEEXE=%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"
if not exist "%CODEEXE%" set "CODEEXE="

if exist "tunnel_url.txt" (
    set /a n=0
    for /f "usebackq tokens=*" %%U in ("tunnel_url.txt") do set /a n+=1
    if %n% gtr 0 (
        set "TUNNEL=" & for /f "usebackq tokens=*" %%U in ("tunnel_url.txt") do set "TUNNEL=%%U"
        echo Tunel: !TUNNEL!
        echo.
        echo Testando o modelo...
        python cliente.py --listar
    ) else (
        echo Sem URL salva. Rode:  python subir_kernel.py
    )
) else (
    echo Sem URL salva. Rode:  python subir_kernel.py
)

echo.
echo Abrindo o VS Code com porta de depuracao (o Cline ja esta configurado)...
echo.
if defined CODEEXE (
    start "" "%CODEEXE%" --remote-debugging-port=9222
) else (
    start "" code --remote-debugging-port=9222
)

echo   No VS Code: clique no icone do Cline na barra lateral e digite a tarefa.
echo   Para abrir em tela cheia: Ctrl+Shift+A
echo.
echo Quando terminar, encerre a GPU para nao queimar cota:
echo     python subir_kernel.py --parar
echo.
pause
