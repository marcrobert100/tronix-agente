@echo off
chcp 65001 >nul
title Delivery Bot - Atualizador
color 0B

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║     🔄 DELIVERY BOT - ATUALIZADOR                         ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

:: Verificar se está rodando
tasklist /FI "IMAGENAME eq node.exe" 2>NUL | find /I "node.exe" >NUL
if %errorlevel% equ 0 (
    echo ⚠️  O servidor está rodando!
    echo    Por favor, pare o servidor antes de atualizar.
    echo    Pressione Ctrl+C no terminal do servidor ou feche a janela.
    echo.
    set /p confirmar="Continuar mesmo assim? (S/N): "
    if /i not "%confirmar%"=="S" (
        echo ❌ Operação cancelada.
        pause
        exit /b 0
    )
)

echo [1/3] Atualizando dependências...
call npm update --production
if %errorlevel% neq 0 (
    echo ❌ Erro ao atualizar dependências!
    pause
    exit /b 1
)
echo ✅ Dependências atualizadas

echo.
echo [2/3] Verificando atualizações do npm...
npm outdated --depth=0
echo.

echo [3/3] Limpando cache...
npm cache clean --force 2>nul
echo ✅ Cache limpo

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║     ✅ ATUALIZAÇÃO CONCLUÍDA!                             ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 📋 Execute INICIAR.bat para iniciar o servidor atualizado.
echo.
pause
