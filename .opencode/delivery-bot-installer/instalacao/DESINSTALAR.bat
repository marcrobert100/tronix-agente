@echo off
chcp 65001 >nul
title Delivery Bot - Desinstalador
color 0C

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║     🗑️  DELIVERY BOT - DESINSTALADOR                      ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo ⚠️  ATENÇÃO: Esta ação irá remover:
echo.
echo    • node_modules (dependências)
echo    • logs (histórico de conversas)
echo    • config.json (configurações do bot)
echo    • .env (configurações de API)
echo.
echo    Os arquivos principais (server.js, public/) serão mantidos.
echo.

set /p confirmar="Deseja continuar? (S/N): "
if /i not "%confirmar%"=="S" (
    echo.
    echo ❌ Operação cancelada.
    pause
    exit /b 0
)

echo.
echo [1/3] Removendo dependências...
if exist "node_modules" (
    rmdir /s /q "node_modules"
    echo ✅ node_modules removido
) else (
    echo ✅ node_modules não encontrado
)

echo.
echo [2/3] Removendo logs...
if exist "logs" (
    rmdir /s /q "logs"
    echo ✅ logs removido
) else (
    echo ✅ logs não encontrado
)

echo.
echo [3/3] Removendo configurações...
if exist ".env" (
    del /q ".env"
    echo ✅ .env removido
) else (
    echo ✅ .env não encontrado
)
if exist "config.json" (
    del /q "config.json"
    echo ✅ config.json removido
) else (
    echo ✅ config.json não encontrado
)

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║     ✅ DESINSTALAÇÃO CONCLUÍDA!                           ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 📋 Para reinstalar, execute INSTALAR.bat
echo.
pause
