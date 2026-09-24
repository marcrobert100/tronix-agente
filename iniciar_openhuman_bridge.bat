@echo off
echo ==========================================
echo   OpenHuman + Tronix Bridge Starter
echo ==========================================
echo.

:: 1. Sync memory
echo [1/3] Sincronizando memoria...
python "%~dp0openhuman_memoria_sync.py" --once
echo.

:: 2. Generate bridge config
echo [2/3] Gerando bridge config...
python "%~dp0openhuman_composio_setup.py" bridge-config
echo.

:: 3. Show integration guide
echo [3/3] Guia de integracao...
python "%~dp0openhuman_composio_setup.py" configure
echo.

echo ==========================================
echo   Bridge configurado! Proximos passos:
echo   1. Abra o OpenHuman
echo   2. Conecte integracoes via Settings
echo   3. Use voice: "Hey Tiny, status do Tronix"
echo ==========================================
pause
